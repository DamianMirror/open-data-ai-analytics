"""
Data Research Module - Performs statistical analysis on the data
"""
import os
import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def perform_data_research():
    """Perform statistical analysis and research on the data"""
    # Database connection parameters
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ukraine_data')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')

    logger.info("Starting data research analysis...")

    # Create database connection
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)

    # Read data from database
    table_name = 'ukraine_economic_indicators'
    logger.info(f"Reading data from table: {table_name}")
    df = pd.read_sql_table(table_name, engine)

    logger.info(f"Loaded {len(df)} records for analysis")

    # Prepare research report
    research_report = {}

    # 1. Basic statistics
    research_report['dataset_overview'] = {
        'total_indicators': len(df),
        'total_columns': len(df.columns),
        'columns': df.columns.tolist()
    }

    # 2. Analyze numeric patterns in forecast columns
    # Extract numeric columns (the forecast columns)
    forecast_columns = [col for col in df.columns if 'Прогноз' in col or 'сценарій' in col]

    numeric_stats = {}
    for col in forecast_columns:
        # Try to convert to numeric, handling Ukrainian number format (comma as decimal separator)
        try:
            # Replace comma with dot and convert to float
            numeric_values = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
            numeric_values = pd.to_numeric(numeric_values, errors='coerce')

            stats = {
                'count': int(numeric_values.notna().sum()),
                'mean': float(numeric_values.mean()) if numeric_values.notna().any() else None,
                'median': float(numeric_values.median()) if numeric_values.notna().any() else None,
                'min': float(numeric_values.min()) if numeric_values.notna().any() else None,
                'max': float(numeric_values.max()) if numeric_values.notna().any() else None,
                'std': float(numeric_values.std()) if numeric_values.notna().any() else None
            }
            numeric_stats[col] = stats
        except Exception as e:
            logger.warning(f"Could not analyze column {col}: {e}")

    research_report['numeric_statistics'] = numeric_stats

    # 3. Analyze indicators
    if 'Показник' in df.columns:
        research_report['indicators_list'] = df['Показник'].tolist()
        research_report['total_unique_indicators'] = len(df['Показник'].unique())

    # 4. Scenario comparison (if applicable)
    scenario_comparison = {}
    for year in ['2020', '2021']:
        year_columns = [col for col in forecast_columns if year in col]
        if len(year_columns) >= 2:
            scenario_comparison[f'year_{year}'] = {
                'scenarios': year_columns,
                'scenario_count': len(year_columns)
            }

    research_report['scenario_analysis'] = scenario_comparison

    # Save JSON report
    reports_dir = '/app/reports'
    os.makedirs(reports_dir, exist_ok=True)

    json_path = os.path.join(reports_dir, 'research_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(research_report, f, indent=2, ensure_ascii=False)

    logger.info(f"Research report saved to {json_path}")

    # Save text report
    text_path = os.path.join(reports_dir, 'research_analysis.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("DATA RESEARCH ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")

        f.write("DATASET OVERVIEW:\n")
        f.write(f"  Total Indicators: {research_report['dataset_overview']['total_indicators']}\n")
        f.write(f"  Total Columns: {research_report['dataset_overview']['total_columns']}\n\n")

        if 'indicators_list' in research_report:
            f.write("ECONOMIC INDICATORS ANALYZED:\n")
            for idx, indicator in enumerate(research_report['indicators_list'], 1):
                f.write(f"  {idx}. {indicator}\n")
            f.write("\n")

        f.write("STATISTICAL ANALYSIS OF FORECAST COLUMNS:\n")
        for col, stats in research_report['numeric_statistics'].items():
            f.write(f"\n  {col}:\n")
            if stats['count'] > 0:
                f.write(f"    - Count: {stats['count']}\n")
                if stats['mean'] is not None:
                    f.write(f"    - Mean: {stats['mean']:.2f}\n")
                if stats['median'] is not None:
                    f.write(f"    - Median: {stats['median']:.2f}\n")
                if stats['min'] is not None:
                    f.write(f"    - Min: {stats['min']:.2f}\n")
                if stats['max'] is not None:
                    f.write(f"    - Max: {stats['max']:.2f}\n")
                if stats['std'] is not None:
                    f.write(f"    - Std Dev: {stats['std']:.2f}\n")
            else:
                f.write(f"    - No numeric data available\n")

        if research_report['scenario_analysis']:
            f.write("\nSCENARIO ANALYSIS:\n")
            for year, info in research_report['scenario_analysis'].items():
                f.write(f"  {year.upper()}:\n")
                f.write(f"    - Number of scenarios: {info['scenario_count']}\n")
                f.write(f"    - Scenarios: {', '.join(info['scenarios'])}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("Research analysis completed successfully!\n")
        f.write("=" * 70 + "\n")

    logger.info(f"Text report saved to {text_path}")
    logger.info("Data research analysis completed!")

    return research_report


if __name__ == "__main__":
    perform_data_research()
