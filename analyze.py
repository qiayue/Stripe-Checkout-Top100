#!/usr/bin/env python3
"""
Stripe Checkout Top 100 Inbound Traffic Analysis
Analyzes 26 months of checkout.stripe.com referral data (2024-01 to 2026-02)
"""

import json
import os
from collections import defaultdict
from datetime import datetime

DATA_DIR = "data"
REPORT_DIR = "report"

def load_all_data():
    """Load all monthly JSON files and return structured data."""
    months = []
    for f in sorted(os.listdir(DATA_DIR)):
        if not f.endswith('.json'):
            continue
        with open(os.path.join(DATA_DIR, f)) as fh:
            d = json.load(fh)
        year_month = f.replace('.json', '')
        label = f"{year_month[:4]}-{year_month[4:]}"
        months.append({
            'file': f,
            'label': label,
            'total_visits': d['TotalVisits'],
            'total_count': d['TotalCount'],
            'records': d['Records']
        })
    return months


def simplify_category(cat):
    """Extract top-level category."""
    return cat.split('~')[0] if '~' in cat else cat


def report_01_overview(months):
    """Report 1: Macro overview of Stripe Checkout traffic trends."""
    lines = []
    lines.append("# Stripe Checkout 入站流量总览报告")
    lines.append("")
    lines.append("## 数据范围")
    lines.append(f"- 时间跨度：{months[0]['label']} 至 {months[-1]['label']}（共 {len(months)} 个月）")

    all_domains = set()
    all_cats = set()
    for m in months:
        for r in m['records']:
            all_domains.add(r['Domain'])
            all_cats.add(r['Category'])

    lines.append(f"- 累计出现过的独立域名：{len(all_domains)} 个")
    lines.append(f"- 涉及行业类别：{len(all_cats)} 个")
    lines.append("")

    # Monthly traffic table
    lines.append("## 月度总流量趋势")
    lines.append("")
    lines.append("| 月份 | 总访问量 | 环比变化 | Top 100 域名数 |")
    lines.append("|------|---------|---------|---------------|")

    for i, m in enumerate(months):
        change = ""
        if i > 0:
            prev = months[i-1]['total_visits']
            pct = (m['total_visits'] - prev) / prev * 100
            change = f"{pct:+.1f}%"
        lines.append(f"| {m['label']} | {m['total_visits']:,.0f} | {change} | {len(m['records'])} |")

    lines.append("")

    # Key stats
    visits = [m['total_visits'] for m in months]
    lines.append("## 关键统计")
    lines.append("")
    lines.append(f"- 最高月流量：{max(visits):,.0f}（{months[visits.index(max(visits))]['label']}）")
    lines.append(f"- 最低月流量：{min(visits):,.0f}（{months[visits.index(min(visits))]['label']}）")
    lines.append(f"- 平均月流量：{sum(visits)/len(visits):,.0f}")
    lines.append(f"- 总流量增长：{(visits[-1] - visits[0]) / visits[0] * 100:+.1f}%（首尾月对比）")

    # Year-over-year
    lines.append("")
    lines.append("## 年度对比")
    lines.append("")
    y2024 = [m for m in months if m['label'].startswith('2024')]
    y2025 = [m for m in months if m['label'].startswith('2025')]
    y2026 = [m for m in months if m['label'].startswith('2026')]

    avg_2024 = sum(m['total_visits'] for m in y2024) / len(y2024)
    avg_2025 = sum(m['total_visits'] for m in y2025) / len(y2025)
    avg_2026 = sum(m['total_visits'] for m in y2026) / len(y2026)

    lines.append(f"- 2024年月均流量：{avg_2024:,.0f}（{len(y2024)} 个月）")
    lines.append(f"- 2025年月均流量：{avg_2025:,.0f}（{len(y2025)} 个月）")
    lines.append(f"- 2026年月均流量：{avg_2026:,.0f}（{len(y2026)} 个月）")
    lines.append(f"- 2024→2025 增长：{(avg_2025 - avg_2024) / avg_2024 * 100:+.1f}%")
    lines.append(f"- 2025→2026 增长：{(avg_2026 - avg_2025) / avg_2025 * 100:+.1f}%")

    write_report("01_总览_Traffic_Overview.md", lines)


