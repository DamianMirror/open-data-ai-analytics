# Changelog

## [0.2.0] - 2026-03-22

### Added
- CI/CD infrastructure using GitHub Actions (Lab 2)
- `requirements.txt`: Project dependencies (pandas, requests, matplotlib, jupyter, notebook)
- `.github/workflows/ci.yml`: Main CI pipeline with matrix strategy
  - Automated testing of all modules (data_load, data_quality_analysis, analysis_and_models, data_visualization)
  - Parallel execution using matrix strategy
  - Jupyter notebooks execution and HTML conversion
  - Artifacts upload (logs, reports, figures)
  - CD: Automatic GitHub Pages deployment on main branch
- `.github/workflows/ci-selfhosted.yml`: Self-hosted runner workflow
  - Manual trigger with module selection
  - Performance metrics collection
  - Local resource access support
- `.github/workflows/ci-paths.yml`: Path-based filtering workflow (bonus)
  - Smart module execution based on changed files
  - Optimized CI resource usage
- `.github/workflows/README.md`: Comprehensive CI/CD documentation
  - Workflows overview and usage instructions
  - Self-hosted runner setup guide
  - GitHub Pages configuration
  - Comparison: GitHub-hosted vs Self-hosted runners

### Changed
- Project now supports automated CI/CD workflows
- All modules can be executed and verified automatically

## [0.1.0] - 2026-02-26

### Added
- Project structure, dataset description and research hypotheses (`README.md`)
- Data loading module (`src/data_load.py`): downloads CSV from data.gov.ua, auto-detects encoding
- Data quality analysis notebook (`notebooks/data_quality_analysis.ipynb`): shape, dtypes, missing values, descriptive statistics
- Analysis & modelling notebook (`notebooks/analysis_and_models.ipynb`):
  - Ukrainian locale number parsing and tidy data reshaping
  - Investigation of 3 research hypotheses with Pearson correlation and scatter plots
  - Linear regression model predicting unemployment from GDP and export growth (R² ≈ 0.97)
  - Correlation heatmap across key indicators
- Data visualization notebook (`notebooks/data_visualization.ipynb`):
  - GDP (nominal and real) by scenario
  - Price indices (CPI, PPI)
  - Labour market: employment and unemployment
  - Wages and real income dynamics
  - Foreign trade: export, import, trade balance
  - Radar chart comparing scenarios
  - Growth dynamics 2020 → 2021
