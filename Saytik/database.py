"""
============================================================
  database.py  —  JSON File "Database" Helper
============================================================

WHAT THIS FILE DOES:
  Since we are not using a real database (like PostgreSQL or
  SQLite), we simulate one using plain .json files stored in
  the  data/  folder.

  This module exposes two functions that every router can
  import and use:
    • read_db(filename)   → loads JSON → returns Python list
    • write_db(filename, data) → saves Python list → JSON file

WHY A SEPARATE FILE?
  If we copy-pasted these functions into every router, any
  bug fix would need to be applied in multiple places.
  Centralising them here (DRY principle: Don't Repeat Yourself)
  means we fix or change things in exactly one place.

FILE LAYOUT ASSUMED:
  project/
  ├── main.py
  ├── database.py        ← this file
  ├── routers/
  │   ├── __init__.py
  │   ├── posts.py
  │   └── comments.py
  └── data/
      ├── posts.json
      └── comments.json
"""

import json       # Python's built-in JSON encoder/decoder
import os         # For checking if a file exists

# ----------------------------------------------------------
# Where the JSON "database" files live.
# os.path.dirname(__file__) gives the directory of this
# very file, so the path works regardless of where you
# run the server from.
# ----------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def read_db(filename: str) -> list:
    """
    Load and return the contents of a JSON database file.

    Parameters
    ----------
    filename : str
        The name of the JSON file, e.g. "posts.json"

    Returns
    -------
    list
        A Python list of dicts (each dict = one record).
        Returns an empty list [] if the file doesn't exist yet.

    HOW IT WORKS:
        1. Build the full file path.
        2. If the file doesn't exist, return [] so callers
           don't crash on a missing file.
        3. Open the file in read mode ("r") with UTF-8 encoding.
        4. json.load() parses the JSON text into a Python object.
    """
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_db(filename: str, data: list) -> None:
    """
    Persist a Python list back to a JSON database file.

    Parameters
    ----------
    filename : str
        The name of the JSON file, e.g. "posts.json"
    data : list
        The full list of records to save.

    HOW IT WORKS:
        1. Make sure the data/ directory exists (creates it
           if missing — helpful on first run).
        2. Open the file in write mode ("w"). This OVERWRITES
           the entire file — just like a simple DB commit.
        3. json.dump() serialises the Python list to JSON text.
           indent=2 makes it human-readable (pretty-printed).

    NOTE ON SAFETY:
        Writing the whole file every time is fine for a
        learning project. A real DB uses transactions and
        atomic writes to avoid data corruption.
    """
    os.makedirs(DATA_DIR, exist_ok=True)   # create data/ if needed
    path = os.path.join(DATA_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