def report_02_top_domains(months):
    """Report 2: Top domains ranking and persistence analysis."""
    lines = []
    lines.append("# Top 域名排行与持久力分析")
    lines.append("")

    # Aggregate across all months
    domain_stats = defaultdict(lambda: {
        'total_visits': 0, 'months_present': 0, 'shares': [],
        'categories': set(), 'first_seen': None, 'last_seen': None,
        'monthly_visits': {}
    })

    for m in months:
        for r in m['records']:
            d = r['Domain']
            ds = domain_stats[d]
            ds['total_visits'] += r['TotalVisits']
            ds['months_present'] += 1
            ds['shares'].append(r['Share'])
            ds['categories'].add(r['Category'])
            if ds['first_seen'] is None:
                ds['first_seen'] = m['label']
            ds['last_seen'] = m['label']
            ds['monthly_visits'][m['label']] = r['TotalVisits']

    # Top 30 by total visits
    lines.append("## 累计流量 Top 30 域名")
    lines.append("")
    lines.append("| 排名 | 域名 | 累计访问量 | 出现月数 | 平均份额 | 行业 |")
    lines.append("|------|------|-----------|---------|---------|------|")

    sorted_domains = sorted(domain_stats.items(), key=lambda x: -x[1]['total_visits'])

    for i, (domain, stats) in enumerate(sorted_domains[:30]):
        avg_share = sum(stats['shares']) / len(stats['shares']) * 100
        cat = sorted(stats['categories'])[0].split('~')[-1].replace('_', ' ')
        lines.append(f"| {i+1} | {domain} | {stats['total_visits']:,.0f} | {stats['months_present']}/{len(months)} | {avg_share:.2f}% | {cat} |")

    # Persistence analysis: domains present in all 26 months
    lines.append("")
    lines.append("## 常青域名（出现在所有 26 个月）")
    lines.append("")
    evergreen = [(d, s) for d, s in sorted_domains if s['months_present'] == len(months)]
    lines.append(f"共有 **{len(evergreen)}** 个域名在全部 {len(months)} 个月中均出现在 Top 100 榜单中：")
    lines.append("")
    for d, s in evergreen:
        avg_share = sum(s['shares']) / len(s['shares']) * 100
        lines.append(f"- **{d}** — 累计 {s['total_visits']:,.0f} 次访问，平均份额 {avg_share:.2f}%")

    # Most volatile (high variance in share)
    lines.append("")
    lines.append("## 流量波动最大的域名（出现≥6个月）")
    lines.append("")
    volatile = []
    for d, s in sorted_domains:
        if s['months_present'] >= 6:
            import statistics
            if len(s['shares']) >= 2:
                cv = statistics.stdev(s['shares']) / statistics.mean(s['shares'])
                volatile.append((d, cv, s))
    volatile.sort(key=lambda x: -x[1])

    lines.append("| 域名 | 变异系数 | 出现月数 | 最高份额 | 最低份额 |")
    lines.append("|------|---------|---------|---------|---------|")
    for d, cv, s in volatile[:15]:
        lines.append(f"| {d} | {cv:.2f} | {s['months_present']} | {max(s['shares'])*100:.2f}% | {min(s['shares'])*100:.2f}% |")

    write_report("02_Top域名排行_Domain_Rankings.md", lines)


def report_03_category_analysis(months):
    """Report 3: Industry category analysis."""
    lines = []
    lines.append("# 行业类别分析报告")
    lines.append("")

    # Aggregate by top-level category per month
    monthly_cat = []
    for m in months:
        cat_data = defaultdict(lambda: {'visits': 0, 'count': 0, 'domains': set()})
        for r in m['records']:
            top_cat = simplify_category(r['Category'])
            cat_data[top_cat]['visits'] += r['TotalVisits']
            cat_data[top_cat]['count'] += 1
            cat_data[top_cat]['domains'].add(r['Domain'])
        monthly_cat.append((m['label'], cat_data))

    # Overall category ranking
    overall_cat = defaultdict(lambda: {'visits': 0, 'domains': set(), 'month_count': 0})
    for label, cat_data in monthly_cat:
        for cat, data in cat_data.items():
            overall_cat[cat]['visits'] += data['visits']
            overall_cat[cat]['domains'] |= data['domains']
            overall_cat[cat]['month_count'] += 1

    sorted_cats = sorted(overall_cat.items(), key=lambda x: -x[1]['visits'])

    lines.append("## 行业类别累计流量排名（顶级分类）")
    lines.append("")
    lines.append("| 排名 | 行业 | 累计访问量 | 占比 | 涉及域名数 |")
    lines.append("|------|------|-----------|------|-----------|")

    total_all = sum(v['visits'] for v in overall_cat.values())
    for i, (cat, data) in enumerate(sorted_cats):
        pct = data['visits'] / total_all * 100
        cat_display = cat.replace('_', ' ')
        lines.append(f"| {i+1} | {cat_display} | {data['visits']:,.0f} | {pct:.1f}% | {len(data['domains'])} |")

    # Category trend over time (top 8 categories)
    lines.append("")
    lines.append("## 主要行业月度流量趋势（Top 8）")
    lines.append("")
    top8_cats = [c for c, _ in sorted_cats[:8]]

    header = "| 月份 | " + " | ".join(c.replace('_', ' ')[:20] for c in top8_cats) + " |"
    sep = "|------|" + "|".join(["------" for _ in top8_cats]) + "|"
    lines.append(header)
    lines.append(sep)

    for label, cat_data in monthly_cat:
        vals = []
        for cat in top8_cats:
            v = cat_data.get(cat, {})
            visits = v['visits'] if isinstance(v, dict) and 'visits' in v else 0
            vals.append(f"{visits/1e6:.1f}M")
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    # Sub-category detail for AI
    lines.append("")
    lines.append("## AI 相关子类别详情")
    lines.append("")

    ai_domains = defaultdict(lambda: {'visits': 0, 'first': None, 'last': None, 'months': 0})
    for m in months:
        for r in m['records']:
            if 'AI' in r['Category']:
                d = r['Domain']
                ai_domains[d]['visits'] += r['TotalVisits']
                ai_domains[d]['months'] += 1
                if ai_domains[d]['first'] is None:
                    ai_domains[d]['first'] = m['label']
                ai_domains[d]['last'] = m['label']

    sorted_ai = sorted(ai_domains.items(), key=lambda x: -x[1]['visits'])
    lines.append("| 域名 | 累计访问量 | 出现月数 | 首次出现 | 最后出现 |")
    lines.append("|------|-----------|---------|---------|---------|")
    for d, s in sorted_ai[:25]:
        lines.append(f"| {d} | {s['visits']:,.0f} | {s['months']} | {s['first']} | {s['last']} |")

    write_report("03_行业类别分析_Category_Analysis.md", lines)


