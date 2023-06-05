import json
from flask_sqlalchemy import SQLAlchemy 
from flask_sqlalchemy.model import Model
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, Integer, String, ForeignKey
import hashlib
from urllib import parse
from sqlalchemy.orm import mapped_column, relationship, backref
from tools.tools import url_from_id

# Create the database connection object
db = SQLAlchemy()


class User(db.Model):
    """
    User model
    """
    # Self explanatory
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    name = Column(String(80), nullable=False)

    # the password hash (so we don't store the password in plaintext)
    password_hash = Column(String(128))
    email = Column(String(120), unique=True, nullable=False)

    # the secret for the 2fa (if enabled)
    otp_secret = Column(String(16), nullable=True)
    # if user wants to change their 2fa secret, this is the proposed secret
    proposed_otp_secret = Column(String(16), nullable=True)

    # very high privilege
    admin = Column(Boolean, default=False)

    # the linked tables that the user has interacted with (created collection or liked collection)
    collections = relationship("Collection", back_populates="user")
    likes = relationship("CollectionLike", backref='Collection')

    def __repr__(self):
        """
        String representation of user
        """
        return f'<User {self.username}>'
    
    def to_dict(self, show_recursion=True):
        """
        Convert user to dict (mainly for showing in json api)
        """
        if show_recursion:
            collections = [collection.to_dict(show_recursion=False) for collection in self.collections]
        else:
            collections = [collection.id for collection in self.collections]

        return {
            "id": self.id,
            "username": escape(self.username),
            "name": escape(self.name),
            "gravatar": self.get_gravatar(),
            "admin": self.admin,
            "collections": collections,
            "likes": [like.to_dict() for like in self.likes]
        }
    
    def to_json(self):
        """
        String representation of user in json
        """
        return json.dumps(self.to_dict(show_recursion=False), default=str)
    
    def get_gravatar(self):
        """
        Get gravatar url for the user
        """
        if not self.email: return ''

        email = self.email.encode('utf-8')
        # default = "https://www.example.com/default.jpg"
        default = ""
        size = 128

        # construct the url
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += parse.urlencode({'d':default, 's':str(size), 'r': 'g'})

        return gravatar_url


    def set_password(self, password: str):
        """
        Set password (hash it)
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        """
        Check password (checks hash)
        """
        return check_password_hash(self.password_hash, password)
    
    def get_url(self):
        """
        Gets the url of the user:
        `/user/{id}`
        """
        return f"/user/{self.id}"
    
    def get_url_with_name(self):
        """
        Gets the url of the user:
        `/user/{id}-{username}`
        """
        return f"/user/{url_from_id(self.id, self.username)}"
    
    def get_url_with_username(self):
        """
        Gets the url of the user:
        `/user/@{username}`
        """
        return f"/@{self.username}"



# The items
# 3 options (movie, book, song) - they all have a default collection and then extending (using id)
# Only admins can add new options
class Item(db.Model):
    """
    Item model
    """

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    type = Column(String(255))
    created_timestamp = Column(DateTime)
    updated_timestamp = Column(DateTime)

    # the cover image url for the item
    image_url = Column(String(255))

    # the different types of items as a reference
    movie = relationship('Movie', backref='Item', uselist=False, viewonly=True)
    book = relationship('Book', backref='Item', uselist=False, viewonly=True)
    song = relationship('Song', backref='Item', uselist=False, viewonly=True)

    # the collections that the item is in
    collections = relationship('Collection', secondary='collection_item', back_populates='items', viewonly=True)
    
    # comments on the item
    comments = relationship('ItemComment', backref='Item', viewonly=True)

    def __repr__(self):
        """
        String representation of item
        """
        return f'<Item {self.name}>'
    
    def to_dict(self, collections_full=True):
        """
        Convert item to dict (mainly for showing in json api)

        if `collections_full` is true, then it will show the full collection, otherwise it will just show the id
        """

        if collections_full:
            collections = [collection.to_dict(show_recursion=False) for collection in self.collections]
        else:
            collections = [collection.id for collection in self.collections]
            

        return {
            "id": self.id,
            "name": escape(self.name),
            "type": escape(self.type),
            "description": escape(self.description),
            "movie": self.movie.to_dict() if self.movie else None,
            "book": self.book.to_dict() if self.book else None,
            "song": self.song.to_dict() if self.song else None,
            "collections": collections,
        }
    
    def to_json(self):
        """
        String representation of item in json
        """
        return json.dumps(self.to_dict(), default=str)
    
    def has_collection(self, collection_id):
        """
        Check if item has collection
        """
        return collection_id in [collection.id for collection in self.collections]
    
    def get_url(self):
        """
        Get url of item
        """
        return f'/item/{self.id}'
    
    def get_url_with_name(self):
        """
        Get url of item with id and name
        """
        return f'/item/{url_from_id(self.id, self.name)}'
    
    def get_image_url(self):
        """
        Get image url
        """
        if self.image_url:
            return self.image_url
        else:
            return 'https://placehold.co/600x400/EEE/31343C/?text=No+image+provided'
    

# The specific items: movie, book, song
class Movie(Item):
    """
    Movie model
    """
    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    director = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)

    def __repr__(self):
        """
        String representation of movie
        """
        return f'<Movie {self.name}>'
    
    def to_dict(self):
        """
        Convert movie to dict (mainly for showing in json api)
        """

        return {
            "id": self.id,
            "director": escape(self.director),
            "year": escape(self.year),
            "length": escape(self.length),
        }
    

class Book(Item):
    """
    Book model
    """
    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    author = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    language = Column(Integer, nullable=False)
    country = Column(Integer, nullable=False)

    def __repr__(self):
        """
        String representation of book
        """
        return f'<Book {self.name}>'
    
    def to_dict(self):
        """
        Convert book to dict (mainly for showing in json api)
        """
        return {
            "id": self.id,
            "author": escape(self.author),
            "year": escape(self.year),
            "language": escape(self.language),
            "country": escape(self.country),
        }
    
    
class Song(Item):
    """
    Song model
    """
    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    artist = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)

    def __repr__(self):
        """
        String representation of song
        """
        return f'<Song {self.name}>'
    
    def to_dict(self):
        """
        Convert song to dict (mainly for showing in json api)
        """
        return {
            "id": self.id,
            "artist": escape(self.artist),
            "year": escape(self.year),
            "length": escape(self.length),
        }
    
    
# A collection is a list of items
# A collection can be made up of any type (movie, book, song)
# A collection can be forked (copied) by another user (and the timestamp is saved - so we can suggest update)
# A collection can be liked by another user (and the timestamp is saved)
# A collection can be commented on by another user (and the timestamp is saved)

class Collection(db.Model):
    """
    Collection model
    """

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(80), nullable=False)
    # tag = Column(String(80))

    # forking metadata (is_fork will be true if original collection is deleted)
    forked_from_id = mapped_column(Integer, ForeignKey('collection.id'))
    forked_from = relationship('Collection', remote_side=id, backref='Collection', uselist=False, cascade="all, delete", viewonly=True)
    is_fork = Column(Boolean, default=False, nullable=False)
    
    # timestamps
    created_timestamp = Column(DateTime, nullable=False)
    updated_timestamp = Column(DateTime, nullable=False)

    # the user who created the collection
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='Collection', uselist=False, viewonly=True)
        
    # references to other tables which use this collection
    forks = relationship('Collection', backref=backref('forked_collection', remote_side=[id], overlaps="Collection,forked_from", viewonly=True))
    items = relationship('Item', secondary='collection_item', backref='Collection', viewonly=True)
    comments = relationship('CollectionComment', backref='Collection', viewonly=True)
    likes = relationship('CollectionLike', viewonly=True)    

    def __repr__(self):
        """
        String representation of collection
        """
        return f'<Collection {self.name}>'
    
    def to_dict(self, show_recursion=True):
        """
        Convert collection to dict (mainly for showing in json api)

        if `show_recursion` is true, then show the full collection (including forks and items) otherwise just show the ids
        """

        forked_from = None

        # gets the forks and items in full 
        if show_recursion:
            if self.forked_from:
                forked_from = self.forked_from.to_dict(show_recursion=False)
            forks = [fork.to_dict(show_recursion=False) for fork in self.forks]
            items = [item.to_dict(collections_full=False) for item in self.items]
        
        # just gets the ids
        else:
            if self.forked_from:
                forked_from = self.forked_from.id
            forks = [fork.id for fork in self.forks]
            items = [item.id for item in self.items]
                    
        return {
            "id": self.id,
            "name": escape(self.name),
            "description": escape(self.description),
            "forked_from": forked_from,
            "is_fork": self.is_fork,
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
            "forks": forks,
            "items": items,
            "user": self.user.to_dict(show_recursion=False),
            "user_id": self.user_id,
            "likes": self.get_number_of_likes(),
            
        }
    
    def to_json(self):
        """
        Convert collection to json
        """
        return json.dumps(self.to_dict(), default=str)
    
    def has_item(self, item_id):
        """
        Check if collection has item
        """
        return item_id in [item.id for item in self.items]
    
    def get_number_of_likes(self):
        """
        Get number of likes
        """
        return len(self.likes or [])
    
    def get_url(self):
        """
        Get url
        """
        return f'/collection/{self.id}'
    
    def get_url_with_name(self):
        """
        Get url of collection with id and name
        """
        return f'/collection/{url_from_id(self.id, self.name)}'
    
    def get_image_url(self):
        """
        Uses first item as image
        """
        if self.items:
            # use first item as image
            return self.items[0].get_image_url()
        return 'https://placehold.co/600x400/EEE/31343C/?text=No+image+available'
    
    def user_likes(self, user_id):
        """
        Check if user likes collection
        """
        return user_id in [like.user_id for like in self.likes]


class CollectionItem(db.Model):
    """
    CollectionItem model

    This is a many-to-many relationship between Collection and Item
    """
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('collection.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    added_timestamp = Column(DateTime, nullable=False)    

    def __repr__(self):
        """
        String representation of collection item
        """
        return f'<CollectionItem {self.id}>'
    
    def to_dict(self):
        """
        Convert collection item to dict
        """
        return {
            "id": self.id,
            "collection": self.collection,
            "item": self.item,
            "added_timestamp": self.added_timestamp,
            "message": self.message
        }
    
class CollectionLike(db.Model):
    """
    CollectionLike model

    This is a many-to-many relationship between Collection and User
    """
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('collection.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # reference the collection (useful in templates)
    collection = relationship('Collection', backref='CollectionLike', uselist=False, viewonly=True)
    

    def __repr__(self):
        """
        String representation of collection like
        """
        return f'<CollectionLike {self.id}>'
    
    def to_dict(self):
        """
        Convert collection like to dict
        """
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp
        }
    
class CollectionComment(db.Model):
    """
    CollectionComment model
    """
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('collection.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # the comment that the user made
    comment = Column(String(500), nullable=False)

    # reference the collection (useful in templates)
    user = relationship('User', backref='CollectionComment', uselist=False, viewonly=True)
    

    def __repr__(self):
        """
        String representation of collection comment
        """

        return f'<CollectionComment {self.id}>'
    
    def to_dict(self):
        """
        Convert collection comment to dict
        """
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "user_id": self.user_id,
            "comment": self.comment,
            "timestamp": self.timestamp
        }

    
class ItemComment(db.Model):
    """
    ItemComment model
    """
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # the comment that the user made
    comment = Column(String(500), nullable=False)

    # reference the collection (useful in templates)
    user = relationship('User', backref='ItemComment', uselist=False, viewonly=True)
    

    def __repr__(self):
        """
        String representation of item comment
        """
        return f'<CollectionComment {self.id}>'
    
    def to_dict(self):
        """
        Convert item comment to dict
        """

        return {
            "id": self.id,
            "item_id": self.item_id,
            "user_id": self.user_id,
            "comment": self.comment,
            "timestamp": self.timestamp
        }
