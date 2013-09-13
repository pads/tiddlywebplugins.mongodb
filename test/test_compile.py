def test_compile():
    try:
        import tiddlywebplugins.mongodb

        assert True
    except ImportError, exc:
        assert False, exc
