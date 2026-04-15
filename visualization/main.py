"""
Visualization Module - Creates charts and graphs from the data
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Russian font for matplotlib
plt.rcParams['font.family'] = 'DejaVu Sans'


def create_visualizations():
    """Create visualizations from the data"""
    # Database connection parameters
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ukraine_data')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')

    logger.info("Starting visualization creation...")

    # Create database connection
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)

    # Read data from database
    table_name = 'ukraine_economic_indicators'
    logger.info(f"Reading data from table: {table_name}")
    df = pd.read_sql_table(table_name, engine)

    logger.info(f"Loaded {len(df)} records for visualization")

    # Create plots directory
    plots_dir = '/app/plots'
    os.makedirs(plots_dir, exist_ok=True)

    # Get forecast columns
    forecast_columns_2020 = [col for col in df.columns if '2020' in col and 'сценарій' in col]
    forecast_columns_2021 = [col for col in df.columns if '2021' in col and 'сценарій' in col]

    # Visualization 1: GDP Forecast Comparison (first indicator)
    try:
        logger.info("Creating GDP forecast comparison chart...")
        fig, ax = plt.subplots(figsize=(12, 6))

        # Get first row (GDP data)
        gdp_row = df.iloc[0]

        scenarios = []
        values_2020 = []
        values_2021 = []

        for i in range(1, 4):  # 3 scenarios
            scenario_label = f'Scenario {i}'
            scenarios.append(scenario_label)

            # Get 2020 and 2021 values
            col_2020 = f'Прогноз 2020 сценарій {i}'
            col_2021 = f'Прогноз 2021 сценарій {i}'

            if col_2020 in df.columns:
                val = str(gdp_row[col_2020]).replace(',', '.').replace(' ', '')
                try:
                    values_2020.append(float(val))
                except:
                    values_2020.append(0)

            if col_2021 in df.columns:
                val = str(gdp_row[col_2021]).replace(',', '.').replace(' ', '')
                try:
                    values_2021.append(float(val))
                except:
                    values_2021.append(0)

        x = np.arange(len(scenarios))
        width = 0.35

        bars1 = ax.bar(x - width/2, values_2020, width, label='2020', color='#3498db')
        bars2 = ax.bar(x + width/2, values_2021, width, label='2021', color='#2ecc71')

        ax.set_xlabel('Scenarios', fontsize=12)
        ax.set_ylabel('GDP (billion UAH)', fontsize=12)
        ax.set_title('GDP Forecast Comparison by Scenario (2020 vs 2021)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plot1_path = os.path.join(plots_dir, 'gdp_forecast_comparison.png')
        plt.savefig(plot1_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"GDP comparison chart saved to {plot1_path}")

    except Exception as e:
        logger.error(f"Error creating GDP comparison chart: {e}")

    # Visualization 2: All Indicators Heatmap for Scenario 1
    try:
        logger.info("Creating indicators overview chart...")
        fig, ax = plt.subplots(figsize=(14, 10))

        # Select first 10 indicators and scenario 1 columns
        indicators = df['Показник'].head(10).tolist() if 'Показник' in df.columns else [f'Indicator {i}' for i in range(10)]
        scenario1_cols = [col for col in df.columns if 'сценарій 1' in col]

        if len(scenario1_cols) >= 2:
            # Extract numeric data
            data_matrix = []
            for idx in range(min(10, len(df))):
                row_data = []
                for col in scenario1_cols[:2]:  # 2020 and 2021
                    val = str(df.iloc[idx][col]).replace(',', '.').replace(' ', '')
                    try:
                        row_data.append(float(val))
                    except:
                        row_data.append(0)
                data_matrix.append(row_data)

            data_matrix = np.array(data_matrix)

            # Normalize by row to see relative changes
            normalized_data = np.zeros_like(data_matrix)
            for i in range(len(data_matrix)):
                row_max = data_matrix[i].max()
                if row_max > 0:
                    normalized_data[i] = data_matrix[i] / row_max * 100

            im = ax.imshow(normalized_data, cmap='YlOrRd', aspect='auto')

            # Set ticks
            ax.set_xticks(np.arange(len(scenario1_cols[:2])))
            ax.set_yticks(np.arange(len(indicators)))
            ax.set_xticklabels(['2020', '2021'])
            ax.set_yticklabels([ind[:50] + '...' if len(ind) > 50 else ind for ind in indicators], fontsize=9)

            ax.set_title('Economic Indicators Heatmap (Scenario 1, Normalized)', fontsize=14, fontweight='bold')

            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Relative Value (%)', rotation=270, labelpad=20)

            # Add value annotations
            for i in range(len(indicators)):
                for j in range(len(scenario1_cols[:2])):
                    text = ax.text(j, i, f'{normalized_data[i, j]:.0f}',
                                 ha="center", va="center", color="black", fontsize=8)

            plt.tight_layout()
            plot2_path = os.path.join(plots_dir, 'indicators_heatmap.png')
            plt.savefig(plot2_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Indicators heatmap saved to {plot2_path}")

    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")

    # Visualization 3: Scenario Comparison for Selected Indicator
    try:
        logger.info("Creating scenario comparison line chart...")
        fig, ax = plt.subplots(figsize=(12, 6))

        # Use second indicator (GDP growth rate)
        if len(df) >= 2:
            indicator_row = df.iloc[1]
            indicator_name = indicator_row['Показник'] if 'Показник' in df.columns else 'Indicator 2'

            years = ['2020', '2021']
            for scenario in range(1, 4):
                values = []
                for year in years:
                    col = f'Прогноз {year} сценарій {scenario}'
                    if col in df.columns:
                        val = str(indicator_row[col]).replace(',', '.').replace(' ', '')
                        try:
                            values.append(float(val))
                        except:
                            values.append(None)

                if len(values) == 2:
                    ax.plot(years, values, marker='o', linewidth=2, markersize=8, label=f'Scenario {scenario}')

            ax.set_xlabel('Year', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.set_title(f'Scenario Comparison: {indicator_name[:60]}', fontsize=13, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plot3_path = os.path.join(plots_dir, 'scenario_comparison_line.png')
            plt.savefig(plot3_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Scenario comparison chart saved to {plot3_path}")

    except Exception as e:
        logger.error(f"Error creating scenario comparison: {e}")

    # Save visualization summary
    summary_path = os.path.join(plots_dir, 'visualization_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("VISUALIZATION SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write("Generated Visualizations:\n\n")
        f.write("1. gdp_forecast_comparison.png\n")
        f.write("   - GDP forecast comparison across scenarios (2020 vs 2021)\n")
        f.write("   - Bar chart showing three scenarios\n\n")
        f.write("2. indicators_heatmap.png\n")
        f.write("   - Heatmap of top 10 economic indicators\n")
        f.write("   - Normalized values for Scenario 1\n\n")
        f.write("3. scenario_comparison_line.png\n")
        f.write("   - Line chart comparing all scenarios over time\n")
        f.write("   - Shows GDP growth rate trends\n\n")
        f.write("=" * 60 + "\n")

    logger.info("Visualization creation completed!")


if __name__ == "__main__":
    create_visualizations()
