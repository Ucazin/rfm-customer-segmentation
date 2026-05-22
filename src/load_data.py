"""
load_data.py — download + clean the UCI Online Retail II dataset.

Outputs data/transactions.parquet with one row per line item.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

DATA = Path("data"); DATA.mkdir(exist_ok=True)
URL  = ("https://archive.ics.uci.edu/static/public/502/"
        "online+retail+ii.zip")
RAW  = DATA / "online_retail_II.xlsx"
OUT  = DATA / "transactions.parquet"


def download() -> Path:
    if RAW.exists():
        print(f"Already downloaded: {RAW}")
        return RAW
    print(f"Downloading from {URL} ...")
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    zip_path = DATA / "online_retail_II.zip"
    zip_path.write_bytes(r.content)
    # The zip contains a single .xlsx
    import zipfile
    with zipfile.ZipFile(zip_path) as zf:
        member = [n for n in zf.namelist() if n.endswith(".xlsx")][0]
        with zf.open(member) as src, open(RAW, "wb") as dst:
            dst.write(src.read())
    zip_path.unlink()
    return RAW


def clean(raw: Path) -> pd.DataFrame:
    print("Reading both sheets of the workbook (this takes ~30 s)...")
    a = pd.read_excel(raw, sheet_name="Year 2009-2010")
    b = pd.read_excel(raw, sheet_name="Year 2010-2011")
    df = pd.concat([a, b], ignore_index=True)
    print(f"Raw rows: {len(df):,}")

    # Normalize columns
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    rename = {"customer_id": "customer_id", "invoice": "invoice",
              "stockcode":  "stock_code",  "invoicedate": "invoice_date"}
    df.rename(columns=rename, inplace=True)

    # Drop rows without a customer (guest checkouts) — RFM needs a customer
    df = df.dropna(subset=["customer_id"])
    df["customer_id"] = df["customer_id"].astype(int).astype(str)

    # Filter cancellations (invoice starting with "C") and negative quantities
    df = df[~df["invoice"].astype(str).str.startswith("C")]
    df = df[(df["quantity"] > 0) & (df["price"] > 0)]

    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["revenue"] = (df["quantity"] * df["price"]).round(2)

    # Force mixed-type object columns (stock_code, invoice, country, description)
    # to string so pyarrow can serialize them deterministically.
    for col in ("stock_code", "invoice", "country", "description"):
        if col in df.columns:
            df[col] = df[col].astype(str)

    df.to_parquet(OUT, index=False)
    print(f"Clean rows: {len(df):,}  →  {OUT}")
    return df


def main() -> None:
    raw = download()
    clean(raw)


if __name__ == "__main__":
    main()
