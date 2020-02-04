import MySQLdb
def connection():
    conn = MySQLdb.connect(
        host = "localhost",
        user = "root",
        password = "Dotest123456",
        db = "test_flask"
    )
    c = conn.cursor()
    return c,conn