import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nykaa Marketing Intelligence",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background: #0f0f14 !important;
    color: #e8e8f0 !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #16161f !important;
    border-right: 1px solid #2a2a38 !important;
}
section[data-testid="stSidebar"] * { color: #c8c8d8 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiselect label,
section[data-testid="stSidebar"] .stDateInput label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: #fc2779 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="input"] > div {
    background: #1e1e2c !important;
    border: 1px solid #2e2e42 !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
}

/* ── Main area ── */
.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 100% !important;
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #1a0a14 0%, #2d0f24 40%, #1a0a2e 100%);
    border: 1px solid #3d1535;
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(252,39,121,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -40px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(108,92,231,0.14) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-tag {
    display: inline-block;
    background: rgba(252,39,121,0.15);
    border: 1px solid rgba(252,39,121,0.35);
    border-radius: 30px;
    padding: 3px 14px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #fc2779;
    margin-bottom: 0.8rem;
}
.hero h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.4rem !important;
    font-weight: 400 !important;
    color: #ffffff !important;
    line-height: 1.15 !important;
    margin-bottom: 0.5rem !important;
}
.hero h1 span { color: #fc2779; }
.hero p {
    color: #8888aa !important;
    font-size: 0.95rem !important;
    font-weight: 300 !important;
    max-width: 520px;
}
.hero-stats {
    display: flex; gap: 2rem; margin-top: 1.4rem;
    flex-wrap: wrap;
}
.hero-stat-val { font-size: 1.4rem; font-weight: 700; color: #fff; }
.hero-stat-lbl { font-size: 0.7rem; color: #666688; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 2px; }

/* ── KPI cards ── */
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1.8rem; flex-wrap: wrap; }
.kpi {
    flex: 1; min-width: 140px;
    background: #16161f;
    border: 1px solid #2a2a38;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi:hover { border-color: #fc2779; }
.kpi::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent, #fc2779);
    border-radius: 14px 14px 0 0;
}
.kpi-icon { font-size: 1.3rem; margin-bottom: 0.5rem; }
.kpi-val {
    font-size: 1.65rem; font-weight: 700;
    color: #ffffff; line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-lbl {
    font-size: 0.71rem; font-weight: 600;
    color: #666688; text-transform: uppercase; letter-spacing: 0.8px;
}
.kpi-delta { font-size: 0.78rem; color: #00d68f; margin-top: 0.3rem; font-weight: 500; }
.kpi-delta.neg { color: #ff4d6d; }

/* ── Section heading ── */
.sec-head {
    display: flex; align-items: center; gap: 0.6rem;
    margin: 1.8rem 0 1rem;
}
.sec-head-line {
    width: 4px; height: 22px;
    background: linear-gradient(180deg, #fc2779, #6c5ce7);
    border-radius: 4px;
}
.sec-head-text {
    font-size: 1.05rem; font-weight: 700;
    color: #ffffff; letter-spacing: -0.2px;
}

/* ── Tabs ── */
div[data-baseweb="tab-list"] {
    background: #16161f !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #2a2a38 !important;
    margin-bottom: 1.5rem !important;
}
button[data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: #666688 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.1rem !important;
    transition: all 0.2s !important;
}
button[data-baseweb="tab"]:hover { color: #ffffff !important; }
button[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #fc2779, #c0205e) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(252,39,121,0.35) !important;
}

/* ── Chart containers ── */
.chart-box {
    background: #16161f;
    border: 1px solid #2a2a38;
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    height: 100%;
}
.chart-title {
    font-size: 0.88rem; font-weight: 700;
    color: #c8c8d8; margin-bottom: 0.8rem;
    text-transform: uppercase; letter-spacing: 0.5px;
}

/* ── Insight cards ── */
.insight {
    background: #16161f;
    border: 1px solid #2a2a38;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.75rem;
    display: flex; gap: 1rem; align-items: flex-start;
    transition: border-color 0.2s, transform 0.2s;
}
.insight:hover { border-color: #fc2779; transform: translateX(3px); }
.insight-icon {
    font-size: 1.6rem; flex-shrink: 0;
    background: rgba(252,39,121,0.1);
    border-radius: 10px; width: 44px; height: 44px;
    display: flex; align-items: center; justify-content: center;
}
.insight-title { font-size: 0.9rem; font-weight: 700; color: #ffffff; margin-bottom: 0.25rem; }
.insight-body { font-size: 0.82rem; color: #888899; line-height: 1.5; }

/* ── Rec cards ── */
.rec {
    background: linear-gradient(135deg, #1a1a28 0%, #16161f 100%);
    border: 1px solid #2a2a38;
    border-left: 3px solid #6c5ce7;
    border-radius: 14px;
    padding: 1rem 1.3rem;
    margin-bottom: 0.75rem;
}
.rec-title { font-size: 0.9rem; font-weight: 700; color: #ffffff; margin-bottom: 0.25rem; }
.rec-body { font-size: 0.82rem; color: #888899; line-height: 1.55; }

/* ── Metric override ── */
div[data-testid="metric-container"] {
    background: #16161f !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
div[data-testid="metric-container"] label { color: #666688 !important; font-size: 0.78rem !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.4rem !important; font-weight: 700 !important; }

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid #2a2a38 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Filter reset badge ── */
.filter-active {
    background: rgba(252,39,121,0.15);
    border: 1px solid #fc2779;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: #fc2779;
    font-weight: 600;
}

/* ── Divider ── */
hr { border-color: #2a2a38 !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f0f14; }
::-webkit-scrollbar-thumb { background: #2a2a38; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_excel("NYKAA_DATASET.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Campaign_Type'] = df['Campaign_Type'].fillna('Unknown')
    df['Month']   = df['Date'].dt.to_period('M').astype(str)
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['YearMon'] = df['Date'].dt.strftime('%b %Y')
    df['CTR']  = (df['Clicks']      / df['Impressions'].replace(0,1) * 100).round(2)
    df['CVR']  = (df['Conversions'] / df['Clicks'].replace(0,1)      * 100).round(2)
    df['CPC']  = (df['Acquisition_Cost'] / df['Clicks'].replace(0,1)).round(2)
    df['CPL']  = (df['Acquisition_Cost'] / df['Leads'].replace(0,1) ).round(2)
    df['CPA']  = (df['Acquisition_Cost'] / df['Conversions'].replace(0,1)).round(2)
    # exclude 'Unknown' (single record)
    df = df[df['Campaign_Type'] != 'Unknown']
    return df

df = load_data()

# ─────────────────────────────────────────────
# COLOUR PALETTE  (consistent across charts)
# ─────────────────────────────────────────────
PAL = {
    'Email':        '#fc2779',
    'Influencer':   '#6c5ce7',
    'Paid Ads':     '#ffa45c',
    'SEO':          '#00cec9',
    'Social Media': '#fdcb6e',
}
COLORS = list(PAL.values())

CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans, sans-serif', color='#a0a0b8', size=12),
    title_font=dict(family='DM Sans, sans-serif', color='#ffffff', size=14),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#a0a0b8')),
    xaxis=dict(gridcolor='#1e1e2c', zerolinecolor='#2a2a38', tickfont=dict(color='#666688')),
    yaxis=dict(gridcolor='#1e1e2c', zerolinecolor='#2a2a38', tickfont=dict(color='#666688')),
    margin=dict(l=10, r=10, t=40, b=10),
)


# ─────────────────────────────────────────────
# SIDEBAR — FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem;'>
        <div style='font-size:2rem'>💄</div>
        <div style='font-size:1.1rem; font-weight:700; color:#fff; margin:4px 0'>Nykaa Analytics</div>
        <div style='font-size:0.72rem; color:#666688; letter-spacing:1px; text-transform:uppercase'>Marketing Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── Campaign Type (multiselect so "all" is explicit) ──
    all_types = sorted(df['Campaign_Type'].unique().tolist())
    sel_types = st.multiselect(
        "Campaign Type",
        options=all_types,
        default=all_types,
        help="Select one or more campaign types"
    )
    if not sel_types:
        sel_types = all_types   # guard: never empty

    # ── Customer Segment ──
    all_segs = sorted(df['Customer_Segment'].unique().tolist())
    sel_segs = st.multiselect(
        "Customer Segment",
        options=all_segs,
        default=all_segs,
    )
    if not sel_segs:
        sel_segs = all_segs

    # ── Target Audience ──
    all_auds = sorted(df['Target_Audience'].unique().tolist())
    sel_auds = st.multiselect(
        "Target Audience",
        options=all_auds,
        default=all_auds,
    )
    if not sel_auds:
        sel_auds = all_auds

    # ── Language ──
    all_langs = sorted(df['Language'].unique().tolist())
    sel_langs = st.multiselect(
        "Language",
        options=all_langs,
        default=all_langs,
    )
    if not sel_langs:
        sel_langs = all_langs

    # ── Date ──
    dmin = df['Date'].min().date()
    dmax = df['Date'].max().date()
    date_rng = st.date_input("Date Range", value=[dmin, dmax], min_value=dmin, max_value=dmax)

    st.markdown("---")
    if st.button("🔄  Reset all filters", use_container_width=True):
        st.rerun()

    st.markdown(f"""
    <div style='font-size:0.75rem; color:#444466; padding-top:0.5rem; line-height:1.8;'>
        <b style='color:#666688'>Dataset</b><br>
        Records: <b style='color:#fff'>55,554</b><br>
        Period: <b style='color:#fff'>Jul 2024 – Jun 2025</b><br>
        Channels: <b style='color:#fff'>5</b>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
fdf = df[
    df['Campaign_Type'].isin(sel_types) &
    df['Customer_Segment'].isin(sel_segs) &
    df['Target_Audience'].isin(sel_auds) &
    df['Language'].isin(sel_langs)
].copy()

if len(date_rng) == 2:
    fdf = fdf[(fdf['Date'].dt.date >= date_rng[0]) & (fdf['Date'].dt.date <= date_rng[1])]

# Safety: if filters wipe everything, revert to full df
if fdf.empty:
    st.warning("⚠️ No data matches the selected filters. Showing full dataset.")
    fdf = df.copy()

# Filtered colour map (only channels present in filtered data)
active_channels = sorted(fdf['Campaign_Type'].unique().tolist())
fpal = {c: PAL.get(c, '#aaaacc') for c in active_channels}


# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
tot_rev  = fdf['Revenue'].sum()
avg_roi  = fdf['ROI'].mean()
tot_conv = fdf['Conversions'].sum()
tot_imp  = fdf['Impressions'].sum()
tot_spend= fdf['Acquisition_Cost'].sum()
avg_ctr  = fdf['CTR'].mean()

st.markdown(f"""
<div class="hero">
    <div class="hero-tag">📊 Marketing Intelligence Platform</div>
    <h1>Nykaa <span>Campaign ROI</span> Dashboard</h1>
    <p>Channel performance · Audience insights · Budget optimisation · Strategic recommendations</p>
    <div class="hero-stats">
        <div>
            <div class="hero-stat-val">₹{tot_rev/1e6:.1f}M</div>
            <div class="hero-stat-lbl">Total Revenue</div>
        </div>
        <div>
            <div class="hero-stat-val">{avg_roi:.2f}x</div>
            <div class="hero-stat-lbl">Average ROI</div>
        </div>
        <div>
            <div class="hero-stat-val">{tot_conv:,}</div>
            <div class="hero-stat-lbl">Conversions</div>
        </div>
        <div>
            <div class="hero-stat-val">{len(fdf):,}</div>
            <div class="hero-stat-lbl">Campaigns Analysed</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
kpis = [
    (k1, "💰", f"₹{tot_rev/1e6:.1f}M",   "Revenue",        "#fc2779"),
    (k2, "📈", f"{avg_roi:.2f}x",          "Avg ROI",        "#6c5ce7"),
    (k3, "🎯", f"{tot_conv:,}",            "Conversions",    "#00cec9"),
    (k4, "💸", f"₹{tot_spend/1e6:.1f}M",  "Ad Spend",       "#ffa45c"),
    (k5, "👁️", f"{tot_imp/1e6:.1f}M",     "Impressions",    "#fdcb6e"),
    (k6, "🖱️", f"{avg_ctr:.2f}%",          "Avg CTR",        "#00b894"),
    (k7, "⚡", f"₹{(tot_rev/tot_spend):.1f}",  "ROAS",      "#fd79a8"),
]
for col, icon, val, lbl, accent in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi" style="--accent:{accent}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-val">{val}</div>
            <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Channel Performance",
    "💹  ROI Analysis",
    "🎯  Audience & Segments",
    "📅  Time Trends",
    "💡  Insights & Strategy"
])

def sec(title):
    st.markdown(f"""
    <div class="sec-head">
        <div class="sec-head-line"></div>
        <div class="sec-head-text">{title}</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 1 – CHANNEL PERFORMANCE
# ══════════════════════════════════════════════
with tab1:
    sec("Channel-wise Performance Overview")

    ch = fdf.groupby('Campaign_Type').agg(
        Campaigns   =('Campaign_ID','count'),
        Impressions =('Impressions','sum'),
        Clicks      =('Clicks','sum'),
        Leads       =('Leads','sum'),
        Conversions =('Conversions','sum'),
        Revenue     =('Revenue','sum'),
        Spend       =('Acquisition_Cost','sum'),
        Avg_ROI     =('ROI','mean'),
        Avg_CTR     =('CTR','mean'),
        Avg_CVR     =('CVR','mean'),
        Avg_Eng     =('Engagement_Score','mean'),
        Avg_CPA     =('CPA','mean'),
    ).reset_index()
    ch['ROAS'] = (ch['Revenue'] / ch['Spend'].replace(0,1)).round(2)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            ch.sort_values('Revenue'),
            x='Revenue', y='Campaign_Type', orientation='h',
            color='Campaign_Type',
            color_discrete_map=fpal,
            text=ch.sort_values('Revenue')['Revenue'].map(lambda v: f'₹{v/1e6:.1f}M'),
            title='Total Revenue by Channel'
        )
        fig.update_traces(textposition='outside', textfont_size=11)
        fig.update_layout(**CHART_LAYOUT, showlegend=False, height=300,
                          xaxis_title="Revenue (₹)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            ch.sort_values('Avg_ROI'),
            x='Avg_ROI', y='Campaign_Type', orientation='h',
            color='Avg_ROI',
            color_continuous_scale=[[0,'#2d0f24'],[0.5,'#a01050'],[1,'#fc2779']],
            text=ch.sort_values('Avg_ROI')['Avg_ROI'].map(lambda v: f'{v:.2f}x'),
            title='Average ROI by Channel'
        )
        fig.update_traces(textposition='outside', textfont_size=11)
        fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False,
                          showlegend=False, height=300, xaxis_title="ROI (x)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Funnel stages
        stages = ['Impressions','Clicks','Leads','Conversions']
        fd = []
        for _, row in ch.iterrows():
            for s in stages:
                fd.append({'Channel': row['Campaign_Type'], 'Stage': s, 'Count': row[s]})
        fd = pd.DataFrame(fd)
        fig = px.bar(fd, x='Stage', y='Count', color='Channel',
                     color_discrete_map=fpal,
                     barmode='group',
                     category_orders={'Stage': stages},
                     title='Marketing Funnel by Channel')
        fig.update_layout(**CHART_LAYOUT, height=320, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Radar
        metrics = ['Avg_CTR','Avg_CVR','Avg_ROI','Avg_Eng','ROAS']
        labels  = ['CTR','CVR','ROI','Engagement','ROAS']
        maxes   = ch[metrics].max()
        fig = go.Figure()
        for _, row in ch.iterrows():
            normed = [(row[m]/maxes[m] if maxes[m]>0 else 0) for m in metrics]
            normed.append(normed[0])
            fig.add_trace(go.Scatterpolar(
                r=normed, theta=labels+[labels[0]],
                fill='toself', name=row['Campaign_Type'],
                line_color=fpal.get(row['Campaign_Type'],'#aaa'),
                opacity=0.75
            ))
        fig.update_layout(
            **{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis')},
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0,1], gridcolor='#2a2a38', tickfont_color='#666688'),
                angularaxis=dict(gridcolor='#2a2a38', tickfont_color='#c0c0d0')
            ),
            title='Multi-metric Channel Radar',
            height=320, showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # CPA vs ROAS bubble
    sec("Efficiency Matrix")
    fig = px.scatter(ch, x='ROAS', y='Avg_CPA', size='Revenue',
                     color='Campaign_Type', color_discrete_map=fpal,
                     text='Campaign_Type', size_max=60,
                     title='ROAS vs Cost Per Acquisition  (bubble size = Revenue)')
    fig.update_traces(textposition='top center', textfont=dict(color='#c0c0d0', size=10))
    fig.update_layout(**CHART_LAYOUT, height=350, showlegend=False,
                      xaxis_title='ROAS', yaxis_title='Avg CPA (₹)')
    st.plotly_chart(fig, use_container_width=True)

    # Table
    sec("Detailed Metrics Table")
    disp = ch[['Campaign_Type','Campaigns','Revenue','Spend','Avg_ROI','ROAS',
               'Avg_CTR','Avg_CVR','Conversions','Avg_Eng','Avg_CPA']].copy()
    disp.columns = ['Channel','Campaigns','Revenue (₹)','Spend (₹)','Avg ROI','ROAS',
                    'CTR (%)','CVR (%)','Conversions','Eng. Score','Avg CPA (₹)']
    disp['Revenue (₹)'] = disp['Revenue (₹)'].map('{:,.0f}'.format)
    disp['Spend (₹)']   = disp['Spend (₹)'].map('{:,.0f}'.format)
    disp['Avg ROI']     = disp['Avg ROI'].map('{:.2f}x'.format)
    disp['ROAS']        = disp['ROAS'].map('{:.2f}'.format)
    disp['CTR (%)']     = disp['CTR (%)'].map('{:.2f}%'.format)
    disp['CVR (%)']     = disp['CVR (%)'].map('{:.2f}%'.format)
    disp['Avg CPA (₹)']= disp['Avg CPA (₹)'].map('{:.0f}'.format)
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# TAB 2 – ROI ANALYSIS
# ══════════════════════════════════════════════
with tab2:
    sec("ROI Distribution & Deep Dive")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.violin(fdf, x='Campaign_Type', y='ROI',
                        color='Campaign_Type', color_discrete_map=fpal,
                        box=True, points=False,
                        title='ROI Distribution (Violin + Box)')
        fig.update_layout(**CHART_LAYOUT, showlegend=False, height=360, xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sample = fdf.sample(min(6000,len(fdf)), random_state=42)
        fig = px.scatter(sample, x='Acquisition_Cost', y='ROI',
                         color='Campaign_Type', color_discrete_map=fpal,
                         opacity=0.45, size_max=5,
                         title='ROI vs Ad Spend (6k sample)')
        fig.update_layout(**CHART_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        roi_seg = fdf.groupby(['Campaign_Type','Customer_Segment'])['ROI'].mean().reset_index()
        pivot   = roi_seg.pivot(index='Customer_Segment', columns='Campaign_Type', values='ROI').fillna(0)
        fig = px.imshow(pivot,
                        color_continuous_scale=[[0,'#0f0f14'],[0.4,'#3d1535'],[1,'#fc2779']],
                        text_auto='.2f', aspect='auto',
                        title='Avg ROI Heatmap: Segment × Channel')
        fig.update_layout(**{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis')},
                          height=340)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        grp = fdf.groupby('Campaign_Type').agg(Revenue=('Revenue','sum'),
                                                Spend=('Acquisition_Cost','sum')).reset_index()
        grp['Profit'] = grp['Revenue'] - grp['Spend']
        fig = go.Figure()
        for col_name, col_color, label in [
            ('Revenue','#fc2779','Revenue'),
            ('Spend','#ffa45c','Ad Spend'),
            ('Profit','#6c5ce7','Net Profit')
        ]:
            fig.add_bar(name=label, x=grp['Campaign_Type'], y=grp[col_name],
                        marker_color=col_color)
        fig.update_layout(**CHART_LAYOUT, barmode='group', height=340,
                          title='Revenue · Spend · Net Profit by Channel')
        st.plotly_chart(fig, use_container_width=True)

    sec("ROI Frequency Distribution")
    fig = px.histogram(fdf, x='ROI', color='Campaign_Type',
                       color_discrete_map=fpal,
                       nbins=80, barmode='overlay', opacity=0.6,
                       title='ROI Histogram — All Campaigns')
    fig.add_vline(x=fdf['ROI'].mean(), line_dash='dash', line_color='#ffffff',
                  annotation_text=f"Mean {fdf['ROI'].mean():.2f}x",
                  annotation_font_color='#ffffff')
    fig.update_layout(**CHART_LAYOUT, height=320, xaxis_title='ROI', yaxis_title='Count')
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3 – AUDIENCE & SEGMENTS
# ══════════════════════════════════════════════
with tab3:
    sec("Customer Segment Analysis")

    seg = fdf.groupby('Customer_Segment').agg(
        Revenue=('Revenue','sum'), ROI=('ROI','mean'),
        Conversions=('Conversions','sum'), Eng=('Engagement_Score','mean')
    ).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(seg, names='Customer_Segment', values='Revenue',
                     color_discrete_sequence=COLORS, hole=0.55,
                     title='Revenue Share by Segment')
        fig.update_traces(textposition='outside',
                          texttemplate='%{label}<br>%{percent}')
        fig.update_layout(**{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis')},
                          height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(seg.sort_values('ROI'), x='ROI', y='Customer_Segment',
                     orientation='h', color='ROI',
                     color_continuous_scale=[[0,'#2d0f24'],[1,'#fc2779']],
                     text=seg.sort_values('ROI')['ROI'].map(lambda v: f'{v:.2f}x'),
                     title='Average ROI by Segment')
        fig.update_traces(textposition='outside')
        fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False,
                          height=360, showlegend=False, xaxis_title='ROI (x)', yaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        aud = fdf.groupby('Target_Audience').agg(
            Revenue=('Revenue','sum'), ROI=('ROI','mean'), Eng=('Engagement_Score','mean')
        ).reset_index()
        fig = px.scatter(aud, x='Revenue', y='ROI', size='Eng',
                         color='Target_Audience',
                         color_discrete_sequence=COLORS,
                         hover_name='Target_Audience', size_max=50,
                         title='Audience: Revenue vs ROI (size = Engagement)')
        fig.update_layout(**CHART_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        lang = fdf.groupby('Language').agg(Revenue=('Revenue','sum'),
                                            ROI=('ROI','mean')).reset_index()
        fig = go.Figure(go.Treemap(
            labels=lang['Language'],
            parents=['']*len(lang),
            values=lang['Revenue'],
            customdata=lang[['ROI']],
            texttemplate="%{label}<br>₹%{value:,.0f}<br>ROI: %{customdata[0]:.2f}x",
            marker=dict(colorscale=[[0,'#1a0a14'],[1,'#fc2779']],
                        colors=lang['ROI'], colorbar=dict(title='ROI'))
        ))
        fig.update_layout(
            **{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis')},
            title='Revenue & ROI by Language', height=360
        )
        st.plotly_chart(fig, use_container_width=True)

    sec("Segment × Channel Revenue Matrix")
    pivot = fdf.pivot_table(values='Revenue', index='Customer_Segment',
                             columns='Campaign_Type', aggfunc='sum', fill_value=0)
    fig = px.imshow(pivot,
                    color_continuous_scale=[[0,'#0f0f14'],[0.5,'#3d1535'],[1,'#fc2779']],
                    text_auto='.2s', aspect='auto',
                    title='Revenue Matrix: Segment × Channel')
    fig.update_layout(**{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis')},
                      height=320)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4 – TIME TRENDS
# ══════════════════════════════════════════════
with tab4:
    sec("Monthly & Quarterly Trends")

    monthly = fdf.groupby(['Month','Campaign_Type']).agg(
        Revenue=('Revenue','sum'), ROI=('ROI','mean'),
        Conversions=('Conversions','sum'), Spend=('Acquisition_Cost','sum')
    ).reset_index().sort_values('Month')

    fig = px.line(monthly, x='Month', y='Revenue', color='Campaign_Type',
                  color_discrete_map=fpal, markers=True,
                  title='Monthly Revenue Trend by Channel')
    fig.update_traces(line_width=2.5)
    fig.update_layout(**CHART_LAYOUT, height=360,
                      xaxis_title="", yaxis_title="Revenue (₹)")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.area(monthly, x='Month', y='Conversions', color='Campaign_Type',
                      color_discrete_map=fpal, title='Monthly Conversions by Channel')
        fig.update_layout(**CHART_LAYOUT, height=340, xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        overall_avg = fdf['ROI'].mean()
        fig = px.line(monthly, x='Month', y='ROI', color='Campaign_Type',
                      color_discrete_map=fpal, markers=True,
                      title='Monthly Average ROI Trend')
        fig.add_hline(y=overall_avg, line_dash='dot', line_color='#ffffff',
                      annotation_text=f'Avg {overall_avg:.2f}x',
                      annotation_font_color='#ffffff', annotation_position='right')
        fig.update_traces(line_width=2.5)
        fig.update_layout(**CHART_LAYOUT, height=340, xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    sec("Quarterly Performance")
    qtr = fdf.groupby(['Quarter','Campaign_Type']).agg(Revenue=('Revenue','sum')).reset_index()
    fig = px.bar(qtr, x='Quarter', y='Revenue', color='Campaign_Type',
                 color_discrete_map=fpal, barmode='stack',
                 title='Quarterly Revenue Stack by Channel')
    fig.update_layout(**CHART_LAYOUT, height=340)
    st.plotly_chart(fig, use_container_width=True)

    # Monthly Engagement heatmap
    sec("Engagement Score Heatmap")
    eng_heat = fdf.groupby(['Month','Campaign_Type'])['Engagement_Score'].mean().reset_index()
    eng_pivot= eng_heat.pivot(index='Campaign_Type', columns='Month', values='Engagement_Score').fillna(0)
    fig = px.imshow(eng_pivot,
                    color_continuous_scale=[[0,'#0f0f14'],[0.5,'#3d1535'],[1,'#fc2779']],
                    text_auto='.1f', aspect='auto',
                    title='Avg Engagement Score: Channel × Month')
    fig.update_layout(**{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis')},
                      height=300)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 5 – INSIGHTS & STRATEGY
# ══════════════════════════════════════════════
with tab5:
    sec("Data-Driven Insights")

    best_ch   = fdf.groupby('Campaign_Type')['ROI'].mean().idxmax()
    best_roi  = fdf.groupby('Campaign_Type')['ROI'].mean().max()
    best_rev  = fdf.groupby('Campaign_Type')['Revenue'].sum().idxmax()
    best_seg  = fdf.groupby('Customer_Segment')['Revenue'].sum().idxmax()
    best_aud  = fdf.groupby('Target_Audience')['ROI'].mean().idxmax()
    low_ctr   = fdf.groupby('Campaign_Type')['CTR'].mean().idxmin()
    best_ctr  = fdf.groupby('Campaign_Type')['CTR'].mean().idxmax()
    best_lang = fdf.groupby('Language')['ROI'].mean().idxmax()
    hi_roi_pct= (fdf['ROI'] > 5).mean() * 100
    best_eng  = fdf.groupby('Campaign_Type')['Engagement_Score'].mean().idxmax()

    insights = [
        ("🏆", "Top ROI Channel",        f"<b>{best_ch}</b> delivers the highest avg ROI of <b>{best_roi:.2f}x</b>. Prioritise this channel for performance budgets."),
        ("💰", "Revenue Leader",          f"<b>{best_rev}</b> generates the highest total revenue in the filtered view. Monitor spend efficiency here."),
        ("👥", "Most Valuable Segment",   f"<b>{best_seg}</b> is the top revenue-contributing segment. Personalised campaigns here yield the highest returns."),
        ("🎯", "Best Audience ROI",       f"<b>{best_aud}</b> audience shows the strongest ROI. Tailor creative messaging specifically for this group."),
        ("📣", "CTR Champion",            f"<b>{best_ctr}</b> achieves the best click-through rate. Replicate its creative learnings across other channels."),
        ("🌐", "Language Winner",         f"<b>{best_lang}</b>-language campaigns outperform on ROI. Scale localised content in this language."),
        ("⚠️", "Low CTR Alert",           f"<b>{low_ctr}</b> has the lowest CTR — indicating audience-creative mismatch. Immediate A/B testing recommended."),
        ("💡", "High-ROI Campaign Rate",  f"<b>{hi_roi_pct:.1f}%</b> of campaigns hit ROI > 5x. Isolate these patterns and build a replication playbook."),
        ("✨", "Engagement Leader",       f"<b>{best_eng}</b> leads on engagement score. High engagement often precedes conversion uplift — scale this channel's content approach."),
    ]

    c1, c2 = st.columns(2)
    for i,(icon,title,body) in enumerate(insights):
        with (c1 if i%2==0 else c2):
            st.markdown(f"""
            <div class="insight">
                <div class="insight-icon">{icon}</div>
                <div>
                    <div class="insight-title">{title}</div>
                    <div class="insight-body">{body}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    sec("Strategic Recommendations")

    recs = [
        ("🔝", f"Scale {best_ch} — Highest ROI Channel",
         f"Reallocate 20–30% of underperforming channel budgets to {best_ch} (avg ROI {best_roi:.1f}x). Use incrementality testing to validate the lift before full-scale reallocation."),
        ("👤", f"Segment-First Planning Around {best_seg}",
         f"Build dedicated campaign calendars for {best_seg}. Create bespoke creatives, offers, and landing pages rather than adapting generic campaigns — this segment converts at the highest rate."),
        (f"🌍", f"Expand {best_lang} Localisation Strategy",
         f"{best_lang}-language content drives the strongest ROI. Commission {best_lang} creators, influencers, and copywriters. Pilot adjacent regional languages with similar audience profiles."),
        ("🔄", f"Revive {low_ctr} with Creative Overhaul",
         f"The low CTR on {low_ctr} signals a creative or targeting problem. Run 3–5 creative variants (UGC video, testimonial carousel, discount-led static) with tightened audience segmentation within the next sprint."),
        ("📅", "Seasonality-Driven Budget Shifts",
         "Monthly trend data shows clear peak and trough months. Pre-load awareness spend 4–6 weeks before high-conversion months and throttle budgets during historically low-ROI windows."),
        ("📊", "Implement ROI-Gated Bidding Rules",
         "Set automated rules: pause campaigns below 0.5x ROI for 2 consecutive weeks; increase budgets by 15% for campaigns sustaining >3x ROI. This creates a self-optimising portfolio."),
        ("🤝", "Influencer × Paid Ads Whitelisting",
         "Repurpose top influencer content as whitelisted paid ads — typically lifts CTR by 30–50%. Start with the top 5 performing influencer posts on the best CTR channel."),
        ("🛠️", "Build a Marketing Mix Model (MMM)",
         "With 55K+ campaign records across 12 months, Nykaa has sufficient data for an MMM. This would quantify channel interaction effects, diminishing returns, and the optimal budget split scientifically."),
    ]

    for icon, title, body in recs:
        st.markdown(f"""
        <div class="rec">
            <div class="rec-title">{icon} &nbsp;{title}</div>
            <div class="rec-body">{body}</div>
        </div>""", unsafe_allow_html=True)

    sec("ROI-Weighted Budget Allocation")
    ch2 = fdf.groupby('Campaign_Type')['ROI'].mean().reset_index()
    ch2['Weight'] = ch2['ROI'].clip(lower=0)
    ch2['Pct']    = (ch2['Weight'] / ch2['Weight'].sum() * 100).round(1)
    ch2['Color']  = ch2['Campaign_Type'].map(fpal)

    fig = go.Figure(go.Pie(
        labels=ch2['Campaign_Type'], values=ch2['Pct'],
        hole=0.6,
        marker=dict(colors=ch2['Color'].tolist()),
        texttemplate="%{label}<br><b>%{value}%</b>",
        textposition='outside',
        pull=[0.03]*len(ch2)
    ))
    fig.update_layout(
        **{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis')},
        title='Recommended Budget Split (ROI-Weighted)',
        height=420, showlegend=False,
        annotations=[dict(text='Budget<br>Allocation', x=0.5, y=0.5,
                          font=dict(size=13, color='#ffffff', family='DM Sans'), showarrow=False)]
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; padding:1rem 0; color:#444466; font-size:0.78rem;'>
    💄 <b style='color:#666688'>Nykaa Marketing Intelligence Dashboard</b> &nbsp;·&nbsp;
    Built with Streamlit & Plotly &nbsp;·&nbsp;
    Dataset: Jul 2024 – Jun 2025 &nbsp;·&nbsp;
    <span style='color:#fc2779'>{len(fdf):,} campaigns analysed</span>
</div>
""", unsafe_allow_html=True)
