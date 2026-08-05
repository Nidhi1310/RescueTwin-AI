# Synthetic flood data pipeline

`data/generate_flood_dataset.py` creates a deterministic CSV for future flood-model training. The default output contains 1,200 rows, enough for a small baseline model while remaining quick to generate.

## Columns

| Column | Range |
| --- | --- |
| `rainfall_mm` | 0–320 mm |
| `elevation_m` | 55–110 m |
| `drainage_score` | 1–10, where 10 is best drainage |
| `previous_water_level_m` | 0–4 m |
| `flood_severity` | 0–100 target label |

Validation checks schema, missing values, all feature/target ranges, and the low/medium/high target-label distribution. Generation is deterministic for the same sample count and seed.

```powershell
python data/generate_flood_dataset.py --samples 1200 --seed 20260805
```
