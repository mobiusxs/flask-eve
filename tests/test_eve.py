def test_app_fixture(app):
    assert app is not None


def test_extensions_applied(app):
    assert 'sqlalchemy' in app.extensions
    assert 'eve' in app.extensions
