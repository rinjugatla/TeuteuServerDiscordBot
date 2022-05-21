import pymysql, pymysql.cursors, os
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const


class DatabaseUtility():
    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(
            host=secret.DB_HOST,
            user=secret.DB_USER,
            password=secret.DB_PASSWORD,
            database=secret.DB_DB_NAME,
            port=secret.DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection.open:
            self.connection.close()

    def re_connect(self):
        if self.connection == None:
            self.connect()
            return

        if not self.connection.open:
            self.connection.ping()
            return

        if self.connection.open:
            self.connect()
            return

    def commit(self):
        if self.connection.open:
            self.connection.commit()

    def close(self):
        if self.connection.open:
            self.connection.close()