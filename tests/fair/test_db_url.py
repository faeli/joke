from joke.fair.db_url import connect as db_url_connect


def test_db_url_connect():
    db = db_url_connect('sqlite:///joke.db')
    ret = db.execute_sql("SELECT 1+1").fetchone()
    assert ret[0] == 2