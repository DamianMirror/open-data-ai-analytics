"""
Web Interface Module - Flask application to display results
"""
import os
import json
from flask import Flask, render_template, send_from_directory
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)


def get_db_connection():
    """Get database connection"""
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ukraine_data')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')

    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    return create_engine(connection_string)


def load_json_report(filename):
    """Load JSON report if it exists"""
    path = f'/app/reports/{filename}'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_text_report(filename):
    """Load text report if it exists"""
    path = f'/app/reports/{filename}'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/data')
def data():
    """Display database data"""
    try:
        engine = get_db_connection()
        df = pd.read_sql_table('ukraine_economic_indicators', engine)

        # Convert DataFrame to HTML
        table_html = df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('data.html',
                             table=table_html,
                             row_count=len(df),
                             col_count=len(df.columns))
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/quality')
def quality():
    """Display quality analysis results"""
    quality_report = load_json_report('quality_analysis.json')
    quality_text = load_text_report('quality_analysis.txt')

    return render_template('quality.html',
                         report=quality_report,
                         report_text=quality_text)


@app.route('/research')
def research():
    """Display research results"""
    research_report = load_json_report('research_analysis.json')
    research_text = load_text_report('research_analysis.txt')

    return render_template('research.html',
                         report=research_report,
                         report_text=research_text)


@app.route('/visualizations')
def visualizations():
    """Display visualizations"""
    plots_dir = '/app/plots'
    plot_files = []

    if os.path.exists(plots_dir):
        plot_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]

    viz_summary = load_text_report('../plots/visualization_summary.txt')

    return render_template('visualizations.html',
                         plots=plot_files,
                         summary=viz_summary)


@app.route('/plots/<filename>')
def serve_plot(filename):
    """Serve plot images"""
    return send_from_directory('/app/plots', filename)


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
