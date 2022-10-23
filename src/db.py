import pandas as pd
import sqlite3

class SQLite():
    def __init__(self, file: pathlib.Path):
        assert file.exists(), f"File {file} does not exist"
        assert file.name.endswith('.sqlite') or file.name.endswith('.db'), \
            f"File {file} is not a SQLite database"
        
        self.file = file

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

    def __repr__(self) -> str:
        return f"SQLite({self.file})"

    def __str__(self) -> str:
        return f"SQLite({self.file})"

    def connect(self):
        self.conn = sqlite3.connect(self.file);
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def commit(self):
        self.conn.commit()

    def execute(self, query):
        if 'select' in query.lower():
            return self.select(query)
        else:
            self.cursor.execute(query)

    def disconnect(self):
        self.conn.close()

    def select(self, query):
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No rows returned for query")
            return None
        else:
            df = pd.DataFrame(rows)
            df.columns = [col[0] for col in self.cursor.description]
            return df

with SQLite(DB_PATH.joinpath('database.sqlite')) as cur:
    print(cur.execute('SELECT sqlite_version();').fetchall()[0][0])