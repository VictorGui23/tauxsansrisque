import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from process_raw_excel import file_to_db_format
from credentials import DB_PARAMS

def load_file(file_as_df, engine, table_name):
    # check connection
    connection = test_connection(engine)
    if connection == 1:
        print("Connection to the database succesful.")
    else:
        print("An error occured while connecting to the database.")
        print(str(connection))
    # check date uniqueness 
    is_date_unique = (file_as_df['date'].nunique() == 1)
    if is_date_unique:
        date = file_as_df['date'].iloc[0]
        print("Only one date in the file. Preparing to load {} into the database.".format(date))
    else:
        print("Error : dates in the file are not unique. Exiting.")
        return
    
    # check date is not already in DB
    date_already_in = check_date(engine, table_name, "date", date)
    if not date_already_in:
        print("Date not already present. Loading data into database.")
        file_as_df.to_sql(table_name, engine, if_exists='append', index=False)
        print("Data loaded in table {}.".format(table_name))
    if date_already_in:
        print("Error : date already present in database. Exiting.")
        return
    return

def check_date(engine, table_name, date_column, date_str):
    try:
        date_local = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("date_str must be in the format 'yyyy-mm-dd'")

    # Create the SQL query
    query = text(f"SELECT 1 FROM {table_name} WHERE {date_column} = :date_local LIMIT 1")
    # Execute the query
    with engine.connect() as connection:
        result = connection.execute(query, {"date_local": date_local})
        return result.fetchone() is not None
    
def test_connection(engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return 1
    except SQLAlchemyError as e:
        return e

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 load_to_db.py file_to_load table_to_load_on")
        sys.exit(1)

    engine = create_engine(f"postgresql+psycopg2://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['database']}")

    path_to_file = sys.argv[1]

    table_name = sys.argv[2]

    file = file_to_db_format(path_to_file)

    load_file(file, engine, table_name)