def report_04_ai_revolution(months):
    """Report 4: The AI revolution in Stripe Checkout traffic."""
    lines = []
    lines.append("# AI 浪潮：Stripe Checkout 中的 AI 产品崛起")
    lines.append("")
    lines.append("本报告聚焦分析 AI 相关产品在 Stripe Checkout 入站流量中的表现和趋势。")
    lines.append("")

    # Track AI category share over time
    # Curated list of known AI product domains
    ai_domains_manual = {
        'midjourney.com', 'elevenlabs.io', 'cursor.com', 'blackbox.ai',
        'suno.com', 'lovable.dev', 'grok.com', 'manus.im',
        'perplexity.ai', 'bolt.new', 'chatgpt.com', 'openai.com',
        'claude.ai', 'anthropic.com', 'replit.com', 'v0.dev',
        'windsurf.com', 'devin.ai', 'heygen.com', 'runwayml.com',
        'synthesia.io', 'jasper.ai', 'copy.ai', 'descript.com',
        'leonardo.ai', 'ideogram.ai', 'pika.art', 'kling.ai',
    }

    def is_ai_product(record):
        if record['Domain'] in ai_domains_manual:
            return True
        if record['Category'] == 'AI_Chatbots_and_Tools':
            return True
        return False

    monthly_ai_data = []
    for m in months:
        ai_visits = 0
        ai_count = 0
        ai_list = []
        total = m['total_visits']
        for r in m['records']:
            if is_ai_product(r):
                ai_visits += r['TotalVisits']
                ai_count += 1
                ai_list.append((r['Domain'], r['TotalVisits'], r['Share']))
        monthly_ai_data.append({
            'label': m['label'],
            'ai_visits': ai_visits,
            'ai_share': ai_visits / total * 100,
            'ai_count': ai_count,
            'total': total,
            'top_ai': sorted(ai_list, key=lambda x: -x[1])[:10]
        })

    lines.append("## AI 产品在 Stripe Checkout 流量中的占比趋势")
    lines.append("")
    lines.append("| 月份 | AI 产品流量 | 总流量 | AI 占比 | AI 域名数 |")
    lines.append("|------|-----------|-------|--------|----------|")

    for d in monthly_ai_data:
        lines.append(f"| {d['label']} | {d['ai_visits']:,.0f} | {d['total']:,.0f} | {d['ai_share']:.1f}% | {d['ai_count']} |")

    # Growth narrative
    first_ai = monthly_ai_data[0]
    last_ai = monthly_ai_data[-1]
    lines.append("")
    lines.append("## 关键发现")
    lines.append("")
    lines.append(f"- **AI 占比从 {first_ai['ai_share']:.1f}% 增长到 {last_ai['ai_share']:.1f}%**，增长了 {last_ai['ai_share'] - first_ai['ai_share']:.1f} 个百分点")
    lines.append(f"- AI 相关域名数从 {first_ai['ai_count']} 个增长到 {last_ai['ai_count']} 个")
    lines.append(f"- AI 产品带来的绝对流量从 {first_ai['ai_visits']:,.0f} 增长到 {last_ai['ai_visits']:,.0f}")

    # AI product timeline
    lines.append("")
    lines.append("## 主要 AI 产品进入 Top 100 的时间线")
    lines.append("")

    ai_timeline = {}
    for m in months:
        for r in m['records']:
            if is_ai_product(r) and r['Domain'] not in ai_timeline:
                ai_timeline[r['Domain']] = m['label']

    # Group by first appearance month
    by_month = defaultdict(list)
    for domain, first_month in sorted(ai_timeline.items(), key=lambda x: x[1]):
        by_month[first_month].append(domain)

    for month, domains in sorted(by_month.items()):
        lines.append(f"### {month}")
        for d in domains:
            lines.append(f"- {d}")
        lines.append("")

    # Monthly top 5 AI
    lines.append("## 每月 AI 产品 Top 5")
    lines.append("")
    for d in monthly_ai_data:
        lines.append(f"### {d['label']}")
        lines.append("")
        for i, (domain, visits, share) in enumerate(d['top_ai'][:5]):
            lines.append(f"{i+1}. **{domain}** — {visits:,.0f} 次访问（{share*100:.2f}%）")
        lines.append("")

    write_report("04_AI浪潮分析_AI_Revolution.md", lines)


