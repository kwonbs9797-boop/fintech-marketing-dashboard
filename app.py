import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="핀테크 마케팅 분석 대시보드",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════
BG         = "#0d1117"
CARD       = "#161b27"
CARD2      = "#1c2333"
BORDER     = "#30363d"
TEXT       = "#e6edf3"
TEXT_SEC   = "#8b949e"
ACCENT     = "#58a6ff"
GREEN      = "#3fb950"
AMBER      = "#d29922"
RED        = "#f85149"
PLOT_BG    = "#161b27"
GRID_CLR   = "#21262d"

CHANNEL_COLORS = {"구글": "#4285F4", "페이스북": "#1877F2", "네이버검색": "#00b900"}
FORMAT_COLORS  = {"영상": "#58a6ff", "이미지": "#3fb950", "브랜드키워드": "#d29922", "일반키워드": "#f85149"}

def chart_layout(title="", height=400, show_legend=True):
    return dict(
        title=dict(text=title, font=dict(size=15, color=TEXT), x=0, pad=dict(l=0, b=12)),
        height=height,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        font=dict(color=TEXT_SEC, size=12),
        xaxis=dict(gridcolor=GRID_CLR, linecolor=BORDER, tickfont=dict(color=TEXT_SEC)),
        yaxis=dict(gridcolor=GRID_CLR, linecolor=BORDER, tickfont=dict(color=TEXT_SEC)),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER,
            font=dict(color=TEXT_SEC),
        ) if show_legend else dict(visible=False),
        margin=dict(l=16, r=16, t=48, b=16),
        hoverlabel=dict(bgcolor=CARD2, bordercolor=BORDER, font_color=TEXT),
    )

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: {BG};
    color: {TEXT};
  }}
  .block-container {{ padding: 2rem 2.5rem 3rem; max-width: 1400px; }}
  section[data-testid="stSidebar"] > div:first-child {{ background-color: {CARD}; border-right: 1px solid {BORDER}; }}

  /* KPI Cards */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 8px; }}
  .kpi-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 12px 12px 0 0;
  }}
  .kpi-card.blue::before   {{ background: {ACCENT}; }}
  .kpi-card.green::before  {{ background: {GREEN}; }}
  .kpi-card.amber::before  {{ background: {AMBER}; }}
  .kpi-card.red::before    {{ background: {RED}; }}
  .kpi-label  {{ color: {TEXT_SEC}; font-size: 12px; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; margin-bottom: 8px; }}
  .kpi-value  {{ color: {TEXT}; font-size: 26px; font-weight: 700; letter-spacing: -.02em; line-height: 1; }}
  .kpi-sub    {{ color: {TEXT_SEC}; font-size: 12px; margin-top: 6px; }}
  .kpi-badge  {{ display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px; margin-top: 6px; }}
  .badge-green {{ background: rgba(63,185,80,.15); color: {GREEN}; }}
  .badge-red   {{ background: rgba(248,81,73,.15); color: {RED}; }}
  .badge-amber {{ background: rgba(210,153,34,.15); color: {AMBER}; }}

  /* Section Headers */
  .section-header {{
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid {BORDER};
  }}
  .section-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    background: {ACCENT};
    flex-shrink: 0;
  }}
  .section-title {{ color: {TEXT}; font-size: 15px; font-weight: 600; }}

  /* Analysis Boxes */
  .analysis-box {{
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 14px;
    margin-bottom: 4px;
    border: 1px solid;
    line-height: 1.65;
  }}
  .analysis-box.info    {{ background: rgba(88,166,255,.07); border-color: rgba(88,166,255,.25); }}
  .analysis-box.success {{ background: rgba(63,185,80,.07);  border-color: rgba(63,185,80,.25); }}
  .analysis-box.warning {{ background: rgba(210,153,34,.07); border-color: rgba(210,153,34,.25); }}
  .analysis-box.danger  {{ background: rgba(248,81,73,.07);  border-color: rgba(248,81,73,.25); }}
  .analysis-head {{
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; font-weight: 600; margin-bottom: 6px;
  }}
  .analysis-head.info    {{ color: {ACCENT}; }}
  .analysis-head.success {{ color: {GREEN}; }}
  .analysis-head.warning {{ color: {AMBER}; }}
  .analysis-head.danger  {{ color: {RED}; }}
  .analysis-body {{ color: {TEXT_SEC}; font-size: 13px; }}
  .analysis-body strong {{ color: {TEXT}; }}

  /* Insight Cards */
  .insight-row {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 15px 18px;
    margin-bottom: 10px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
  }}
  .insight-badge {{
    flex-shrink: 0;
    width: 28px; height: 28px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700;
  }}
  .ib-danger  {{ background: rgba(248,81,73,.2);  color: {RED}; }}
  .ib-success {{ background: rgba(63,185,80,.2);  color: {GREEN}; }}
  .ib-warning {{ background: rgba(210,153,34,.2); color: {AMBER}; }}
  .ib-info    {{ background: rgba(88,166,255,.2); color: {ACCENT}; }}
  .insight-content .title {{ color: {TEXT}; font-size: 13px; font-weight: 600; margin-bottom: 3px; }}
  .insight-content .body  {{ color: {TEXT_SEC}; font-size: 12px; line-height: 1.6; }}

  /* Dividers */
  hr {{ border-color: {BORDER} !important; margin: 24px 0; }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{ background: transparent; border-bottom: 1px solid {BORDER}; gap: 0; }}
  .stTabs [data-baseweb="tab"] {{
    color: {TEXT_SEC}; background: transparent;
    padding: 10px 18px; font-size: 13px; font-weight: 500;
    border-bottom: 2px solid transparent;
  }}
  .stTabs [aria-selected="true"] {{ color: {TEXT} !important; border-bottom-color: {ACCENT} !important; }}
  .stTabs [data-baseweb="tab-border"] {{ display: none; }}
  .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}

  /* Metrics */
  div[data-testid="metric-container"] {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; padding: 14px 16px; }}

  /* Sidebar */
  .stSidebar .stMultiSelect label, .stSidebar label {{ color: {TEXT_SEC} !important; font-size: 12px !important; }}

  /* Table */
  div[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 8px; overflow: hidden; }}

  /* Page title */
  .page-title {{
    font-size: 24px; font-weight: 700; color: {TEXT};
    letter-spacing: -.03em; margin-bottom: 4px;
  }}
  .page-sub {{ color: {TEXT_SEC}; font-size: 13px; }}

  /* Action table */
  .action-row {{
    display: grid;
    grid-template-columns: 90px 1fr 160px;
    gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid {BORDER};
    align-items: center;
    font-size: 13px;
  }}
  .action-row:last-child {{ border-bottom: none; }}
  .action-row:first-child {{ font-weight: 600; color: {TEXT_SEC}; font-size: 11px; text-transform: uppercase; letter-spacing: .05em; }}
  .action-table {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; overflow: hidden; margin-top: 8px; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def section(title):
    st.markdown(f"""
    <div class="section-header">
      <div class="section-dot"></div>
      <div class="section-title">{title}</div>
    </div>""", unsafe_allow_html=True)

def analysis(kind, head, body):
    icons = {"info": "→", "success": "✓", "warning": "!", "danger": "✕"}
    st.markdown(f"""
    <div class="analysis-box {kind}">
      <div class="analysis-head {kind}">{icons.get(kind,'·')} {head}</div>
      <div class="analysis-body">{body}</div>
    </div>""", unsafe_allow_html=True)

def kpi_card(label, value, sub="", badge="", badge_kind=""):
    color_map = {"blue": "blue", "green": "green", "amber": "amber", "red": "red"}
    c = color_map.get(badge_kind, "blue")
    badge_html = f'<span class="kpi-badge badge-{badge_kind}">{badge}</span>' if badge else ""
    return f"""
    <div class="kpi-card {c}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {f'<div class="kpi-sub">{sub}</div>' if sub else ''}
      {badge_html}
    </div>"""


# ══════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_excel("핀테크_테이터분석.xlsx", sheet_name="Sheet1")
    df["date"]        = pd.to_datetime(df["date"])
    df["month"]       = df["date"].dt.month
    df["month_label"] = df["date"].dt.strftime("%Y-%m")
    df["CTR"]         = df["광고클릭"] / df["광고노출"].replace(0, np.nan) * 100
    df["CPC"]         = df["광고비"]   / df["광고클릭"].replace(0, np.nan)
    df["install_rate"]= df["앱설치"]   / df["광고클릭"].replace(0, np.nan) * 100
    df["CVR_signup"]  = df["회원가입"] / df["앱설치"].replace(0, np.nan)   * 100
    df["CVR_account"] = df["계좌개설"] / df["회원가입"].replace(0, np.nan) * 100
    df["CVR_trade"]   = df["첫거래"]   / df["계좌개설"].replace(0, np.nan) * 100
    df["CAC"]         = df["광고비"]   / df["회원가입"].replace(0, np.nan)
    df["CPA_account"] = df["광고비"]   / df["계좌개설"].replace(0, np.nan)
    return df

df = load_data()
MONTH_KOR = {i: f"{i}월" for i in range(1, 13)}


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="color:{TEXT};font-size:14px;font-weight:600;padding:8px 0 16px;">필터</div>', unsafe_allow_html=True)
    sel_channels   = st.multiselect("채널", ["구글","페이스북","네이버검색"], default=["구글","페이스북","네이버검색"])
    sel_months     = st.multiselect("월", list(range(1,13)), default=list(range(1,13)), format_func=lambda x: MONTH_KOR[x])
    sel_objectives = st.multiselect("캠페인 목적", df["campaign_objective"].unique().tolist(), default=df["campaign_objective"].unique().tolist())
    sel_groups     = st.multiselect("광고그룹", ["논타겟","리타겟"], default=["논타겟","리타겟"])

fdf = df[
    df["channel"].isin(sel_channels) &
    df["month"].isin(sel_months) &
    df["campaign_objective"].isin(sel_objectives) &
    df["ad_group"].isin(sel_groups)
].copy()


# ══════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class="page-title">핀테크 마케팅 분석 대시보드</div>
<div class="page-sub">데이터 기간: 2025.01 ~ 2025.12 &nbsp;·&nbsp; 채널: 구글 · 페이스북 · 네이버검색</div>
""", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "KPI 개요", "월별 추이", "채널 분석",
    "캠페인 · 그룹 · 소재", "퍼널 분석", "인사이트"
])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — KPI 개요
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    tot_spend   = fdf["광고비"].sum()
    tot_signup  = fdf["회원가입"].sum()
    tot_account = fdf["계좌개설"].sum()
    tot_trade   = fdf["첫거래"].sum()
    tot_click   = fdf["광고클릭"].sum()
    tot_imp     = fdf["광고노출"].sum()
    tot_install = fdf["앱설치"].sum()
    cac  = tot_spend / tot_signup  if tot_signup  else 0
    cpa  = tot_spend / tot_account if tot_account else 0
    ctr  = tot_click / tot_imp * 100 if tot_imp else 0
    cvr1 = tot_signup  / tot_install  * 100 if tot_install  else 0
    cvr2 = tot_account / tot_signup   * 100 if tot_signup   else 0
    cvr3 = tot_trade   / tot_account  * 100 if tot_account  else 0

    section("전체 KPI 요약")
    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_card("총 광고비", f"₩{tot_spend/1e9:.2f}B", f"집행 총액 {tot_spend/1e8:.0f}억원", "", "blue")}
      {kpi_card("총 회원가입", f"{tot_signup/1e6:.2f}M", f"계좌개설 {tot_account/1e6:.2f}M · 첫거래 {tot_trade/1e6:.2f}M", "", "green")}
      {kpi_card("CAC", f"₩{cac:,.0f}", "회원가입당 획득 비용 (MMP 기준)", "요주의" if cac > 1500 else "양호", "red" if cac > 1500 else "green")}
      {kpi_card("퍼널 전환율", f"{cvr1:.1f}%", f"앱설치→회원가입 · 계좌개설 CVR {cvr2:.1f}%", "", "amber")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # 2nd row KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("CPA (계좌개설)", f"₩{cpa:,.0f}")
    with c2: st.metric("CTR", f"{ctr:.2f}%")
    with c3: st.metric("CVR 회원가입/계좌개설", f"{cvr2:.1f}%")
    with c4: st.metric("CVR 계좌개설/첫거래", f"{cvr3:.1f}%")

    analysis("warning", "KPI 해석",
        f"전체 광고비 <strong>₩{tot_spend/1e9:.2f}B</strong>을 집행해 회원가입 <strong>{tot_signup/1e6:.2f}M명</strong>을 획득했습니다. "
        f"CAC ₩{cac:,.0f}는 구글(₩900) · 페이스북(₩1,429) · 네이버검색(₩3,280)의 가중평균으로, "
        "채널 간 효율 격차가 매우 크기 때문에 채널별 예산 재분배가 전체 CAC를 즉시 낮출 수 있는 핵심 레버입니다.")

    st.markdown("<hr>", unsafe_allow_html=True)
    section("채널별 KPI 비교표")

    ch = fdf.groupby("channel").agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"),
        앱설치=("앱설치","sum"), 회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum")
    ).reset_index()
    ch["CTR(%)"]      = (ch["광고클릭"] / ch["광고노출"] * 100).round(2)
    ch["CAC(₩)"]      = (ch["광고비"]   / ch["회원가입"]).round(0).astype(int)
    ch["CPA계좌(₩)"]  = (ch["광고비"]   / ch["계좌개설"]).round(0).astype(int)
    ch["CVR가입(%)"]  = (ch["회원가입"] / ch["앱설치"] * 100).round(1)
    ch["CVR계좌(%)"]  = (ch["계좌개설"] / ch["회원가입"] * 100).round(1)
    ch["CVR거래(%)"]  = (ch["첫거래"]   / ch["계좌개설"] * 100).round(1)
    ch["광고비(억)"]  = (ch["광고비"]   / 1e8).round(1)

    st.dataframe(
        ch[["channel","광고비(억)","회원가입","계좌개설","CTR(%)","CAC(₩)","CPA계좌(₩)","CVR가입(%)","CVR계좌(%)","CVR거래(%)"]].rename(columns={"channel":"채널"}),
        hide_index=True, use_container_width=True
    )
    analysis("danger", "채널 비교 핵심 문제",
        "네이버검색은 광고비 <strong>33%</strong>를 소진하면서 회원가입 기여율은 <strong>14.8%</strong>에 그칩니다. "
        "구글 대비 <strong>CAC가 3.6배</strong> 높으며, 이 불균형이 전체 평균 CAC를 끌어올리는 주범입니다. "
        "반면 구글은 38.8% 예산으로 41.1% 회원가입을 가져오는 유일하게 예산 대비 기여가 높은 채널입니다.")

    st.markdown("<hr>", unsafe_allow_html=True)
    section("채널별 CAC vs 광고비 집행")

    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure()
        colors_list = [CHANNEL_COLORS.get(c, ACCENT) for c in ch["channel"]]
        fig.add_trace(go.Bar(
            x=ch["channel"], y=ch["CAC(₩)"],
            marker_color=colors_list,
            marker_line_width=0,
            text=[f"₩{v:,}" for v in ch["CAC(₩)"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=12),
        ))
        avg_cac = int(ch["CAC(₩)"].mean())
        fig.add_hline(y=avg_cac, line_dash="dot", line_color=AMBER,
                      annotation_text=f"평균 CAC ₩{avg_cac:,}", annotation_font_color=AMBER)
        fig.update_layout(**chart_layout("채널별 CAC — 회원가입당 비용 (낮을수록 효율적)", 360, False))
        fig.update_yaxes(title_text="CAC (₩)")
        st.plotly_chart(fig, use_container_width=True)

        analysis("danger", "CAC 격차 분석",
            "구글(₩900) · 페이스북(₩1,429) · 네이버검색(₩3,280) 순으로 효율이 극명하게 갈립니다. "
            "네이버검색은 <strong>검색 의도 기반</strong>이라 클릭 단가가 높고, "
            "앱설치 전환율도 낮아 CAC가 구조적으로 높을 수밖에 없습니다. "
            "<strong>권고:</strong> 네이버 예산 30% 삭감 → 구글 재투입 시 동일 예산으로 회원가입 약 +12% 기대.")

    with col_b:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=ch["channel"], y=ch["광고비(억)"],
            marker_color=colors_list,
            marker_line_width=0,
            text=[f"{v}억" for v in ch["광고비(억)"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=12),
        ))
        fig2.update_layout(**chart_layout("채널별 광고비 집행액", 360, False))
        fig2.update_yaxes(title_text="광고비 (억원)")
        st.plotly_chart(fig2, use_container_width=True)

        analysis("warning", "광고비 배분 현황",
            "페이스북이 전체 광고비의 <strong>43%</strong>로 가장 많이 집행되고 있으나, "
            "CAC 효율은 구글이 훨씬 우수합니다. "
            "현재 배분은 '인지도 확보' 목적과 '전환 효율' 목적이 혼재된 구조입니다. "
            "전환 효율 중심으로 재설계한다면 <strong>구글 비중 확대, 네이버 축소</strong>가 최우선 조정점입니다.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — 월별 추이
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    monthly = fdf.groupby(["month","month_label","channel"]).agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"),
        앱설치=("앱설치","sum"), 회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum")
    ).reset_index().sort_values("month")
    monthly["CAC"]         = monthly["광고비"] / monthly["회원가입"].replace(0,np.nan)
    monthly["CTR"]         = monthly["광고클릭"] / monthly["광고노출"].replace(0,np.nan) * 100
    monthly["CVR_signup"]  = monthly["회원가입"] / monthly["앱설치"].replace(0,np.nan) * 100
    monthly["CVR_account"] = monthly["계좌개설"] / monthly["회원가입"].replace(0,np.nan) * 100

    monthly_total = fdf.groupby(["month","month_label"]).agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"),
        첫거래=("첫거래","sum"), 광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"), 앱설치=("앱설치","sum")
    ).reset_index().sort_values("month")
    monthly_total["CAC"]         = monthly_total["광고비"] / monthly_total["회원가입"]
    monthly_total["CTR"]         = monthly_total["광고클릭"] / monthly_total["광고노출"] * 100
    monthly_total["CVR_signup"]  = monthly_total["회원가입"] / monthly_total["앱설치"] * 100
    monthly_total["CVR_account"] = monthly_total["계좌개설"] / monthly_total["회원가입"] * 100

    # ── 광고비 × CAC 이중축 ──
    section("월별 광고비 집행 vs CAC 추이")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly_total["month_label"], y=monthly_total["광고비"],
        name="광고비", marker_color=ACCENT, opacity=0.6, marker_line_width=0,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly_total["month_label"], y=monthly_total["CAC"],
        name="CAC", mode="lines+markers",
        line=dict(color=RED, width=2.5), marker=dict(size=7, color=RED),
    ), secondary_y=True)
    # spike months
    for m, label in [("2025-03", "3월 급등"), ("2025-09", "9월 급등"), ("2025-12", "12월 급등")]:
        fig.add_vline(x=m, line_dash="dot", line_color=AMBER, opacity=0.5)
    fig.update_layout(**chart_layout("", 420))
    fig.update_yaxes(title_text="광고비 (원)", secondary_y=False, gridcolor=GRID_CLR, tickfont=dict(color=TEXT_SEC))
    fig.update_yaxes(title_text="CAC (₩)", secondary_y=True, gridcolor="rgba(0,0,0,0)", tickfont=dict(color=RED))
    st.plotly_chart(fig, use_container_width=True)

    analysis("danger", "예산 증액 = CAC 상승 패턴 발견",
        "<strong>3월(₩292억) · 9월(₩310억) · 12월(₩335억)</strong>에 광고비가 급증할 때마다 CAC도 동반 상승합니다. "
        "3월 CAC ₩1,601 → 4월 ₩1,389로 회복, 9월 ₩1,664 → 10월 ₩1,524로 회복 패턴이 반복됩니다. "
        "이는 <strong>예산 증액이 반드시 효율을 보장하지 않음</strong>을 보여줍니다. "
        "급등 시기는 경쟁사 광고 집중 · 입찰가 상승 효과로 추정되며, "
        "무계획적 예산 확대보다 소재 다양화와 타겟 정밀화가 우선되어야 합니다.")

    # ── 채널별 CAC 월간 추이 ──
    section("채널별 월간 CAC 추이")
    fig2 = go.Figure()
    for ch_name, color in CHANNEL_COLORS.items():
        sub = monthly[monthly["channel"] == ch_name].sort_values("month")
        fig2.add_trace(go.Scatter(
            x=sub["month_label"], y=sub["CAC"],
            name=ch_name, mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
        ))
    fig2.update_layout(**chart_layout("", 380))
    fig2.update_yaxes(title_text="CAC (₩)")
    st.plotly_chart(fig2, use_container_width=True)

    analysis("info", "채널별 CAC 계절성 패턴",
        "세 채널 모두 <strong>동일한 계절성 패턴</strong>(3·9·12월 피크)을 보입니다. "
        "구글은 1·7월 최저 ₩759~761 / 12월 최고 ₩1,108로 연간 변동폭이 약 46%에 달합니다. "
        "네이버검색은 12월 ₩4,028까지 치솟아 비수기(₩2,757) 대비 <strong>46% 상승</strong>합니다. "
        "따라서 <strong>1월·7월 비수기</strong>에 예산을 집중하는 역발상 전략이 CAC 절감에 효과적입니다.")

    # ── 월별 지표 선택 ──
    section("월별 지표 상세 추이")
    metric_map = {
        "회원가입수": "회원가입", "계좌개설수": "계좌개설",
        "CTR (%)": "CTR", "CVR 앱설치→회원가입 (%)": "CVR_signup", "CVR 회원가입→계좌개설 (%)": "CVR_account"
    }
    chosen_label = st.selectbox("지표 선택", list(metric_map.keys()), label_visibility="collapsed")
    chosen_col = metric_map[chosen_label]

    fig3 = go.Figure()
    for ch_name, color in CHANNEL_COLORS.items():
        sub = monthly[monthly["channel"] == ch_name].sort_values("month")
        fig3.add_trace(go.Scatter(
            x=sub["month_label"], y=sub[chosen_col],
            name=ch_name, mode="lines+markers",
            line=dict(color=color, width=2), marker=dict(size=6),
        ))
    fig3.update_layout(**chart_layout(f"채널별 월간 {chosen_label}", 360))
    st.plotly_chart(fig3, use_container_width=True)

    if "CVR" in chosen_label:
        analysis("success", "CVR은 채널에 무관하게 일정",
            "앱설치→회원가입 CVR과 회원가입→계좌개설 CVR 모두 채널을 막론하고 <strong>거의 동일한 수준</strong>을 유지합니다. "
            "이는 CVR이 광고 소재나 채널 품질보다 <strong>앱 내 온보딩 UX</strong>에 의해 결정된다는 의미입니다. "
            "전환율을 높이려면 광고 최적화보다 <strong>앱 내 경험 개선</strong>에 투자하는 것이 더 직접적인 효과를 냅니다.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — 채널 분석
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    ch_det = fdf.groupby("channel").agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"),
        앱설치=("앱설치","sum"), 회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum")
    ).reset_index()
    ch_det["CTR"]         = ch_det["광고클릭"] / ch_det["광고노출"] * 100
    ch_det["CVR_signup"]  = ch_det["회원가입"] / ch_det["앱설치"]   * 100
    ch_det["CVR_account"] = ch_det["계좌개설"] / ch_det["회원가입"] * 100
    ch_det["CVR_trade"]   = ch_det["첫거래"]   / ch_det["계좌개설"] * 100
    ch_det["CAC"]         = ch_det["광고비"]   / ch_det["회원가입"]

    # ── 광고비 vs 회원가입 파이 ──
    section("채널별 광고비 투입 vs 회원가입 기여 비교")
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Pie(
            labels=ch_det["channel"], values=ch_det["광고비"],
            hole=0.55, pull=[0.05,0,0],
            marker=dict(colors=[CHANNEL_COLORS.get(c, ACCENT) for c in ch_det["channel"]],
                        line=dict(color=BG, width=2)),
            textfont=dict(color=TEXT),
            hovertemplate="%{label}<br>₩%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig.add_annotation(text="광고비", x=0.5, y=0.55, showarrow=False, font=dict(color=TEXT_SEC, size=11))
        fig.add_annotation(text="투입 비율", x=0.5, y=0.45, showarrow=False, font=dict(color=TEXT, size=13, weight=700 if hasattr(dict, 'weight') else 400))
        fig.update_layout(**chart_layout("광고비 채널 배분", 360, True))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = go.Figure(go.Pie(
            labels=ch_det["channel"], values=ch_det["회원가입"],
            hole=0.55,
            marker=dict(colors=[CHANNEL_COLORS.get(c, ACCENT) for c in ch_det["channel"]],
                        line=dict(color=BG, width=2)),
            textfont=dict(color=TEXT),
            hovertemplate="%{label}<br>%{value:,}명<br>%{percent}<extra></extra>",
        ))
        fig2.update_layout(**chart_layout("회원가입 기여 비율", 360, True))
        st.plotly_chart(fig2, use_container_width=True)

    analysis("danger", "투입 대비 성과 불균형",
        "네이버검색은 광고비 <strong>33.1%</strong>를 가져가지만 회원가입 기여는 <strong>14.8%</strong>에 불과합니다 — "
        "투입 대비 기여율 <strong>갭 18.3%p</strong>. "
        "반면 구글은 38.8% 투입으로 41.1%를 기여하며 유일하게 플러스 효율입니다. "
        "파이 차트 두 개를 나란히 비교하면 네이버의 구조적 비효율을 직관적으로 확인할 수 있습니다.")

    # ── CVR 단계 비교 ──
    section("채널별 단계별 전환율 비교")
    cvr_melt = ch_det[["channel","CVR_signup","CVR_account","CVR_trade"]].melt(
        id_vars="channel", var_name="단계", value_name="전환율(%)")
    cvr_melt["단계"] = cvr_melt["단계"].map({
        "CVR_signup": "앱설치 → 회원가입",
        "CVR_account": "회원가입 → 계좌개설",
        "CVR_trade": "계좌개설 → 첫거래",
    })
    fig3 = go.Figure()
    for ch_name, color in CHANNEL_COLORS.items():
        sub = cvr_melt[cvr_melt["channel"] == ch_name]
        fig3.add_trace(go.Bar(
            name=ch_name, x=sub["단계"], y=sub["전환율(%)"],
            marker_color=color, marker_line_width=0,
            text=[f"{v:.1f}%" for v in sub["전환율(%)"]],
            textposition="outside", textfont=dict(color=TEXT, size=11),
        ))
    fig3.update_layout(**chart_layout("", 400), barmode="group")
    fig3.update_yaxes(title_text="전환율 (%)", range=[0, 100])
    st.plotly_chart(fig3, use_container_width=True)

    analysis("success", "CVR 채널 무관성 — 핵심 발견",
        "앱설치→회원가입 CVR은 세 채널 모두 <strong>약 69.5%</strong>로 통일되고, "
        "회원가입→계좌개설 CVR도 <strong>약 76.9%</strong>로 동일합니다. "
        "단, 계좌개설→첫거래 CVR은 <strong>51.2%</strong>로 채널 공통 병목입니다. "
        "이 패턴은 전환율 저하가 광고 채널 문제가 아니라 <strong>앱 내 UX/프로세스 문제</strong>임을 강력하게 시사합니다.")

    # ── 채널 × 광고그룹 ──
    section("채널 × 광고그룹별 CAC 비교")
    ch_group = fdf.groupby(["channel","ad_group"]).agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum")
    ).reset_index()
    ch_group["CAC"] = ch_group["광고비"] / ch_group["회원가입"].replace(0, np.nan)

    fig4 = go.Figure()
    for grp, color in [("논타겟", ACCENT), ("리타겟", GREEN)]:
        sub = ch_group[ch_group["ad_group"] == grp]
        fig4.add_trace(go.Bar(
            name=grp, x=sub["channel"], y=sub["CAC"],
            marker_color=color, marker_line_width=0,
            text=[f"₩{v:,.0f}" for v in sub["CAC"]],
            textposition="outside", textfont=dict(color=TEXT, size=11),
        ))
    fig4.update_layout(**chart_layout("", 380), barmode="group")
    fig4.update_yaxes(title_text="CAC (₩)")
    st.plotly_chart(fig4, use_container_width=True)

    analysis("success", "리타겟팅 우위 확인",
        "모든 채널에서 <strong>리타겟팅이 논타겟 대비 CAC가 낮습니다</strong>. "
        "전체 기준 리타겟 CAC ₩1,336 vs 논타겟 ₩1,735 — <strong>23% 절감</strong>. "
        "리타겟팅은 이미 앱에 관심을 보인 유저를 재유입시키므로 전환 의도가 높아 효율적입니다. "
        "<strong>권고:</strong> 리타겟팅 예산 비율을 현재보다 10~15%p 확대하면 전체 CAC가 의미있게 낮아질 수 있습니다.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — 캠페인 · 그룹 · 소재
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    camp = fdf.groupby(["channel","campaign_id","campaign_objective"]).agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"),
        첫거래=("첫거래","sum"), 광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"), 앱설치=("앱설치","sum")
    ).reset_index()
    camp["CAC"]         = camp["광고비"] / camp["회원가입"].replace(0,np.nan)
    camp["CVR_account"] = camp["계좌개설"] / camp["회원가입"].replace(0,np.nan) * 100
    camp["CTR"]         = camp["광고클릭"] / camp["광고노출"].replace(0,np.nan) * 100

    # ── TOP / BOTTOM 캠페인 ──
    section("캠페인별 효율 순위 (CAC 기준)")
    top_n = st.slider("표시 개수", 5, 15, 10, label_visibility="collapsed")
    top_camp = camp.sort_values("CAC").head(top_n)
    bot_camp = camp.sort_values("CAC", ascending=False).head(top_n)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Bar(
            x=top_camp["CAC"], y=top_camp["campaign_id"],
            orientation="h",
            marker_color=[CHANNEL_COLORS.get(c, ACCENT) for c in top_camp["channel"]],
            marker_line_width=0,
            text=[f"₩{v:,.0f}" for v in top_camp["CAC"]],
            textposition="outside", textfont=dict(color=TEXT, size=10),
        ))
        fig.update_layout(**chart_layout(f"TOP {top_n} — 효율 우수 캠페인", 420, False))
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = go.Figure(go.Bar(
            x=bot_camp["CAC"], y=bot_camp["campaign_id"],
            orientation="h",
            marker_color=[CHANNEL_COLORS.get(c, ACCENT) for c in bot_camp["channel"]],
            marker_line_width=0,
            text=[f"₩{v:,.0f}" for v in bot_camp["CAC"]],
            textposition="outside", textfont=dict(color=TEXT, size=10),
        ))
        fig2.update_layout(**chart_layout(f"BOTTOM {top_n} — 비효율 캠페인", 420, False))
        fig2.update_yaxes(categoryorder="total descending")
        st.plotly_chart(fig2, use_container_width=True)

    analysis("danger", "캠페인 효율 극단 분포",
        "최고 효율 캠페인(구글 회원가입 계열, CAC ₩783~790)과 최하위(네이버검색 계좌개설 계열, CAC ₩3,803~3,829)의 "
        "<strong>격차는 약 4.9배</strong>에 달합니다. "
        "네이버검색 계좌개설 캠페인은 전 하위권을 독점하며, "
        "이들 캠페인을 정지하는 것만으로도 전체 평균 CAC를 즉시 낮출 수 있습니다.")

    # ── 소재 포맷별 CAC & CTR ──
    section("소재 포맷별 성과 분석")
    creative = fdf.groupby(["channel","creative_format"]).agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"),
        앱설치=("앱설치","sum"), 회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum")
    ).reset_index()
    creative["CTR"] = creative["광고클릭"] / creative["광고노출"] * 100
    creative["CAC"] = creative["광고비"]   / creative["회원가입"].replace(0,np.nan)

    # 전체 소재별 요약
    creative_total = fdf.groupby("creative_format").agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"),
        광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum")
    ).reset_index()
    creative_total["CAC"] = creative_total["광고비"] / creative_total["회원가입"]
    creative_total["CTR"] = creative_total["광고클릭"] / creative_total["광고노출"] * 100

    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure(go.Bar(
            x=creative_total["creative_format"],
            y=creative_total["CAC"],
            marker_color=[FORMAT_COLORS.get(f, ACCENT) for f in creative_total["creative_format"]],
            marker_line_width=0,
            text=[f"₩{v:,.0f}" for v in creative_total["CAC"]],
            textposition="outside", textfont=dict(color=TEXT, size=11),
        ))
        avg_cac_line = creative_total["CAC"].mean()
        fig3.add_hline(y=avg_cac_line, line_dash="dot", line_color=AMBER,
                       annotation_text=f"평균 ₩{avg_cac_line:,.0f}", annotation_font_color=AMBER)
        fig3.update_layout(**chart_layout("소재 포맷별 CAC", 380, False))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure(go.Bar(
            x=creative_total["creative_format"],
            y=creative_total["CTR"],
            marker_color=[FORMAT_COLORS.get(f, ACCENT) for f in creative_total["creative_format"]],
            marker_line_width=0,
            text=[f"{v:.2f}%" for v in creative_total["CTR"]],
            textposition="outside", textfont=dict(color=TEXT, size=11),
        ))
        fig4.update_layout(**chart_layout("소재 포맷별 CTR (%)", 380, False))
        st.plotly_chart(fig4, use_container_width=True)

    analysis("info", "소재 포맷 효율 해석",
        "<strong>영상(CAC ₩1,126)</strong>이 이미지(₩1,236) 대비 9% 낮아 디스플레이 소재 중 우위입니다. "
        "CTR은 브랜드키워드(13.3%) · 일반키워드(8.9%)가 높게 나오지만, "
        "이는 검색광고 특성상 자연스러운 것이며 CAC는 오히려 <strong>최하위</strong>입니다. "
        "CTR과 CAC가 반비례하는 역설은 '많이 클릭한다 ≠ 효율적으로 전환한다'는 것을 보여줍니다. "
        "<strong>권고:</strong> 구글/페이스북 영상 소재 비중 확대, 네이버 키워드 소재 단가 재조정.")

    # ── 광고그룹별 CAC ──
    section("광고그룹별 성과")
    adgrp_total = fdf.groupby("ad_group").agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"),
        계좌개설=("계좌개설","sum"), 앱설치=("앱설치","sum")
    ).reset_index()
    adgrp_total["CAC"]        = adgrp_total["광고비"] / adgrp_total["회원가입"]
    adgrp_total["CVR_signup"] = adgrp_total["회원가입"] / adgrp_total["앱설치"] * 100
    adgrp_total["예산비율"]   = adgrp_total["광고비"] / adgrp_total["광고비"].sum() * 100

    col5, col6 = st.columns(2)
    with col5:
        fig5 = go.Figure(go.Bar(
            x=adgrp_total["ad_group"], y=adgrp_total["CAC"],
            marker_color=[ACCENT, GREEN], marker_line_width=0,
            text=[f"₩{v:,.0f}" for v in adgrp_total["CAC"]],
            textposition="outside", textfont=dict(color=TEXT, size=12),
        ))
        fig5.update_layout(**chart_layout("광고그룹별 CAC", 360, False))
        st.plotly_chart(fig5, use_container_width=True)
    with col6:
        fig6 = go.Figure(go.Bar(
            x=adgrp_total["ad_group"], y=adgrp_total["예산비율"],
            marker_color=[ACCENT, GREEN], marker_line_width=0,
            text=[f"{v:.1f}%" for v in adgrp_total["예산비율"]],
            textposition="outside", textfont=dict(color=TEXT, size=12),
        ))
        fig6.update_layout(**chart_layout("광고그룹별 예산 비율 (%)", 360, False))
        st.plotly_chart(fig6, use_container_width=True)

    analysis("success", "리타겟 vs 논타겟 — 예산 배분 최적화 여지",
        "리타겟팅 CAC ₩1,336 vs 논타겟 ₩1,735로 <strong>리타겟이 23% 효율적</strong>이지만, "
        f"현재 리타겟팅 예산 비율은 {adgrp_total[adgrp_total['ad_group']=='리타겟']['예산비율'].values[0]:.1f}%에 불과합니다. "
        "리타겟팅 예산 비율을 현재보다 10%p 높이면 동일 광고비로 더 많은 회원가입을 기대할 수 있습니다. "
        "단, 리타겟팅 모수(기존 방문자)가 고갈되지 않도록 신규 유입 캠페인과의 균형이 필요합니다.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — 퍼널 분석
# ════════════════════════════════════════════════════════════════════════════════
with tab5:
    funnel_cols = ["광고노출","광고클릭","앱설치","앱실행","회원가입","계좌개설","첫거래","반복사용","자동이체설정","추천완료"]
    funnel_labels = ["광고 노출","광고 클릭","앱 설치","앱 실행","회원 가입","계좌 개설","첫 거래","반복 사용","자동이체 설정","추천 완료"]
    totals = fdf[funnel_cols].sum()

    rates = []
    for i in range(1, len(funnel_cols)):
        prev = totals.iloc[i-1]; curr = totals.iloc[i]
        rates.append({
            "단계": f"{funnel_labels[i-1]} → {funnel_labels[i]}",
            "전환율(%)": round(curr/prev*100, 1) if prev else 0,
            "이탈율(%)": round((1-curr/prev)*100, 1) if prev else 0,
            "모수": int(prev), "전환수": int(curr),
        })
    rate_df = pd.DataFrame(rates)

    section("전체 퍼널 전환 시각화")
    col1, col2 = st.columns([1.3, 1])
    with col1:
        funnel_colors = [
            "#58a6ff","#4d9de0","#3fb950","#36a445",
            "#d29922","#c08c1e","#f85149","#e04842",
            "#bc8cff","#a87de0"
        ]
        fig_f = go.Figure(go.Funnel(
            y=funnel_labels,
            x=[int(totals[c]) for c in funnel_cols],
            textinfo="value+percent previous",
            textfont=dict(color=TEXT, size=12),
            marker=dict(color=funnel_colors, line=dict(color=BG, width=1)),
            connector=dict(line=dict(color=BORDER, width=1)),
        ))
        fig_f.update_layout(**chart_layout("전체 퍼널 (연간 누적)", 500, False))
        st.plotly_chart(fig_f, use_container_width=True)

    with col2:
        section("단계별 전환율 / 이탈율")
        # 색상 강조: 낮은 전환율은 빨간색 배경
        def highlight_row(row):
            if row["전환율(%)"] < 30:
                bg = "rgba(248,81,73,0.15)"
            elif row["전환율(%)"] < 60:
                bg = "rgba(210,153,34,0.1)"
            else:
                bg = "transparent"
            return bg

        for _, row in rate_df.iterrows():
            bg = highlight_row(row)
            pct = row["전환율(%)"]
            bar_color = RED if pct < 30 else AMBER if pct < 60 else GREEN
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {BORDER};border-radius:8px;
                        padding:10px 14px;margin-bottom:7px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                <span style="color:{TEXT_SEC};font-size:11px;">{row['단계']}</span>
                <span style="color:{bar_color};font-size:13px;font-weight:700;">{pct}%</span>
              </div>
              <div style="background:{BORDER};border-radius:4px;height:5px;overflow:hidden;">
                <div style="background:{bar_color};height:100%;width:{min(pct,100)}%;border-radius:4px;"></div>
              </div>
              <div style="color:{TEXT_SEC};font-size:10px;margin-top:4px;">
                이탈 {row['이탈율(%)']:}% &nbsp;·&nbsp; 전환수 {row['전환수']:,}
              </div>
            </div>""", unsafe_allow_html=True)

    analysis("danger", "퍼널 2대 병목 발견",
        "<strong>1순위 병목 — 자동이체설정 전환율 21.9%:</strong> "
        "반복 사용자 중 78.1%가 자동이체 기능을 외면합니다. "
        "자동이체 설정 완료 시 혜택(이자 우대 등)을 강조하는 인앱 토스트 메시지 + CRM 시퀀스를 신설해야 합니다.<br><br>"
        "<strong>2순위 병목 — 계좌개설→첫거래 전환율 51.2%:</strong> "
        "계좌를 열었지만 한 번도 거래하지 않은 사용자가 절반 가까이 됩니다. "
        "온보딩 완료 직후 '첫 거래 보너스' 또는 '소액 자동 투자 체험' 플로우를 제공하면 이 병목을 효과적으로 해소할 수 있습니다.")

    # ── 채널별 퍼널 비교 ──
    section("채널별 퍼널 단계 전환율 비교")
    ch_funnel = fdf.groupby("channel")[funnel_cols].sum().reset_index()

    stage_options = {
        "광고클릭 → 앱설치": ("광고클릭","앱설치"),
        "앱설치 → 회원가입": ("앱설치","회원가입"),
        "회원가입 → 계좌개설": ("회원가입","계좌개설"),
        "계좌개설 → 첫거래": ("계좌개설","첫거래"),
    }
    chosen_stage = st.selectbox("비교 단계 선택", list(stage_options.keys()), label_visibility="collapsed")
    n, d = stage_options[chosen_stage]
    ch_funnel["cvr"] = ch_funnel[d] / ch_funnel[n].replace(0,np.nan) * 100

    fig_ch = go.Figure(go.Bar(
        x=ch_funnel["channel"], y=ch_funnel["cvr"],
        marker_color=[CHANNEL_COLORS.get(c, ACCENT) for c in ch_funnel["channel"]],
        marker_line_width=0,
        text=[f"{v:.1f}%" for v in ch_funnel["cvr"]],
        textposition="outside", textfont=dict(color=TEXT, size=12),
    ))
    fig_ch.update_layout(**chart_layout(f"채널별 {chosen_stage} 전환율", 360, False))
    fig_ch.update_yaxes(range=[0, 110])
    st.plotly_chart(fig_ch, use_container_width=True)

    if "앱설치" in chosen_stage or "회원가입" in chosen_stage:
        analysis("info", "채널 CVR 수렴 현상",
            f"{chosen_stage} CVR이 모든 채널에서 거의 동일합니다. "
            "이는 해당 단계의 전환이 <strong>채널 품질이 아닌 앱 내부 경험</strong>에 의해 결정됨을 의미합니다. "
            "채널 최적화에 리소스를 더 투입해도 이 CVR은 크게 변하지 않습니다. "
            "앱 UI 개선, 온보딩 플로우 축소, 마찰 포인트 제거가 더 높은 ROI를 가져옵니다.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 6 — 인사이트
# ════════════════════════════════════════════════════════════════════════════════
with tab6:
    section("메트릭 하이어라키 — CAC 분해 트리")

    st.markdown(f"""
    <div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:24px 28px;font-size:13px;line-height:2;font-family:'Courier New',monospace;color:{TEXT_SEC};">
      <span style="color:{TEXT};font-weight:700;">전체 CAC ₩1,595</span> <span style="color:{AMBER};">(개선 필요)</span><br>
      │<br>
      ├─ <span style="color:#4285F4;font-weight:600;">구글</span>&nbsp;&nbsp; CAC <span style="color:{GREEN};font-weight:700;">₩900</span> &nbsp;<span style="color:{GREEN};">✓</span>&nbsp; 광고비 38.8% / 회원가입 기여 41.1%<br>
      │&nbsp;&nbsp;&nbsp;├─ 영상 소재 &nbsp; CAC <span style="color:{GREEN};">₩862</span> &nbsp;<span style="color:{GREEN};">← 전체 최우수</span><br>
      │&nbsp;&nbsp;&nbsp;└─ 이미지 소재 CAC ₩949<br>
      │<br>
      ├─ <span style="color:#1877F2;font-weight:600;">페이스북</span> CAC <span style="color:{AMBER};font-weight:700;">₩1,429</span> &nbsp;<span style="color:{AMBER};">△</span>&nbsp; 광고비 43.0% / 회원가입 기여 44.1%<br>
      │&nbsp;&nbsp;&nbsp;├─ 영상 소재 &nbsp; CAC ₩1,371<br>
      │&nbsp;&nbsp;&nbsp;└─ 이미지 소재 CAC ₩1,506<br>
      │<br>
      └─ <span style="color:#00b900;font-weight:600;">네이버검색</span> CAC <span style="color:{RED};font-weight:700;">₩3,280</span> &nbsp;<span style="color:{RED};">✕</span>&nbsp; 광고비 33.1% / 회원가입 기여 14.8%<br>
      &nbsp;&nbsp;&nbsp;&nbsp;├─ 브랜드KW &nbsp;CAC <span style="color:{RED};">₩2,978</span> ← 비용 대비 성과 저조<br>
      &nbsp;&nbsp;&nbsp;&nbsp;└─ 일반KW &nbsp;&nbsp;CAC <span style="color:{RED};">₩3,870</span> ← <span style="color:{RED};font-weight:700;">전체 최하위</span>
    </div>
    """, unsafe_allow_html=True)

    section("퍼널 병목 트리")
    st.markdown(f"""
    <div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:24px 28px;font-size:13px;line-height:2;font-family:'Courier New',monospace;color:{TEXT_SEC};">
      광고노출 <span style="color:{TEXT};">4.55B</span><br>
      &nbsp;&nbsp;→ 광고클릭 47M &nbsp;&nbsp;&nbsp;&nbsp; CTR <span style="color:{ACCENT};">1.03%</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;→ 앱설치 26.4M &nbsp;&nbsp; 설치율 <span style="color:{ACCENT};">56.2%</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 앱실행 23.8M &nbsp;&nbsp; 실행율 <span style="color:{GREEN};">90.0%</span> &nbsp;<span style="color:{TEXT_SEC};">(10% 미실행 이탈)</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 회원가입 18.4M &nbsp;CVR <span style="color:{GREEN};">77.3%</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 계좌개설 14.2M &nbsp;CVR <span style="color:{GREEN};">76.9%</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 첫거래 7.2M &nbsp;&nbsp;&nbsp;&nbsp;CVR <span style="color:{AMBER};">51.2%</span> &nbsp;<span style="color:{AMBER};">⚠ 병목 2</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 반복사용 4.6M &nbsp;&nbsp;CVR <span style="color:{GREEN};">63.7%</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 자동이체설정 1.0M &nbsp;CVR <span style="color:{RED};">21.9%</span> &nbsp;<span style="color:{RED};">✕ 최대 병목</span><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 추천완료 0.5M &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;CVR <span style="color:{AMBER};">50.0%</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    section("핵심 인사이트 15선")

    insights = [
        ("danger","!","1. 네이버검색 CAC, 구글 대비 3.6배",
         "네이버검색 CAC <strong>₩3,280</strong> vs 구글 <strong>₩900</strong>. 광고비 33.1% 투입 → 회원가입 기여 14.8%에 불과. 예산 재배분 즉시 검토 필요."),
        ("danger","!","2. 일반키워드 CAC ₩3,870 — 전체 최하위",
         "네이버 일반키워드 CAC가 전체 소재 포맷 중 가장 높음. 즉각적인 입찰가 인하 또는 중단 검토."),
        ("warning","~","3. 예산 급등 월(3·9·12월)에 CAC 동반 상승",
         "3월 CAC <strong>₩1,601</strong>, 9월 <strong>₩1,664</strong>, 12월 <strong>₩1,820</strong>으로 연간 최고. 예산 증액이 효율 저하를 동반 — 경쟁 심화 시기 전략 재검토 필요."),
        ("danger","!","4. 계좌개설→첫거래 전환율 51.2% — 병목 2",
         "계좌를 개설한 사람의 절반 가까이가 첫 거래 없이 이탈. 온보딩 직후 첫거래 유도 인앱 메시지/리마케팅 캠페인 필요."),
        ("danger","!","5. 자동이체설정 전환율 21.9% — 최대 병목",
         "반복사용 고객 중 78.1%가 자동이체 미설정. 설정 완료 시 혜택 강조 CRM 시퀀스 신설 필요."),
        ("success","✓","6. 구글 영상 소재 CAC ₩862 — 전체 최우수",
         "구글 영상 소재 CAC가 전체 소재 포맷 · 채널 조합 중 최저. 해당 소재 증량 및 유사 크리에이티브 확대 권장."),
        ("success","✓","7. 리타겟팅 CAC가 논타겟보다 23% 낮음",
         "리타겟 CAC <strong>₩1,336</strong> vs 논타겟 <strong>₩1,735</strong>. 리타겟팅 예산 비율 확대 검토."),
        ("info","→","8. 채널 무관 CVR 수렴 — 앱 UX가 핵심",
         "모든 채널에서 앱설치→회원가입 CVR <strong>~69.5%</strong>, 회원가입→계좌개설 CVR <strong>~76.9%</strong>로 동일. 광고 최적화보다 앱 내 UX 개선이 더 큰 CVR 효과."),
        ("warning","~","9. 앱설치→앱실행 10% 이탈",
         "설치 후 미실행 이탈 10% 존재. 설치 직후 푸시 알림 + 딥링크 온보딩 시퀀스로 실행 유도 필요."),
        ("danger","!","10. 네이버검색 계좌개설 캠페인 CVR_account ≈ 99%",
         "회원가입 후 계좌개설 전환율이 비정상적으로 높음 — 어트리뷰션 오류 또는 이중 집계 의심. 실제 로그 교차검증 필요."),
        ("success","✓","11. 영상 소재, 이미지 대비 CAC 9% 낮음",
         "영상 CAC <strong>₩1,126</strong> vs 이미지 <strong>₩1,236</strong>. 디스플레이 채널 내 영상 소재 비중 확대 권장."),
        ("warning","~","12. 12월 CAC ₩1,820 — 연간 최고",
         "연말 광고 경쟁 심화. 반대로 1·7월은 CAC ₩1,250~1,254로 최저 — 비수기 집중 집행으로 CAC 최적화 가능."),
        ("success","✓","13. 채널 효율 순위: 구글 > 페이스북 > 네이버검색",
         "구글(₩900) > 페이스북(₩1,429) > 네이버검색(₩3,280). 예산 재배분 시 구글 최우선."),
        ("warning","~","14. 자동이체 설정자의 50%가 추천 완료",
         "자동이체 설정률(21.9%) 개선 시 추천 바이럴 효과 배가. 자동이체 설정이 추천 전환의 선행 조건."),
        ("danger","!","15. 하위 퍼널(자동이체 이후) 전환 급락",
         "첫거래 이후 반복사용(63.7%)은 양호하나 자동이체설정(21.9%) 급락. 기능 이점 전달 강화 및 설정 유도 UX 개선 필요."),
    ]

    col_a, col_b = st.columns(2)
    for i, (kind, icon, title, body) in enumerate(insights):
        target = col_a if i % 2 == 0 else col_b
        color_map = {"danger": RED, "success": GREEN, "warning": AMBER, "info": ACCENT}
        bg_map = {"danger": "rgba(248,81,73,.15)", "success": "rgba(63,185,80,.15)",
                  "warning": "rgba(210,153,34,.15)", "info": "rgba(88,166,255,.15)"}
        with target:
            st.markdown(f"""
            <div class="insight-row">
              <div class="insight-badge ib-{kind}">{icon}</div>
              <div class="insight-content">
                <div class="title">{title}</div>
                <div class="body">{body}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    section("우선순위별 액션 플랜")

    actions = [
        ("header", "우선순위", "액션 항목", "예상 임팩트"),
        ("red",    "즉시 실행",  "네이버 일반KW 캠페인 예산 50% 삭감",                 "CAC ₩200~400 절감"),
        ("red",    "즉시 실행",  "계좌개설 후 첫거래 유도 인앱 메시지 시퀀스 신설",   "첫거래 CVR +10%p 목표"),
        ("red",    "즉시 실행",  "구글 영상 소재 예산 30% 증량",                        "회원가입 +15% (동일 예산)"),
        ("amber",  "1개월 내",   "자동이체설정 유도 CRM 시퀀스 강화",                  "자동이체 CVR +5%p"),
        ("amber",  "1개월 내",   "3·9·12월 예산 급등 시기 CAC 임계값 자동 알림 설정",  "계절성 CAC 편차 축소"),
        ("green",  "3개월 내",   "앱설치→앱실행 딥링크 푸시 온보딩 구축",              "설치 이탈 -5%p"),
    ]

    st.markdown('<div class="action-table">', unsafe_allow_html=True)
    for row in actions:
        kind, col1_val, col2_val, col3_val = row
        if kind == "header":
            st.markdown(f"""
            <div class="action-row" style="color:{TEXT_SEC};font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;">
              <span>{col1_val}</span><span>{col2_val}</span><span>{col3_val}</span>
            </div>""", unsafe_allow_html=True)
        else:
            badge_colors = {"red": RED, "amber": AMBER, "green": GREEN}
            badge_bg = {"red": "rgba(248,81,73,.15)", "amber": "rgba(210,153,34,.15)", "green": "rgba(63,185,80,.15)"}
            bc = badge_colors.get(kind, ACCENT)
            bb = badge_bg.get(kind, "transparent")
            st.markdown(f"""
            <div class="action-row">
              <span style="background:{bb};color:{bc};border-radius:6px;padding:3px 8px;font-size:11px;font-weight:600;">{col1_val}</span>
              <span style="color:{TEXT};font-size:13px;">{col2_val}</span>
              <span style="color:{TEXT_SEC};font-size:12px;">{col3_val}</span>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
