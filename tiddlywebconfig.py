import mangler

config = {
    'log_level': 'DEBUG',
    'server_store': ['tiddlywebplugins.mongodb', {
        'db_config': 'mongodb://localhost:27017/'}],
    'indexer': 'tiddlywebplugins.mongodb',
}