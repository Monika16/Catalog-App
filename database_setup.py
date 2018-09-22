import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):

	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

class Categories(Base):
	
	__tablename__ = 'categories'

	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=False)

	@property
	def serialize(self):
		return {
			'id' : self.id,
			'name' : self.name
		}

class Items(Base):

	__tablename__ = 'items'

	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=False)
	description = Column(String(450))
	categories_id = Column(Integer, ForeignKey('categories.id'))
	categories = relationship(Categories, backref='items')
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description
		}

engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread': False})

Base.metadata.create_all(engine)



