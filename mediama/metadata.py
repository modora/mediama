import sqlite3
from typing import List, Tuple, Any, Dict, TypedDict

Metadata = Dict[str, Any]


class SourceMetadata(Metadata):
    name: str


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

        self._resolve_ids(cfg)

    def __setitem__(self, key, value):
        self.set_({key: value}, self.id)

    def __getitem__(self, key: str):
        """
        Return the default value of a key stored in the database
        """
        results = self.get_all(key)
        priority = self._ids.get(key, self._priority)
        if self.id:
            priority.insert(0, self.id)
        for id_ in priority:
            try:
                return results[id_]
            except KeyError:
                continue
        raise KeyError(f"{key} not found in database")

    def _resolve_ids(self, cfg):
        # TODO: parse cfg for id priority order

        # Last > First
        posts_priority = [task.id for task in cfg["posts"]]
        posts_priority.reverse()
        # First > Last
        sources_priority = [task.id for task in cfg["sources"]]
        # Last > First
        pres_priority = [task.id for task in cfg["pres"]]
        pres_priority.reverse()
        self._priority = posts_priority + sources_priority + pres_priority

        # We make a special key mapping for individual keys
        # This is accomplished by placing the remapping at the beginning of
        # the priority list and deleting the old indices
        self._ids = {}
        for key, remapping in cfg["key_sources"]:
            priority = remapping + self._priority
            start_idx = len(remapping)
            for k in remapping:
                idx = priority.index(k, start_idx)
                del priority[idx]
            self._ids.update({key, priority})

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

    def set_(self, data: Dict[str, Any], id_: str):
        if id_ is None:
            raise ValueError("No key specified")
        c = self.conn.cursor()
        c.executemany(
            """
            INSERT INTO pool (id, key, value)
            VALUES (?,?,?)
            """,
            [(id_, key, value) for key, value in data.items()],
        )

    def get_all(self, key: str):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT
                id, value
            FROM
                pool
            WHERE
                key = ?
            """,
            (key,),
        )

        return {id_: value for (id_, value) in c.fetchall()}
