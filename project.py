from flask import (Flask, render_template,
                   flash, request, redirect, url_for, jsonify)
from flask import make_response
from flask import session as login_session
import random
import string
import httplib2
import json
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, Categories, Items, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from datetime import timedelta

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# create database connection
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login method and create state token for anti-forgery
@app.route('/login')
def showLogin():
    login_session.permanent = True
    state = '' . join(random.choice(string.ascii_uppercase +
                      string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


# Google Sign-In
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameters'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data
    try:
        # Upgrade authorization code into credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                    json.dumps('Failed to upgrade the authorization code.'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check if access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if error in response then abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify Access token is for intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
                    json.dumps("Token user_id does not match given user_id"),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                    json.dumps("Token's client ID does not match app's."),
                    401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if (stored_access_token is not None and
            gplus_id == stored_gplus_id):
            response = make_response(
                        json.dumps('Current user is already connected.'),
                        200)
            response.headers['Content-Type'] = 'application/json'
            return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = getUserId(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Output while logging
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;'
    output += 'height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    # Message displayed on home page once logged.
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Method to get User Id by providing email
def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Method to get User Profile by providing id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Method to create new user
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Method to disconnect, revokes current user's token and resey thier session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
                    json.dumps('Current user not connected.'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        login_session.clear()
        flash('Successfully disconnected!')
        return redirect(url_for('showCategories'))
    else:
        response = make_response(
                        json.dumps('Failed to revoke token for given user.'),
                        400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON way of presenting the catalog
@app.route('/catalog.JSON')
def catalogJSON():
    cat = session.query(Categories).options(joinedload(Categories.items)).all()
    return jsonify(Categories=[dict(category.serialize,
                                    items=[i.serialize
                                           for i in category.items])
                               for category in cat])


# Home Page of catalog
@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = session.query(Categories).all()
    items_all = session.query(Items).all()
    lat_items = items_all[-10:]
    name = []
    for lat in lat_items:
        cat = session.query(Categories).filter_by(id=lat.categories_id).one()
        name.append([str(lat.name), str(cat.name)])
    return render_template("categories.html",
                           categories=categories, latest=name)


# To show items for each category
@app.route('/catalog/<string:category_name>/items')
def showItems(category_name):
    categories = session.query(Categories).all()
    cat = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(categories_id=cat.id).all()
    return render_template("categories.html",
                           categories=categories, items=items,
                           category=cat, length=len(items))


# Provides Description of item
@app.route('/catalog/<string:category_name>/<string:item_name>')
def itemDesc(category_name, item_name):
    cat = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(name=item_name).filter_by(
                                            categories_id=cat.id).one()
    return render_template("item.html", item=item, category=cat)


# To add new Item
@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        cat = session.query(Categories).filter_by(
                                        name=request.form['category']).one()
        newItem = Items(name=request.form['title'],
                        description=request.form['description'],
                        categories_id=cat.id,
                        user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Categories).all()
        return render_template('newItem.html', categories=categories)


# To edit a Item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    cat = session.query(Categories).filter_by(name=category_name).one()
    editItem = session.query(Items).filter_by(name=item_name).filter_by(
                                              categories_id=cat.id).one()
    if request.method == 'POST':
        if request.form['title']:
            editItem.name = request.form['title']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['category']:
            cat = session.query(Categories).filter_by(
                                            name=request.form[
                                                 'category']).one()
            editItem.categories_id = cat.id
        session.add(editItem)
        session.commit()
        return redirect(url_for('itemDesc',
                                category_name=cat.name,
                                item_name=editItem.name))
    else:
        categories = session.query(Categories).all()
        return render_template('editItem.html',
                               item=editItem, category=cat,
                               categories=categories)


# To delete a Item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    cat = session.query(Categories).filter_by(name=category_name).one()
    delItem = session.query(Items).filter_by(name=item_name).filter_by(
                                             categories_id=cat.id).one()
    if request.method == 'POST':
        session.delete(delItem)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteItem.html', item=delItem, category=cat)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.permanent_session_lifetime = timedelta(minutes=5)
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
