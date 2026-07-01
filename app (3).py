import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Nykaa · Marketing Intelligence",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
    background: #060610 !important;
    color: #dde0f0 !important;
}

/* scrollbar */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#060610; }
::-webkit-scrollbar-thumb { background:#2a2a45; border-radius:4px; }

/* main padding */
.main .block-container { padding: 1.2rem 2rem 2rem !important; max-width:100% !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d0d1a 0%,#0a0a16 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * { color:#b0b4d0 !important; font-family:'Space Grotesk',sans-serif !important; }
section[data-testid="stSidebar"] label {
    font-size:0.7rem !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:1.2px !important;
    color:#ff3d8a !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="input"] > div {
    background:#13132a !important; border:1px solid #252545 !important;
    border-radius:10px !important; color:#dde0f0 !important;
}
section[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background:rgba(255,61,138,0.18) !important;
    border:1px solid rgba(255,61,138,0.4) !important;
    border-radius:20px !important;
}

/* ── TABS ── */
div[data-baseweb="tab-list"] {
    background:#0d0d1a !important; border-radius:14px !important;
    padding:5px !important; gap:4px !important;
    border:1px solid rgba(255,255,255,0.05) !important;
    margin-bottom:1.5rem !important;
}
button[data-baseweb="tab"] {
    background:transparent !important; border-radius:10px !important;
    color:#666890 !important; font-size:0.82rem !important;
    font-weight:600 !important; padding:0.55rem 1.2rem !important;
    font-family:'Space Grotesk',sans-serif !important;
    transition: all 0.25s !important;
}
button[data-baseweb="tab"]:hover { color:#dde0f0 !important; background:rgba(255,255,255,0.04) !important; }
button[aria-selected="true"][data-baseweb="tab"] {
    background:linear-gradient(135deg,#ff3d8a,#c4005e) !important;
    color:#fff !important; box-shadow:0 4px 20px rgba(255,61,138,0.4) !important;
}

/* ── DATAFRAME ── */
div[data-testid="stDataFrame"] { border:1px solid #1e1e35 !important; border-radius:14px !important; overflow:hidden !important; }
div[data-testid="stDataFrame"] th { background:#0d0d1a !important; color:#ff3d8a !important; font-size:0.75rem !important; text-transform:uppercase !important; letter-spacing:0.8px !important; }
div[data-testid="stDataFrame"] td { color:#c8ccdd !important; font-size:0.83rem !important; }
div[data-testid="stDataFrame"] tr:hover td { background:rgba(255,61,138,0.05) !important; }

hr { border-color:#1e1e35 !important; margin:1.8rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load():
    df = pd.read_excel("NYKAA_DATASET.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Campaign_Type'] = df['Campaign_Type'].fillna('Unknown')
    df = df[df['Campaign_Type'] != 'Unknown'].copy()
    df['Month']   = df['Date'].dt.to_period('M').astype(str)
    df['MonthLbl']= df['Date'].dt.strftime('%b %Y')
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['Week']    = df['Date'].dt.isocalendar().week.astype(int)
    df['CTR'] = (df['Clicks']      / df['Impressions'].replace(0,1)  * 100).round(3)
    df['CVR'] = (df['Conversions'] / df['Clicks'].replace(0,1)       * 100).round(3)
    df['CPA'] = (df['Acquisition_Cost'] / df['Conversions'].replace(0,1)).round(2)
    df['CPL'] = (df['Acquisition_Cost'] / df['Leads'].replace(0,1)   ).round(2)
    return df

df = load()

# ── Palette ──
PAL = {
    'Email':       '#ff3d8a',
    'Influencer':  '#a78bfa',
    'Paid Ads':    '#fb923c',
    'SEO':         '#34d399',
    'Social Media':'#60a5fa',
}
COLS = list(PAL.values())

def base_layout(h=380, legend=True, margins=(10,16,40,10)):
    return dict(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Grotesk,sans-serif', color='#7a7ea8', size=11),
        title_font=dict(family='Sora,sans-serif', color='#eeeeff', size=13, weight=600),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#9999bb', size=11)) if legend else dict(visible=False),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)',
                   tickfont=dict(color='#55577a'), linecolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)',
                   tickfont=dict(color='#55577a'), linecolor='rgba(255,255,255,0.05)'),
        height=h, margin=dict(l=margins[0],r=margins[1],t=margins[2],b=margins[3]),
        hoverlabel=dict(bgcolor='#13132a', font_color='#eeeeff', font_family='Space Grotesk',
                        bordercolor='#2a2a50'),
    )


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.4rem 0 1.6rem'>
        <div style='font-size:2.4rem;filter:drop-shadow(0 0 12px rgba(255,61,138,0.6))'>💄</div>
        <div style='font-family:Sora,sans-serif;font-size:1.15rem;font-weight:800;
                    color:#fff;margin:6px 0 3px;letter-spacing:-0.3px'>NYKAA</div>
        <div style='font-size:0.68rem;color:#444466;letter-spacing:2px;text-transform:uppercase'>
            Marketing Intelligence</div>
    </div>
    <hr style='border-color:#1a1a2e;margin:0 0 1.2rem'>
    """, unsafe_allow_html=True)

    all_types = sorted(df['Campaign_Type'].unique())
    sel_types = st.multiselect("Campaign Channel", all_types, default=all_types)
    if not sel_types: sel_types = all_types

    all_segs = sorted(df['Customer_Segment'].unique())
    sel_segs = st.multiselect("Customer Segment", all_segs, default=all_segs)
    if not sel_segs: sel_segs = all_segs

    all_auds = sorted(df['Target_Audience'].unique())
    sel_auds = st.multiselect("Target Audience", all_auds, default=all_auds)
    if not sel_auds: sel_auds = all_auds

    all_langs = sorted(df['Language'].unique())
    sel_langs = st.multiselect("Language", all_langs, default=all_langs)
    if not sel_langs: sel_langs = all_langs

    dmin,dmax = df['Date'].min().date(), df['Date'].max().date()
    drng = st.date_input("Date Range", value=[dmin,dmax], min_value=dmin, max_value=dmax)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺  Reset Filters", use_container_width=True):
        st.rerun()

    st.markdown("""
    <div style='margin-top:1.2rem;padding:1rem;background:#0d0d1a;border-radius:12px;
                border:1px solid #1e1e35;font-size:0.75rem;line-height:2;color:#44446a'>
        <span style='color:#ff3d8a;font-weight:700'>DATASET</span><br>
        Records &nbsp;·&nbsp; <b style='color:#aab'>55,554</b><br>
        Channels &nbsp;·&nbsp; <b style='color:#aab'>5</b><br>
        Period &nbsp;·&nbsp; <b style='color:#aab'>Jul 24 – Jun 25</b>
    </div>""", unsafe_allow_html=True)


# ── Apply filters ──
fdf = df[
    df['Campaign_Type'].isin(sel_types) &
    df['Customer_Segment'].isin(sel_segs) &
    df['Target_Audience'].isin(sel_auds) &
    df['Language'].isin(sel_langs)
].copy()
if len(drng)==2:
    fdf = fdf[(fdf['Date'].dt.date>=drng[0])&(fdf['Date'].dt.date<=drng[1])]
if fdf.empty:
    st.warning("No data for current filters — resetting."); fdf=df.copy()

fpal = {c:PAL.get(c,'#aaaacc') for c in sorted(fdf['Campaign_Type'].unique())}

# ── Aggregate ──
ch = fdf.groupby('Campaign_Type').agg(
    N=('Campaign_ID','count'),
    Impressions=('Impressions','sum'), Clicks=('Clicks','sum'),
    Leads=('Leads','sum'), Conversions=('Conversions','sum'),
    Revenue=('Revenue','sum'), Spend=('Acquisition_Cost','sum'),
    ROI=('ROI','mean'), CTR=('CTR','mean'), CVR=('CVR','mean'),
    Eng=('Engagement_Score','mean'), CPA=('CPA','mean'),
).reset_index()
ch['ROAS']   = (ch['Revenue']/ch['Spend'].replace(0,1)).round(2)
ch['Profit'] = ch['Revenue']-ch['Spend']

# ── Summary KPIs ──
T_REV   = fdf['Revenue'].sum()
T_SPEND = fdf['Acquisition_Cost'].sum()
T_CONV  = fdf['Conversions'].sum()
T_IMP   = fdf['Impressions'].sum()
T_CLICK = fdf['Clicks'].sum()
AVG_ROI = fdf['ROI'].mean()
AVG_CTR = fdf['CTR'].mean()
AVG_CVR = fdf['CVR'].mean()
ROAS    = T_REV/T_SPEND if T_SPEND else 0
T_LEADS = fdf['Leads'].sum()


# ═══════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div style='
    background:linear-gradient(135deg,#0d0020 0%,#1a0035 35%,#0a0020 65%,#000d20 100%);
    border:1px solid rgba(255,61,138,0.2);border-radius:24px;padding:2.4rem 2.8rem;
    margin-bottom:1.8rem;position:relative;overflow:hidden;'>

  <div style='position:absolute;top:-80px;right:-80px;width:320px;height:320px;
    background:radial-gradient(circle,rgba(255,61,138,0.15) 0%,transparent 65%);border-radius:50%'></div>
  <div style='position:absolute;bottom:-60px;left:25%;width:250px;height:250px;
    background:radial-gradient(circle,rgba(96,165,250,0.1) 0%,transparent 65%);border-radius:50%'></div>
  <div style='position:absolute;top:20px;left:55%;width:180px;height:180px;
    background:radial-gradient(circle,rgba(167,139,250,0.1) 0%,transparent 65%);border-radius:50%'></div>

  <div style='position:relative;z-index:1'>
    <div style='display:inline-flex;align-items:center;gap:8px;
      background:rgba(255,61,138,0.1);border:1px solid rgba(255,61,138,0.3);
      border-radius:30px;padding:4px 16px;margin-bottom:1rem'>
      <span style='width:6px;height:6px;background:#ff3d8a;border-radius:50%;
        box-shadow:0 0 8px #ff3d8a;display:inline-block'></span>
      <span style='font-size:0.68rem;font-weight:700;letter-spacing:2px;
        text-transform:uppercase;color:#ff3d8a'>Live Analytics Dashboard</span>
    </div>

    <div style='font-family:Sora,sans-serif;font-size:2.5rem;font-weight:800;
      color:#fff;line-height:1.1;margin-bottom:0.5rem;letter-spacing:-1px'>
      Nykaa <span style='color:#ff3d8a'>Marketing</span> ROI Intelligence
    </div>
    <div style='color:#555880;font-size:0.9rem;font-weight:400;max-width:540px;line-height:1.7'>
      Multi-channel campaign analytics · Real-time ROI tracking ·
      Audience intelligence · Strategic budget optimisation
    </div>

    <div style='display:flex;gap:2.5rem;margin-top:1.6rem;flex-wrap:wrap'>
      <div>
        <div style='font-family:Sora,sans-serif;font-size:1.9rem;font-weight:800;color:#ff3d8a'>
          ₹{T_REV/1e9:.2f}B</div>
        <div style='font-size:0.68rem;color:#44446a;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>Total Revenue</div>
      </div>
      <div>
        <div style='font-family:Sora,sans-serif;font-size:1.9rem;font-weight:800;color:#a78bfa'>
          {AVG_ROI:.2f}x</div>
        <div style='font-size:0.68rem;color:#44446a;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>Avg ROI</div>
      </div>
      <div>
        <div style='font-family:Sora,sans-serif;font-size:1.9rem;font-weight:800;color:#60a5fa'>
          {T_CONV/1e6:.1f}M</div>
        <div style='font-size:0.68rem;color:#44446a;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>Conversions</div>
      </div>
      <div>
        <div style='font-family:Sora,sans-serif;font-size:1.9rem;font-weight:800;color:#34d399'>
          {ROAS:.1f}x</div>
        <div style='font-size:0.68rem;color:#44446a;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>ROAS</div>
      </div>
      <div>
        <div style='font-family:Sora,sans-serif;font-size:1.9rem;font-weight:800;color:#fb923c'>
          {len(fdf):,}</div>
        <div style='font-size:0.68rem;color:#44446a;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>Campaigns</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# KPI STRIP
# ═══════════════════════════════════════════════════════════
kpis = [
    ("💰","Total Revenue",   f"₹{T_REV/1e6:.0f}M",     "#ff3d8a"),
    ("📈","Avg ROI",         f"{AVG_ROI:.2f}x",          "#a78bfa"),
    ("🎯","Conversions",     f"{T_CONV/1e6:.2f}M",       "#60a5fa"),
    ("💸","Ad Spend",        f"₹{T_SPEND/1e6:.0f}M",    "#fb923c"),
    ("👁️","Impressions",     f"{T_IMP/1e6:.0f}M",        "#34d399"),
    ("🖱️","Avg CTR",         f"{AVG_CTR:.2f}%",          "#f9a8d4"),
    ("⚡","ROAS",            f"{ROAS:.1f}x",             "#fcd34d"),
    ("🧲","Total Leads",     f"{T_LEADS/1e6:.2f}M",      "#6ee7b7"),
]

cols = st.columns(8)
for col,(icon,lbl,val,clr) in zip(cols,kpis):
    with col:
        st.markdown(f"""
        <div style='background:#0d0d1a;border:1px solid #1a1a2e;border-radius:16px;
          padding:1rem 0.9rem;position:relative;overflow:hidden;cursor:default;
          transition:border-color 0.2s;height:100%'>
          <div style='position:absolute;top:0;left:0;right:0;height:2px;
            background:linear-gradient(90deg,{clr},transparent)'></div>
          <div style='font-size:1.3rem;margin-bottom:6px'>{icon}</div>
          <div style='font-family:Sora,sans-serif;font-size:1.3rem;font-weight:800;
            color:{clr};line-height:1;margin-bottom:5px'>{val}</div>
          <div style='font-size:0.65rem;color:#444466;text-transform:uppercase;
            letter-spacing:0.8px;font-weight:600'>{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SECTION HELPER
# ═══════════════════════════════════════════════════════════
def section(title, sub=""):
    st.markdown(f"""
    <div style='margin:2rem 0 1.2rem'>
      <div style='display:flex;align-items:center;gap:10px;margin-bottom:4px'>
        <div style='width:3px;height:20px;background:linear-gradient(180deg,#ff3d8a,#a78bfa);
          border-radius:3px;flex-shrink:0'></div>
        <div style='font-family:Sora,sans-serif;font-size:1rem;font-weight:700;
          color:#eeeeff;letter-spacing:-0.2px'>{title}</div>
      </div>
      {'<div style="font-size:0.78rem;color:#444466;margin-left:13px">'+sub+'</div>' if sub else ''}
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════
t1,t2,t3,t4,t5 = st.tabs([
    "📊  Channel Performance",
    "💹  ROI & Efficiency",
    "🎯  Audience & Segments",
    "📅  Time Trends",
    "💡  Insights & Strategy",
])


# ──────────────────────────────────────────────────────────
# TAB 1 — CHANNEL PERFORMANCE
# ──────────────────────────────────────────────────────────
with t1:
    section("Channel Performance Overview","Revenue, reach and funnel metrics per channel")

    # ── Row 1: Revenue gradient bars + Donut ──
    c1,c2 = st.columns([3,2])
    with c1:
        fig = go.Figure()
        ch_s = ch.sort_values('Revenue',ascending=True)
        for _,r in ch_s.iterrows():
            fig.add_trace(go.Bar(
                y=[r['Campaign_Type']], x=[r['Revenue']],
                orientation='h', name=r['Campaign_Type'],
                marker=dict(
                    color=fpal[r['Campaign_Type']],
                    opacity=0.85,
                    line=dict(width=0)
                ),
                text=f"  ₹{r['Revenue']/1e6:.0f}M",
                textposition='outside',
                textfont=dict(color='#ccccdd',size=11),
                hovertemplate=f"<b>{r['Campaign_Type']}</b><br>Revenue: ₹{r['Revenue']/1e6:.1f}M<br>ROI: {r['ROI']:.2f}x<extra></extra>",
            ))
        fig.update_layout(**base_layout(h=320,legend=False),
                          xaxis_title="Revenue (₹)", yaxis_title="",
                          title="Revenue by Channel",
                          bargap=0.35)
        st.plotly_chart(fig,use_container_width=True)

    with c2:
        fig = go.Figure(go.Pie(
            labels=ch['Campaign_Type'], values=ch['Revenue'],
            hole=0.65,
            marker=dict(colors=[fpal[c] for c in ch['Campaign_Type']],
                        line=dict(color='#060610',width=3)),
            texttemplate='%{label}<br><b>%{percent}</b>',
            textposition='outside',
            textfont=dict(size=10,color='#9999bb'),
            pull=[0.04]*len(ch),
        ))
        fig.update_layout(**{k:v for k,v in base_layout(h=320).items() if k not in('xaxis','yaxis')},
                          title="Revenue Share",
                          showlegend=False,
                          annotations=[dict(text=f'₹{T_REV/1e9:.1f}B<br>Total',
                                           x=0.5,y=0.5,font=dict(size=13,color='#eeeeff',family='Sora'),showarrow=False)])
        st.plotly_chart(fig,use_container_width=True)

    # ── Row 2: Grouped metric bars ──
    c3,c4 = st.columns(2)
    with c3:
        metrics_bar = ch[['Campaign_Type','CTR','CVR','Eng']].copy()
        fig = go.Figure()
        for metric,color,label in [('CTR','#ff3d8a','CTR %'),('CVR','#a78bfa','CVR %'),('Eng','#60a5fa','Engagement')]:
            fig.add_trace(go.Bar(
                name=label, x=metrics_bar['Campaign_Type'], y=metrics_bar[metric],
                marker_color=color, opacity=0.85,
                text=metrics_bar[metric].map(lambda v:f'{v:.2f}'),
                textposition='outside', textfont=dict(size=9,color='#aaaacc')
            ))
        fig.update_layout(**base_layout(h=340),title="CTR · CVR · Engagement by Channel",
                          barmode='group',xaxis_title="",yaxis_title="Score / %",bargap=0.25)
        st.plotly_chart(fig,use_container_width=True)

    with c4:
        # Funnel waterfall style
        stages = ['Impressions','Clicks','Leads','Conversions']
        totals = [fdf[s].sum() for s in stages]
        pcts   = [100]+[totals[i]/totals[0]*100 for i in range(1,4)]
        fig = go.Figure()
        clrs = ['#ff3d8a','#a78bfa','#60a5fa','#34d399']
        for i,(stage,tot,pct,clr) in enumerate(zip(stages,totals,pcts,clrs)):
            fig.add_trace(go.Bar(
                name=stage, x=[stage], y=[tot],
                marker=dict(color=clr,opacity=0.8,
                            line=dict(color=clr,width=1.5)),
                text=f'{pct:.1f}%',
                textposition='outside',
                textfont=dict(size=11,color=clr),
                hovertemplate=f"<b>{stage}</b><br>Count: {tot:,.0f}<br>vs Impressions: {pct:.1f}%<extra></extra>",
            ))
        fig.update_layout(**base_layout(h=340,legend=False),
                          title="Conversion Funnel",
                          xaxis_title="",yaxis_title="Count",showlegend=False,bargap=0.3)
        st.plotly_chart(fig,use_container_width=True)

    # ── Row 3: Radar + ROAS bubble ──
    c5,c6 = st.columns(2)
    with c5:
        mets  = ['CTR','CVR','ROI','Eng','ROAS']
        lbls  = ['CTR','CVR','ROI','Engagement','ROAS']
        maxes = ch[mets].max()
        def hex_to_rgba(hex_color, alpha=0.15):
            h = hex_color.lstrip('#')
            r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
            return f'rgba({r},{g},{b},{alpha})'

        fig = go.Figure()
        for _,r in ch.iterrows():
            vals = [(r[m]/maxes[m] if maxes[m]>0 else 0) for m in mets]+[(r[mets[0]]/maxes[mets[0]])]
            clr  = fpal[r['Campaign_Type']]
            fig.add_trace(go.Scatterpolar(
                r=vals, theta=lbls+[lbls[0]], fill='toself',
                name=r['Campaign_Type'],
                line=dict(color=clr, width=2),
                fillcolor=hex_to_rgba(clr, 0.15),
                opacity=0.9,
            ))
        fig.update_layout(
            **{k:v for k,v in base_layout(h=360).items() if k not in('xaxis','yaxis')},
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True,range=[0,1],gridcolor='rgba(255,255,255,0.06)',
                                tickfont=dict(color='#33334a',size=9)),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.06)',tickfont=dict(color='#7777aa',size=11))
            ),
            title="Multi-metric Channel Radar",
        )
        st.plotly_chart(fig,use_container_width=True)

    with c6:
        fig = px.scatter(ch, x='ROAS', y='CPA', size='Revenue',
                         color='Campaign_Type', color_discrete_map=fpal,
                         size_max=55, text='Campaign_Type',
                         title='ROAS vs CPA Efficiency Matrix')
        fig.update_traces(textposition='top center',
                          textfont=dict(color='#ccccdd',size=10),
                          marker=dict(line=dict(width=1.5,color='rgba(255,255,255,0.15)')))
        fig.update_layout(**base_layout(h=360,legend=False),
                          xaxis_title='ROAS',yaxis_title='Cost Per Acquisition (₹)')
        st.plotly_chart(fig,use_container_width=True)

    # ── Metrics Table ──
    section("Full Channel Metrics","All computed KPIs per channel")
    disp = ch.copy()
    disp['Revenue']  = disp['Revenue'].map('₹{:,.0f}'.format)
    disp['Spend']    = disp['Spend'].map('₹{:,.0f}'.format)
    disp['Profit']   = disp['Profit'].map('₹{:,.0f}'.format)
    disp['ROI']      = disp['ROI'].map('{:.3f}x'.format)
    disp['ROAS']     = disp['ROAS'].map('{:.2f}'.format)
    disp['CTR']      = disp['CTR'].map('{:.3f}%'.format)
    disp['CVR']      = disp['CVR'].map('{:.3f}%'.format)
    disp['CPA']      = disp['CPA'].map('₹{:.0f}'.format)
    disp['Eng']      = disp['Eng'].map('{:.2f}'.format)
    disp.columns     = ['Channel','Campaigns','Impressions','Clicks','Leads',
                        'Conversions','Revenue','Spend','ROI','CTR','CVR',
                        'Engagement','CPA','ROAS','Profit']
    st.dataframe(disp[['Channel','Revenue','Spend','Profit','ROI','ROAS',
                        'CTR','CVR','CPA','Engagement','Conversions']],
                 use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────
# TAB 2 — ROI & EFFICIENCY
# ──────────────────────────────────────────────────────────
with t2:
    section("ROI Distribution & Efficiency Analysis","Deep dive into return metrics across channels")

    c1,c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        for ch_name, grp in fdf.groupby('Campaign_Type'):
            fig.add_trace(go.Violin(
                x=grp['Campaign_Type'], y=grp['ROI'],
                name=ch_name, box_visible=True, meanline_visible=True,
                fillcolor=fpal[ch_name]+'33',
                line_color=fpal[ch_name],
                points=False, opacity=0.85,
            ))
        fig.update_layout(**base_layout(h=380,legend=False),
                          title="ROI Distribution — Violin + Box",
                          xaxis_title="",yaxis_title="ROI (x)")
        st.plotly_chart(fig,use_container_width=True)

    with c2:
        # Revenue vs Spend stacked comparison
        fig = go.Figure()
        for name,clr,key in [('Revenue','#ff3d8a','Revenue'),
                               ('Ad Spend','#fb923c','Spend'),
                               ('Net Profit','#34d399','Profit')]:
            fig.add_trace(go.Bar(
                name=name, x=ch['Campaign_Type'], y=ch[key],
                marker=dict(color=clr,opacity=0.82,
                            line=dict(color='rgba(0,0,0,0)',width=0)),
                text=ch[key].map(lambda v:f'₹{v/1e6:.0f}M'),
                textposition='outside',textfont=dict(size=9,color='#aaaacc')
            ))
        fig.update_layout(**base_layout(h=380),barmode='group',
                          title="Revenue · Spend · Net Profit",
                          xaxis_title="",yaxis_title="₹",bargap=0.2)
        st.plotly_chart(fig,use_container_width=True)

    # ROI heatmap Segment × Channel
    c3,c4 = st.columns(2)
    with c3:
        pivot = fdf.groupby(['Customer_Segment','Campaign_Type'])['ROI'].mean()\
                   .unstack(fill_value=0)
        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0,'#060610'],[0.3,'#2d0030'],[0.65,'#8b0057'],[1,'#ff3d8a']],
            text=np.round(pivot.values,2),
            texttemplate='%{text}x',
            textfont=dict(size=11,color='#eeeeff'),
            hovertemplate='Segment: %{y}<br>Channel: %{x}<br>ROI: %{z:.2f}x<extra></extra>',
            showscale=True,
            colorbar=dict(tickfont=dict(color='#7777aa'),
                          title=dict(text='ROI',font=dict(color='#7777aa')))
        ))
        fig.update_layout(**{k:v for k,v in base_layout(h=340).items() if k not in('xaxis','yaxis')},
                          title="ROI Heatmap: Segment × Channel",
                          xaxis=dict(tickfont=dict(color='#7777aa')),
                          yaxis=dict(tickfont=dict(color='#7777aa')))
        st.plotly_chart(fig,use_container_width=True)

    with c4:
        # Scatter ROI vs Engagement coloured by channel
        samp = fdf.sample(min(5000,len(fdf)),random_state=7)
        fig = px.scatter(samp, x='Engagement_Score', y='ROI',
                         color='Campaign_Type', color_discrete_map=fpal,
                         opacity=0.4, size_max=4,
                         title='ROI vs Engagement Score')
        fig.update_traces(marker=dict(size=3))
        fig.update_layout(**base_layout(h=340),
                          xaxis_title='Engagement Score',yaxis_title='ROI (x)')
        st.plotly_chart(fig,use_container_width=True)

    section("ROI Histogram","Frequency distribution across all campaigns")
    fig = go.Figure()
    for ch_name,grp in fdf.groupby('Campaign_Type'):
        fig.add_trace(go.Histogram(
            x=grp['ROI'], name=ch_name,
            nbinsx=70, opacity=0.6,
            marker_color=fpal[ch_name],
        ))
    fig.add_vline(x=AVG_ROI,line_dash='dash',line_color='rgba(255,255,255,0.5)',line_width=1.5,
                  annotation_text=f'Mean {AVG_ROI:.2f}x',
                  annotation_font=dict(color='#eeeeff',size=11))
    fig.update_layout(**base_layout(h=320),barmode='overlay',
                      xaxis_title='ROI',yaxis_title='Campaigns')
    st.plotly_chart(fig,use_container_width=True)


# ──────────────────────────────────────────────────────────
# TAB 3 — AUDIENCE & SEGMENTS
# ──────────────────────────────────────────────────────────
with t3:
    section("Audience & Customer Segment Intelligence","Which audiences and segments deliver the best returns")

    seg = fdf.groupby('Customer_Segment').agg(
        Revenue=('Revenue','sum'), ROI=('ROI','mean'),
        Conversions=('Conversions','sum'), Eng=('Engagement_Score','mean'),
        Spend=('Acquisition_Cost','sum')
    ).reset_index()
    seg['ROAS'] = seg['Revenue']/seg['Spend']

    c1,c2 = st.columns(2)
    with c1:
        # Lollipop chart for ROI by segment
        seg_s = seg.sort_values('ROI')
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=seg_s['ROI'], y=seg_s['Customer_Segment'],
            mode='markers', name='ROI',
            marker=dict(size=14, color=seg_s['ROI'],
                        colorscale=[[0,'#2d0030'],[1,'#ff3d8a']],
                        showscale=False, line=dict(color='#060610',width=2)),
            hovertemplate='<b>%{y}</b><br>ROI: %{x:.3f}x<extra></extra>'
        ))
        for _,r in seg_s.iterrows():
            fig.add_shape(type='line',
                x0=seg_s['ROI'].min()*0.999, x1=r['ROI'],
                y0=r['Customer_Segment'], y1=r['Customer_Segment'],
                line=dict(color='rgba(255,61,138,0.25)',width=2))
        fig.update_layout(**base_layout(h=340,legend=False),
                          title='ROI by Customer Segment',
                          xaxis_title='Avg ROI (x)',yaxis_title='')
        st.plotly_chart(fig,use_container_width=True)

    with c2:
        # Bubble: Revenue vs ROAS, size=Conversions
        fig = px.scatter(seg, x='Revenue', y='ROAS', size='Conversions',
                         color='Customer_Segment',
                         color_discrete_sequence=['#ff3d8a','#a78bfa','#60a5fa','#34d399','#fb923c'],
                         size_max=55, text='Customer_Segment',
                         title='Segment: Revenue vs ROAS (size = Conversions)')
        fig.update_traces(textposition='top center',
                          textfont=dict(color='#ccccdd',size=10),
                          marker=dict(line=dict(width=1.5,color='rgba(255,255,255,0.12)')))
        fig.update_layout(**base_layout(h=340,legend=False),
                          xaxis_title='Revenue (₹)',yaxis_title='ROAS')
        st.plotly_chart(fig,use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        lang = fdf.groupby('Language').agg(
            Revenue=('Revenue','sum'), ROI=('ROI','mean'),
            Conversions=('Conversions','sum')
        ).reset_index().sort_values('Revenue',ascending=False)

        fig = go.Figure()
        for i,(_,r) in enumerate(lang.iterrows()):
            fig.add_trace(go.Bar(
                x=[r['Language']], y=[r['Revenue']],
                name=r['Language'],
                marker=dict(color=COLS[i%len(COLS)],opacity=0.82),
                text=f"ROI {r['ROI']:.2f}x",
                textposition='outside',
                textfont=dict(color='#aaaacc',size=10)
            ))
        fig.update_layout(**base_layout(h=340,legend=False),
                          title='Revenue & ROI by Language',
                          xaxis_title='',yaxis_title='Revenue (₹)',showlegend=False,bargap=0.35)
        st.plotly_chart(fig,use_container_width=True)

    with c4:
        # Audience performance bars
        aud = fdf.groupby('Target_Audience').agg(
            ROI=('ROI','mean'), Revenue=('Revenue','sum'), CTR=('CTR','mean')
        ).reset_index().sort_values('ROI',ascending=True)
        fig = go.Figure(go.Bar(
            y=aud['Target_Audience'], x=aud['ROI'], orientation='h',
            marker=dict(
                color=aud['ROI'],
                colorscale=[[0,'#0d0d1a'],[0.5,'#6d2060'],[1,'#ff3d8a']],
                showscale=False,
                line=dict(width=0)
            ),
            text=aud['ROI'].map(lambda v:f'  {v:.3f}x'),
            textposition='outside',
            textfont=dict(color='#ccccdd',size=11),
            hovertemplate='<b>%{y}</b><br>ROI: %{x:.3f}x<extra></extra>'
        ))
        fig.update_layout(**base_layout(h=340,legend=False),
                          title='ROI by Target Audience',
                          xaxis_title='Avg ROI (x)',yaxis_title='')
        st.plotly_chart(fig,use_container_width=True)

    section("Segment × Channel Revenue Matrix","Cross-dimensional revenue breakdown")
    pvt = fdf.pivot_table(values='Revenue',index='Customer_Segment',
                           columns='Campaign_Type',aggfunc='sum',fill_value=0)
    fig = go.Figure(go.Heatmap(
        z=pvt.values, x=pvt.columns.tolist(), y=pvt.index.tolist(),
        colorscale=[[0,'#060610'],[0.3,'#0d1a35'],[0.7,'#1a4060'],[1,'#60a5fa']],
        text=(pvt.values/1e6).round(1),
        texttemplate='₹%{text}M',
        textfont=dict(size=11,color='#eeeeff'),
        hovertemplate='Segment: %{y}<br>Channel: %{x}<br>Revenue: ₹%{z:,.0f}<extra></extra>',
        colorbar=dict(tickfont=dict(color='#7777aa'),
                      title=dict(text='₹',font=dict(color='#7777aa')))
    ))
    fig.update_layout(**{k:v for k,v in base_layout(h=300).items() if k not in('xaxis','yaxis')},
                      xaxis=dict(tickfont=dict(color='#7777aa')),
                      yaxis=dict(tickfont=dict(color='#7777aa')))
    st.plotly_chart(fig,use_container_width=True)


# ──────────────────────────────────────────────────────────
# TAB 4 — TIME TRENDS
# ──────────────────────────────────────────────────────────
with t4:
    section("Time-Series Performance","Monthly and quarterly trends across channels")

    monthly = fdf.groupby(['Month','Campaign_Type']).agg(
        Revenue=('Revenue','sum'), ROI=('ROI','mean'),
        Conversions=('Conversions','sum'), Spend=('Acquisition_Cost','sum'),
        Eng=('Engagement_Score','mean'), CTR=('CTR','mean'),
    ).reset_index().sort_values('Month')

    # Revenue sparklines with area fill
    fig = go.Figure()
    for ch_name,grp in monthly.groupby('Campaign_Type'):
        clr = fpal[ch_name]
        fig.add_trace(go.Scatter(
            x=grp['Month'], y=grp['Revenue'],
            name=ch_name, mode='lines+markers',
            line=dict(color=clr, width=2.5, shape='spline'),
            marker=dict(size=5, color=clr,
                        line=dict(color='#060610',width=1.5)),
            fill='tozeroy',
            fillcolor=clr+'15',
            hovertemplate=f'<b>{ch_name}</b><br>Month: %{{x}}<br>Revenue: ₹%{{y:,.0f}}<extra></extra>'
        ))
    fig.update_layout(**base_layout(h=380),
                      title='Monthly Revenue Trend by Channel',
                      xaxis_title='',yaxis_title='Revenue (₹)')
    st.plotly_chart(fig,use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        # ROI trend with reference line
        fig = go.Figure()
        for ch_name,grp in monthly.groupby('Campaign_Type'):
            clr = fpal[ch_name]
            fig.add_trace(go.Scatter(
                x=grp['Month'], y=grp['ROI'],
                name=ch_name, mode='lines+markers',
                line=dict(color=clr,width=2,shape='spline'),
                marker=dict(size=4.5,color=clr),
            ))
        fig.add_hline(y=AVG_ROI,line_dash='dot',line_color='rgba(255,255,255,0.3)',
                      line_width=1.5,
                      annotation_text=f'Avg {AVG_ROI:.2f}x',
                      annotation_font=dict(color='#aaaacc',size=10))
        fig.update_layout(**base_layout(h=340),
                          title='Monthly ROI Trend',xaxis_title='',yaxis_title='ROI (x)')
        st.plotly_chart(fig,use_container_width=True)

    with c2:
        # Stacked area: conversions
        fig = go.Figure()
        for ch_name,grp in monthly.groupby('Campaign_Type'):
            clr = fpal[ch_name]
            fig.add_trace(go.Scatter(
                x=grp['Month'], y=grp['Conversions'],
                name=ch_name, mode='lines',
                line=dict(color=clr,width=1.5,shape='spline'),
                fill='tonexty' if ch_name!=list(monthly.groupby('Campaign_Type').groups.keys())[0] else 'tozeroy',
                fillcolor=clr+'30',
                stackgroup='one',
            ))
        fig.update_layout(**base_layout(h=340),
                          title='Monthly Conversions (Stacked Area)',
                          xaxis_title='',yaxis_title='Conversions')
        st.plotly_chart(fig,use_container_width=True)

    # Quarterly stacked bars
    qtr = fdf.groupby(['Quarter','Campaign_Type']).agg(Revenue=('Revenue','sum')).reset_index()
    fig = go.Figure()
    for ch_name in sorted(fdf['Campaign_Type'].unique()):
        sub = qtr[qtr['Campaign_Type']==ch_name]
        fig.add_trace(go.Bar(
            name=ch_name, x=sub['Quarter'], y=sub['Revenue'],
            marker=dict(color=fpal[ch_name],opacity=0.85,line=dict(width=0)),
            hovertemplate=f'<b>{ch_name}</b><br>Quarter: %{{x}}<br>₹%{{y:,.0f}}<extra></extra>'
        ))
    fig.update_layout(**base_layout(h=340),barmode='stack',
                      title='Quarterly Revenue Stack',xaxis_title='',yaxis_title='Revenue (₹)',bargap=0.25)
    st.plotly_chart(fig,use_container_width=True)

    # Engagement heatmap month × channel
    section("Engagement Heatmap","Monthly engagement score per channel")
    eng = fdf.groupby(['Month','Campaign_Type'])['Engagement_Score'].mean().reset_index()
    pvt = eng.pivot(index='Campaign_Type',columns='Month',values='Engagement_Score').fillna(0)
    fig = go.Figure(go.Heatmap(
        z=pvt.values, x=pvt.columns.tolist(), y=pvt.index.tolist(),
        colorscale=[[0,'#060610'],[0.4,'#1a1060'],[0.7,'#6030a0'],[1,'#a78bfa']],
        text=np.round(pvt.values,1),
        texttemplate='%{text}',
        textfont=dict(size=10,color='#eeeeff'),
        colorbar=dict(tickfont=dict(color='#7777aa'),
                      title=dict(text='Score',font=dict(color='#7777aa')))
    ))
    fig.update_layout(**{k:v for k,v in base_layout(h=280).items() if k not in('xaxis','yaxis')},
                      xaxis=dict(tickfont=dict(color='#55557a'),tickangle=-30),
                      yaxis=dict(tickfont=dict(color='#7777aa')))
    st.plotly_chart(fig,use_container_width=True)


# ──────────────────────────────────────────────────────────
# TAB 5 — INSIGHTS & STRATEGY
# ──────────────────────────────────────────────────────────
with t5:
    # Dynamic computations
    best_ch   = ch.loc[ch['ROI'].idxmax(),'Campaign_Type']
    best_roi  = ch['ROI'].max()
    best_rev  = ch.loc[ch['Revenue'].idxmax(),'Campaign_Type']
    worst_ctr = ch.loc[ch['CTR'].idxmin(),'Campaign_Type']
    best_ctr  = ch.loc[ch['CTR'].idxmax(),'Campaign_Type']
    best_seg  = fdf.groupby('Customer_Segment')['Revenue'].sum().idxmax()
    best_aud  = fdf.groupby('Target_Audience')['ROI'].mean().idxmax()
    best_lang = fdf.groupby('Language')['ROI'].mean().idxmax()
    best_eng  = ch.loc[ch['Eng'].idxmax(),'Campaign_Type']
    hi_roi_pct= (fdf['ROI']>5).mean()*100
    best_roas = ch.loc[ch['ROAS'].idxmax(),'Campaign_Type']

    section("Data-Driven Insights","Auto-calculated from your filtered dataset")

    insights = [
        ("#ff3d8a","🏆","Top ROI Channel",
         f"<b>{best_ch}</b> delivers the highest avg ROI of <b>{best_roi:.3f}x</b>. Prioritise budget here for maximum return efficiency."),
        ("#a78bfa","💰","Revenue Leader",
         f"<b>{best_rev}</b> generates the highest total revenue. Combine with ROI analysis to ensure spend efficiency at scale."),
        ("#60a5fa","👥","Most Valuable Segment",
         f"<b>{best_seg}</b> is the top revenue-contributing segment. Personalised campaigns here unlock the highest monetisation potential."),
        ("#34d399","🎯","Best Audience ROI",
         f"<b>{best_aud}</b> audience shows the strongest ROI. Build dedicated creative briefs and offers exclusively for this group."),
        ("#fb923c","📣","CTR Champion",
         f"<b>{best_ctr}</b> achieves the best click-through rate. Extract creative patterns and apply them cross-channel."),
        ("#f9a8d4","🌐","Language Winner",
         f"<b>{best_lang}</b>-language campaigns outperform on ROI. Scale localised content: creators, copy, and landing pages."),
        ("#fcd34d","⚡","Top ROAS Channel",
         f"<b>{best_roas}</b> returns the most revenue per rupee spent. Ideal for performance-led budgets with strict efficiency KPIs."),
        ("#6ee7b7","✨","Engagement Leader",
         f"<b>{best_eng}</b> leads on engagement. High engagement is a leading indicator of future conversion uplift — invest early."),
        ("#ff3d8a","⚠️","Low CTR Alert",
         f"<b>{worst_ctr}</b> has the lowest CTR — audience-creative mismatch detected. Immediate A/B testing with 3+ creative variants recommended."),
        ("#a78bfa","📊","High-ROI Campaign Rate",
         f"<b>{hi_roi_pct:.1f}%</b> of campaigns hit ROI > 5x. Isolate these, build a pattern playbook, and replicate across channels."),
    ]

    c1,c2 = st.columns(2)
    for i,(clr,icon,title,body) in enumerate(insights):
        with (c1 if i%2==0 else c2):
            st.markdown(f"""
            <div style='background:#0d0d1a;border:1px solid #1a1a2e;border-left:3px solid {clr};
              border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.75rem;
              transition:transform 0.2s'>
              <div style='display:flex;align-items:center;gap:8px;margin-bottom:6px'>
                <span style='font-size:1.3rem'>{icon}</span>
                <span style='font-family:Sora,sans-serif;font-size:0.88rem;font-weight:700;
                  color:#eeeeff'>{title}</span>
              </div>
              <div style='font-size:0.8rem;color:#555880;line-height:1.6'>{body}</div>
            </div>""", unsafe_allow_html=True)

    section("Strategic Recommendations","Action plan for the next campaign cycle")

    recs = [
        ("#ff3d8a","🔝",f"Double Down on {best_ch}",
         f"Reallocate 20–30% of underperforming channel budgets to {best_ch} (avg ROI {best_roi:.2f}x). Use incrementality testing to validate lift before full-scale shift."),
        ("#a78bfa","👤",f"Segment-First Planning for {best_seg}",
         f"Build dedicated campaign calendars with bespoke creatives, offers, and landing pages for {best_seg}. This segment converts at the highest rate in your data."),
        ("#60a5fa","🌍",f"Scale {best_lang} Localisation",
         f"Commission {best_lang} creators, influencers, and copywriters. Pilot adjacent regional languages with similar demographic profiles to extend reach."),
        ("#34d399","🔄",f"Revive {worst_ctr} with Creative Overhaul",
         f"Run 3–5 creative variants (UGC video, testimonial carousel, discount-led static) for {worst_ctr} with tightened audience segmentation within the next sprint."),
        ("#fb923c","📅","Seasonality-Driven Budget Shifts",
         "Pre-load awareness spend 4–6 weeks before high-conversion months. Throttle spend during historically low-ROI windows and reinvest in pre-peak build-up."),
        ("#f9a8d4","📊","ROI-Gated Bidding Rules",
         "Pause campaigns below 0.5x ROI for 2 consecutive weeks. Increase budgets 15% for campaigns sustaining >3x ROI. Creates a self-optimising portfolio."),
        ("#fcd34d","🤝","Influencer × Paid Ads Whitelisting",
         "Repurpose top influencer content as whitelisted paid ads — typically lifts CTR by 30–50%. Start with the 5 best performing posts on your top CTR channel."),
        ("#6ee7b7","🛠️","Build a Marketing Mix Model (MMM)",
         "With 55K+ records across 12 months, Nykaa has sufficient data for an MMM. This quantifies channel interaction effects, diminishing returns, and optimal budget split scientifically."),
    ]

    for clr,icon,title,body in recs:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#0d0d1a,#0a0a14);
          border:1px solid #1a1a2e;border-left:3px solid {clr};
          border-radius:14px;padding:1rem 1.4rem;margin-bottom:0.7rem'>
          <div style='font-family:Sora,sans-serif;font-size:0.9rem;font-weight:700;
            color:#eeeeff;margin-bottom:5px'>{icon}&nbsp; {title}</div>
          <div style='font-size:0.8rem;color:#555880;line-height:1.65'>{body}</div>
        </div>""", unsafe_allow_html=True)

    section("ROI-Weighted Budget Allocation","Recommended spend split based on channel ROI performance")
    ch3 = ch[['Campaign_Type','ROI']].copy()
    ch3['w']   = ch3['ROI'].clip(lower=0)
    ch3['pct'] = (ch3['w']/ch3['w'].sum()*100).round(1)

    fig = go.Figure()
    # Outer donut
    fig.add_trace(go.Pie(
        labels=ch3['Campaign_Type'], values=ch3['pct'],
        hole=0.65, name='Budget',
        marker=dict(colors=[fpal[c] for c in ch3['Campaign_Type']],
                    line=dict(color='#060610',width=4)),
        texttemplate='<b>%{label}</b><br>%{value}%',
        textposition='outside',
        textfont=dict(size=11,color='#9999bb'),
        pull=[0.04]*len(ch3),
        hovertemplate='%{label}<br>Recommended Budget: %{value}%<extra></extra>',
        rotation=45,
    ))
    fig.update_layout(
        **{k:v for k,v in base_layout(h=440).items() if k not in('xaxis','yaxis')},
        title='Recommended Budget Allocation (ROI-Weighted)',
        showlegend=True,
        annotations=[dict(
            text='<b>Budget<br>Split</b>',
            x=0.5,y=0.5,
            font=dict(size=13,color='#eeeeff',family='Sora'),
            showarrow=False
        )]
    )
    st.plotly_chart(fig,use_container_width=True)


# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;padding:1rem 0;color:#2a2a45;font-size:0.75rem;
  font-family:Space Grotesk,sans-serif'>
  💄 &nbsp;<b style='color:#333355'>Nykaa Marketing Intelligence</b>&nbsp; · &nbsp;
  Powered by Streamlit & Plotly &nbsp; · &nbsp;
  Dataset: Jul 2024 – Jun 2025 &nbsp; · &nbsp;
  <span style='color:#ff3d8a'>{len(fdf):,} campaigns analysed</span>
</div>
""", unsafe_allow_html=True)
