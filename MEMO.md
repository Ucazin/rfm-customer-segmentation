# Memo — 49.5% of revenue rides on 609 customers

**To:** Head of Marketing, VP of Customer Retention
**From:** Lucca Cesar, Data Analyst
**Re:** Where the next promotional dollar belongs

## Question

Across 5,878 customers and £17.7M in revenue over two years (UCI Online Retail II), how concentrated is our customer revenue, and how should we tier promotional spending?

## Finding

The revenue is extraordinarily top-heavy:

| Customer slice | Customers | Revenue share |
|---|---|---|
| Top 5% | 294 | **52%** |
| Top 11% | 647 | 66% |
| Top 20% | 1,176 | 77% |
| Top 50% | 2,939 | 94% |

A single segment — **Champions, 609 customers, average recency 8 days** — accounts for **49.5% of revenue (£8.8M)**. Loyal adds another 20%. Below the top 11%, every additional segment matters less than the marginal cost of keeping a Champion happy.

This is not a "we have a long tail" story. It is "the long tail is the floor; the head is the building."

## Where the at-risk dollars live

| Segment | Customers | Historical revenue | Why it's at risk |
|---|---|---|---|
| At Risk | 177 | £845k | Recency 2 (60–290 days), but F & M both 4–5 |
| Can't Lose Them | 11 | £98k | Recency ≤ 2 *and* F=5, M=5 — used to be Champions |

Combined: **188 customers, ~£943k of historical revenue, not currently buying.**

Lost (1,892 customers, £3M) is technically larger, but Lost customers are by definition outside the window where a re-engagement campaign converts above floor cost. At Risk + Can't Lose Them are the people who *were* buying and *just stopped* — the right moment to intervene.

## Recommended playbook

| Tier | Segments | Cost / customer | Why this cost |
|---|---|---|---|
| **VIP** | Champions, Can't Lose Them | $6–22 | High-touch human outreach, not just an automated email — every dollar of Champion revenue is worth more than the next acquisition (no CAC) |
| **Retain** | Loyal, Potential Loyalist, At Risk | $2.50–18 | Mid-touch — cross-sell, onboarding nurture, or a targeted win-back campaign with discount + concierge |
| **Reactivate** | Hibernating, About to Sleep, Need Attention | $0.80–5 | Low-cost reactivation email; if it doesn't work, walk away |
| **Don't spend** | Lost, Promising | $0–1 | A coupon to someone who hasn't ordered in a year is theatre — and a coupon to a one-time buyer (Promising) without a recommendation engine is wasted |

Total quarterly cost on the 5,878-customer book: **$13.7k**. Projected retained/new revenue: **$144.7k**. Blended ROI: **10.5×**. The single biggest dollar contributor is the Champions campaign (ROI 23.8×) because the unit revenue is large and the conversion rate is high — these customers want to hear from you.

Full per-segment numbers in [`outputs/PLAYBOOK.md`](outputs/PLAYBOOK.md).

## What this is honest about

- **Conversion rates are quoted from industry benchmarks** (Klaviyo / Mailchimp / Optimove). They are not measured from your data. Re-run after one quarter of A/B and update. The playbook code in `src/playbook.py` makes every assumption visible so it can be challenged.
- **Snapshot date is 2011-12-10** (one day after the last invoice). RFM is a snapshot, not a trend. Production deployment re-runs this monthly.
- **The k-means cluster comparison (`04_kmeans_vs_rules.png`) shows the same Champions cluster emerges from both methods.** That is the right outcome — it means the rule-based segmentation is not arbitrary, and the rule-based labels (which are explainable to marketing) win on communication.

## Recommendation

1. **Lock in the Champions program for Q1.** Highest unit cost, highest ROI, and the lowest risk of being wrong. Test internally that the 65% assumed conversion holds in your data and adjust.
2. **Run the At Risk + Can't Lose Them win-back as a campaign, not a one-shot email.** Human outreach for the top-monetary 50 of those 188 customers. Cost is ~$1,000; even a 15% recovery rate pulls back £140k+ of revenue.
3. **Cap Hibernating reactivation budget at $0.80 / customer.** Their ROI is ~2.2× — fine, but does not justify a $10 coupon. The risk of going too generous on Hibernating is far higher than the upside.