def report_05_newcomers_and_exits(months):
    """Report 5: New entrants and exits analysis."""
    lines = []
    lines.append("# 新进与退出：Top 100 榜单变动分析")
    lines.append("")

    prev_domains = set()
    monthly_changes = []

    for m in months:
        current_domains = set(r['Domain'] for r in m['records'])
        if prev_domains:
            new_entries = current_domains - prev_domains
            exits = prev_domains - current_domains
            monthly_changes.append({
                'label': m['label'],
                'new': new_entries,
                'exits': exits,
                'new_details': [(r['Domain'], r['TotalVisits'], r['Category'])
                               for r in m['records'] if r['Domain'] in new_entries],
                'current_count': len(current_domains)
            })
        prev_domains = current_domains

    lines.append("## 月度榜单变动概览")
    lines.append("")
    lines.append("| 月份 | 新进域名数 | 退出域名数 | 净变化 |")
    lines.append("|------|----------|----------|--------|")

    for mc in monthly_changes:
        net = len(mc['new']) - len(mc['exits'])
        lines.append(f"| {mc['label']} | {len(mc['new'])} | {len(mc['exits'])} | {net:+d} |")

    # Detailed new entries per month
    lines.append("")
    lines.append("## 每月新进域名详情")
    lines.append("")

    for mc in monthly_changes:
        if mc['new_details']:
            lines.append(f"### {mc['label']}（{len(mc['new'])} 个新进）")
            lines.append("")
            sorted_new = sorted(mc['new_details'], key=lambda x: -x[1])
            for domain, visits, cat in sorted_new[:10]:
                cat_short = cat.split('~')[-1].replace('_', ' ')
                lines.append(f"- **{domain}** — {visits:,.0f} 次访问 [{cat_short}]")
            if len(sorted_new) > 10:
                lines.append(f"- ...及其他 {len(sorted_new)-10} 个域名")
            lines.append("")

    # "Shooting stars" - domains that appeared briefly then disappeared
    lines.append("## 昙花一现：仅出现 1-2 个月的域名")
    lines.append("")

    domain_months = defaultdict(list)
    for m in months:
        for r in m['records']:
            domain_months[r['Domain']].append((m['label'], r['TotalVisits']))

    shooting_stars = [(d, ms) for d, ms in domain_months.items() if len(ms) <= 2]
    shooting_stars.sort(key=lambda x: -max(v for _, v in x[1]))

    lines.append("| 域名 | 出现月份 | 最高流量 |")
    lines.append("|------|---------|---------|")
    for d, ms in shooting_stars[:30]:
        months_str = ", ".join(m for m, _ in ms)
        max_v = max(v for _, v in ms)
        lines.append(f"| {d} | {months_str} | {max_v:,.0f} |")

    write_report("05_新进与退出_Newcomers_Exits.md", lines)


