# RFM Customer Segmentation

> 🌐 **Live walkthrough:** https://ucazin.github.io/rfm-customer-segmentation/

Classical customer segmentation on the [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) dataset — **805,549 transactions** from a UK-based online retailer between **December 2009 and December 2011**, totalling **£17.7M in revenue** across **5,878 customers**.

We compute **RFM scores** (Recency / Frequency / Monetary), tag every customer with a marketable segment (Champions, Loyal, At Risk, Hibernating, Lost, …), and write a **playbook** that ties each segment to a specific marketing action with cost and projected revenue.

The portfolio's **marketing-analytics anchor**. Every e-commerce DA role in the US/Canada market screens for this exact analysis at some point in the interview loop.

## Headline findings

| | Value |
|---|---|
| Transactions analysed | **805,549** |
| Customers | 5,878 |
| Revenue (Dec 2009 – Dec 2011) | **£17.7 M** |
| **Top 5% of customers** | **52% of revenue** |
| Top 11% of customers (Champions + Loyal) | 66% of revenue |
| **Champions alone (609 customers)** | **49.5% of revenue (£8.8 M)** |
| At Risk + Can't Lose Them | 188 customers, **£943k of historical revenue** |
| Quarterly playbook cost | $13.7k |
| Projected retained / new revenue | **$144.7k** |
| **Blended ROI** | **10.5×** |

## Segment composition

| Segment | Customers | Revenue (£) | Avg recency (days) | Share of revenue |
|---|---|---|---|---|
| Champions | 609 | 8,776,444 | 8 | 49.5% |
| Loyal | 715 | 3,465,614 | 30 | 19.5% |
| Lost | 1,892 | 2,981,789 | 225 | 16.8% |
| At Risk | 177 | 845,385 | 289 | 4.8% |
| Hibernating | 1,424 | 783,161 | 430 | 4.4% |
| Potential Loyalist | 356 | 486,430 | 10 | 2.7% |
| Need Attention | 157 | 154,735 | 108 | 0.9% |
| Can't Lose Them | 11 | 97,671 | 470 | 0.6% |
| About to Sleep | 317 | 101,928 | 110 | 0.6% |
| Promising | 143 | 31,658 | 38 | 0.2% |
| New Customers | 77 | 18,613 | 11 | 0.1% |

Full quarterly action plan in [`outputs/PLAYBOOK.md`](outputs/PLAYBOOK.md).

## Business Questions

1. **Who are our Champions** (top 5% of customers by RFM) and how much of total revenue do they represent?
2. **Who is About to Churn** — historically high-value customers whose recency is degrading — and what's the dollar value at risk?
3. **How should we tier our promotional spend?** A £10 coupon to a Champion is wasted; the same coupon to an At-Risk customer can pull back £300 of LTV.
4. **Does k-means produce meaningfully different clusters from rule-based RFM scoring?** If not, RFM wins on explainability.
5. **What's the expected lift** from rolling out the segment-specific playbook for the next quarter?

## Methodology

### Step 1 — RFM Scores

For each customer:
- **R (Recency)** = days since last purchase. Lower is better — split into quintiles, score 1–5 with 5 = most recent.
- **F (Frequency)** = number of distinct orders. Quintile score 1–5.
- **M (Monetary)** = total revenue (negative refunds excluded). Quintile score 1–5.

Concatenated into an `RFM` triplet: `555` = best, `111` = worst.

### Step 2 — Rule-based segments

Eleven canonical segments mapped from RFM triplets (mapping in `src/rfm.py::assign_segment`, matching the Klaviyo / Mailchimp / Putler documentation).

### Step 3 — k-means alternative

Standardised RFM features → silhouette analysis to pick `k` → k-means → cluster profiling. Comparison of the rule-based segments vs the k-means clusters via a crosstab heatmap. Charts in `outputs/03_kmeans_silhouette.png` and `outputs/04_kmeans_vs_rules.png`.

### Step 4 — Playbook + revenue projection

Each segment is assigned a marketing action with:
- A unit cost per customer
- An assumed conversion rate (from Klaviyo / Mailchimp / Optimove benchmarks, documented inline in `src/playbook.py`)
- A retained-or-new revenue per converted customer

Total cost and projected revenue are summed per segment in `outputs/PLAYBOOK.md`.

## Charts

| # | Chart | Source |
|---|---|---|
| 01 | [`01_rfm_distribution.png`](outputs/01_rfm_distribution.png) | Histograms of R / F / M |
| 02 | [`02_segments_heatmap.png`](outputs/02_segments_heatmap.png) | Share of revenue by segment |
| 03 | [`03_kmeans_silhouette.png`](outputs/03_kmeans_silhouette.png) | Silhouette score by k |
| 04 | [`04_kmeans_vs_rules.png`](outputs/04_kmeans_vs_rules.png) | Rule-based segments × k-means cluster |

## Tech Stack

- **Python 3.10+** — pandas, numpy, scikit-learn (k-means + silhouette + scaling), matplotlib, seaborn
- **DuckDB** (optional) — SQL version of the RFM scoring in `sql/rfm.sql` for the SQL-first reviewer
- No paid SaaS or BI license — everything renders to PNG / Markdown.

## Project Structure

```
06-rfm-customer-segmentation/
├── src/
│   ├── load_data.py             # Download + clean Online Retail II
│   ├── rfm.py                   # RFM score computation + segment rules
│   ├── segment.py               # Full pipeline + charts
│   ├── playbook.py              # Marketing actions + ROI projection + memo
│   └── extract_key_numbers.py   # Pull headline numbers for README/MEMO
├── sql/
│   └── rfm.sql                  # SQL version of the same scoring
├── data/                        # Raw + processed (gitignored)
├── outputs/
│   ├── 01_rfm_distribution.png
│   ├── 02_segments_heatmap.png
│   ├── 03_kmeans_silhouette.png
│   ├── 04_kmeans_vs_rules.png
│   └── PLAYBOOK.md              # The marketing playbook memo
├── MEMO.md                      # One-page business memo
├── README.md
├── LICENSE                      # MIT
├── requirements.txt
└── .gitignore
```

## How to run

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1. Download + clean the UCI Online Retail II dataset (~25 MB, ~60 s)
python src/load_data.py

# 2. Compute RFM, segment, k-means alternative, write playbook
python src/segment.py

# Optional: print headline numbers used in this README
python src/extract_key_numbers.py
```

## Skills demonstrated

- **Marketing analytics fundamentals** — RFM is the most-asked DA interview topic for e-commerce / retail roles
- **Clustering** — k-means + silhouette + StandardScaler, with a written justification of method choice
- **Business framing** — every segment is tied to a marketing action and a dollar projection, not just a label
- **SQL + Python parity** — the same scoring is implemented in both `src/rfm.py` and `sql/rfm.sql`
- **Honest assumption-disclosure** — conversion rates are quoted from industry benchmarks and documented inline (in `playbook.py`) so they can be challenged

## Dataset citation

Chen, D. (2019). *Online Retail II* [Data set]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D
