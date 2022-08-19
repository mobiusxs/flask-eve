def test_table_exists(db):
    assert 'user' in db.metadata.tables


def test_columns(db):
    user = db.metadata.tables['user']
    assert user.columns.keys() == [
        'id',
        'modified',
        'session_id',
        'expires_at',
        'token_type',
        'refresh_token',
        'access_token',
        'name',
        'character_id',
    ]


def test_methods_exist(user):
    assert hasattr(user, 'is_authenticated')
    assert hasattr(user, 'portrait_url')
    assert hasattr(user, 'get_auth_header')


def test_is_authenticated(user):
    assert user.is_authenticated is True


def test_get_auth_header(user):
    assert user.get_auth_header() == {'Authorization': 'Bearer access_token'}


def test_save_delete(app, db, user):
    with app.app_context():
        db.create_all()
        assert db.session.query(user.__class__).filter_by(session_id=user.session_id).first() is None
        user.save()
        saved = db.session.query(user.__class__).filter_by(session_id=user.session_id).first()
        assert saved is not None
        saved.delete()
        assert db.session.query(user.__class__).filter_by(session_id=user.session_id).first() is None