def report_06_roblox_deep_dive(months):
    """Report 6: Roblox - the #1 domain deep dive."""
    lines = []
    lines.append("# Roblox：Stripe Checkout 流量之王深度分析")
    lines.append("")
    lines.append("Roblox 长期占据 checkout.stripe.com 入站流量第一名，本报告深入分析其表现。")
    lines.append("")

    roblox_data = []
    for m in months:
        for r in m['records']:
            if r['Domain'] == 'roblox.com':
                roblox_data.append({
                    'label': m['label'],
                    'visits': r['TotalVisits'],
                    'share': r['Share'] * 100,
                    'rank_in_list': m['records'].index(r) + 1,
                    'total': m['total_visits']
                })
                break

    lines.append("## 月度数据")
    lines.append("")
    lines.append("| 月份 | 访问量 | 份额 | 榜单排名 | 环比变化 |")
    lines.append("|------|-------|------|---------|---------|")

    for i, rd in enumerate(roblox_data):
        change = ""
        if i > 0:
            pct = (rd['visits'] - roblox_data[i-1]['visits']) / roblox_data[i-1]['visits'] * 100
            change = f"{pct:+.1f}%"
        lines.append(f"| {rd['label']} | {rd['visits']:,.0f} | {rd['share']:.2f}% | #{rd['rank_in_list']} | {change} |")

    visits = [rd['visits'] for rd in roblox_data]
    shares = [rd['share'] for rd in roblox_data]

    lines.append("")
    lines.append("## 关键发现")
    lines.append("")
    lines.append(f"- 最高月访问量：{max(visits):,.0f}（{roblox_data[visits.index(max(visits))]['label']}）")
    lines.append(f"- 最低月访问量：{min(visits):,.0f}（{roblox_data[visits.index(min(visits))]['label']}）")
    lines.append(f"- 平均月访问量：{sum(visits)/len(visits):,.0f}")
    lines.append(f"- 平均份额：{sum(shares)/len(shares):.2f}%")

    # When did Roblox lose #1?
    lines.append("")
    lines.append("## Roblox 排名变化")
    lines.append("")
    lost_first = [rd for rd in roblox_data if rd['rank_in_list'] > 1]
    if lost_first:
        lines.append("Roblox 未能保持第一名的月份：")
        for rd in lost_first:
            lines.append(f"- {rd['label']}：排名 #{rd['rank_in_list']}")

    # Check if Roblox dropped out entirely
    roblox_months = set(rd['label'] for rd in roblox_data)
    all_months = set(m['label'] for m in months)
    missing = all_months - roblox_months
    if missing:
        lines.append("")
        lines.append(f"Roblox 未出现在榜单的月份：{', '.join(sorted(missing))}")
    else:
        lines.append("")
        lines.append(f"Roblox 在全部 {len(months)} 个月中均出现在 Top 100 榜单。")

    write_report("06_Roblox深度分析_Roblox_Deep_Dive.md", lines)


def report_07_coding_tools(months):
    """Report 7: Developer/coding tools analysis."""
    lines = []
    lines.append("# 开发者工具与编程产品分析")
    lines.append("")
    lines.append("聚焦分析编程、开发者工具类产品在 Stripe Checkout 中的表现。")
    lines.append("")

    dev_domains = {
        'cursor.com', 'replit.com', 'github.com', 'bolt.new', 'v0.dev',
        'lovable.dev', 'windsurf.com', 'devin.ai', 'blackbox.ai',
        'gitpod.io', 'codepen.io', 'stackblitz.com', 'railway.app',
        'vercel.com', 'netlify.com', 'render.com', 'fly.io',
        'supabase.com', 'planetscale.com', 'neon.tech'
    }
    dev_categories = ['Programming_and_Developer_Software', 'Web_Hosting']

    dev_monthly = defaultdict(lambda: defaultdict(float))
    dev_all = defaultdict(lambda: {'visits': 0, 'months': 0, 'first': None, 'last': None, 'monthly': {}})

    for m in months:
        for r in m['records']:
            is_dev = (r['Domain'] in dev_domains or
                     any(kw in r['Category'] for kw in dev_categories))
            if is_dev:
                d = r['Domain']
                dev_monthly[m['label']][d] = r['TotalVisits']
                dev_all[d]['visits'] += r['TotalVisits']
                dev_all[d]['months'] += 1
                dev_all[d]['monthly'][m['label']] = r['TotalVisits']
                if dev_all[d]['first'] is None:
                    dev_all[d]['first'] = m['label']
                dev_all[d]['last'] = m['label']

    sorted_dev = sorted(dev_all.items(), key=lambda x: -x[1]['visits'])

    lines.append("## 开发者工具累计流量排名")
    lines.append("")
    lines.append("| 排名 | 域名 | 累计访问量 | 出现月数 | 首次出现 | 最后出现 |")
    lines.append("|------|------|-----------|---------|---------|---------|")

    for i, (d, s) in enumerate(sorted_dev[:20]):
        lines.append(f"| {i+1} | {d} | {s['visits']:,.0f} | {s['months']} | {s['first']} | {s['last']} |")

    # Cursor.com deep dive
    lines.append("")
    lines.append("## Cursor.com 崛起之路")
    lines.append("")

    if 'cursor.com' in dev_all:
        cursor = dev_all['cursor.com']
        lines.append(f"- 首次进入 Top 100：{cursor['first']}")
        lines.append(f"- 累计访问量：{cursor['visits']:,.0f}")
        lines.append(f"- 出现月数：{cursor['months']}")
        lines.append("")
        lines.append("月度数据：")
        lines.append("")
        lines.append("| 月份 | 访问量 |")
        lines.append("|------|-------|")
        for label in sorted(cursor['monthly'].keys()):
            lines.append(f"| {label} | {cursor['monthly'][label]:,.0f} |")

    # AI-powered coding tools competition
    lines.append("")
    lines.append("## AI 编程工具竞争格局")
    lines.append("")
    ai_coding = ['cursor.com', 'blackbox.ai', 'bolt.new', 'lovable.dev', 'v0.dev', 'windsurf.com', 'devin.ai', 'replit.com']

    lines.append("| 月份 | " + " | ".join(ai_coding) + " |")
    lines.append("|------|" + "|".join(["------" for _ in ai_coding]) + "|")

    for m in months:
        vals = []
        dom_visits = {r['Domain']: r['TotalVisits'] for r in m['records']}
        for d in ai_coding:
            v = dom_visits.get(d, 0)
            vals.append(f"{v/1e3:.0f}K" if v > 0 else "-")
        lines.append(f"| {m['label']} | " + " | ".join(vals) + " |")

    write_report("07_开发者工具分析_Developer_Tools.md", lines)


