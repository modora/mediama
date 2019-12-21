import sqlite3
from typing import List, Tuple, Any

class VariablePool:
    def __init__(self, cfg: dict, id_: str = None):
        self.cfg = cfg
        self.id = id_
        
        self.conn = sqlite3.connect(":memory:")

        c = self.conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS pool (
                id TEXT NOT NULL,
                key TEXT NOT NULL,
                value BLOB NOT NULL,
                
                PRIMARY KEY(id, key))
            """
        )

    def __setitem__(self, key, value):
        c = self.conn.cursor()
        c.execute(
            """
            INSERT INTO pool (id, key, value)
            VALUES (?,?,?)
            """,
            (self.id, key, value),
        )

    def __getitem__(self, key: str):
        """
        Return the default value of a key stored in the database
        """
        c = self.conn.cursor()
        c.execute(
            """
            SELECT id, value
            FROM pool
            WHERE key = ?
            """,
            (key,),
        )

        if self.cfg is None:
            return c.fetchone()[1]
        results = {id_: value for (id_,value) in c.fetchall() }
        # TODO: implement cfg id resolver

        try:
            return results
        except KeyError:
            raise KeyError(f"{key} not found in database")

    def get(self, key: str, id_: str = None) -> Any:
        if id_ is None:
            return self.__getitem__(key)
        
        c = self.conn.cursor()
        c.execute(
            """
            SELECT
                value
            FROM
                pool
            WHERE
                key = ?
            AND
                id = ?
            """,
            (key, id_),
        )

        result = c.fetchone()
        if result:
            return result[0]  # unpack tuple
        raise KeyError(f"({id_}, {key}) not found in database")

    def set_id(self, id_: str):
        self.id = id_
