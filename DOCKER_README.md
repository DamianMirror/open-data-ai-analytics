# Docker Setup Guide - Lab 3

## Overview

This project implements a containerized multi-service data analytics pipeline for Ukrainian economic forecasts (2020-2021). All services run in Docker containers and communicate through a PostgreSQL database and shared volumes.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Network                   │
│                                                              │
│  ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │  PostgreSQL  │◄───│      data_load                  │   │
│  │   Database   │    │  (CSV → Database)               │   │
│  └──────┬───────┘    └─────────────────────────────────┘   │
│         │                                                    │
│         │            ┌─────────────────────────────────┐   │
│         ├───────────►│  data_quality_analysis          │   │
│         │            │  (Quality checks)               │   │
│         │            └─────────────────────────────────┘   │
│         │                                                    │
│         │            ┌─────────────────────────────────┐   │
│         ├───────────►│  data_research                  │   │
│         │            │  (Statistical analysis)         │   │
│         │            └─────────────────────────────────┘   │
│         │                                                    │
│         │            ┌─────────────────────────────────┐   │
│         ├───────────►│  visualization                  │   │
│         │            │  (Generate charts)              │   │
│         │            └─────────────────────────────────┘   │
│         │                                                    │
│         │            ┌─────────────────────────────────┐   │
│         └───────────►│  web (Flask)                    │   │
│                      │  Port: 5000                     │   │
│                      │  (Display results)              │   │
│                      └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Services

### 1. PostgreSQL Database (`postgres`)
- **Image**: `postgres:15-alpine`
- **Purpose**: Stores economic indicator data
- **Port**: Internal (5432)
- **Health Check**: Automatic readiness check
- **Volume**: `postgres_data` for data persistence

### 2. Data Load (`data_load`)
- **Purpose**: Reads CSV file and loads data into PostgreSQL
- **Dependencies**: Waits for database to be healthy
- **Input**: `/data/raw/nabir-16-2020-2021.csv`
- **Output**: Database table `ukraine_economic_indicators`
- **Status**: `/reports/data_load_status.txt`

### 3. Data Quality Analysis (`data_quality_analysis`)
- **Purpose**: Analyzes data quality (missing values, duplicates, types)
- **Dependencies**: Runs after data_load completes
- **Output**:
  - `/reports/quality_analysis.json`
  - `/reports/quality_analysis.txt`

### 4. Data Research (`data_research`)
- **Purpose**: Performs statistical analysis on economic indicators
- **Dependencies**: Runs after data_load completes
- **Output**:
  - `/reports/research_analysis.json`
  - `/reports/research_analysis.txt`

### 5. Visualization (`visualization`)
- **Purpose**: Generates charts and graphs
- **Dependencies**: Runs after data_load completes
- **Output**: PNG files in `/plots/`
  - `gdp_forecast_comparison.png`
  - `indicators_heatmap.png`
  - `scenario_comparison_line.png`

### 6. Web Interface (`web`)
- **Purpose**: Flask web application to display all results
- **Port**: 5000 (host) → 5000 (container)
- **Dependencies**: Runs after all analysis services complete
- **Health Check**: HTTP endpoint at `/health`
- **Access**: http://localhost:5000

## Quick Start

### Prerequisites
- Docker Desktop installed (Windows/Mac) or Docker Engine (Linux)
- Docker Compose V2
- At least 2GB RAM available for Docker

### Running the Application

1. **Navigate to project directory**:
```bash
cd d:\code\AI\open-data-ai-analytics
```

2. **Build and start all services**:
```bash
docker compose up --build
```

3. **Access the web interface**:
Open browser to http://localhost:5000

4. **Stop all services**:
```bash
docker compose down
```

5. **Stop and remove all data**:
```bash
docker compose down -v
```

## Commands

### Build without starting
```bash
docker compose build
```

### Start in detached mode (background)
```bash
docker compose up -d
```

### View logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs web
docker compose logs data_load

# Follow logs
docker compose logs -f web
```

### Check service status
```bash
docker compose ps
```

### Restart a specific service
```bash
docker compose restart web
```

### Execute commands in a container
```bash
# Access PostgreSQL
docker compose exec postgres psql -U postgres -d ukraine_data

# Access web container shell
docker compose exec web /bin/bash
```

## Configuration

### Environment Variables (`.env`)

```env
# Database
DB_NAME=ukraine_data
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432

