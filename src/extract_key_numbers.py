"""extract_key_numbers.py — pull headline numbers for README and MEMO."""

import pandas as pd

tx  = pd.read_parquet("data/transactions.parquet")
rfm = pd.read_parquet("data/rfm.parquet")

print("\n--- Dataset ---")
print(f"Transactions: {len(tx):,}")
print(f"Customers:    {tx['customer_id'].nunique():,}")
print(f"Revenue GBP:  £{tx['revenue'].sum():,.0f}")
print(f"Date range:   {tx['invoice_date'].min().date()} to {tx['invoice_date'].max().date()}")

print("\n--- Segment counts ---")
print(rfm['segment'].value_counts().to_string())

print("\n--- Revenue concentration ---")
top_pct = rfm.copy().sort_values("monetary", ascending=False)
total = top_pct["monetary"].sum()
for pct in (5, 11, 20, 50):
    n = int(round(len(top_pct) * pct / 100))
    share = top_pct.head(n)["monetary"].sum() / total
    print(f"Top {pct:>3}% of customers ({n:>5} ppl): {share*100:.1f}% of revenue")

print("\n--- Revenue by segment ---")
seg_rev = (rfm.groupby("segment")
              .agg(customers=("customer_id", "count"),
                   revenue=("monetary", "sum"),
                   avg_recency=("recency_days", "mean"))
              .sort_values("revenue", ascending=False))
seg_rev["pct_revenue"] = seg_rev["revenue"] / seg_rev["revenue"].sum() * 100
print(seg_rev.round(1).to_string())

print("\n--- At-risk dollars ---")
at_risk = rfm[rfm['segment'].isin(['At Risk', "Can't Lose Them"])]
print(f"At Risk + Can't Lose Them customers: {len(at_risk)}")
print(f"Their historical revenue: £{at_risk['monetary'].sum():,.0f}")
