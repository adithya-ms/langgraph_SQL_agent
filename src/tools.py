import pandas as pd
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import logging

def run_query(query: str):
    """
    Run a SQL query and return the results as a pandas DataFrame.
    """
    database_url = "postgresql+psycopg2://adithya@localhost:5432/price_db"
    engine = create_engine(database_url)
    
    return_dict = dict()
    return_dict['output_df'] = pd.DataFrame()  # Initialize empty DataFrame
    return_dict['query'] = query
    return_dict['error_log'] = None
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            
        if df.empty:
            return_dict['error_log'] = "Query returned no results"
        else:
            return_dict['output_df'] = df
            
    except SQLAlchemyError as e:
        # SQLAlchemy specific errors (connection, syntax, etc.)
        return_dict['error_log'] = f"SQLAlchemy Error: {str(e)}"
        logging.error(f"SQLAlchemy Error in query '{query}': {str(e)}")
        
    except pd.errors.DatabaseError as e:
        # Pandas specific database errors
        return_dict['error_log'] = f"Database Error: {str(e)}"
        logging.error(f"Pandas Database Error in query '{query}': {str(e)}")
        
    except Exception as e:
        # Catch any other unexpected errors
        return_dict['error_log'] = f"Unexpected Error: {str(e)}"
        logging.error(f"Unexpected Error in query '{query}': {str(e)}")
        
    finally:
        engine.dispose()

    return return_dict

def get_date_today():
    """
    Returns today's datetime in PostgreSQL-compatible format (ISO 8601).
    """
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d')

if __name__ == "__main__":
    database_url = "postgresql+psycopg2://adithya@localhost:5432/price_db"
    sample_query = "SELECT * FROM price_food_commodities LIMIT 10;"
    results = run_query(sample_query, database_url)
    print(results)