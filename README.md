# Catalog-App

It is a RESTful web application using the Python framework Flask along with implementing OAuth authentication. It has some Categories and each Category can have n no. of items. After login to the app we can Add Item, Edit Item, Delete Item in a Category.

## Files in the Project
1. project.py - It contains RESTful features using the Python framework Flask and OAuth authentication.
2. database_setup.py - It contains database setup with python DB-API.
3. items.py - It contains data for the database.
4. client_secrets.json - It is JSON file which contains client Id required for authentication.
5. static/styles.css - It contains stylesheet.
6. templates -
   - categories.html - It contains HTML layout of home page
   - item.html - It contains Html layout of item description.
   - newItem.html - It contains form to add item in a Category.
   - editItem.html - It contains form to edit a item.
   - deleteItem.html - It contains Html layout to delete a item.
   - header.html - It contains Html layout for Heading and Login/Layout button.
   - login.html - It contains ajax call for google login button.

## Prerequisites
1. Python 2
2. Vagrant and VirtulBox
3. Google Account to sign-in.

## Execution of project
1. Install Vagrant and VirtulBox
2. Download or clone the project and place it in the same folder as .vagrant
3. Launch Vagrant by `vagrant up` and then `vagrant ssh`
4. Now change the directory to vgrant by `cd /vagrant`
5. Run the file database_setup.py by `python database_setup.py`
6. Run the file items.py to have data in the database by `python items.py`
7. Run the file project.py by `python project.py`
8. Open the browser and with URL "http://localhost:8000/catalog"
9. To view items in a particular Category - Click that particular category.
10. To add, edit or delete any item, we have to login. To login click on the Login button in the Home Page. Now do the Google Sign-In.

## Links in the App
1. "http://localhost:8000/catalog" or "http://localhost:8000/" - Home Page
2. "http://localhost:8000/catalog/<category_name>/items" - Items in category_name
3. "http://localhost:8000/catalog/<category_name>/<item_name>" - item_name description
3. "http://localhost:8000/login - login Page
4. "http://localhost:8000/catalog/new" - Add Item
5. "http://localhost:8000/catalog/<category_name>/<item_name>/edit" - Edit Item
6. "http://localhost:8000/catalog/<category_name>/<item_name>/delete" - Delete Item
