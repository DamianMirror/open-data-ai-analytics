"""
Data Quality Analysis Module - Analyzes data quality from PostgreSQL
"""
import os
import json
import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_data_quality():
    """Analyze data quality: missing values, duplicates, data types"""
    # Database connection parameters
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ukraine_data')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')

    logger.info("Starting data quality analysis...")

    # Create database connection
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)

    # Read data from database
    table_name = 'ukraine_economic_indicators'
    logger.info(f"Reading data from table: {table_name}")
    df = pd.read_sql_table(table_name, engine)

    logger.info(f"Loaded {len(df)} records")

    # Perform quality checks
    quality_report = {}

    # 1. Missing values
    missing_values = df.isnull().sum()
    quality_report['missing_values'] = missing_values.to_dict()
    quality_report['missing_percentage'] = (missing_values / len(df) * 100).to_dict()

    logger.info(f"Missing values check completed")

    # 2. Duplicate rows
    duplicates = df.duplicated().sum()
    quality_report['duplicate_rows'] = int(duplicates)
    quality_report['duplicate_percentage'] = float(duplicates / len(df) * 100)

    logger.info(f"Found {duplicates} duplicate rows")

    # 3. Data types
    quality_report['data_types'] = df.dtypes.astype(str).to_dict()

    # 4. Basic statistics
    quality_report['total_rows'] = len(df)
    quality_report['total_columns'] = len(df.columns)
    quality_report['columns'] = df.columns.tolist()

    # 5. Check for empty strings in object columns
    empty_strings = {}
    for col in df.select_dtypes(include=['object']).columns:
        empty_count = (df[col] == '').sum()
        if empty_count > 0:
            empty_strings[col] = int(empty_count)

    quality_report['empty_strings'] = empty_strings

    # Save JSON report
    reports_dir = '/app/reports'
    os.makedirs(reports_dir, exist_ok=True)

    json_path = os.path.join(reports_dir, 'quality_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, indent=2, ensure_ascii=False)

    logger.info(f"Quality report saved to {json_path}")

    # Save text report
    text_path = os.path.join(reports_dir, 'quality_analysis.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("DATA QUALITY ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Total Rows: {quality_report['total_rows']}\n")
        f.write(f"Total Columns: {quality_report['total_columns']}\n\n")

        f.write("COLUMNS:\n")
        for col in quality_report['columns']:
            f.write(f"  - {col}\n")
        f.write("\n")

        f.write("MISSING VALUES:\n")
        has_missing = False
        for col, count in quality_report['missing_values'].items():
            if count > 0:
                has_missing = True
                pct = quality_report['missing_percentage'][col]
                f.write(f"  - {col}: {count} ({pct:.2f}%)\n")
        if not has_missing:
            f.write("  No missing values found.\n")
        f.write("\n")

        f.write(f"DUPLICATE ROWS: {quality_report['duplicate_rows']} ")
        f.write(f"({quality_report['duplicate_percentage']:.2f}%)\n\n")

        f.write("DATA TYPES:\n")
        for col, dtype in quality_report['data_types'].items():
            f.write(f"  - {col}: {dtype}\n")
        f.write("\n")

        if quality_report['empty_strings']:
            f.write("EMPTY STRINGS:\n")
            for col, count in quality_report['empty_strings'].items():
                f.write(f"  - {col}: {count}\n")
            f.write("\n")

        f.write("=" * 60 + "\n")
        f.write("Analysis completed successfully!\n")
        f.write("=" * 60 + "\n")

    logger.info(f"Text report saved to {text_path}")
    logger.info("Data quality analysis completed!")

    return quality_report


if __name__ == "__main__":
    analyze_data_quality()
