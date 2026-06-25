import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nykaa Marketing ROI Dashboard",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #fc2779 0%, #ff6b6b 50%, #ffa45c 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
    .main-header p  { font-size: 1rem; opacity: 0.9; margin: 0.4rem 0 0; }

    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-left: 4px solid #fc2779;
        height: 100%;
    }
    .kpi-label { font-size: 0.78rem; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1a1a2e; line-height: 1.1; margin: 0.3rem 0; }
    .kpi-delta { font-size: 0.82rem; color: #2ecc71; font-weight: 500; }
    .kpi-delta.neg { color: #e74c3c; }

    .section-header {
        font-size: 1.15rem; font-weight: 700; color: #1a1a2e;
        margin: 1.5rem 0 0.8rem; padding-bottom: 0.5rem;
        border-bottom: 2px solid #fc2779;
    }

    .insight-card {
        background: #fff9fb;
        border: 1px solid #ffd6e7;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
    }
    .insight-card .icon { font-size: 1.4rem; }
    .insight-card .title { font-weight: 700; color: #1a1a2e; font-size: 0.95rem; }
    .insight-card .body  { color: #555; font-size: 0.87rem; margin-top: 0.25rem; }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        background: #f5f5f5;
    }
    .stTabs [aria-selected="true"] { background: #fc2779 !important; color: white !important; }
    
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("NYKAA_DATASET.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['CTR'] = (df['Clicks'] / df['Impressions'] * 100).round(2)
    df['CVR'] = (df['Conversions'] / df['Clicks'] * 100).round(2)
    df['CPC'] = (df['Acquisition_Cost'] / df['Clicks']).round(2)
    df['CPL'] = (df['Acquisition_Cost'] / df['Leads'].replace(0, 1)).round(2)
    df['Campaign_Type'] = df['Campaign_Type'].fillna('Unknown')
    return df

df = load_data()

# ── Sidebar Filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    campaign_types = ["All"] + sorted(df['Campaign_Type'].unique().tolist())
    sel_type = st.selectbox("Campaign Type", campaign_types)
    
    segments = ["All"] + sorted(df['Customer_Segment'].unique().tolist())
    sel_seg  = st.selectbox("Customer Segment", segments)
    
    audiences = ["All"] + sorted(df['Target_Audience'].unique().tolist())
    sel_aud   = st.selectbox("Target Audience", audiences)
    
    languages = ["All"] + sorted(df['Language'].unique().tolist())
    sel_lang  = st.selectbox("Language", languages)
    
    date_min = df['Date'].min().date()
    date_max = df['Date'].max().date()
    date_range = st.date_input("Date Range", value=[date_min, date_max],
                               min_value=date_min, max_value=date_max)
    
    st.markdown("---")
    st.markdown("**Dataset:** Nykaa Marketing Campaigns")
    st.markdown(f"**Records:** {len(df):,}")
    st.markdown(f"**Period:** Jul 2024 – Jun 2025")

# ── Apply Filters ──────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_type != "All":   fdf = fdf[fdf['Campaign_Type'] == sel_type]
if sel_seg  != "All":   fdf = fdf[fdf['Customer_Segment'] == sel_seg]
if sel_aud  != "All":   fdf = fdf[fdf['Target_Audience'] == sel_aud]
if sel_lang != "All":   fdf = fdf[fdf['Language'] == sel_lang]
if len(date_range) == 2:
    fdf = fdf[(fdf['Date'].dt.date >= date_range[0]) & (fdf['Date'].dt.date <= date_range[1])]

# ── Color palette ──────────────────────────────────────────────────────────────
COLORS = ['#fc2779', '#ff6b6b', '#ffa45c', '#6c5ce7', '#00cec9', '#fdcb6e']

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>💄 Nykaa Marketing ROI Dashboard</h1>
    <p>Channel Performance Analysis · Campaign Effectiveness · Strategic Insights</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────────
total_rev   = fdf['Revenue'].sum()
total_cost  = fdf['Acquisition_Cost'].sum()
total_conv  = fdf['Conversions'].sum()
avg_roi     = fdf['ROI'].mean()
avg_eng     = fdf['Engagement_Score'].mean()
total_imp   = fdf['Impressions'].sum()
avg_ctr     = fdf['CTR'].mean()
avg_cvr     = fdf['CVR'].mean()

k1,k2,k3,k4,k5,k6 = st.columns(6)
with k1:
    st.metric("💰 Total Revenue",    f"₹{total_rev/1e6:.1f}M", delta=None)
with k2:
    st.metric("📈 Avg ROI",          f"{avg_roi:.2f}x")
with k3:
    st.metric("🎯 Total Conversions", f"{total_conv:,}")
with k4:
    st.metric("💸 Total Ad Spend",   f"₹{total_cost/1e6:.1f}M")
with k5:
    st.metric("👁️ Impressions",       f"{total_imp/1e6:.1f}M")
with k6:
    st.metric("🖱️ Avg CTR",           f"{avg_ctr:.2f}%")

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Channel Performance",
    "💹 ROI Analysis",
    "🎯 Audience & Segments",
    "📅 Time Trends",
    "💡 Insights & Recommendations"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – CHANNEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Channel-wise Performance Overview</div>', unsafe_allow_html=True)

    ch = fdf.groupby('Campaign_Type').agg(
        Campaigns    =('Campaign_ID','count'),
        Impressions  =('Impressions','sum'),
        Clicks       =('Clicks','sum'),
        Leads        =('Leads','sum'),
        Conversions  =('Conversions','sum'),
        Revenue      =('Revenue','sum'),
        Spend        =('Acquisition_Cost','sum'),
        Avg_ROI      =('ROI','mean'),
        Avg_CTR      =('CTR','mean'),
        Avg_CVR      =('CVR','mean'),
        Avg_Eng      =('Engagement_Score','mean'),
    ).reset_index()
    ch['ROAS'] = (ch['Revenue'] / ch['Spend']).round(2)

    # ── Row 1: Revenue bar + ROI bar ──────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(ch.sort_values('Revenue', ascending=True),
                     x='Revenue', y='Campaign_Type', orientation='h',
                     color='Campaign_Type', color_discrete_sequence=COLORS,
                     title='Total Revenue by Channel', text_auto='.2s')
        fig.update_layout(showlegend=False, height=320,
                          xaxis_title="Revenue (₹)", yaxis_title="",
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(ch.sort_values('Avg_ROI', ascending=True),
                     x='Avg_ROI', y='Campaign_Type', orientation='h',
                     color='Avg_ROI',
                     color_continuous_scale=['#ffd6e7','#fc2779'],
                     title='Average ROI by Channel', text_auto='.2f')
        fig.update_layout(showlegend=False, height=320,
                          xaxis_title="ROI (x)", yaxis_title="",
                          coloraxis_showscale=False,
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Funnel + Radar ─────────────────────────────────────────────────
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Marketing Funnel by Channel**")
        funnel_data = []
        for _, row in ch.iterrows():
            for stage, val in [('Impressions', row['Impressions']),
                                ('Clicks',      row['Clicks']),
                                ('Leads',       row['Leads']),
                                ('Conversions', row['Conversions'])]:
                funnel_data.append({'Channel': row['Campaign_Type'], 'Stage': stage, 'Count': val})
        fdf2 = pd.DataFrame(funnel_data)
        fig = px.bar(fdf2, x='Stage', y='Count', color='Channel',
                     barmode='group', color_discrete_sequence=COLORS,
                     category_orders={'Stage':['Impressions','Clicks','Leads','Conversions']})
        fig.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white',
                          xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown("**Multi-metric Radar: Channel Comparison**")
        metrics = ['Avg_CTR','Avg_CVR','Avg_ROI','Avg_Eng','ROAS']
        labels  = ['CTR','CVR','ROI','Engagement','ROAS']
        fig = go.Figure()
        for i, row in ch.iterrows():
            vals = [row[m] for m in metrics]
            # normalize 0-1
            maxes = ch[metrics].max()
            normed = [v/maxes[m] if maxes[m]>0 else 0 for v,m in zip(vals,metrics)]
            normed.append(normed[0])
            fig.add_trace(go.Scatterpolar(
                r=normed, theta=labels+[labels[0]],
                fill='toself', name=row['Campaign_Type'],
                line_color=COLORS[i % len(COLORS)], opacity=0.7))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])),
                          showlegend=True, height=340, paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    # ── Table ─────────────────────────────────────────────────────────────────
    st.markdown("**Detailed Channel Metrics Table**")
    disp = ch[['Campaign_Type','Campaigns','Revenue','Spend','Avg_ROI','ROAS',
               'Avg_CTR','Avg_CVR','Conversions','Avg_Eng']].copy()
    disp.columns = ['Channel','Campaigns','Revenue (₹)','Spend (₹)','Avg ROI',
                    'ROAS','CTR (%)','CVR (%)','Conversions','Eng. Score']
    disp['Revenue (₹)'] = disp['Revenue (₹)'].map('{:,.0f}'.format)
    disp['Spend (₹)']   = disp['Spend (₹)'].map('{:,.0f}'.format)
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – ROI ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">ROI Deep Dive</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(fdf, x='Campaign_Type', y='ROI', color='Campaign_Type',
                     color_discrete_sequence=COLORS,
                     title='ROI Distribution by Channel')
        fig.update_layout(showlegend=False, height=360, plot_bgcolor='white',
                          paper_bgcolor='white', xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # ROI vs Spend scatter
        fig = px.scatter(fdf.sample(min(5000,len(fdf))), x='Acquisition_Cost', y='ROI',
                         color='Campaign_Type', color_discrete_sequence=COLORS,
                         title='ROI vs Ad Spend (sample)',
                         opacity=0.5, size_max=6,
                         hover_data=['Campaign_Type','Customer_Segment'])
        fig.update_layout(height=360, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Revenue vs Cost
        ch_roi = fdf.groupby('Campaign_Type').agg(Revenue=('Revenue','sum'),
                                                    Spend=('Acquisition_Cost','sum')).reset_index()
        ch_roi['Profit'] = ch_roi['Revenue'] - ch_roi['Spend']
        fig = go.Figure()
        fig.add_bar(name='Revenue', x=ch_roi['Campaign_Type'], y=ch_roi['Revenue'],
                    marker_color='#fc2779')
        fig.add_bar(name='Spend',   x=ch_roi['Campaign_Type'], y=ch_roi['Spend'],
                    marker_color='#ffa45c')
        fig.add_bar(name='Net Profit', x=ch_roi['Campaign_Type'], y=ch_roi['Profit'],
                    marker_color='#6c5ce7')
        fig.update_layout(barmode='group', title='Revenue vs Spend vs Net Profit',
                          height=360, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        roi_seg = fdf.groupby(['Campaign_Type','Customer_Segment'])['ROI'].mean().reset_index()
        fig = px.density_heatmap(roi_seg, x='Campaign_Type', y='Customer_Segment', z='ROI',
                                  color_continuous_scale='RdPu',
                                  title='Avg ROI Heatmap: Channel × Segment')
        fig.update_layout(height=360, paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    # ROI percentile distribution
    st.markdown("**ROI Percentile Distribution**")
    fig = px.histogram(fdf, x='ROI', color='Campaign_Type',
                       color_discrete_sequence=COLORS,
                       nbins=60, barmode='overlay', opacity=0.65,
                       title='ROI Frequency Distribution by Channel')
    fig.update_layout(height=320, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – AUDIENCE & SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Audience & Segment Analysis</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        seg = fdf.groupby('Customer_Segment').agg(
            Revenue=('Revenue','sum'), ROI=('ROI','mean'),
            Conversions=('Conversions','sum'), Spend=('Acquisition_Cost','sum')
        ).reset_index()
        fig = px.pie(seg, names='Customer_Segment', values='Revenue',
                     color_discrete_sequence=COLORS,
                     title='Revenue Share by Customer Segment', hole=0.4)
        fig.update_layout(height=360, paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(seg.sort_values('ROI'), x='Customer_Segment', y='ROI',
                     color='Customer_Segment', color_discrete_sequence=COLORS,
                     title='Average ROI by Customer Segment', text_auto='.2f')
        fig.update_layout(showlegend=False, height=360, plot_bgcolor='white',
                          paper_bgcolor='white', xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        aud = fdf.groupby('Target_Audience').agg(
            Revenue=('Revenue','sum'), ROI=('ROI','mean'), Eng=('Engagement_Score','mean')
        ).reset_index()
        fig = px.scatter(aud, x='Revenue', y='ROI', size='Eng', color='Target_Audience',
                         color_discrete_sequence=COLORS,
                         title='Audience: Revenue vs ROI (bubble = Engagement)',
                         hover_name='Target_Audience', size_max=40)
        fig.update_layout(height=360, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        lang = fdf.groupby('Language').agg(
            Revenue=('Revenue','sum'), ROI=('ROI','mean'), Campaigns=('Campaign_ID','count')
        ).reset_index()
        fig = go.Figure(go.Treemap(
            labels=lang['Language'],
            parents=[''] * len(lang),
            values=lang['Revenue'],
            customdata=lang[['ROI','Campaigns']],
            texttemplate="%{label}<br>Rev: ₹%{value:,.0f}<br>ROI: %{customdata[0]:.2f}x",
            marker_colorscale='RdPu'))
        fig.update_layout(title='Revenue by Language (Treemap)', height=360,
                          paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    # Segment × Channel performance table
    st.markdown("**Segment × Channel Revenue Matrix**")
    matrix = fdf.pivot_table(values='Revenue', index='Customer_Segment',
                              columns='Campaign_Type', aggfunc='sum', fill_value=0)
    fig = px.imshow(matrix, color_continuous_scale='RdPu',
                    title='Revenue Heatmap: Segment × Channel',
                    text_auto='.2s', aspect='auto')
    fig.update_layout(height=320, paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – TIME TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Time-Series Trends</div>', unsafe_allow_html=True)

    monthly = fdf.groupby(['Month','Campaign_Type']).agg(
        Revenue=('Revenue','sum'), ROI=('ROI','mean'),
        Conversions=('Conversions','sum'), Spend=('Acquisition_Cost','sum')
    ).reset_index().sort_values('Month')

    fig = px.line(monthly, x='Month', y='Revenue', color='Campaign_Type',
                  color_discrete_sequence=COLORS,
                  title='Monthly Revenue Trend by Channel', markers=True)
    fig.update_layout(height=360, plot_bgcolor='white', paper_bgcolor='white',
                      xaxis_title="", yaxis_title="Revenue (₹)")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.area(monthly, x='Month', y='Conversions', color='Campaign_Type',
                      color_discrete_sequence=COLORS,
                      title='Monthly Conversions by Channel')
        fig.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.line(monthly, x='Month', y='ROI', color='Campaign_Type',
                      color_discrete_sequence=COLORS,
                      title='Monthly Average ROI Trend', markers=True)
        fig.add_hline(y=fdf['ROI'].mean(), line_dash='dash', line_color='gray',
                      annotation_text=f"Overall avg: {fdf['ROI'].mean():.2f}x")
        fig.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    # Quarterly comparison
    qtr = fdf.groupby(['Quarter','Campaign_Type']).agg(
        Revenue=('Revenue','sum'), Spend=('Acquisition_Cost','sum')
    ).reset_index().sort_values('Quarter')
    qtr['ROAS'] = qtr['Revenue'] / qtr['Spend']

    fig = px.bar(qtr, x='Quarter', y='Revenue', color='Campaign_Type',
                 barmode='stack', color_discrete_sequence=COLORS,
                 title='Quarterly Revenue Stack by Channel')
    fig.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – INSIGHTS & RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)

    # Compute dynamic insights
    best_ch  = fdf.groupby('Campaign_Type')['ROI'].mean().idxmax()
    best_roi = fdf.groupby('Campaign_Type')['ROI'].mean().max()
    best_rev = fdf.groupby('Campaign_Type')['Revenue'].sum().idxmax()
    best_seg = fdf.groupby('Customer_Segment')['Revenue'].sum().idxmax()
    best_aud = fdf.groupby('Target_Audience')['ROI'].mean().idxmax()
    low_ctr  = fdf.groupby('Campaign_Type')['CTR'].mean().idxmin()
    best_ctr_ch = fdf.groupby('Campaign_Type')['CTR'].mean().idxmax()
    best_lang   = fdf.groupby('Language')['ROI'].mean().idxmax()
    high_roi_pct = (fdf['ROI'] > 5).mean() * 100

    insights = [
        ("🏆", "Top ROI Channel",
         f"<b>{best_ch}</b> delivers the highest average ROI of <b>{best_roi:.2f}x</b> — making it the most efficient channel for budget allocation."),
        ("💰", "Revenue Leader",
         f"<b>{best_rev}</b> generates the highest total revenue. However, pure revenue must be weighed against spend to find true profitability."),
        ("👥", "Most Valuable Segment",
         f"<b>{best_seg}</b> is the top revenue-contributing customer segment. Campaigns targeting this group should receive priority budget."),
        ("🎯", "Highest Engagement Audience",
         f"<b>{best_aud}</b> shows the strongest ROI per audience. Creative and messaging should be tailored specifically to this group."),
        ("📣", "CTR Champion",
         f"<b>{best_ctr_ch}</b> has the best click-through rate, indicating strong creative resonance. Learnings should be applied to other channels."),
        ("🌐", "Language Performance",
         f"<b>{best_lang}</b>-language campaigns outperform other languages on ROI. Localisation in this language should be scaled."),
        ("⚠️", "Low CTR Alert",
         f"<b>{low_ctr}</b> has the lowest average CTR, suggesting poor ad relevance or audience-message mismatch. Immediate creative refresh needed."),
        ("📊", "High-ROI Campaign Rate",
         f"<b>{high_roi_pct:.1f}%</b> of campaigns achieve ROI > 5x. Identifying common patterns in these campaigns can unlock significant growth."),
    ]

    c1, c2 = st.columns(2)
    for i, (icon, title, body) in enumerate(insights):
        col = c1 if i % 2 == 0 else c2
        with col:
            st.markdown(f"""
            <div class="insight-card">
                <span class="icon">{icon}</span>
                <span class="title"> {title}</span>
                <div class="body">{body}</div>
            </div>""", unsafe_allow_html=True)

    # ── Strategic Recommendations ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Strategic Recommendations</div>', unsafe_allow_html=True)

    recs = [
        ("🔝", "Double down on high-ROI channels",
         f"Reallocate 20–30% of budget from low-performing channels to {best_ch}, which consistently delivers {best_roi:.1f}x ROI. Use a test-and-scale approach to validate increased spend."),
        ("👤", "Segment-first budget planning",
         f"Build campaign calendars around {best_seg} and {best_aud} audiences. Create dedicated creatives and offers per segment rather than generic campaigns."),
        ("🌍", "Expand {best_lang} localisation".format(best_lang=best_lang),
         f"{best_lang}-language content drives stronger ROI. Invest in {best_lang} creators, influencers, and ad copy. Extend to adjacent regional languages for similar audiences."),
        ("🔄", "Fix the leaky funnel on {low_ctr}".format(low_ctr=low_ctr),
         f"The low CTR on {low_ctr} indicates an awareness-to-interest gap. A/B test at least 3 new creative formats (video, UGC, carousel) with refined audience targeting before next season."),
        ("📅", "Seasonality-based spend optimisation",
         "Use the monthly trend data to shift budget peaks to high-conversion months. Reduce spend during historically low-ROI months and reinvest in pre-peak awareness build-up."),
        ("📊", "Implement ROI-based bidding",
         "Set channel-specific ROI thresholds. Campaigns below 1x ROI for 2 consecutive weeks should be paused and funds redistributed to campaigns exceeding 3x ROI."),
        ("🤝", "Influencer + Paid Ads synergy",
         "Whitelisted influencer content repurposed as paid ads typically improves CTR by 30–50%. Test this approach on the top-performing audience segments."),
        ("🛠️", "Build a Marketing Mix Model (MMM)",
         "With 55K+ campaign records, Nykaa is well-positioned to build an MMM to quantify channel interaction effects and determine optimal budget split scientifically."),
    ]

    for icon, title, body in recs:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:1rem 1.4rem;margin-bottom:0.7rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid #6c5ce7;">
            <b style="color:#1a1a2e;">{icon} {title}</b>
            <p style="color:#555;margin:0.3rem 0 0;font-size:0.88rem;">{body}</p>
        </div>""", unsafe_allow_html=True)

    # ── Budget Allocation Suggestion ──────────────────────────────────────────
    st.markdown('<div class="section-header">Suggested Budget Reallocation</div>', unsafe_allow_html=True)
    
    ch2 = fdf.groupby('Campaign_Type').agg(ROI=('ROI','mean')).reset_index()
    ch2['Weight'] = ch2['ROI'].clip(lower=0)
    ch2['Suggested_%'] = (ch2['Weight'] / ch2['Weight'].sum() * 100).round(1)

    fig = go.Figure(go.Pie(
        labels=ch2['Campaign_Type'], values=ch2['Suggested_%'],
        hole=0.5,
        marker=dict(colors=COLORS),
        texttemplate="%{label}<br>%{value}%",
        textposition='outside'))
    fig.update_layout(
        title='ROI-Weighted Budget Allocation Recommendation',
        height=400, paper_bgcolor='white',
        annotations=[dict(text='Allocation', x=0.5, y=0.5, font_size=14, showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#aaa;font-size:0.82rem;'>"
    "Nykaa Marketing Analytics Dashboard · Built with Streamlit & Plotly · "
    f"Data: {df['Date'].min().strftime('%b %Y')} – {df['Date'].max().strftime('%b %Y')}"
    "</p>", unsafe_allow_html=True)
