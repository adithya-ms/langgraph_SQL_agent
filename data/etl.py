import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine
import os
import argparse

def extract(csv_path: str,
         table_name: str,
         database_url: str,
         if_exists: str = "replace",
         ) -> None:
    """
    Reads a CSV file and writes its contents to a PostgreSQL database table.
    Args:
        csv_path (str): Path to the CSV file.
        table_name (str): Name of the target table in the database.
        database_url (str): SQLAlchemy database URL.
        if_exists (str): Behavior when the table already exists. Options are 'fail', 'replace', 'append'.
    """
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set. Provide a valid SQLAlchemy URL.")

    # Read CSV
    df = pd.read_csv(csv_path)

    # Create engine and write to DB
    engine = create_engine(database_url)
    try:
        with engine.begin() as conn:  # ensures transaction and proper closing
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    finally:
        engine.dispose()

    print(f"Wrote {len(df)} rows to table '{table_name}' in database.")

def transform(database_url: str,
              table_name: str):
    """
    # Example transformation: Convert 'date' column to datetime
    # Read data from database table
    Args:
        df (pd.DataFrame): Input DataFrame to transform.
        database_url (str): SQLAlchemy database URL.
        table_name (str): Name of the target table in the database.
    """
    engine = create_engine(database_url)
    try:
        df = pd.read_sql_table(table_name, engine)
    finally:
        engine.dispose()
    
    df['date'] = pd.to_datetime(df['date'], dayfirst=True).dt.date

    df['product'] = df['product'].str.lower().str.strip()
    df['source'] = df['source'].str.lower().str.strip()
    df['ts_name'] = df['product'] + ' - ' + df['source']

    ###
    # Add any additional transformations here
    ###
    # Write transformed data back to database with new table name
    
    engine = create_engine(database_url)
    try:
        with engine.begin() as conn:
            df.to_sql(f"{table_name}_transform", conn, if_exists="replace", index=False)
    finally:
        engine.dispose()
    
    print(f"Transformed data written to table '{table_name}_transform'.")


def main():
    csv_path = os.path.join("data","case_data.csv")
    table_name = "price_food_commodities"
    database_url = "postgresql+psycopg2://adithya@localhost:5432/price_db"

    extract(csv_path,
         table_name,
         database_url)
    transform(
        database_url,
        table_name
    )

if __name__ == "__main__":
    main()    