def report_08_seasonal_patterns(months):
    """Report 8: Seasonal and cyclical patterns."""
    lines = []
    lines.append("# 季节性与周期性分析")
    lines.append("")

    # Monthly patterns (averaging same months across years)
    month_avg = defaultdict(list)
    for m in months:
        month_num = m['label'].split('-')[1]
        month_avg[month_num].append(m['total_visits'])

    lines.append("## 月度季节性规律")
    lines.append("")
    lines.append("| 月份 | 平均流量 | 数据点 | 最高 | 最低 |")
    lines.append("|------|---------|--------|------|------|")

    month_names = {'01': '一月', '02': '二月', '03': '三月', '04': '四月',
                   '05': '五月', '06': '六月', '07': '七月', '08': '八月',
                   '09': '九月', '10': '十月', '11': '十一月', '12': '十二月'}

    for mn in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        if mn in month_avg:
            vals = month_avg[mn]
            avg = sum(vals)/len(vals)
            lines.append(f"| {month_names[mn]} | {avg:,.0f} | {len(vals)} | {max(vals):,.0f} | {min(vals):,.0f} |")

    # Quarter analysis
    lines.append("")
    lines.append("## 季度分析")
    lines.append("")

    quarter_data = defaultdict(list)
    for m in months:
        year = m['label'][:4]
        month_num = int(m['label'].split('-')[1])
        q = (month_num - 1) // 3 + 1
        quarter_data[f"{year} Q{q}"].append(m['total_visits'])

    lines.append("| 季度 | 总流量 | 月均流量 |")
    lines.append("|------|-------|---------|")
    for q in sorted(quarter_data.keys()):
        vals = quarter_data[q]
        lines.append(f"| {q} | {sum(vals):,.0f} | {sum(vals)/len(vals):,.0f} |")

    # Year-end spike analysis
    lines.append("")
    lines.append("## 年末效应分析")
    lines.append("")
    lines.append("12月通常是电商消费旺季，分析 Stripe Checkout 流量的年末表现：")
    lines.append("")

    for m in months:
        if m['label'].endswith('-12'):
            prev = [pm for pm in months if pm['label'].endswith('-11') and pm['label'][:4] == m['label'][:4]]
            if prev:
                change = (m['total_visits'] - prev[0]['total_visits']) / prev[0]['total_visits'] * 100
                lines.append(f"- {m['label'][:4]}年：12月流量 {m['total_visits']:,.0f}，较11月变化 {change:+.1f}%")

    write_report("08_季节性分析_Seasonal_Patterns.md", lines)


def report_09_gaming_entertainment(months):
    """Report 9: Gaming and entertainment sector."""
    lines = []
    lines.append("# 游戏与娱乐行业分析")
    lines.append("")

    game_cats = ['Games', 'Arts_and_Entertainment']

    gaming_data = defaultdict(lambda: {'visits': 0, 'months': 0, 'monthly': {}, 'cat': ''})
    monthly_gaming_total = {}

    for m in months:
        gaming_total = 0
        for r in m['records']:
            top_cat = simplify_category(r['Category'])
            if top_cat in game_cats:
                d = r['Domain']
                gaming_data[d]['visits'] += r['TotalVisits']
                gaming_data[d]['months'] += 1
                gaming_data[d]['monthly'][m['label']] = r['TotalVisits']
                gaming_data[d]['cat'] = r['Category'].split('~')[-1].replace('_', ' ')
                gaming_total += r['TotalVisits']
        monthly_gaming_total[m['label']] = gaming_total

    sorted_gaming = sorted(gaming_data.items(), key=lambda x: -x[1]['visits'])

    lines.append("## 游戏与娱乐域名 Top 20")
    lines.append("")
    lines.append("| 排名 | 域名 | 类别 | 累计访问量 | 出现月数 |")
    lines.append("|------|------|------|-----------|---------|")

    for i, (d, s) in enumerate(sorted_gaming[:20]):
        lines.append(f"| {i+1} | {d} | {s['cat']} | {s['visits']:,.0f} | {s['months']} |")

    # Gaming share trend
    lines.append("")
    lines.append("## 游戏与娱乐流量占比趋势")
    lines.append("")
    lines.append("| 月份 | 游戏娱乐流量 | 总流量 | 占比 |")
    lines.append("|------|-----------|-------|------|")

    for m in months:
        gt = monthly_gaming_total.get(m['label'], 0)
        pct = gt / m['total_visits'] * 100
        lines.append(f"| {m['label']} | {gt:,.0f} | {m['total_visits']:,.0f} | {pct:.1f}% |")

    write_report("09_游戏娱乐分析_Gaming_Entertainment.md", lines)


