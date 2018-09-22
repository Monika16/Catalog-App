from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categories, Base, Items, User

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

User1 = User(name="Monika Thokala", email="monikathokala16@gmail.com",
				picture="static/smiling-doodle-face.png")
session.add(User1)
session.commit()

category1 = Categories(name="Soccer")
session.add(category1)
session.commit()

item1 = Items(name="Soccer Cleats", 
			  description="Soccer cleats, or what the English call boots,"+
                          " are like baseball or softball cleats but the cleats are short "+
                          "and made of rubber (metal cleats are not allowed)." +
                          "Up to the age of 8 or 9, a child doesn't even need soccer shoes"+
                          " and will do perfectly fine in any type of athletic shoe,"+
                          " as long as it fits and provides good support.",
               categories=category1,
               user = User1)
session.add(item1)
session.commit()

item2 = Items(name="Shin Guards",
			  description="Soccer is definitely a contact sport."+
			              " Shin guards help reduce the chance of injury to the shin (tibia),"+
			              " the third-most likely area of the body to be injured playing soccer,"+
			              " according to a recent study.",
			  categories=category1,
			  user = User1)

session.add(item2)
session.commit()

category2 = Categories(name="Hockey")
session.add(category2)
session.commit()

item1 = Items(name="Stick",
			  description="Your hockey stick is like your weapon on the battlefield."+
			  			  " After choosing the most suitable hockey stick for yourself,"+
			  			  " you will learn to use it and after a while,"+
			  			  " be so comfortable with it that it becomes a part of you.",
			   categories=category2,
			   user = User1)
session.add(item1)
session.commit()

item2 = Items(name="Helmet",
			  description="The helmet protects your head and face from injury."+
			  			  " When you are buying a helmet,"+
			  			  " the most important thing you should"+
			  			  " take note of is that it fits your head comfortably.",
			  categories=category2,
			  user = User1)
session.add(item2)
session.commit()

item3 = Items(name="Throat Protector",
	          description="The throat protector wraps around your neck and is essential"+
	                      " in protecting the goalies throat against fast moving balls.",
	          categories=category2,
	          user = User1)
session.add(item3)
session.commit()

category1 = Categories(name="Basketball")
session.add(category1)
session.commit()

category2 = Categories(name="Baseball")
session.add(category2)
session.commit()

category1 = Categories(name="Frisbee")
session.add(category1)
session.commit()

category2 = Categories(name="Snowboarding")
session.add(category2)
session.commit()

category1 = Categories(name="Rock Climbing")
session.add(category1)
session.commit()

category2 = Categories(name="Football")
session.add(category2)
session.commit()


category1 = Categories(name="Skating")
session.add(category1)
session.commit()

print "added items!!"



