"""
A MongoDB-based store for TiddlyWeb

Configure tiddlyweb as follows:

    'server_store': ['tiddlywebplugins.mongodb', {
        'db_config': 'mongodb://localhost:27017/'}],
    'indexer': 'tiddlywebplugins.mongodb'
"""

import logging
import urllib
import simplejson


from pymongo import MongoClient

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User
from tiddlyweb.serializer import Serializer
from tiddlyweb.stores import StorageInterface


LOGGER = logging.getLogger(__name__)


class Store(StorageInterface):
    """
    A store to interact with MongoDB to persist tiddlers, bags, recipes and users.
    It also provides a search interface to query the database.
    """

    def __init__(self, store_config=None, environ=None):
        super(Store, self).__init__(store_config, environ)
        self.serializer = Serializer('json', environ)
        self.init_store()

    def init_store(self):
        client = MongoClient(self.store_config['db_config'])
        self.mongodb_client = client
        self.db = client.tiddlyweb

    def bag_get(self, bag):
        """
        Get a bag from the store and deserialize it into a bag object.
        """
        bag_json = self.db.bags.find_one({'name': bag.name})
        # Remove DB-specific ID before deserialization other wise a TypeError will be raised
        bag_json.pop("_id", None)
        bag_string = simplejson.dumps(bag_json)
        bag = Bag(bag.name)
        self.serializer.object = bag
        self.serializer.from_string(bag_string)
        return bag

    def bag_put(self, bag):
        """
        Put a bag into the store by serializing it to a JSON object
        """
        self.serializer.object = bag
        bag_json = simplejson.loads(self.serializer.to_string())
        # The name needs to be added to the serialization so that it can be found uniquely
        bag_json['name'] = bag.name.encode('ascii', 'ignore')
        self.db.bags.insert(bag_json)

    def list_bags(self):
        """
        List all the bags in the store
        """
        return (Bag(urllib.unquote(bag['name']).decode('utf-8')) for bag in self.db.bags.find())

    def tiddler_put(self, tiddler):
        """
        Write a tiddler into the store by serializing it to a JSON object
        """
        self.serializer.object = tiddler
        # MongoDB can't handle . or $ in key names so replace these with their unicode equivalents
        tiddler_json = simplejson.loads(self.serializer.to_string().replace('$', '\uff04').replace('.', '\uff0e'))
        self.db.tiddlers.insert(tiddler_json)

    def tiddler_get(self, tiddler):
        """
        Get a tiddler from the store and deserialize it into a tiddler object.
        """
        tiddler_json = self.db.tiddlers.find_one({'title': tiddler.title})
        # Remove DB-specific ID before deserialization other wise a TypeError will be raised
        tiddler_json.pop("_id", None)
        tiddler_string = simplejson.dumps(tiddler_json)
        tiddler = Tiddler(tiddler.title, tiddler.bag)
        self.serializer.object = tiddler
        self.serializer.from_string(tiddler_string)
        return tiddler

    def list_bag_tiddlers(self, bag):
        """
        List all the tiddlers from the given bag in the store
        """
        tiddlers = self.db.tiddlers.find({'bag': bag.name})
        for tiddler in tiddlers:
            title = urllib.unquote(tiddler['title']).decode('utf-8')
            tiddler = Tiddler(title, bag.name)
            yield tiddler

    def recipe_put(self, recipe):
        """
        Put a recipe into the store by serializing it to a JSON object
        """
        self.serializer.object = recipe
        recipe_json = simplejson.loads(self.serializer.to_string())
        # The name needs to be added to the serialization so that it can be found uniquely
        recipe_json['name'] = recipe.name.encode('ascii', 'ignore')
        self.db.recipes.insert(recipe_json)

    def list_recipes(self):
        """
        List all the recipes in the store
        """
        return (Recipe(urllib.unquote(recipe['name']).decode('utf-8')) for recipe in self.db.recipes.find())

    def user_put(self, user):
        """
        Put user data into the store.  Converts the user object into JSON first.
        """
        user_dict = {}
        for key in ['usersign', 'note', '_password', 'roles']:
            value = user.__getattribute__(key)
            if key == 'roles':
                user_dict[key] = list(value)
                continue
            if key == '_password':
                key = 'password'
            user_dict[key] = value
        self.db.users.insert(user_dict)

    def list_users(self):
        """
        List all the users in the store
        """
        return (User(urllib.unquote(user['usersign']).decode('utf-8')) for user in self.db.users.find())
