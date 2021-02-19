# encoding: utf-8

import logging
import os
import sys

import psycopg2

from .settings import Database

logger = logging.getLogger("util")
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

current_path = os.path.dirname(os.path.realpath(__file__))


def load_demo_data() -> None:
    """Create DB schema if doesn't exist and load demo data utility.

    Simulate data entry for the websites we wanna collect statistics.
    """
    db = Database()
    demo_data = [
        ("twitter", "https://www.twitter.com"),
        ("amazon", "https://www.amazon.com"),
    ]
    try:
        sql_schema = open(os.path.join(current_path, "db_schema.sql"), "r")
        db.query(sql_schema.read())
    except psycopg2.errors.DuplicateTable:
        logger.error("Table already exists!")
        exit(1)
    for data in demo_data:
        db.query(
            "INSERT INTO public.websites (name, url) VALUES (%s, %s);",
            (data[0], data[1]),
        )
    logger.info("Demo data loaded!")


if __name__ == "__main__":
    globals()[sys.argv[1]]()
