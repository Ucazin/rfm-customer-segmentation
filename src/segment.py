"""
segment.py — full segmentation pipeline.

1.  Load cleaned transactions
2.  Compute RFM
3.  Assign rule-based segments
4.  Fit k-means on standardized RFM features, choose k by silhouette
5.  Produce charts + the playbook memo
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from playbook import build_playbook, write_memo
from rfm      import add_segment, compute_rfm

DATA = Path("data")
OUT  = Path("outputs"); OUT.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.dpi"] = 110


def chart_rfm_distribution(rfm: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, (col, title, log) in zip(axes,
        [("recency_days", "Recency (days)", False),
         ("frequency",    "Frequency (orders)", True),
         ("monetary",     "Monetary (£)",        True)]):
        sns.histplot(rfm[col].clip(upper=rfm[col].quantile(0.99)),
                     bins=40, ax=ax, color="#2E86AB")
        ax.set_title(title)
        ax.set_xlabel("")
        if log:
            ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(OUT / "01_rfm_distribution.png")
    plt.close(fig)


def chart_segment_heatmap(rfm: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(13, 8))
    order = (rfm.groupby("segment")["monetary"]
                 .sum()
                 .sort_values(ascending=False)
                 .index.tolist())
    seg_summary = (rfm.groupby("segment")
                       .agg(customers=("customer_id", "count"),
                            avg_monetary=("monetary", "mean"),
                            total_revenue=("monetary", "sum"))
                       .reindex(order))
    seg_summary["pct_revenue"] = seg_summary["total_revenue"] / seg_summary["total_revenue"].sum()
    sns.barplot(data=seg_summary.reset_index(),
                y="segment", x="pct_revenue",
                palette="Blues_r", ax=ax)
    ax.set_xlim(0, seg_summary["pct_revenue"].max() * 1.15)
    ax.set_title("Share of Total Revenue by Segment")
    ax.set_xlabel("Share of revenue")
    ax.set_ylabel("")
    for i, (_, row) in enumerate(seg_summary.iterrows()):
        ax.annotate(f"{row['customers']:,} cust  |  £{row['total_revenue']:,.0f}",
                    xy=(row["pct_revenue"], i),
                    xytext=(5, 0), textcoords="offset points",
                    va="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "02_segments_heatmap.png")
    plt.close(fig)


def chart_silhouette(rfm: pd.DataFrame, max_k: int = 8) -> int:
    X = StandardScaler().fit_transform(rfm[["recency_days", "frequency", "monetary"]])
    scores = {}
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(X)
        scores[k] = silhouette_score(X, km.labels_)
    best_k = max(scores, key=scores.get)

    fig, ax = plt.subplots(figsize=(9, 5))
    pd.Series(scores).plot(kind="bar", color="#2E86AB", ax=ax)
    ax.set_title("Silhouette score by k (higher = better-separated clusters)")
    ax.set_xlabel("k")
    ax.set_ylabel("Silhouette")
    ax.axvline(best_k - 2, color="#C73E1D", linestyle="--", alpha=0.6)
    ax.annotate(f"best k = {best_k}", xy=(best_k - 2, scores[best_k]),
                xytext=(best_k - 2 + 0.3, scores[best_k]),
                color="#C73E1D")
    fig.tight_layout()
    fig.savefig(OUT / "03_kmeans_silhouette.png")
    plt.close(fig)
    return best_k


def chart_kmeans_vs_rules(rfm: pd.DataFrame, k: int) -> None:
    X = StandardScaler().fit_transform(rfm[["recency_days", "frequency", "monetary"]])
    rfm = rfm.copy()
    rfm["kmeans"] = KMeans(n_clusters=k, n_init="auto", random_state=42).fit_predict(X)

    crosstab = pd.crosstab(rfm["segment"], rfm["kmeans"], normalize="index")
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.heatmap(crosstab, annot=True, fmt=".0%", cmap="Blues", ax=ax)
    ax.set_title("Rule-based segment vs k-means cluster\n(row-normalized — share of each rule segment going to each cluster)")
    ax.set_ylabel("Rule-based segment")
    ax.set_xlabel("k-means cluster")
    fig.tight_layout()
    fig.savefig(OUT / "04_kmeans_vs_rules.png")
    plt.close(fig)


def main() -> None:
    tx = pd.read_parquet(DATA / "transactions.parquet")
    print(f"Transactions: {len(tx):,} rows, "
          f"{tx['customer_id'].nunique():,} customers, "
          f"date range {tx['invoice_date'].min().date()} → {tx['invoice_date'].max().date()}")

    rfm = compute_rfm(tx)
    rfm = add_segment(rfm)
    rfm.to_parquet(DATA / "rfm.parquet", index=False)

    print("\nSegment counts:")
    print(rfm["segment"].value_counts().to_string())

    chart_rfm_distribution(rfm)
    chart_segment_heatmap(rfm)
    best_k = chart_silhouette(rfm)
    chart_kmeans_vs_rules(rfm, best_k)

    playbook = build_playbook(rfm)
    print("\nPlaybook summary:")
    print(playbook.to_string(index=False))
    write_memo(playbook, OUT / "PLAYBOOK.md")
    print(f"\nMemo written → {OUT / 'PLAYBOOK.md'}")


if __name__ == "__main__":
    main()
