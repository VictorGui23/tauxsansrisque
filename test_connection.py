from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from credentials import DB_PARAMS
import sys


def test_connection(engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Connection successful!")
            for row in result:
                print(row)
    except SQLAlchemyError as e:
        print("An error occured while connecting to the database:")
        print(str(e))

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("Usage: python3 test_connection.py")

    engine = create_engine(f"postgresql+psycopg2://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['database']}")

    test_connection(engine)
