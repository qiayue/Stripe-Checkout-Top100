# stripe-checkout-top100

> Monthly rankings of the top 100 websites sending traffic to `checkout.stripe.com` — 26 months of data (January 2024 – February 2026).

## 📖 About

This dataset tracks which websites drive the most inbound traffic to `checkout.stripe.com` each month. It serves as a proxy for identifying the most active Stripe-powered businesses on the web — covering SaaS products, AI tools, e-commerce stores, marketplaces, and more.

Data spans **26 consecutive months**, giving researchers, founders, and analysts a longitudinal view of the Stripe ecosystem.

## 📦 Data Structure

```
data/
├── 202401.json
├── 202402.json
├── ...
└── 202602.json
```

Each `.json` file represents one calendar month and contains an array of up to **100 entries**, ranked by estimated traffic share to `checkout.stripe.com`.

### Top-level Fields

| Field | Description |
|-------|-------------|
| `TotalShare` | Sum of all shares in the file (≈ 1.0) |
| `TotalVisits` | Estimated total visits to `checkout.stripe.com` that month |
| `TotalCount` | Number of grouped referring domains tracked |
| `Records` | Array of up to 100 referring site entries, sorted by traffic share |

### Record Entry Fields

| Field | Description |
|-------|-------------|
| `Domain` | Referring website domain (e.g. `midjourney.com`) |
| `Category` | Similarweb category, format: `Sector~Subcategory` |
| `Share` | This site's share of traffic sent to `checkout.stripe.com` that month |
| `TotalVisits` | Estimated absolute visit count referred that month |
| `Change` | Month-over-month change in share (negative = decline) |
| `Rank` | Similarweb global traffic rank of the referring domain |
| `HasAdsense` | Whether the site runs Google AdSense |
| `EngagementScore` | Similarweb engagement quality score |
| `TotalSharePerMonth` | Share values for current and prior month (for delta calculation) |

### Example Entry

```json
{
  "Domain": "midjourney.com",
  "Category": "Computers_Electronics_and_Technology~Graphics_Multimedia_and_Web_Design",
  "Share": 0.0619,
  "TotalVisits": 871423,
  "Change": -0.2427,
  "Rank": 1720,
  "HasAdsense": false,
  "EngagementScore": 2.0
}
```

## 📊 Analysis Reports

The `reports/` directory contains analysis generated from this dataset, including:

- **Monthly trend reports** — which sites climbed or dropped in rankings
- **Sector breakdowns** — AI tools, SaaS, e-commerce, creator economy, etc.
- **Newcomer spotlights** — sites that entered the top 100 for the first time
- **Long-term dominators** — sites that held top positions across the full 26 months
- **Churn analysis** — how quickly the rankings turn over month to month

Reports were generated with [Claude Code](https://claude.ai/code).

## 🗓️ Coverage

| Period | Months | Files |
|--------|--------|-------|
| 2024 Q1 | Jan – Mar 2024 | 3 |
| 2024 Q2 | Apr – Jun 2024 | 3 |
| 2024 Q3 | Jul – Sep 2024 | 3 |
| 2024 Q4 | Oct – Dec 2024 | 3 |
| 2025 Q1 | Jan – Mar 2025 | 3 |
| 2025 Q2 | Apr – Jun 2025 | 3 |
| 2025 Q3 | Jul – Sep 2025 | 3 |
| 2025 Q4 | Oct – Dec 2025 | 3 |
| 2026 Q1 | Jan – Feb 2026 | 2 |
| **Total** | | **26 files** |

## 🔍 Use Cases

- **Competitive intelligence** — discover fast-growing Stripe-powered products
- **Market research** — understand which verticals are monetizing most aggressively
- **Trend analysis** — track the rise of AI-native SaaS businesses over time
- **Startup scouting** — spot emerging companies before they become well known

## 📋 Data Source & Methodology

Traffic data is sourced from [Similarweb](https://www.similarweb.com/), specifically the referral traffic breakdown for `checkout.stripe.com`. Rankings reflect estimated traffic share, not absolute visitor counts.

**Limitations:**
- Data reflects estimated traffic, not verified transaction volume
- Sites with direct Stripe API integrations (no redirect to `checkout.stripe.com`) are not captured
- Low-traffic sites may be underrepresented due to Similarweb's estimation methodology

## 🤝 Contributing

Contributions are welcome! If you have scripts for parsing, visualizing, or extending this dataset, feel free to open a PR.

If you find this data useful in your research or writing, a link back to this repo is appreciated.

## 📄 License

Data is provided for research and informational purposes under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Analysis code is under [MIT License](LICENSE).

---

*Maintained by [@gefei](https://twitter.com/gefei55) — founder of an overseas indie hacker community with 5,000+ members.*