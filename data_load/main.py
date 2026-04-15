"""
Data Load Module - Loads CSV data into PostgreSQL database
"""
import os
import time
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def wait_for_db(host, port, user, password, database, max_retries=30):
    """Wait for database to be ready"""
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            logger.info("Database is ready!")
            return True
        except psycopg2.OperationalError:
            retries += 1
            logger.info(f"Waiting for database... ({retries}/{max_retries})")
            time.sleep(2)

    raise Exception("Database not available after maximum retries")


def load_csv_to_db():
    """Load CSV data into PostgreSQL"""
    # Database connection parameters from environment
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ukraine_data')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')

    # CSV file path
    csv_path = '/app/data/nabir-16-2020-2021.csv'

    logger.info("Starting data load process...")

    # Wait for database to be ready
    wait_for_db(db_host, db_port, db_user, db_password, db_name)

    # Read CSV file
    logger.info(f"Reading CSV file: {csv_path}")
    for encoding in ("utf-8", "cp1251", "latin-1"):
        try:
            df = pd.read_csv(csv_path, encoding=encoding, sep=None, engine="python")
            logger.info(f"Successfully loaded CSV with encoding={encoding}")
            logger.info(f"Data shape: {df.shape[0]} rows, {df.shape[1]} columns")
            break
        except UnicodeDecodeError:
            continue

    # Clean column names - remove spaces and special characters
    df.columns = df.columns.str.strip()

    # Create database connection
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)

    # Load data to PostgreSQL
    table_name = 'ukraine_economic_indicators'
    logger.info(f"Loading data to table: {table_name}")

    df.to_sql(
        table_name,
        engine,
        if_exists='replace',
        index=False,
        method='multi'
    )

    logger.info(f"Successfully loaded {len(df)} records to {table_name}")

    # Verify data
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.fetchone()[0]
        logger.info(f"Verification: {count} records in database")

    # Save success status
    status_path = '/app/reports/data_load_status.txt'
    os.makedirs('/app/reports', exist_ok=True)
    with open(status_path, 'w', encoding='utf-8') as f:
        f.write(f"Data load completed successfully\n")
        f.write(f"Records loaded: {len(df)}\n")
        f.write(f"Table: {table_name}\n")
        f.write(f"Database: {db_name}\n")

    logger.info("Data load process completed!")


if __name__ == "__main__":
    load_csv_to_db()
