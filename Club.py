import psycopg2
from psycopg2 import Error
from ClubOperation import *
from db import DBConnection

# from MandatoryFunctions import *


def main():
    # Database info
    db = DBConnection()
    db.init_db()
    db.populate_db()
    db.drop_db()


if __name__ == "__main__":
    main()
