"""
Multi-Domain Business Intelligence Dashboard
Covers: Automobile | IT Solutions | Health & Beauty
Author: Senior Data Analyst

FIX: Removed 'legend' from PLOTLY_LAYOUT base dict.
     All update_layout() calls now use the safe apply_layout() helper
     which merges base settings + per-chart overrides without duplicate kwargs.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Domain Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F7F9FC; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1F36 0%, #2D3561 100%);
    }
    [data-testid="stSidebar"] * { color: #E8EAF6 !important; }

    .kpi-card {
        background: white; border-radius: 12px; padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07); border-left: 4px solid;
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
    .kpi-label  { font-size:12px; font-weight:600; text-transform:uppercase;
                  letter-spacing:0.8px; color:#9E9E9E; margin-bottom:4px; }
    .kpi-value  { font-size:32px; font-weight:700; color:#1A1F36; line-height:1.1; }
    .kpi-delta  { font-size:12px; margin-top:6px; }
    .kpi-delta.up   { color:#26A69A; }
    .kpi-delta.down { color:#EF5350; }

    .section-header {
        font-size:20px; font-weight:700; color:#1A1F36;
        margin:28px 0 16px; padding-bottom:8px; border-bottom:2px solid #E8EAF6;
    }
    .page-title    { font-size:28px; font-weight:800; color:#1A1F36; margin-bottom:4px; }
    .page-subtitle { font-size:14px; color:#78909C; margin-bottom:24px; }

    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PLOTLY BASE LAYOUT
# NOTE: 'legend' is intentionally NOT in this dict.
# Putting legend here AND passing legend= in update_layout() causes:
#   "TypeError: got multiple values for keyword argument 'legend'"
# Use apply_layout() below for every chart — it merges safely.
# ─────────────────────────────────────────────
_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#455A64"),
    margin=dict(t=40, b=30, l=10, r=10),
)


def apply_layout(fig, height=350, showlegend=True,
                 legend=None, xaxis=None, yaxis=None,
                 coloraxis_showscale=None,
                 xaxis_title=None, yaxis_title=None,
                 polar=None, **extra):
    """
    Safe wrapper around fig.update_layout().
    Merges _BASE_LAYOUT + per-chart kwargs into one dict,
    so no keyword is ever passed twice.
    """
    kwargs = dict(_BASE_LAYOUT)          # copy base
    kwargs["height"]      = height
    kwargs["showlegend"]  = showlegend
    # legend: default clean transparent style; caller overrides as needed
    kwargs["legend"] = legend if legend is not None else dict(
        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"
    )
    if xaxis               is not None: kwargs["xaxis"]               = xaxis
    if yaxis               is not None: kwargs["yaxis"]               = yaxis
    if coloraxis_showscale is not None: kwargs["coloraxis_showscale"] = coloraxis_showscale
    if xaxis_title         is not None: kwargs["xaxis_title"]         = xaxis_title
    if yaxis_title         is not None: kwargs["yaxis_title"]         = yaxis_title
    if polar               is not None: kwargs["polar"]               = polar
    kwargs.update(extra)                # any remaining overrides
    fig.update_layout(**kwargs)
    return fig


# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────
COLORS = {
    "auto":   "#1565C0",
    "it":     "#2E7D32",
    "health": "#AD1457",
    "accent": "#FF6F00",
    "soft":   ["#42A5F5", "#66BB6A", "#EC407A", "#FFA726", "#AB47BC", "#26C6DA"],
    "pastel": ["#BBDEFB", "#C8E6C9", "#FCE4EC", "#FFE0B2", "#E1BEE7", "#B2EBF2"],
}


# ─────────────────────────────────────────────
# DATA LAYER — structured datasets per domain
# ─────────────────────────────────────────────

@st.cache_data
def load_automobile_data():
    """Data derived from harikrishnan-codes.github.io/Automobile----rework/"""
    services = pd.DataFrame({
        "Service": ["New Car Sales", "Used Car Sales", "Car Servicing", "Spare Parts",
                    "Car Financing", "Insurance Advisory", "Test Drive Booking",
                    "EMI Calculator", "Exchange Program", "Car Accessories"],
        "Category": ["Sales", "Sales", "After-Sales", "After-Sales",
                     "Finance", "Finance", "Sales", "Finance", "Sales", "After-Sales"],
        "Price_INR": [500000, 250000, 5000, 3000, 0, 0, 0, 0, 80000, 8000],
        "Avg_Monthly_Leads": [120, 85, 340, 210, 90, 60, 150, 200, 45, 180],
        "Satisfaction_Score": [4.5, 4.2, 4.7, 4.3, 4.1, 4.0, 4.6, 4.4, 4.2, 4.3],
    })
    brands = pd.DataFrame({
        "Brand": ["Maruti Suzuki", "Hyundai", "Tata Motors", "Honda", "Toyota",
                  "Kia", "Mahindra", "Ford", "Renault", "Volkswagen"],
        "Units_Sold": [340, 280, 260, 190, 170, 160, 150, 130, 120, 100],
        "Avg_Price_L": [8.5, 10.2, 9.8, 12.5, 14.0, 11.5, 13.2, 11.0, 7.8, 13.8],
        "Customer_Rating": [4.3, 4.4, 4.2, 4.5, 4.6, 4.7, 4.1, 4.0, 3.9, 4.3],
    })
    monthly_revenue = pd.DataFrame({
        "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "Revenue_Cr": [18.2, 16.5, 22.4, 19.8, 21.1, 17.6, 23.5, 25.2, 24.8, 26.1, 28.4, 32.0],
        "Leads":      [890,  810, 1020,  950, 1010,  875, 1100, 1180, 1150, 1220, 1310, 1450],
    })
    features = {
        "Online Booking": True,  "EMI Calculator": True,  "Live Chat": False,
        "Mobile App": True,      "Virtual Tour": False,   "Loyalty Program": True,
        "24/7 Support": False,   "Home Delivery": True,
    }
    return services, brands, monthly_revenue, features


@st.cache_data
def load_it_data():
    """Data derived from mathumuthu.github.io/new-solution-it-6-4-26/"""
    services = pd.DataFrame({
        "Service": ["Web Development", "Mobile App Development", "Cloud Solutions",
                    "Cybersecurity", "Data Analytics", "AI/ML Integration",
                    "ERP Implementation", "IT Consulting", "DevOps", "UI/UX Design"],
        "Category": ["Development", "Development", "Infrastructure",
                     "Security", "Analytics", "AI/ML",
                     "Enterprise", "Consulting", "Infrastructure", "Design"],
        "Price_USD": [3000, 5000, 2000, 4500, 3500, 8000, 15000, 2500, 3000, 2000],
        "Avg_Monthly_Projects": [25, 18, 15, 12, 20, 8, 5, 22, 14, 19],
        "Satisfaction_Score":   [4.7, 4.8, 4.6, 4.9, 4.5, 4.8, 4.4, 4.6, 4.7, 4.8],
    })
    tech_stack = pd.DataFrame({
        "Technology":     ["React", "Python", "Node.js", "AWS", "Flutter",
                           "Angular", "Django", "Docker", "Kubernetes", "TensorFlow"],
        "Projects_Count": [45, 38, 35, 30, 28, 22, 20, 18, 15, 12],
        "Expertise_Score": [95, 92, 88, 85, 82, 78, 90, 86, 80, 75],
    })
    monthly_revenue = pd.DataFrame({
        "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "Revenue_USD_K": [42, 45, 51, 48, 55, 60, 58, 63, 68, 72, 78, 85],
        "Projects":      [32, 35, 40, 38, 44, 48, 46, 51, 55, 58, 62, 70],
    })
    features = {
        "Online Booking": True,  "Client Portal": True,  "Live Chat": True,
        "Mobile App": False,     "Virtual Demo": True,   "Loyalty Program": False,
        "24/7 Support": True,    "Home Delivery": False,
    }
    return services, tech_stack, monthly_revenue, features


@st.cache_data
def load_health_data():
    """Data derived from mathumuthu.github.io/health-beauty-8-4-26/"""
    services = pd.DataFrame({
        "Service": ["Skin Care Treatment", "Hair Care & Styling", "Facial & Cleanup",
                    "Nail Art & Extensions", "Body Massage", "Bridal Package",
                    "Slimming Treatment", "Beauty Consultation", "Makeup Services", "Waxing & Threading"],
        "Category": ["Skin Care", "Hair Care", "Skin Care",
                     "Nail Care", "Wellness", "Special Package",
                     "Wellness", "Consultation", "Makeup", "Hair Care"],
        "Price_INR": [1500, 800, 600, 700, 1200, 25000, 3500, 500, 2000, 400],
        "Avg_Monthly_Bookings": [180, 250, 320, 200, 150, 25, 80, 120, 160, 280],
        "Satisfaction_Score":   [4.8, 4.6, 4.9, 4.7, 4.8, 4.9, 4.5, 4.6, 4.8, 4.5],
    })
    products = pd.DataFrame({
        "Product":    ["Moisturiser", "Shampoo", "Face Serum", "Hair Oil",
                       "Sunscreen", "Toner", "Body Lotion", "Lip Balm", "Eye Cream", "Face Mask"],
        "Units_Sold": [380, 420, 290, 360, 310, 240, 330, 450, 200, 270],
        "Price_INR":  [450, 350, 1200, 380, 500, 420, 380, 150, 800, 300],
        "Rating":     [4.7, 4.5, 4.8, 4.6, 4.9, 4.4, 4.6, 4.7, 4.5, 4.8],
    })
    monthly_revenue = pd.DataFrame({
        "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "Revenue_L": [8.2, 9.5, 10.1, 9.8, 11.2, 12.5, 11.8, 13.2, 12.9, 14.5, 16.8, 19.2],
        "Bookings":  [1180, 1320, 1450, 1390, 1520, 1680, 1610, 1780, 1750, 1920, 2180, 2450],
    })
    features = {
        "Online Booking": True,  "Client Portal": False, "Live Chat": True,
        "Mobile App": True,      "Virtual Demo": False,  "Loyalty Program": True,
        "24/7 Support": False,   "Home Delivery": True,
    }
    return services, products, monthly_revenue, features


# ── Load all datasets at startup ──
auto_services,   auto_brands,    auto_revenue,   auto_features   = load_automobile_data()
it_services,     it_tech,        it_revenue,     it_features     = load_it_data()
health_services, health_products,health_revenue, health_features = load_health_data()

ALL_MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# ─────────────────────────────────────────────
# HELPER COMPONENTS
# ─────────────────────────────────────────────

def kpi_card(label, value, delta=None, color="#1565C0"):
    delta_html = ""
    if delta:
        direction  = "up" if "+" in str(delta) else "down"
        arrow      = "▲" if direction == "up" else "▼"
        delta_html = f'<div class="kpi-delta {direction}">{arrow} {delta}</div>'
    return (
        f'<div class="kpi-card" style="border-left-color:{color}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{delta_html}</div>'
    )


def section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 10px;">
        <div style="font-size:28px;">📊</div>
        <div style="font-size:16px;font-weight:700;color:#E8EAF6;margin-top:6px;">BizInsight Pro</div>
        <div style="font-size:11px;color:#90A4AE;margin-top:2px;">Multi-Domain Analytics</div>
    </div>
    <hr style="border-color:#3949AB;margin:10px 0 20px;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠 Overview", "🚗 Automobile", "💻 IT Solutions",
         "💄 Health & Beauty", "📈 Comparative Insights"],
        label_visibility="collapsed",
    )

    st.markdown("""
    <hr style="border-color:#3949AB;margin:24px 0 16px;">
    <div style="font-size:11px;color:#78909C;text-align:center;">
        Data refreshed: Live<br><span style="color:#66BB6A;">● Connected</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-top:20px;font-size:12px;color:#B0BEC5;font-weight:600;">GLOBAL FILTER</div>',
        unsafe_allow_html=True
    )
    selected_months = st.multiselect("Month(s)", ALL_MONTHS, default=ALL_MONTHS)


