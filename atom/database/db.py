import sqlite3

from collections import namedtuple
from pathlib import Path

from atom.core.io import path_utils


def namedtuple_factory(cursor, row):
    """ Returns a named tuple when retrieving rows. """
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)


# <editor-fold desc="Base Database Methods">
def get(
        table: str,
        col: str,
        val: int,
        db: Path | str,
        one_or_none: bool = False
) -> list:
    """
    Queries the database and returns one or none entries.

    Parameters
    ----------
    table : str
        The table name to query.

    col : str
        The column name containing `val`.

    val : int
        The value to check.

    db : Path or str, optional, default=None
        The path to the database file, or `:memory:`. If not provided,
        defaults to `path_utils.database_path()`.

    one_or_none: bool, optional, default=False
        If ``True``, only returns one or none entries. In the event that the
        query results in multiple entries and `one_or_none=True`, then only
        the first entry is returned.

    Returns
    -------
    namedtuple or None
        The row corresponding to `row_id`.

    See Also
    --------
    ``atom.core.io.path_utils.database_path()``
    """
    if db is None:
        db = path_utils.database_path()

    q = f"SELECT * FROM {table} WHERE {col} = ?"

    with sqlite3.connect(db) as con:
        con.row_factory = namedtuple_factory
        cursor = con.cursor()
        cursor.execute(q, (val,))

        return cursor.fetchone() if one_or_none else cursor.fetchall()


def add(table: str, data: dict, db: Path | str = None) -> int:
    """
    Queries the database and returns one or none entries.

    Parameters
    ----------
    table : str
        The table name to query.

    data: dict
        Key, value pairs of the col, value for the table. Auto-generated
        and nullable columns may be omitted.

    db : Path or str, optional, default=None
        The path to the database file, or `:memory:`. If not provided,
        defaults to `path_utils.database_path()`.

    Returns
    -------
    int
        The row ID for the added entry.

    See Also
    --------
    ``atom.core.io.path_utils.database_path()``
    """
    if db is None:
        db = path_utils.database_path()

    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    with sqlite3.connect(db) as con:
        cursor = con.cursor()
        cursor.execute(q, tuple(data.values()))
        return cursor.lastrowid


def update(table: str, row: int, data: dict, db: Path | str = None):
    """
    Updates the database and returns one or none entries.

    Parameters
    ----------
    table : str
        The table name to query.

    row : int
        The row ID to update.

    data: dict
        Key, value pairs of the col, value for the table. Auto-generated
        and nullable columns may be omitted.

    db : Path or str, optional, default=None
        The path to the database file, or `:memory:`. If not provided,
        defaults to `path_utils.database_path()`.

    See Also
    --------
    ``atom.core.io.path_utils.database_path()``
    """
    if db is None:
        db = path_utils.database_path()

    set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
    q = f"UPDATE {table} SET {set_clause} WHERE id = {row}"

    with sqlite3.connect(db) as con:
        cursor = con.cursor()
        cursor.execute(q, tuple(data.values()))
# </editor-fold>


class Notice:
    """ API for interacting with the notice table. """
    def __init__(self):
        pass

    @staticmethod
    def get(
            col: str,
            val,
            db: Path | str = None,
            one_or_none: bool = False
    ):
        """
        Queries the notice table and returns the matching entries.

        Parameters
        ----------
        col : int
            The `response` row ID.

        val : Any
            The value to check.

        db : Path or str, optional, default=None
            The path to the database file, or `:memory:`. If not provided,
            the sub-method ``get`` defaults to `path_utils.database_path()`.

        one_or_none: bool, optional, default=False
            If ``True``, only returns one or none entries. In the event that the
            query results in multiple entries and `one_or_none=True`, then only
            the first entry is returned.

        Returns
        -------
        NamedTuple or list of NamedTuple or None
            The database entries corresponding to the `col` and `val` args.
        """
        return get('notice', col, val, db, one_or_none)

    @staticmethod
    def add(notice, transient_id: int, db: Path | str = None) -> int:
        """
        Add an entry to the notice table.

        Parameters
        ----------
        notice : `atom.responders.<responder>.<responder>`
            The notice to add.

        transient_id : int
            The transient ID that the notice corresponds to.

        db : Path or str, optional, default=None
            The path to the database file, or `:memory:`. If not provided,
            defaults to `path_utils.database_path()`.

        Returns
        -------
        int
            The ID of the new entry.
        """
        data = {
            'trigger_id' : notice.id,
            'transient_id' : transient_id,
            'trigger_time' : notice.event_time,
            'observatory' : notice.observatory,
            'instrument' : notice.instrument,
            'ra_deg' : notice.coords.ra.deg,
            'dec_deg' : notice.coords.dec.deg,
            'pos_error_deg' : notice.coords_error_deg
        }
        return add('notice', data, db)


