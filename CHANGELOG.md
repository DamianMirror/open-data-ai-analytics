# Changelog

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