def report_10_concentration(months):
    """Report 10: Market concentration and long tail analysis."""
    lines = []
    lines.append("# 市场集中度与长尾分析")
    lines.append("")
    lines.append("分析 Stripe Checkout 入站流量的集中度变化——流量是越来越集中于少数大站，还是更加分散？")
    lines.append("")

    lines.append("## 月度流量集中度指标")
    lines.append("")
    lines.append("| 月份 | Top 1 份额 | Top 5 份额 | Top 10 份额 | Top 20 份额 | HHI 指数 |")
    lines.append("|------|----------|----------|-----------|-----------|---------|")

    for m in months:
        shares = sorted([r['Share'] for r in m['records']], reverse=True)
        top1 = shares[0] * 100
        top5 = sum(shares[:5]) * 100
        top10 = sum(shares[:10]) * 100
        top20 = sum(shares[:20]) * 100
        hhi = sum(s**2 for s in shares) * 10000
        lines.append(f"| {m['label']} | {top1:.1f}% | {top5:.1f}% | {top10:.1f}% | {top20:.1f}% | {hhi:.0f} |")

    lines.append("")
    lines.append("## 分析说明")
    lines.append("")
    lines.append("- **HHI 指数**（赫芬达尔指数）：衡量市场集中度，值越高表示流量越集中于少数域名")
    lines.append("- Top N 份额：前 N 个域名占总流量的比例")
    lines.append("")

    # First vs last month comparison
    first = months[0]
    last = months[-1]

    first_shares = sorted([r['Share'] for r in first['records']], reverse=True)
    last_shares = sorted([r['Share'] for r in last['records']], reverse=True)

    lines.append("## 首尾月对比")
    lines.append("")
    lines.append(f"**{first['label']}**：Top1={first_shares[0]*100:.1f}%, Top5={sum(first_shares[:5])*100:.1f}%, Top10={sum(first_shares[:10])*100:.1f}%")
    lines.append("")
    lines.append(f"**{last['label']}**：Top1={last_shares[0]*100:.1f}%, Top5={sum(last_shares[:5])*100:.1f}%, Top10={sum(last_shares[:10])*100:.1f}%")

    change_top5 = sum(last_shares[:5])*100 - sum(first_shares[:5])*100
    lines.append("")
    if change_top5 < 0:
        lines.append(f"Top 5 集中度下降了 {abs(change_top5):.1f} 个百分点，说明流量分布更加分散，长尾效应增强。")
    else:
        lines.append(f"Top 5 集中度上升了 {change_top5:.1f} 个百分点，说明流量更加集中于头部域名。")

    write_report("10_市场集中度分析_Concentration.md", lines)


def report_11_monthly_champions(months):
    """Report 11: Monthly #1 champion history."""
    lines = []
    lines.append("# 月度冠军变迁史")
    lines.append("")
    lines.append("每月 checkout.stripe.com 入站流量第一名的变化记录。")
    lines.append("")

    lines.append("| 月份 | 冠军域名 | 访问量 | 份额 | 第二名 | 第三名 |")
    lines.append("|------|---------|-------|------|--------|--------|")

    champions = defaultdict(int)
    for m in months:
        recs = m['records']
        r1 = recs[0]
        r2 = recs[1] if len(recs) > 1 else None
        r3 = recs[2] if len(recs) > 2 else None
        champions[r1['Domain']] += 1
        lines.append(f"| {m['label']} | **{r1['Domain']}** | {r1['TotalVisits']:,.0f} | {r1['Share']*100:.1f}% | {r2['Domain'] if r2 else '-'} | {r3['Domain'] if r3 else '-'} |")

    lines.append("")
    lines.append("## 冠军统计")
    lines.append("")
    for d, count in sorted(champions.items(), key=lambda x: -x[1]):
        lines.append(f"- **{d}**：{count} 次月度冠军")

    # Throne changes
    lines.append("")
    lines.append("## 王座更替时刻")
    lines.append("")

    prev_champion = None
    for m in months:
        champion = m['records'][0]['Domain']
        if prev_champion and champion != prev_champion:
            lines.append(f"- **{m['label']}**：{prev_champion} → {champion}")
        prev_champion = champion

    write_report("11_月度冠军变迁_Monthly_Champions.md", lines)


