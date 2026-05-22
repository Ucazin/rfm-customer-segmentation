"""
rfm.py — compute Recency / Frequency / Monetary values + scores.
"""

from __future__ import annotations

import pandas as pd


def compute_rfm(transactions: pd.DataFrame,
                snapshot_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Returns one row per customer with columns:
        customer_id, recency_days, frequency, monetary, R, F, M, RFM
    """
    if snapshot_date is None:
        snapshot_date = transactions["invoice_date"].max() + pd.Timedelta(days=1)

    rfm = transactions.groupby("customer_id").agg(
        last_order=("invoice_date", "max"),
        frequency=("invoice", "nunique"),
        monetary=("revenue", "sum"),
    )
    rfm["recency_days"] = (snapshot_date - rfm["last_order"]).dt.days
    rfm = rfm.drop(columns=["last_order"]).reset_index()

    # Quintile scoring — lower recency = higher score
    rfm["R"] = pd.qcut(rfm["recency_days"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"),
                       5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM"] = rfm[["R", "F", "M"]].astype(str).agg("".join, axis=1)

    return rfm


def assign_segment(row: pd.Series) -> str:
    """Map an RFM triplet to a marketing-actionable segment label."""
    r, f, m = int(row["R"]), int(row["F"]), int(row["M"])
    score_fm = (f + m) / 2

    if r == 5 and score_fm >= 4.5:        return "Champions"
    if r >= 4 and score_fm >= 4:          return "Loyal"
    if r == 5 and 2 <= score_fm <= 3.5:   return "Potential Loyalist"
    if r == 5 and score_fm <= 1.5:        return "New Customers"
    if r == 4 and score_fm <= 1.5:        return "Promising"
    if r == 3 and score_fm == 3:          return "Need Attention"
    if r == 3 and score_fm <= 2:          return "About to Sleep"
    if r == 2 and score_fm >= 4:          return "At Risk"
    if r <= 2 and f == 5 and m == 5:      return "Can't Lose Them"
    if r <= 2 and 1.5 <= score_fm <= 3:   return "Hibernating"
    return "Lost"


def add_segment(rfm: pd.DataFrame) -> pd.DataFrame:
    rfm = rfm.copy()
    rfm["segment"] = rfm.apply(assign_segment, axis=1)
    return rfm
