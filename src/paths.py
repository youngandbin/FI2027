"""Repository paths, resolved from the repository root so scripts run from any directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
WRDS_DIR = DATA_DIR / "wrds"        # CRSP / Compustat Global parquet files (not in git)
RF_DIR = DATA_DIR / "rf"            # FRED risk-free series
VIEWS_DIR = DATA_DIR / "views"      # LLM draws, one JSON per (market, model, prompt, date)
RESULTS_DIR = ROOT / "results"
