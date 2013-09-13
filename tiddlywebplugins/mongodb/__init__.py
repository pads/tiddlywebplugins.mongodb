"""
A MongoDB-based store for TiddlyWeb

Configure tiddlyweb as follows:

    'server_store': ['tiddlywebplugins.mongodb', {
        'db_config': 'mongodb://localhost:27017/'}],
    'indexer': 'tiddlywebplugins.mongodb'
"""

import logging
import simplejson


from pymongo import MongoClient

from tiddlyweb.model.bag import Bag
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
        self.serializer = Serializer('json')
        print self.serializer.environ
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
        print bag_json
        bag_string = simplejson.dumps(bag_json)
        print bag_string
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

    def tiddler_put(self, tiddler):
        """
        Write a tiddler into the store by serializing it to a JSON object
        """
        self.serializer.object = tiddler
        # TODO: figure out why the serializer.to_string() call
        # is throwing a tiddlyweb.config KeyError further down the stack
        tiddler_json = simplejson.loads(self.serializer.to_string())
        self.db.tiddlers.insert(tiddler_json)
