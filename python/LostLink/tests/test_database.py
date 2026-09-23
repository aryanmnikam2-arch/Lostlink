from database import get_db, init_db

def test_database_initializes():
    init_db()
    db = get_db()
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='items'"
    ).fetchone()
    db.close()
    assert tables is not None