def report_12_emerging_trends(months):
    """Report 12: Emerging trends and predictions."""
    lines = []
    lines.append("# 新兴趋势与行业洞察")
    lines.append("")

    # Find rapidly growing domains (present in recent months with increasing traffic)
    lines.append("## 近期快速增长的域名")
    lines.append("")
    lines.append("分析最近 6 个月（2025-09 至 2026-02）中增长最快的域名：")
    lines.append("")

    recent_months = months[-6:]
    growth_data = {}

    for r in recent_months[0]['records']:
        growth_data[r['Domain']] = {'first_visits': r['TotalVisits'], 'first_share': r['Share']}

    for r in recent_months[-1]['records']:
        d = r['Domain']
        if d in growth_data:
            growth_data[d]['last_visits'] = r['TotalVisits']
            growth_data[d]['last_share'] = r['Share']
            if growth_data[d]['first_visits'] > 0:
                growth_data[d]['growth'] = (r['TotalVisits'] - growth_data[d]['first_visits']) / growth_data[d]['first_visits'] * 100

    growers = [(d, g) for d, g in growth_data.items() if 'growth' in g and g['growth'] > 0]
    growers.sort(key=lambda x: -x[1]['growth'])

    lines.append("| 域名 | 起始流量 | 最新流量 | 增长率 |")
    lines.append("|------|---------|---------|--------|")
    for d, g in growers[:20]:
        lines.append(f"| {d} | {g['first_visits']:,.0f} | {g['last_visits']:,.0f} | {g['growth']:+.0f}% |")

    # New categories appearing
    lines.append("")
    lines.append("## 行业类别变化趋势")
    lines.append("")

    first_half = months[:13]  # 2024-01 to 2025-01
    second_half = months[13:]  # 2025-02 to 2026-02

    cats_first = defaultdict(float)
    cats_second = defaultdict(float)

    for m in first_half:
        for r in m['records']:
            cats_first[simplify_category(r['Category'])] += r['TotalVisits']
    for m in second_half:
        for r in m['records']:
            cats_second[simplify_category(r['Category'])] += r['TotalVisits']

    all_cats = set(cats_first.keys()) | set(cats_second.keys())
    cat_changes = []
    for cat in all_cats:
        v1 = cats_first.get(cat, 0)
        v2 = cats_second.get(cat, 0)
        if v1 > 0:
            change = (v2/len(second_half) - v1/len(first_half)) / (v1/len(first_half)) * 100
            cat_changes.append((cat, v1/len(first_half), v2/len(second_half), change))
        elif v2 > 0:
            cat_changes.append((cat, 0, v2/len(second_half), float('inf')))

    cat_changes.sort(key=lambda x: -x[3] if x[3] != float('inf') else -1e18)

    lines.append("前半期（2024-01~2025-01）vs 后半期（2025-02~2026-02）月均流量变化：")
    lines.append("")
    lines.append("| 行业 | 前半期月均 | 后半期月均 | 变化 |")
    lines.append("|------|----------|----------|------|")
    for cat, v1, v2, change in cat_changes:
        if v1 == 0:
            change_str = "新增"
        else:
            change_str = f"{change:+.0f}%"
        lines.append(f"| {cat.replace('_', ' ')} | {v1:,.0f} | {v2:,.0f} | {change_str} |")

    # Key narrative trends
    lines.append("")
    lines.append("## 关键趋势总结")
    lines.append("")
    lines.append("1. **AI 产品全面崛起**：从 Midjourney 独领风骚到 Cursor、Suno、Lovable、Grok 等多产品百花齐放")
    lines.append("2. **开发者工具付费化**：Cursor 等 AI 编程工具成为 Stripe 支付的重要流量来源")
    lines.append("3. **游戏行业稳定**：以 Roblox 为代表的游戏平台保持稳定的付费用户基础")
    lines.append("4. **Stripe 生态整体增长**：总流量从约 1400 万增长到约 1900 万，增长约 37%")
    lines.append("5. **市场多元化**：新领域不断涌入，流量分布从集中走向分散")

    write_report("12_新兴趋势_Emerging_Trends.md", lines)


def write_report(filename, lines):
    """Write report lines to file."""
    path = os.path.join(REPORT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Generated: {path}")


def main():
    months = load_all_data()
    print(f"Loaded {len(months)} months of data\n")

    report_01_overview(months)
    report_02_top_domains(months)
    report_03_category_analysis(months)
    report_04_ai_revolution(months)
    report_05_newcomers_and_exits(months)
    report_06_roblox_deep_dive(months)
    report_07_coding_tools(months)
    report_08_seasonal_patterns(months)
    report_09_gaming_entertainment(months)
    report_10_concentration(months)
    report_11_monthly_champions(months)
    report_12_emerging_trends(months)

    print("\nAll reports generated!")


if __name__ == '__main__':
    main()