class Response:
    """ API for interacting with the response table. """
    def __init__(self):
        pass

    @staticmethod
    def get(col: str, val, db: Path | str = None, one_or_none: bool = False):
        """
        Queries the database and returns one or none entries.

        Parameters
        ----------
        col : int
            The `response` row ID.

        val : Any
            The value to check.

        db : Path or str, optional, default=None
            The path to the database file, or `:memory:`. If not provided,
            defaults to `path_utils.database_path()`.

        one_or_none: bool, optional, default=False
            If ``True``, only returns one or none entries. In the event that the
            query results in multiple entries and `one_or_none=True`, then only
            the first entry is returned.

        Returns
        -------
        namedtuple or None
            The row corresponding to `row_id`.
        """
        return get('response', col, val, db, one_or_none)

    @staticmethod
    def add(obs_id: int, transient_id: int, db: Path | str = None) -> int:
        """
        Adds the follow-up observation to the `response` table.

        Parameters
        ----------
        obs_id : int
            The notice object.

        transient_id : int
            The notice object.

        db : Path or str, optional, default=None
            The path to the database file, or `:memory:`. If not provided,
            defaults to `path_utils.database_path()`.

        Returns
        -------
        int
            The row ID for the response entry.
        """
        data = {
            'obs_id': obs_id,
            'transient_id': transient_id
        }
        return add('response', data, db)


class Transient:
    """ API for interacting with the transient table. """
    def __init__(self):
        pass

    @staticmethod
    def get(col: str, val, db: Path | str = None, one_or_none: bool = False):
        """"""
        return get('transient', col, val, db, one_or_none)

    @staticmethod
    def add(notice, db: Path | str = None) -> int:
        """"""
        data = {
            'event_time': notice.event_time,
            'ra_deg': notice.coords.ra.deg,
            'dec_deg': notice.coords.dec.deg,
            'pos_error_deg': notice.coords_error_deg,
            'astrophysical': int(notice.astrophysical)
        }
        return add('transient', data, db)

    @staticmethod
    def update(transient_id: int, notice, db: Path | str = None):
        """"""
        data = {
            'ra_deg': notice.coords.ra.deg,
            'dec_deg': notice.coords.dec.deg,
            'pos_error_deg': notice.coords_error_deg
        }
        return update('transient', transient_id, data, db)

    @staticmethod
    def set_false_alarm(transient_id: int, db: Path | str = None):
        """"""
        data = {'astrophysical': 0}
        return update('transient', transient_id, data, db)

    @staticmethod
    def search(
            ra_deg: float,
            dec_deg: float,
            range_deg: float,
            start_time: str,
            end_time: str,
            db: Path | str = None,
            one_or_none: bool = False
    ) -> list | None:
        """
        Searches for transient entries within a location and time range.

        Parameters
        ----------
        ra_deg : float
            The right ascension measured in degrees.

        dec_deg : float
            The declination measured in degrees.

        range_deg
            The search range measured in degrees.

        start_time : str | datetime.datetime
            The 8601 ISO format datetime to begin searching.

        end_time : str | datetime.datetime
            The 8601 ISO format datetime to end searching.

        db : Path or str, optional, default=None
            The path to the database file, or `:memory:`. If not provided,
            will read the database at `path_utils.database_path()`.

        one_or_none: bool, optional, default=False
            If ``True``, only returns one or none entries. In the event that the
            query results in multiple entries and `one_or_none=True`, then only
            the first entry is returned.

        Returns
        -------
        NamedTuple or list of NamedTuple or None
            The matching transient entries.
        """
        if db is None:
            db = path_utils.database_path()

        # Calculate RA and Dec ranges
        ra_min = ra_deg - range_deg
        ra_max = ra_deg + range_deg
        dec_min = dec_deg - range_deg
        dec_max = dec_deg + range_deg

        # Adjust RA range for wraparound at 0° and 360°
        ra_conditions = []
        if ra_min < 0:
            ra_conditions.append("(ra_deg BETWEEN 0 AND ? OR ra_deg BETWEEN ? AND 360)")
        elif ra_max > 360:
            ra_conditions.append("(ra_deg BETWEEN 0 AND ? OR ra_deg BETWEEN ? AND 360)")
        else:
            ra_conditions.append("ra_deg BETWEEN ? AND ?")

        # Build SQL query dynamically
        q = f"""
            SELECT *
            FROM transient
            WHERE event_time BETWEEN ? AND ?
              AND {" OR ".join(ra_conditions)}
              AND dec_deg BETWEEN ? AND ?
            """

        # Parameters for the query
        if ra_min < 0:
            params = [start_time, end_time, ra_max, 360 + ra_min, dec_min, dec_max]
        elif ra_max > 360:
            params = [start_time, end_time, ra_max - 360, ra_min, dec_min, dec_max]
        else:
            params = [start_time, end_time, ra_min, ra_max, dec_min, dec_max]

        # Execute query
        with sqlite3.connect(db) as con:
            con.row_factory = namedtuple_factory
            cursor = con.cursor()
            cursor.execute(q, params)

            return cursor.fetchone() if one_or_none else cursor.fetchall()
