import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Business Gap Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .block-container{padding-top:1.2rem;padding-bottom:2rem;}
  .sec-header{
    font-size:1.15rem;font-weight:800;color:#1e1b4b;
    background:linear-gradient(90deg,#e0e7ff,#f1f5f9);
    border-left:5px solid #4f46e5;padding:0.55rem 1rem;
    border-radius:0 8px 8px 0;margin:2rem 0 0.9rem 0;
    letter-spacing:0.01em;
  }
  .kpi-card{
    background:linear-gradient(135deg,#1e2130,#252a3d);
    border:1px solid #2d3352;border-radius:12px;
    padding:0.9rem 1rem;text-align:center;margin-bottom:0.4rem;
  }
  .kpi-label{font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.06em;}
  .kpi-value{font-size:1.7rem;font-weight:800;color:#e2e8f0;line-height:1.2;}
  .kpi-sub{font-size:0.78rem;color:#64748b;margin-top:2px;}
  .badge{
    display:inline-block;background:#312e81;color:#a5b4fc;
    font-size:0.65rem;font-weight:700;border-radius:20px;padding:1px 8px;margin-left:4px;
  }
  .rec-card{
    background:#1a1f2e;border-left:4px solid #6366f1;
    border-radius:8px;padding:0.85rem 1rem;margin-bottom:0.6rem;
  }
  .rec-title{font-weight:700;color:#a5b4fc;margin-bottom:0.2rem;font-size:0.9rem;}
  .rec-body{font-size:0.82rem;color:#cbd5e1;line-height:1.55;}
  .conc-box{
    background:linear-gradient(135deg,#1a1f2e,#1a2040);
    border:1px solid #3d4f7c;border-radius:12px;
    padding:1.2rem 1.4rem;
  }
  .conc-q{font-weight:700;color:#818cf8;margin-bottom:0.15rem;font-size:0.9rem;}
  .conc-a{font-size:0.82rem;color:#cbd5e1;margin-bottom:0.85rem;line-height:1.6;}
  .drop-box{
    background:#12161f;border-radius:8px;padding:0.55rem 0.8rem;
    font-size:0.78rem;color:#94a3b8;margin-top:0.3rem;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STATIC DATA
# ─────────────────────────────────────────────────────────────────────────────
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

DOMAINS = {
    "Automobile": {
        "color": "#6366f1",
        "rgba_full": "rgba(99,102,241,1)",
        "rgba_mid":  "rgba(99,102,241,0.75)",
        "rgba_low":  "rgba(99,102,241,0.45)",
        "icon": "🚗",
        "lead_label": "Leads",
        "channels": ["Organic Search","Paid Ads","Referral","Social Media","Direct"],
    },
    "IT Solutions": {
        "color": "#22d3ee",
        "rgba_full": "rgba(34,211,238,1)",
        "rgba_mid":  "rgba(34,211,238,0.75)",
        "rgba_low":  "rgba(34,211,238,0.45)",
        "icon": "💻",
        "lead_label": "Bookings",
        "channels": ["Organic Search","Paid Ads","Email","Social Media","Events"],
    },
    "Health & Beauty": {
        "color": "#f472b6",
        "rgba_full": "rgba(244,114,182,1)",
        "rgba_mid":  "rgba(244,114,182,0.75)",
        "rgba_low":  "rgba(244,114,182,0.45)",
        "icon": "💄",
        "lead_label": "Bookings",
        "channels": ["Organic Search","Influencer","Referral","Social Media","Paid Ads"],
    },
}

np.random.seed(42)

def gen_monthly(base_vis, lead_pct, conv_pct, trend=1.02):
    vis, leads, convs = [], [], []
    v = base_vis
    for _ in MONTHS:
        v  = int(v * trend * np.random.uniform(0.96, 1.05))
        l  = int(v * lead_pct  * np.random.uniform(0.93, 1.07))
        c  = int(l * conv_pct  * np.random.uniform(0.90, 1.10))
        vis.append(v); leads.append(l); convs.append(c)
    return vis, leads, convs

RAW = {
    "Automobile":     gen_monthly(12000, 0.18, 0.35, 1.018),
    "IT Solutions":   gen_monthly(9500,  0.22, 0.42, 1.025),
    "Health & Beauty":gen_monthly(15000, 0.14, 0.28, 1.030),
}

# Build per-domain channel DataFrames
DFS = {}
for domain, (vis, leads, convs) in RAW.items():
    meta = DOMAINS[domain]
    ll   = meta["lead_label"]
    rows = []
    for i, m in enumerate(MONTHS):
        split = np.random.dirichlet(np.ones(5))
        for j, ch in enumerate(meta["channels"]):
            v_ch = int(vis[i]   * split[j])
            l_ch = int(leads[i] * split[j] * np.random.uniform(0.85, 1.15))
            c_ch = int(convs[i] * split[j] * np.random.uniform(0.80, 1.20))
            rows.append({"Month": m, "Channel": ch,
                         "Visitors": v_ch, ll: l_ch, "Conversions": c_ch})
    df = pd.DataFrame(rows)
    df["Month"] = pd.Categorical(df["Month"], categories=MONTHS, ordered=True)
    DFS[domain] = df


def monthly_agg(domain):
    """Return monthly aggregated DataFrame with rate columns."""
    df   = DFS[domain]
    ll   = DOMAINS[domain]["lead_label"]
    grp  = df.groupby("Month", observed=True)[["Visitors", ll, "Conversions"]].sum().reset_index()
    grp.columns = ["Month", "Visitors", "Leads", "Conversions"]
    grp["Lead Rate"]   = grp["Leads"]       / grp["Visitors"]
    grp["Conv Rate"]   = grp["Conversions"] / grp["Leads"]
    grp["Overall CR"]  = grp["Conversions"] / grp["Visitors"]
    return grp


# Pre-compute totals (full year)
TOTALS = {}
for d in DOMAINS:
    g = monthly_agg(d)
    tv, tl, tc = g["Visitors"].sum(), g["Leads"].sum(), g["Conversions"].sum()
    TOTALS[d] = {
        "visitors":  tv,
        "leads":     tl,
        "convs":     tc,
        "lead_rate": tl / tv,
        "conv_rate": tc / tl,
        "overall_cr":tc / tv,
        "monthly":   g,
    }

BEST_DOMAIN   = max(DOMAINS, key=lambda d: TOTALS[d]["overall_cr"])
LOWEST_LEADS  = min(DOMAINS, key=lambda d: TOTALS[d]["lead_rate"])
DOMAIN_LIST   = list(DOMAINS.keys())

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Filters")
    sel_months = st.multiselect("Filter by Month", MONTHS, default=MONTHS)
    if not sel_months:
        sel_months = MONTHS

    st.markdown("---")
    st.markdown("### 📌 Quick Snapshot")
    for d, meta in DOMAINS.items():
        t = TOTALS[d]
        st.markdown(
            f"{meta['icon']} **{d}**  \n"
            f"Visitors: `{t['visitors']:,}` | CR: `{t['overall_cr']:.1%}`"
        )
    st.markdown("---")
    st.caption("Dashboard v2.0 · Decision-Driven Analytics")

# ─────────────────────────────────────────────────────────────────────────────
# HEADER BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(90deg,#312e81,#1e1b4b);border-radius:12px;
            padding:1.3rem 2rem;margin-bottom:1.2rem;'>
  <h1 style='color:#e0e7ff;margin:0;font-size:1.7rem;'>
    📊 Business Gap Analysis Dashboard
  </h1>
  <p style='color:#a5b4fc;margin:0.3rem 0 0 0;font-size:0.88rem;'>
    Decision-Making Intelligence · Automobile · IT Solutions · Health &amp; Beauty
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 – EXECUTIVE KPIs
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>① Executive Overview</div>", unsafe_allow_html=True)

kpi_cols = st.columns(9)
col_i = 0
for domain, meta in DOMAINS.items():
    t = TOTALS[domain]
    for label, val, fmt in [
        ("Total Visitors",         t["visitors"],  f"{t['visitors']:,}"),
        (meta["lead_label"],       t["leads"],     f"{t['leads']:,}"),
        ("Overall Conv. Rate",     t["overall_cr"],f"{t['overall_cr']:.1%}"),
    ]:
        badge = "<span class='badge'>🏆 Best</span>" if (
            label == "Overall Conv. Rate" and domain == BEST_DOMAIN) else ""
        kpi_cols[col_i].markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-label'>{meta['icon']} {domain}</div>
          <div class='kpi-value'>{fmt}{badge}</div>
          <div class='kpi-sub'>{label}</div>
        </div>""", unsafe_allow_html=True)
        col_i += 1

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 – CONVERSION FUNNELS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>② Conversion Funnels — Where Drop-offs Occur</div>",
            unsafe_allow_html=True)
st.caption("Shows the full pipeline: Visitors → Leads/Bookings → Conversions. "
           "Wider gaps = bigger customer loss at that stage.")

f_cols = st.columns(3)
for idx, (domain, meta) in enumerate(DOMAINS.items()):
    g  = monthly_agg(domain)
    gf = g[g["Month"].isin(sel_months)]
    v  = int(gf["Visitors"].sum())
    l  = int(gf["Leads"].sum())
    c  = int(gf["Conversions"].sum())

    drop1 = 1 - l / v if v else 0
    drop2 = 1 - c / l if l else 0

    ll = DOMAINS[domain]["lead_label"]
    fig = go.Figure(go.Funnel(
        y=["Visitors", ll, "Conversions"],
        x=[v, l, c],
        texttemplate="%{value:,}<br>(%{percentInitial:.1%} of visitors)",
        textfont={"size": 12, "color": "#e2e8f0"},
        marker=dict(
            color=[meta["rgba_full"], meta["rgba_mid"], meta["rgba_low"]],
            line=dict(width=2, color="#0e1117"),
        ),
        connector=dict(fillcolor="#1e2130"),
    ))
    fig.update_layout(
        title=dict(text=f"{meta['icon']} {domain}", font=dict(color="#e2e8f0", size=14)),
        paper_bgcolor="#1a1f2e",
        plot_bgcolor="#1a1f2e",
        font=dict(color="#cbd5e1"),
        height=310,
        margin=dict(l=10, r=10, t=45, b=10),
    )
    f_cols[idx].plotly_chart(fig, use_container_width=True)
    f_cols[idx].markdown(
        f"<div class='drop-box'>"
        f"🔻 <b style='color:#f87171'>{drop1:.0%}</b> lost: Visitor → {ll}<br>"
        f"🔻 <b style='color:#fbbf24'>{drop2:.0%}</b> lost: {ll} → Conversion"
        f"</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 – CROSS-DOMAIN COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>③ Cross-Domain Performance Comparison</div>",
            unsafe_allow_html=True)

# ── Horizontal grouped bar: actual % values, easy to read ──────────────────
hbar_col, bar_col = st.columns([3, 2])

with hbar_col:
    h_metrics = ["Overall Conv. Rate", "Lead Rate (Visit→Lead)", "Lead→Conv Rate"]
    hbar_fig  = go.Figure()
    for domain in DOMAIN_LIST:
        t      = TOTALS[domain]
        x_vals = [t["overall_cr"], t["lead_rate"], t["conv_rate"]]
        hbar_fig.add_trace(go.Bar(
            name=domain,
            y=h_metrics,
            x=x_vals,
            orientation="h",
            marker_color=DOMAINS[domain]["color"],
            text=[f"{v:.1%}" for v in x_vals],
            textposition="outside",
            textfont=dict(size=11, color="#e2e8f0"),
        ))
    hbar_fig.update_layout(
        barmode="group",
        paper_bgcolor="#1a1f2e",
        plot_bgcolor="#1a1f2e",
        font=dict(color="#cbd5e1"),
        title=dict(
            text="📊 Side-by-Side Metric Comparison (Actual %)",
            font=dict(color="#e2e8f0", size=13),
        ),
        xaxis=dict(tickformat=".0%", gridcolor="#2d3352", range=[0, 0.65]),
        yaxis=dict(gridcolor="#2d3352"),
        legend=dict(bgcolor="#1a1f2e", font=dict(color="#e2e8f0")),
        height=370,
        margin=dict(l=20, r=60, t=50, b=20),
    )
    st.plotly_chart(hbar_fig, use_container_width=True)

with bar_col:
    metrics  = ["Overall CR", "Lead Rate", "Conv Rate (L→C)"]
    bar_fig  = go.Figure()
    for domain in DOMAIN_LIST:
        t = TOTALS[domain]
        y_vals = [t["overall_cr"], t["lead_rate"], t["conv_rate"]]
        bar_fig.add_trace(go.Bar(
            name=domain,
            x=metrics,
            y=y_vals,
            marker_color=DOMAINS[domain]["color"],
            text=[f"{v:.1%}" for v in y_vals],
            textposition="outside",
            textfont=dict(size=11),
        ))
    bar_fig.update_layout(
        barmode="group",
        paper_bgcolor="#1a1f2e",
        plot_bgcolor="#1a1f2e",
        font=dict(color="#cbd5e1"),
        title=dict(text="Conversion Rate Breakdown", font=dict(color="#e2e8f0", size=13)),
        yaxis=dict(tickformat=".0%", gridcolor="#2d3352"),
        xaxis=dict(gridcolor="#2d3352"),
        legend=dict(bgcolor="#1a1f2e"),
        height=370,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(bar_fig, use_container_width=True)

# Heatmap scorecard
st.markdown("##### 🗂️ Performance Scorecard — At a Glance")
score_rows = []
for d in DOMAIN_LIST:
    t = TOTALS[d]
    score_rows.append({
        "Domain": f"{DOMAINS[d]['icon']} {d}",
        "Total Visitors": t["visitors"],
        "Total Leads": t["leads"],
        "Conversions": t["convs"],
        "Lead Rate %": round(t["lead_rate"] * 100, 1),
        "Lead→Conv %": round(t["conv_rate"] * 100, 1),
        "Overall CR %": round(t["overall_cr"] * 100, 2),
    })
score_df = pd.DataFrame(score_rows).set_index("Domain")

heat_z    = score_df[["Lead Rate %", "Lead→Conv %", "Overall CR %"]].values.tolist()
heat_x    = ["Lead Rate %", "Lead→Conv %", "Overall CR %"]
heat_y    = score_df.index.tolist()
heat_text = [[f"{v:.1f}%" for v in row] for row in heat_z]

heat_fig = go.Figure(go.Heatmap(
    z=heat_z,
    x=heat_x,
    y=heat_y,
    text=heat_text,
    texttemplate="%{text}",
    textfont=dict(size=14, color="#1e1b4b"),
    colorscale="Blues",
    showscale=True,
    colorbar=dict(tickfont=dict(color="#e2e8f0"), title=dict(text="%", font=dict(color="#e2e8f0"))),
))
heat_fig.update_layout(
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#1a1f2e",
    font=dict(color="#e2e8f0"),
    xaxis=dict(side="top", tickfont=dict(color="#e2e8f0", size=12)),
    yaxis=dict(tickfont=dict(color="#e2e8f0", size=12)),
    height=200,
    margin=dict(l=20, r=20, t=40, b=10),
)
st.plotly_chart(heat_fig, use_container_width=True)

# Monthly trend
st.markdown("##### Monthly Overall Conversion Rate Trend")
trend_fig = go.Figure()
for domain in DOMAIN_LIST:
    g  = monthly_agg(domain)
    gf = g[g["Month"].isin(sel_months)]
    trend_fig.add_trace(go.Scatter(
        x=gf["Month"].tolist(),
        y=gf["Overall CR"].tolist(),
        name=domain,
        mode="lines+markers",
        line=dict(color=DOMAINS[domain]["color"], width=2.5),
        marker=dict(size=6),
    ))
trend_fig.update_layout(
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#1a1f2e",
    font=dict(color="#cbd5e1"),
    yaxis=dict(tickformat=".1%", gridcolor="#2d3352"),
    xaxis=dict(gridcolor="#2d3352"),
    legend=dict(bgcolor="#1a1f2e"),
    height=240,
    margin=dict(l=20, r=20, t=10, b=20),
)
st.plotly_chart(trend_fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 – CHANNEL SEGMENTATION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>④ Channel Segmentation Analysis</div>",
            unsafe_allow_html=True)
st.caption("Identify which acquisition channels drive conversions — and where to reallocate budget.")

seg_tabs = st.tabs([f"{DOMAINS[d]['icon']} {d}" for d in DOMAIN_LIST])
for tab, domain in zip(seg_tabs, DOMAIN_LIST):
    with tab:
        meta   = DOMAINS[domain]
        ll     = meta["lead_label"]
        df_f   = DFS[domain][DFS[domain]["Month"].isin(sel_months)]
        ch_agg = (
            df_f.groupby("Channel")[["Visitors", ll, "Conversions"]]
            .sum()
            .reset_index()
        )
        ch_agg.columns = ["Channel", "Visitors", "Leads", "Conversions"]
        ch_agg["CR"]   = ch_agg["Conversions"] / ch_agg["Visitors"].replace(0, np.nan)
        ch_agg         = ch_agg.sort_values("Conversions", ascending=False).reset_index(drop=True)

        c1, c2 = st.columns(2)

        with c1:
            vol_fig = go.Figure()
            for col_name, color in [("Visitors","#6366f1"),("Leads","#22d3ee"),("Conversions","#34d399")]:
                vol_fig.add_trace(go.Bar(
                    name=col_name,
                    x=ch_agg["Channel"].tolist(),
                    y=ch_agg[col_name].tolist(),
                    marker_color=color,
                ))
            vol_fig.update_layout(
                barmode="group",
                title=dict(text="Volume by Channel", font=dict(color="#e2e8f0", size=12)),
                paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
                font=dict(color="#cbd5e1"),
                legend=dict(bgcolor="#1a1f2e"),
                xaxis=dict(gridcolor="#2d3352"),
                yaxis=dict(gridcolor="#2d3352"),
                height=270,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(vol_fig, use_container_width=True)

        with c2:
            cr_vals  = ch_agg["CR"].fillna(0).tolist()
            cr_texts = [f"{v:.1%}" for v in cr_vals]
            cr_fig   = go.Figure(go.Bar(
                x=ch_agg["Channel"].tolist(),
                y=cr_vals,
                text=cr_texts,
                textposition="outside",
                marker=dict(
                    color=cr_vals,
                    colorscale="Viridis",
                    showscale=False,
                ),
            ))
            cr_fig.update_layout(
                title=dict(text="Conversion Rate by Channel", font=dict(color="#e2e8f0", size=12)),
                paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
                font=dict(color="#cbd5e1"),
                yaxis=dict(tickformat=".0%", gridcolor="#2d3352"),
                xaxis=dict(gridcolor="#2d3352"),
                height=270,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(cr_fig, use_container_width=True)

        best_ch  = ch_agg.loc[ch_agg["Conversions"].idxmax(), "Channel"]
        worst_ch = ch_agg.loc[ch_agg["CR"].idxmin(), "Channel"]
        st.info(
            f"✅ **Top converting channel:** {best_ch}  |  "
            f"⚠️ **Needs attention:** {worst_ch} (lowest conversion rate)"
        )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 – ACTIONABLE RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>⑤ Actionable Business Recommendations</div>",
            unsafe_allow_html=True)

RECS = {
    "Automobile": [
        (
            "🎯 Improve Lead Qualification to Lift Conversion Efficiency",
            f"Automobile's lead-to-conversion rate sits at {TOTALS['Automobile']['conv_rate']:.0%}. "
            "Deploy chatbot-based pre-qualification on landing pages to filter out low-intent visitors "
            "before they enter the pipeline. Reducing unqualified leads by 20% can improve sales team "
            "productivity without increasing ad spend.",
        ),
        (
            "📣 Reallocate Budget to Top-2 Converting Channels",
            "Shift 30% of spend from the lowest-performing channel to the two highest-converting "
            "channels. Review cost-per-conversion weekly for the first 6 weeks to validate the shift "
            "before committing fully.",
        ),
        (
            "🔄 Launch a 48-Hour Lead Nurture Sequence",
            "Over 50% of leads don't convert on first contact. Introduce a 3-email + 1 SMS nurture "
            "sequence triggered within 48 hours of lead capture to keep prospects warm, share "
            "testimonials, and push toward a test drive booking.",
        ),
    ],
    "IT Solutions": [
        (
            "📅 Remove Booking Friction on the Demo Page",
            f"IT Solutions leads with {TOTALS['IT Solutions']['conv_rate']:.0%} lead-to-conversion — "
            "the best across all domains. Sustain this by embedding a real-time calendar widget directly "
            "on the demo-request page. Studies show eliminating back-and-forth emails lifts booking "
            "rates by 30–40%.",
        ),
        (
            "📊 Invest in Bottom-of-Funnel SEO Content",
            "Organic search is your highest-intent channel. Publish 2–4 technical case studies per "
            "month targeting high-commercial-intent keywords (e.g., 'managed IT pricing', 'IT support "
            "ROI calculator'). Target: +15% organic visitor growth within 90 days.",
        ),
        (
            "🤝 Activate a Partner Referral Programme",
            "Referral traffic currently under-converts relative to its volume. Launch a formal "
            "partner programme offering 10% revenue share for partner-sourced deals that close. "
            "This creates an incentivised outbound sales force at near-zero fixed cost.",
        ),
    ],
    "Health & Beauty": [
        (
            "📸 Link Influencer Campaigns Directly to Bookings",
            f"Health & Beauty has the highest visitor volume but the lowest overall conversion rate "
            f"({TOTALS['Health & Beauty']['overall_cr']:.1%}). Assign unique promo codes to each "
            "influencer so traffic is attributable. Pair each code with a dedicated landing page "
            "that reduces steps to booking to a maximum of two clicks.",
        ),
        (
            "💌 Retarget Drop-offs with Personalised Offers",
            "The majority of visitors leave without booking. Set up a retargeting campaign for anyone "
            "who viewed a service page but did not convert within 48 hours. Retargeting campaigns "
            "typically achieve 2–3× the conversion rate of cold audience ads.",
        ),
        (
            "⭐ Showcase Social Proof Prominently",
            "Health and beauty decisions are trust-driven. Add verified reviews, before/after photo "
            "galleries, and practitioner credentials above the fold on every service page. A/B test "
            "trust-badge placement — industry data shows this alone can lift bookings by 15–25%.",
        ),
    ],
}

rec_tabs = st.tabs([f"{DOMAINS[d]['icon']} {d}" for d in DOMAIN_LIST])
for tab, domain in zip(rec_tabs, DOMAIN_LIST):
    with tab:
        for title, body in RECS[domain]:
            st.markdown(
                f"<div class='rec-card'>"
                f"<div class='rec-title'>{title}</div>"
                f"<div class='rec-body'>{body}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 – STRATEGIC CONCLUSION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>⑥ Strategic Conclusion &amp; Priorities</div>",
            unsafe_allow_html=True)

# Summary bar chart
sum_fig = go.Figure(go.Bar(
    x=DOMAIN_LIST,
    y=[TOTALS[d]["overall_cr"] for d in DOMAIN_LIST],
    marker_color=[DOMAINS[d]["color"] for d in DOMAIN_LIST],
    text=[f"{TOTALS[d]['overall_cr']:.2%}" for d in DOMAIN_LIST],
    textposition="outside",
    textfont=dict(color="#e2e8f0", size=13),
))
sum_fig.update_layout(
    title=dict(
        text="Overall Conversion Rate by Business Domain",
        font=dict(color="#e2e8f0", size=13),
    ),
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#1a1f2e",
    font=dict(color="#e2e8f0"),
    yaxis=dict(tickformat=".1%", gridcolor="#2d3352"),
    xaxis=dict(gridcolor="#2d3352"),
    height=270,
    margin=dict(l=20, r=20, t=50, b=20),
)
st.plotly_chart(sum_fig, use_container_width=True)

conc_l, conc_r = st.columns(2)

best_why = (
    f"{BEST_DOMAIN} leads all domains with an overall conversion rate of "
    f"{TOTALS[BEST_DOMAIN]['overall_cr']:.1%}. This is driven by a strong lead-to-conversion "
    f"rate of {TOTALS[BEST_DOMAIN]['conv_rate']:.0%} and consistent month-over-month visitor "
    f"growth. The domain benefits from high purchase-intent traffic and a streamlined conversion path."
)
lose_text = (
    f"The steepest drop-off is at the Visitor→Lead stage for {LOWEST_LEADS} "
    f"({(1 - TOTALS[LOWEST_LEADS]['lead_rate']):.0%} of visitors never become leads). "
    f"This points to weak calls-to-action, poor landing-page relevance, or a mismatch "
    f"between ad audience and offering. Fixing this stage offers the highest ROI improvement."
)

with conc_l:
    st.markdown(
        f"<div class='conc-box'>"
        f"<div class='conc-q'>🏆 Which domain is performing best and why?</div>"
        f"<div class='conc-a'>{best_why}</div>"
        f"<div class='conc-q'>📉 Where are we losing customers?</div>"
        f"<div class='conc-a'>{lose_text}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

PRIORITIES = [
    (
        "🥇 Priority 1 — Health & Beauty",
        "Highest visitor volume but lowest conversion rate — greatest absolute upside. "
        "Focus: retargeting campaigns, trust-signal optimisation, influencer-to-booking attribution.",
    ),
    (
        "🥈 Priority 2 — Automobile",
        "Mid-tier performance with clear room for lead nurturing improvement. "
        "Focus: pre-qualification workflows and paid-channel budget reallocation.",
    ),
    (
        "🥉 Priority 3 — IT Solutions",
        "Already the strongest performer — protect the gains. "
        "Focus: sustained SEO content investment and formalising the partner referral programme.",
    ),
]

with conc_r:
    inner = "".join(
        f"<div style='margin-bottom:0.75rem;'>"
        f"<div style='font-weight:700;color:#a5b4fc;font-size:0.88rem;'>{t}</div>"
        f"<div style='font-size:0.81rem;color:#cbd5e1;line-height:1.55;'>{b}</div>"
        f"</div>"
        for t, b in PRIORITIES
    )
    st.markdown(
        f"<div class='conc-box'>"
        f"<div class='conc-q'>🎯 What should be prioritised for improvement?</div>"
        f"<div style='margin-top:0.5rem;'>{inner}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div style='text-align:center;color:#4b5563;font-size:0.72rem;margin-top:2rem;'>"
    "Business Gap Analysis Dashboard v2.0 · Built with Streamlit &amp; Plotly"
    "</div>",
    unsafe_allow_html=True,
)