# Web Interface
WEB_PORT=5000

# Environment
ENVIRONMENT=development
```

### Customizing Ports

To change the web interface port, edit `.env`:
```env
WEB_PORT=8080
```

Then restart:
```bash
docker compose down
docker compose up
```

## Project Structure

```
open-data-ai-analytics/
├── docker-compose.yaml          # Main orchestration file
├── .env                         # Environment configuration
├── .dockerignore               # Files to exclude from builds
│
├── data/
│   └── raw/
│       └── nabir-16-2020-2021.csv  # Source data
│
├── data_load/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── data_quality_analysis/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── data_research/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── visualization/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── web/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── data.html
│   │   ├── quality.html
│   │   ├── research.html
│   │   ├── visualizations.html
│   │   └── error.html
│   └── static/              # Static assets
│
├── reports/                 # Generated reports (shared volume)
│   ├── data_load_status.txt
│   ├── quality_analysis.json
│   ├── quality_analysis.txt
│   ├── research_analysis.json
│   └── research_analysis.txt
│
├── plots/                   # Generated visualizations (shared volume)
│   ├── gdp_forecast_comparison.png
│   ├── indicators_heatmap.png
│   ├── scenario_comparison_line.png
│   └── visualization_summary.txt
│
└── db/                      # Database init scripts (if any)
```

## Data Flow

1. **Initialization**: PostgreSQL starts and waits until healthy
2. **Data Load**: CSV file is read and imported into database table
3. **Parallel Analysis**: Three analysis services run simultaneously:
   - Quality analysis checks data integrity
   - Research performs statistical analysis
   - Visualization creates charts
4. **Web Interface**: Flask app starts and displays all results

## Troubleshooting

### Port already in use
```bash
# Change WEB_PORT in .env file
WEB_PORT=8080
```

### Services fail to start
```bash
# Check logs
docker compose logs

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Database connection issues
```bash
# Check database health
docker compose ps postgres

# View database logs
docker compose logs postgres

# Access database directly
docker compose exec postgres psql -U postgres -d ukraine_data -c "SELECT COUNT(*) FROM ukraine_economic_indicators;"
```

### Web interface shows "report not found"
```bash
# Check if analysis services completed
docker compose ps

# Restart analysis services
docker compose up data_quality_analysis data_research visualization
```

### Clear all data and start fresh
```bash
docker compose down -v
rm -rf reports/* plots/*
docker compose up --build
```

## Verification

After starting services, verify everything works:

1. **Check all containers are running**:
```bash
docker compose ps
```

Expected output: 6 containers (postgres, data_load, data_quality_analysis, data_research, visualization, web)

2. **Check database has data**:
```bash
docker compose exec postgres psql -U postgres -d ukraine_data -c "SELECT COUNT(*) FROM ukraine_economic_indicators;"
```

Expected: 17 records

3. **Check reports were generated**:
```bash
ls reports/
```

Expected files: `quality_analysis.json`, `quality_analysis.txt`, `research_analysis.json`, `research_analysis.txt`

4. **Check plots were generated**:
```bash
ls plots/
```

Expected files: `*.png` files

5. **Access web interface**:
Open http://localhost:5000 - should see home page with 4 modules

## Advanced Usage

### Running individual services
```bash
# Run only database and data load
docker compose up postgres data_load

# Run only web interface (assumes data already loaded)
docker compose up web
```

### Rebuilding specific service
```bash
docker compose build web
docker compose up -d web
```

### Inspecting volumes
```bash
# List volumes
docker volume ls

# Inspect postgres volume
docker volume inspect open-data-ai-analytics_postgres_data
```

## Security Notes

- Default PostgreSQL password is `postgres` - change for production
- Database is not exposed to host (only internal network)
- Web interface is exposed on port 5000

## Performance

- Initial build: ~3-5 minutes
- Subsequent starts: ~30-60 seconds
- Complete data pipeline: ~10-15 seconds
- RAM usage: ~500MB-1GB total

## Next Steps

- Customize analysis in `data_research/main.py`
- Add more visualizations in `visualization/main.py`
- Enhance web interface in `web/templates/`
- Add authentication to web interface
- Implement data export features
- Add more economic indicators

## Support

For issues or questions:
1. Check logs: `docker compose logs`
2. Verify configuration in `.env`
3. Review this documentation
4. Check Docker installation: `docker --version` and `docker compose version`
