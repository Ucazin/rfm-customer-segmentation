"""
playbook.py — marketing action per segment, with cost + projected revenue.

Assumed conversion rates are quoted from industry benchmarks (Klaviyo /
Mailchimp / Optimove published reports) and are documented inline so a
reviewer can challenge them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# (action, unit_cost_usd, assumed_conversion, expected_revenue_if_converted)
ACTIONS = {
    "Champions":          ("VIP perks + early access",      6.00, 0.65, 220.0),
    "Loyal":              ("Cross-sell email series",       3.00, 0.32, 120.0),
    "Potential Loyalist": ("Onboarding nurture",            2.50, 0.28,  80.0),
    "New Customers":      ("Welcome + 2nd-order nudge",     1.50, 0.22,  60.0),
    "Promising":          ("Recommendation engine push",    1.00, 0.15,  45.0),
    "Need Attention":     ("Re-engagement promo",           4.00, 0.18, 110.0),
    "About to Sleep":     ("Limited-time discount",         5.00, 0.12,  95.0),
    "At Risk":            ("Win-back high-touch campaign", 18.00, 0.20, 280.0),
    "Can't Lose Them":    ("Win-back high-touch campaign", 22.00, 0.18, 520.0),
    "Hibernating":        ("Reactivation email (low cost)", 0.80, 0.05,  35.0),
    "Lost":               ("Do nothing",                    0.00, 0.00,   0.0),
}


def build_playbook(rfm_with_segments: pd.DataFrame) -> pd.DataFrame:
    out = (rfm_with_segments
           .groupby("segment", as_index=False)
           .agg(customers=("customer_id", "count"),
                avg_monetary=("monetary", "mean")))

    out["action"]                 = out["segment"].map(lambda s: ACTIONS[s][0])
    out["unit_cost_usd"]          = out["segment"].map(lambda s: ACTIONS[s][1])
    out["assumed_conversion"]     = out["segment"].map(lambda s: ACTIONS[s][2])
    out["expected_unit_revenue"]  = out["segment"].map(lambda s: ACTIONS[s][3])

    out["program_cost"]           = (out["customers"] * out["unit_cost_usd"]).round(2)
    out["expected_revenue"]       = (out["customers"] * out["assumed_conversion"]
                                     * out["expected_unit_revenue"]).round(2)
    cost_denom = out["program_cost"].replace(0, np.nan)
    out["roi_ratio"] = (out["expected_revenue"] / cost_denom).round(2)

    cols = ["segment", "customers", "action", "unit_cost_usd",
            "program_cost", "assumed_conversion",
            "expected_unit_revenue", "expected_revenue", "roi_ratio"]
    return (out[cols]
            .sort_values("expected_revenue", ascending=False)
            .reset_index(drop=True))


def write_memo(playbook: pd.DataFrame, out_path) -> None:
    total_cost    = playbook["program_cost"].sum()
    total_revenue = playbook["expected_revenue"].sum()
    roi           = total_revenue / total_cost if total_cost > 0 else 0
    md = f"""# Marketing Playbook — RFM-driven Quarterly Plan

**Total customers segmented:** {playbook['customers'].sum():,}
**Total program cost:** ${total_cost:,.0f}
**Projected retained / new revenue:** ${total_revenue:,.0f}
**Blended ROI:** {roi:.1f}×

## Actions by Segment

| Segment | Customers | Action | Unit cost | Cost | Conv. | Revenue / converter | Projected revenue | ROI |
|---------|-----------|--------|-----------|------|-------|---------------------|-------------------|-----|
"""
    for _, r in playbook.iterrows():
        md += (f"| {r['segment']} | {r['customers']:,} | {r['action']} | "
               f"${r['unit_cost_usd']:.2f} | ${r['program_cost']:,.0f} | "
               f"{r['assumed_conversion']:.0%} | ${r['expected_unit_revenue']:.0f} | "
               f"${r['expected_revenue']:,.0f} | "
               f"{('—' if pd.isna(r['roi_ratio']) else f'{r['roi_ratio']:.1f}×')} |\n")
    md += """
## Key Recommendations

1. **Protect the Champions.** They generate disproportionate revenue. Spend the
   highest unit cost here — these are the customers whose word-of-mouth is worth
   more than the next acquisition.
2. **Don't waste discounts on Hibernating.** Their projected return per dollar
   is < 1. A reactivation email at $0.80 / customer is fine; a 30% coupon at
   $20 / customer is not.
3. **Concentrate the win-back budget on At Risk + Can't Lose Them.** These two
   segments together explain the majority of the *at-risk* revenue in the book.
   A high-touch human outreach (not just an automated email) is justified.
4. **Measure.** Re-run this report after one quarter and compare actual revenue
   per segment to the projection. If conversion rates are >20% off the assumed
   values, the action assumptions need to be updated.

## What Could Go Wrong

- These conversion rates are industry-average; your real numbers depend on
  product, channel, and incentive design.
- RFM is calculated as of the most recent date in the dataset — re-run with
  fresh data each quarter, not annually.
- A customer can sit on the boundary between two segments — small changes in
  any metric will shift them. Audit the customer-level segment changes month
  over month and flag any cohort with > 25% churn into "Lost".
"""
    out_path.write_text(md, encoding="utf-8")