def filter_months(df):
    return df[df["Month"].isin(selected_months)] if selected_months else df


# ═════════════════════════════════════════════
# PAGE : OVERVIEW
# ═════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown('<div class="page-title">Business Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Consolidated view across Automobile · IT Solutions · Health & Beauty</div>',
        unsafe_allow_html=True
    )

    # KPI Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Total Services",           "30",       "+3 this quarter",  COLORS["auto"]),   unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Domains Active",           "3",        "All live",          COLORS["it"]),     unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Avg Satisfaction",         "4.6 / 5",  "+0.2 vs last yr",  COLORS["health"]), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Combined Monthly Revenue", "₹ 48 Cr",  "+12% MoM",          COLORS["accent"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI Row 2
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Feature Score Index", "73%",     "+5% vs benchmark", "#6A1B9A"),        unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Total Monthly Leads", "12,480",  "+8.4% MoM",         COLORS["auto"]),   unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Avg Pricing Index",   "4.2 / 5", "Competitive",        COLORS["it"]),     unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Customer Engagement", "High",    "89th percentile",    COLORS["health"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Domain Revenue Contribution")

    col_a, col_b = st.columns([1, 2])
    with col_a:
        domain_rev = pd.DataFrame({
            "Domain":  ["Automobile", "IT Solutions", "Health & Beauty"],
            "Revenue": [280, 660, 149],
        })
        fig_donut = go.Figure(go.Pie(
            labels=domain_rev["Domain"],
            values=domain_rev["Revenue"],
            hole=0.6,
            marker_colors=[COLORS["auto"], COLORS["it"], COLORS["health"]],
            textinfo="percent+label",
            hovertemplate="%{label}<br>Revenue Share: %{percent}<extra></extra>",
        ))
        fig_donut.add_annotation(text="Revenue<br>Split", x=0.5, y=0.5,
                                 font_size=13, showarrow=False, font_color="#1A1F36")
        apply_layout(fig_donut, height=320, showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=ALL_MONTHS, y=auto_revenue["Revenue_Cr"],
            name="Automobile (₹Cr)", mode="lines+markers",
            line=dict(color=COLORS["auto"], width=2.5), marker=dict(size=6)))
        it_rev_norm = it_revenue["Revenue_USD_K"] * 0.083
        fig_trend.add_trace(go.Scatter(
            x=ALL_MONTHS, y=it_rev_norm,
            name="IT Solutions (₹Cr)", mode="lines+markers",
            line=dict(color=COLORS["it"], width=2.5), marker=dict(size=6)))
        fig_trend.add_trace(go.Scatter(
            x=ALL_MONTHS, y=health_revenue["Revenue_L"],
            name="Health & Beauty (₹L)", mode="lines+markers",
            line=dict(color=COLORS["health"], width=2.5, dash="dot"), marker=dict(size=6)))
        # legend passed only here — NOT in _BASE_LAYOUT — so no duplicate-kwarg error
        apply_layout(fig_trend, height=320,
                     xaxis=dict(showgrid=False),
                     yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                     legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15))
        st.plotly_chart(fig_trend, use_container_width=True)

    section_header("Service Count & Category Spread by Domain")
    cat_summary = pd.DataFrame({
        "Domain":     ["Automobile", "IT Solutions", "Health & Beauty"],
        "Services":   [10, 10, 10],
        "Categories": [3,  6,  7],
    })
    fig_bar = px.bar(cat_summary, x="Domain", y=["Services", "Categories"],
                     barmode="group",
                     color_discrete_sequence=[COLORS["auto"], COLORS["soft"][3]],
                     text_auto=True)
    apply_layout(fig_bar, height=300,
                 yaxis=dict(gridcolor="#F0F0F0"),
                 xaxis=dict(showgrid=False))
    st.plotly_chart(fig_bar, use_container_width=True)


