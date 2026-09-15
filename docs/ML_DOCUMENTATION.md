# ML Documentation

## Model Cards
- **Low Attendance Detection:** Identifies students at risk based on absence streaks.
- **Outstanding Fees:** Predicts likelihood of delayed payments.

## ETL Pipeline
The pipeline runs via a Celery beat schedule (`run_etl_pipeline` nightly) to load Dimensions and Facts into the warehouse schemas.

## Evaluation & Monitoring
Monitored via `DataQualityScore` metrics on completeness, freshness, and accuracy.
