"""Download risk-free series from FRED (no API key) into data/rf/<series>.csv."""
import urllib.request

from blx.wrds import MARKETS
from paths import RF_DIR


def main():
    RF_DIR.mkdir(parents=True, exist_ok=True)
    for key, (_, _, _, _, series) in MARKETS.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
        out = RF_DIR / f"{series}.csv"
        urllib.request.urlretrieve(url, out)
        n = sum(1 for _ in open(out)) - 1
        print(f"{key}: {series} -> {out.name} ({n} rows)")


if __name__ == "__main__":
    main()