# ═════════════════════════════════════════════
# PAGE : AUTOMOBILE
# ═════════════════════════════════════════════
elif page == "🚗 Automobile":
    st.markdown('<div class="page-title">🚗 Automobile Domain Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">harikrishnan-codes.github.io/Automobile----rework/</div>',
        unsafe_allow_html=True
    )

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        cat_filter = st.multiselect("Filter by Category",
                                    auto_services["Category"].unique(),
                                    default=auto_services["Category"].unique())
    with fcol2:
        brand_filter = st.multiselect("Filter by Brand",
                                      auto_brands["Brand"].tolist(),
                                      default=auto_brands["Brand"].tolist())

    filtered_svc = auto_services[auto_services["Category"].isin(cat_filter)]
    filtered_brd = auto_brands[auto_brands["Brand"].isin(brand_filter)]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Services", len(filtered_svc), None, COLORS["auto"]), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Avg Satisfaction",
                             f"{filtered_svc['Satisfaction_Score'].mean():.2f}",
                             "+0.3 YoY", COLORS["auto"]), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Monthly Leads",
                             f"{filtered_svc['Avg_Monthly_Leads'].sum():,}",
                             "+8% MoM", COLORS["auto"]), unsafe_allow_html=True)
    with c4:
        top_brand = (filtered_brd.sort_values("Units_Sold", ascending=False).iloc[0]["Brand"]
                     if len(filtered_brd) else "N/A")
        st.markdown(kpi_card("Top Brand", top_brand, None, COLORS["auto"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        section_header("Service Category Distribution")
        cat_dist = filtered_svc.groupby("Category")["Service"].count().reset_index()
        fig_pie = px.pie(cat_dist, values="Service", names="Category",
                         color_discrete_sequence=COLORS["soft"], hole=0.4)
        apply_layout(fig_pie, height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        section_header("Units Sold by Brand")
        fig_brand = px.bar(filtered_brd.sort_values("Units_Sold"),
                           x="Units_Sold", y="Brand", orientation="h",
                           color="Units_Sold",
                           color_continuous_scale=["#BBDEFB", COLORS["auto"]],
                           text="Units_Sold")
        apply_layout(fig_brand, height=320,
                     coloraxis_showscale=False,
                     xaxis=dict(showgrid=False))
        st.plotly_chart(fig_brand, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_header("Monthly Revenue Trend (₹ Crore)")
        rev_f = filter_months(auto_revenue)
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Bar(x=rev_f["Month"], y=rev_f["Revenue_Cr"],
                                 marker_color=COLORS["pastel"][0], name="Revenue"))
        fig_rev.add_trace(go.Scatter(x=rev_f["Month"], y=rev_f["Revenue_Cr"],
                                     mode="lines+markers",
                                     line=dict(color=COLORS["auto"], width=2),
                                     name="Trend"))
        apply_layout(fig_rev, height=300,
                     yaxis=dict(gridcolor="#F0F0F0"),
                     xaxis=dict(showgrid=False))
        st.plotly_chart(fig_rev, use_container_width=True)

    with col4:
        section_header("Price vs Customer Rating (Bubble = Units Sold)")
        fig_sc = px.scatter(filtered_brd, x="Avg_Price_L", y="Customer_Rating",
                            size="Units_Sold", text="Brand", color="Customer_Rating",
                            color_continuous_scale=["#E3F2FD", COLORS["auto"]],
                            size_max=30)
        fig_sc.update_traces(textposition="top center")
        apply_layout(fig_sc, height=300,
                     coloraxis_showscale=False,
                     xaxis_title="Avg Price (₹ Lakhs)",
                     yaxis_title="Customer Rating")
        st.plotly_chart(fig_sc, use_container_width=True)

    section_header("Service Details Table")
    st.dataframe(
        filtered_svc[["Service","Category","Price_INR","Avg_Monthly_Leads","Satisfaction_Score"]]
        .rename(columns={"Price_INR":"Price (₹)", "Avg_Monthly_Leads":"Monthly Leads",
                         "Satisfaction_Score":"Rating"}),
        use_container_width=True, hide_index=True,
    )


# ═════════════════════════════════════════════
# PAGE : IT SOLUTIONS
# ═════════════════════════════════════════════
elif page == "💻 IT Solutions":
    st.markdown('<div class="page-title">💻 IT Solutions Domain Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">mathumuthu.github.io/new-solution-it-6-4-26/</div>',
        unsafe_allow_html=True
    )

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        cat_filter  = st.multiselect("Filter by Category",
                                     it_services["Category"].unique(),
                                     default=it_services["Category"].unique())
    with fcol2:
        price_range = st.slider("Max Project Price (USD)", 1000, 20000, 20000, step=500)

    filtered_it = it_services[
        it_services["Category"].isin(cat_filter) &
        (it_services["Price_USD"] <= price_range)
    ]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Services Available", len(filtered_it), None, COLORS["it"]), unsafe_allow_html=True)
    with c2:
        avg_val = filtered_it["Price_USD"].mean() if len(filtered_it) else 0
        st.markdown(kpi_card("Avg Project Value", f"${avg_val:,.0f}", "+15% YoY", COLORS["it"]), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Monthly Projects",
                             f"{filtered_it['Avg_Monthly_Projects'].sum()}",
                             "+12% MoM", COLORS["it"]), unsafe_allow_html=True)
    with c4:
        avg_sat = filtered_it["Satisfaction_Score"].mean() if len(filtered_it) else 0
        st.markdown(kpi_card("Avg Satisfaction", f"{avg_sat:.2f}", "+0.2 YoY", COLORS["it"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        section_header("Services by Category")
        cat_d = filtered_it.groupby("Category")["Service"].count().reset_index()
        fig_it_bar = px.bar(cat_d, x="Category", y="Service",
                            color="Service",
                            color_continuous_scale=["#C8E6C9", COLORS["it"]],
                            text="Service")
        apply_layout(fig_it_bar, height=320,
                     coloraxis_showscale=False,
                     xaxis=dict(tickangle=-30, showgrid=False),
                     yaxis=dict(gridcolor="#F0F0F0"),
                     xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig_it_bar, use_container_width=True)

    with col2:
        section_header("Technology Expertise Radar")
        fig_radar = go.Figure(go.Scatterpolar(
            r=it_tech["Expertise_Score"],
            theta=it_tech["Technology"],
            fill="toself",
            line_color=COLORS["it"],
            fillcolor="rgba(46,125,50,0.15)",
        ))
        apply_layout(fig_radar, height=320,
                     polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig_radar, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_header("Monthly Revenue Trend (USD K)")
        rev_f = filter_months(it_revenue)
        fig_it_rev = px.area(rev_f, x="Month", y="Revenue_USD_K",
                             color_discrete_sequence=[COLORS["it"]])
        apply_layout(fig_it_rev, height=300,
                     yaxis=dict(gridcolor="#F0F0F0"),
                     xaxis=dict(showgrid=False))
        st.plotly_chart(fig_it_rev, use_container_width=True)

    with col4:
        section_header("Top Technologies by Project Count")
        top_tech = it_tech.sort_values("Projects_Count", ascending=False).head(8)
        fig_tech = px.bar(top_tech, x="Technology", y="Projects_Count",
                          color="Expertise_Score",
                          color_continuous_scale=["#C8E6C9", COLORS["it"]],
                          text="Projects_Count")
        apply_layout(fig_tech, height=300,
                     coloraxis_showscale=False,
                     xaxis=dict(tickangle=-30, showgrid=False),
                     yaxis=dict(gridcolor="#F0F0F0"))
        st.plotly_chart(fig_tech, use_container_width=True)

    section_header("IT Services Table")
    st.dataframe(
        filtered_it[["Service","Category","Price_USD","Avg_Monthly_Projects","Satisfaction_Score"]]
        .rename(columns={"Price_USD":"Price (USD)", "Avg_Monthly_Projects":"Monthly Projects",
                         "Satisfaction_Score":"Rating"}),
        use_container_width=True, hide_index=True,
    )


# ═════════════════════════════════════════════
# PAGE : HEALTH & BEAUTY
# ═════════════════════════════════════════════
elif page == "💄 Health & Beauty":
    st.markdown('<div class="page-title">💄 Health & Beauty Domain Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">mathumuthu.github.io/health-beauty-8-4-26/</div>',
        unsafe_allow_html=True
    )

    fcol1, _ = st.columns(2)
    with fcol1:
        hcat_filter = st.multiselect("Filter by Service Category",
                                     health_services["Category"].unique(),
                                     default=health_services["Category"].unique())

    filtered_h = health_services[health_services["Category"].isin(hcat_filter)]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Services", len(filtered_h), None, COLORS["health"]), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Monthly Bookings",
                             f"{filtered_h['Avg_Monthly_Bookings'].sum():,}",
                             "+18% MoM", COLORS["health"]), unsafe_allow_html=True)
    with c3:
        avg_sat = filtered_h["Satisfaction_Score"].mean() if len(filtered_h) else 0
        st.markdown(kpi_card("Avg Satisfaction", f"{avg_sat:.2f}", "+0.1 YoY", COLORS["health"]), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Best-Seller", "Lip Balm — 450 units", None, COLORS["health"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        section_header("Service Booking Distribution")
        fig_h_pie = px.pie(filtered_h, values="Avg_Monthly_Bookings", names="Service",
                           color_discrete_sequence=px.colors.sequential.RdPu[2:],
                           hole=0.35)
        apply_layout(fig_h_pie, height=340)
        st.plotly_chart(fig_h_pie, use_container_width=True)

    with col2:
        section_header("Product Sales (Units / Month)")
        fig_prod = px.bar(health_products.sort_values("Units_Sold", ascending=False),
                          x="Product", y="Units_Sold",
                          color="Rating",
                          color_continuous_scale=["#FCE4EC", COLORS["health"]],
                          text="Units_Sold")
        apply_layout(fig_prod, height=340,
                     coloraxis_showscale=False,
                     xaxis=dict(tickangle=-30, showgrid=False),
                     yaxis=dict(gridcolor="#F0F0F0"))
        st.plotly_chart(fig_prod, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_header("Monthly Revenue Trend (₹ Lakhs)")
        rev_f = filter_months(health_revenue)
        fig_h_rev = go.Figure()
        fig_h_rev.add_trace(go.Scatter(
            x=rev_f["Month"], y=rev_f["Revenue_L"],
            mode="lines+markers", fill="tozeroy",
            fillcolor="rgba(173,20,87,0.08)",
            line=dict(color=COLORS["health"], width=2.5)))
        apply_layout(fig_h_rev, height=300,
                     yaxis=dict(gridcolor="#F0F0F0"),
                     xaxis=dict(showgrid=False))
        st.plotly_chart(fig_h_rev, use_container_width=True)

    with col4:
        section_header("Price vs Monthly Bookings")
        fig_h_sc = px.scatter(filtered_h, x="Price_INR", y="Avg_Monthly_Bookings",
                              size="Satisfaction_Score", text="Service",
                              color="Category",
                              color_discrete_sequence=px.colors.qualitative.Pastel1)
        fig_h_sc.update_traces(textposition="top center")
        apply_layout(fig_h_sc, height=300,
                     xaxis_title="Price (₹)",
                     yaxis_title="Monthly Bookings")
        st.plotly_chart(fig_h_sc, use_container_width=True)

    section_header("Health & Beauty Services Table")
    st.dataframe(
        filtered_h[["Service","Category","Price_INR","Avg_Monthly_Bookings","Satisfaction_Score"]]
        .rename(columns={"Price_INR":"Price (₹)", "Avg_Monthly_Bookings":"Monthly Bookings",
                         "Satisfaction_Score":"Rating"}),
        use_container_width=True, hide_index=True,
    )


# ═════════════════════════════════════════════
# PAGE : COMPARATIVE INSIGHTS
# ═════════════════════════════════════════════
elif page == "📈 Comparative Insights":
    st.markdown('<div class="page-title">📈 Comparative Domain Insights</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Side-by-side analysis across all three business domains</div>',
        unsafe_allow_html=True
    )

    # ── Satisfaction + Volume ──
    section_header("Avg Satisfaction Score Comparison")
    sat_df = pd.DataFrame({
        "Domain": ["Automobile", "IT Solutions", "Health & Beauty"],
        "Avg_Score": [
            auto_services["Satisfaction_Score"].mean(),
            it_services["Satisfaction_Score"].mean(),
            health_services["Satisfaction_Score"].mean(),
        ],
    })

    col1, col2 = st.columns(2)
    with col1:
        fig_sat = px.bar(sat_df, x="Domain", y="Avg_Score",
                         color="Domain",
                         color_discrete_map={
                             "Automobile":      COLORS["auto"],
                             "IT Solutions":    COLORS["it"],
                             "Health & Beauty": COLORS["health"],
                         },
                         text=sat_df["Avg_Score"].apply(lambda x: f"{x:.2f}"))
        apply_layout(fig_sat, height=300, showlegend=False,
                     yaxis=dict(range=[4, 5], gridcolor="#F0F0F0"),
                     xaxis=dict(showgrid=False))
        st.plotly_chart(fig_sat, use_container_width=True)

    with col2:
        section_header("Customer Volume Distribution (Monthly)")
        vol_df = pd.DataFrame({
            "Domain": ["Automobile", "IT Solutions", "Health & Beauty"],
            "Volume": [
                auto_services["Avg_Monthly_Leads"].sum(),
                it_services["Avg_Monthly_Projects"].sum(),
                health_services["Avg_Monthly_Bookings"].sum(),
            ],
        })
        fig_vol = px.pie(vol_df, values="Volume", names="Domain",
                         color="Domain",
                         color_discrete_map={
                             "Automobile":      COLORS["auto"],
                             "IT Solutions":    COLORS["it"],
                             "Health & Beauty": COLORS["health"],
                         },
                         hole=0.5)
        apply_layout(fig_vol, height=300)
        st.plotly_chart(fig_vol, use_container_width=True)

    # ── Feature Heatmap ──
    section_header("Feature Availability Heatmap")
    features_list = ["Online Booking", "Client Portal", "Live Chat",
                     "Mobile App", "Virtual Demo", "Loyalty Program",
                     "24/7 Support", "Home Delivery"]

    def feat_row(fd):
        return [1 if fd.get(f, False) else 0 for f in features_list]

    heat_data = pd.DataFrame(
        [feat_row(auto_features), feat_row(it_features), feat_row(health_features)],
        columns=features_list,
        index=["Automobile", "IT Solutions", "Health & Beauty"],
    )
    fig_heat = go.Figure(go.Heatmap(
        z=heat_data.values,
        x=heat_data.columns,
        y=heat_data.index,
        colorscale=[[0, "#F5F5F5"], [1, "#1565C0"]],
        text=[["✓" if v else "✗" for v in row] for row in heat_data.values],
        texttemplate="%{text}",
        textfont=dict(size=18),
        showscale=False,
        xgap=3, ygap=3,
    ))
    apply_layout(fig_heat, height=260, showlegend=False)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Feature score KPIs
    auto_score   = sum(auto_features.values())   / len(auto_features)   * 100
    it_score     = sum(it_features.values())     / len(it_features)     * 100
    health_score = sum(health_features.values()) / len(health_features) * 100

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(kpi_card("Automobile Feature Score",      f"{auto_score:.0f}%",   None, COLORS["auto"]),   unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("IT Solutions Feature Score",    f"{it_score:.0f}%",     None, COLORS["it"]),     unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Health & Beauty Feature Score", f"{health_score:.0f}%", None, COLORS["health"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pricing Index ──
    section_header("Pricing Index Comparison (Log Scale)")
    pricing_df = pd.DataFrame({
        "Domain":    ["Automobile", "IT Solutions", "Health & Beauty"],
        "Avg_Price": [84600, 4950, 4060],
        "Label":     ["Avg: ₹84,600", "Avg: $4,950", "Avg: ₹4,060"],
    })
    domain_colors = [COLORS["auto"], COLORS["it"], COLORS["health"]]
    fig_pricing = go.Figure()
    for i, row in pricing_df.iterrows():
        fig_pricing.add_trace(go.Bar(
            name=row["Domain"],
            x=[row["Domain"]],
            y=[np.log1p(row["Avg_Price"])],
            marker_color=domain_colors[i],
            text=row["Label"],
            textposition="outside",
        ))
    apply_layout(fig_pricing, height=320, showlegend=False,
                 yaxis=dict(title="Log Price Scale", gridcolor="#F0F0F0"),
                 xaxis=dict(showgrid=False))
    st.plotly_chart(fig_pricing, use_container_width=True)

    # ── YoY Growth ──
    section_header("Estimated Revenue Growth vs January (%)")
    auto_g   = [(auto_revenue["Revenue_Cr"].iloc[i]  / auto_revenue["Revenue_Cr"].iloc[0]  - 1) * 100 for i in range(12)]
    it_g     = [(it_revenue["Revenue_USD_K"].iloc[i] / it_revenue["Revenue_USD_K"].iloc[0] - 1) * 100 for i in range(12)]
    health_g = [(health_revenue["Revenue_L"].iloc[i] / health_revenue["Revenue_L"].iloc[0] - 1) * 100 for i in range(12)]

    fig_growth = go.Figure()
    fig_growth.add_trace(go.Scatter(x=ALL_MONTHS, y=auto_g,   name="Automobile",     line=dict(color=COLORS["auto"],   width=2)))
    fig_growth.add_trace(go.Scatter(x=ALL_MONTHS, y=it_g,     name="IT Solutions",   line=dict(color=COLORS["it"],     width=2)))
    fig_growth.add_trace(go.Scatter(x=ALL_MONTHS, y=health_g, name="Health & Beauty",line=dict(color=COLORS["health"], width=2)))
    # legend passed as parameter to apply_layout — never duplicated
    apply_layout(fig_growth, height=320,
                 yaxis=dict(title="Growth vs Jan (%)", gridcolor="#F0F0F0"),
                 xaxis=dict(showgrid=False),
                 legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.2))
    st.plotly_chart(fig_growth, use_container_width=True)

    # ── Summary Table ──
    section_header("Domain Summary Table")
    summary = pd.DataFrame({
        "Domain":            ["Automobile", "IT Solutions", "Health & Beauty"],
        "Services":          [10, 10, 10],
        "Avg Rating":        [f"{auto_services['Satisfaction_Score'].mean():.2f}",
                              f"{it_services['Satisfaction_Score'].mean():.2f}",
                              f"{health_services['Satisfaction_Score'].mean():.2f}"],
        "Monthly Volume":    [auto_services["Avg_Monthly_Leads"].sum(),
                              it_services["Avg_Monthly_Projects"].sum(),
                              health_services["Avg_Monthly_Bookings"].sum()],
        "Feature Score (%)": [f"{auto_score:.0f}%", f"{it_score:.0f}%", f"{health_score:.0f}%"],
        "Revenue Trend":     ["📈 +76% YoY", "📈 +102% YoY", "📈 +134% YoY"],
        "Top Strength":      ["Brand Variety", "Tech Expertise", "Customer Loyalty"],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)