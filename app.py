import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="핀테크 마케팅 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 커스텀 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #2d3050;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-label { color: #8892a4; font-size: 13px; font-weight: 500; margin-bottom: 6px; }
    .metric-value { color: #e8eaf6; font-size: 28px; font-weight: 700; }
    .metric-delta-pos { color: #26d07c; font-size: 13px; margin-top: 4px; }
    .metric-delta-neg { color: #ff4b6e; font-size: 13px; margin-top: 4px; }
    .insight-card {
        background: linear-gradient(135deg, #1a1f35, #1e2540);
        border-left: 4px solid #5c6bc0;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .insight-card.danger { border-left-color: #ff4b6e; }
    .insight-card.success { border-left-color: #26d07c; }
    .insight-card.warning { border-left-color: #ffa726; }
    .insight-title { color: #e8eaf6; font-weight: 600; font-size: 14px; }
    .insight-body { color: #8892a4; font-size: 13px; margin-top: 4px; }
    h1 { color: #e8eaf6 !important; }
    h2 { color: #c5cae9 !important; }
    h3 { color: #9fa8da !important; }
    .stTabs [data-baseweb="tab"] { color: #8892a4; }
    .stTabs [aria-selected="true"] { color: #7986cb !important; }
    div[data-testid="metric-container"] { background: #1e2130; border-radius: 10px; padding: 14px; }
</style>
""", unsafe_allow_html=True)

# ─── 데이터 로드 ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("핀테크_테이터분석.xlsx", sheet_name="Sheet1")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["month_label"] = df["date"].dt.strftime("%Y-%m")
    # 파생 지표
    df["CTR"]          = df["광고클릭"] / df["광고노출"].replace(0, np.nan) * 100
    df["CPC"]          = df["광고비"]   / df["광고클릭"].replace(0, np.nan)
    df["install_rate"] = df["앱설치"]   / df["광고클릭"].replace(0, np.nan) * 100
    df["CVR_signup"]   = df["회원가입"] / df["앱설치"].replace(0, np.nan)   * 100
    df["CVR_account"]  = df["계좌개설"] / df["회원가입"].replace(0, np.nan) * 100
    df["CVR_trade"]    = df["첫거래"]   / df["계좌개설"].replace(0, np.nan) * 100
    df["CAC"]          = df["광고비"]   / df["회원가입"].replace(0, np.nan)
    df["CPA_account"]  = df["광고비"]   / df["계좌개설"].replace(0, np.nan)
    return df

df = load_data()

CHANNEL_COLORS = {"구글": "#4285F4", "페이스북": "#1877F2", "네이버검색": "#03C75A"}
MONTH_KOR = {1:"1월",2:"2월",3:"3월",4:"4월",5:"5월",6:"6월",
             7:"7월",8:"8월",9:"9월",10:"10월",11:"11월",12:"12월"}

# ─── 사이드바 필터 ──────────────────────────────────────────────────────────────
st.sidebar.header("필터")
sel_channels = st.sidebar.multiselect(
    "채널", options=["구글","페이스북","네이버검색"],
    default=["구글","페이스북","네이버검색"]
)
sel_months = st.sidebar.multiselect(
    "월", options=list(range(1, 13)),
    default=list(range(1, 13)),
    format_func=lambda x: MONTH_KOR[x]
)
sel_objectives = st.sidebar.multiselect(
    "캠페인 목적", options=df["campaign_objective"].unique().tolist(),
    default=df["campaign_objective"].unique().tolist()
)
sel_groups = st.sidebar.multiselect(
    "광고그룹", options=["논타겟","리타겟"], default=["논타겟","리타겟"]
)

fdf = df[
    df["channel"].isin(sel_channels) &
    df["month"].isin(sel_months) &
    df["campaign_objective"].isin(sel_objectives) &
    df["ad_group"].isin(sel_groups)
].copy()

# ─── 제목 ───────────────────────────────────────────────────────────────────────
st.title("📊 핀테크 마케팅 분석 대시보드")
st.caption("데이터 기간: 2025.01 ~ 2025.12  |  채널: 구글 · 페이스북 · 네이버검색")
st.divider()

# ─── 탭 구성 ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📌 KPI 개요",
    "📈 월별 추이",
    "📡 채널 분석",
    "🎯 캠페인·그룹·소재",
    "🔽 퍼널 분석",
    "💡 인사이트"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — KPI 개요
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("전체 KPI 요약")

    tot_spend    = fdf["광고비"].sum()
    tot_signup   = fdf["회원가입"].sum()
    tot_account  = fdf["계좌개설"].sum()
    tot_trade    = fdf["첫거래"].sum()
    tot_click    = fdf["광고클릭"].sum()
    tot_imp      = fdf["광고노출"].sum()
    tot_install  = fdf["앱설치"].sum()
    overall_cac  = tot_spend / tot_signup if tot_signup else 0
    overall_cpa  = tot_spend / tot_account if tot_account else 0
    overall_ctr  = tot_click / tot_imp * 100 if tot_imp else 0
    overall_cvr  = tot_signup / tot_install * 100 if tot_install else 0
    overall_cvr2 = tot_account / tot_signup * 100 if tot_signup else 0
    overall_cvr3 = tot_trade / tot_account * 100 if tot_account else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("총 광고비", f"₩{tot_spend/1e9:.2f}B")
        st.metric("총 회원가입", f"{tot_signup:,}명")
    with c2:
        st.metric("총 계좌개설", f"{tot_account:,}건")
        st.metric("총 첫거래", f"{tot_trade:,}건")
    with c3:
        st.metric("CAC (회원가입당 비용)", f"₩{overall_cac:,.0f}")
        st.metric("CPA (계좌개설당 비용)", f"₩{overall_cpa:,.0f}")
    with c4:
        st.metric("CTR", f"{overall_ctr:.2f}%")
        st.metric("CVR (회원가입/설치)", f"{overall_cvr:.1f}%")

    st.divider()
    st.subheader("채널별 KPI 비교")

    ch_summary = fdf.groupby("channel").agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"),
        광고노출=("광고노출","sum"), 앱설치=("앱설치","sum"),
        회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum")
    ).reset_index()
    ch_summary["CTR(%)"]       = (ch_summary["광고클릭"] / ch_summary["광고노출"] * 100).round(2)
    ch_summary["CAC(₩)"]       = (ch_summary["광고비"] / ch_summary["회원가입"]).round(0).astype(int)
    ch_summary["CPA계좌(₩)"]   = (ch_summary["광고비"] / ch_summary["계좌개설"]).round(0).astype(int)
    ch_summary["CVR가입(%)"]   = (ch_summary["회원가입"] / ch_summary["앱설치"] * 100).round(1)
    ch_summary["CVR계좌(%)"]   = (ch_summary["계좌개설"] / ch_summary["회원가입"] * 100).round(1)
    ch_summary["CVR첫거래(%)"] = (ch_summary["첫거래"] / ch_summary["계좌개설"] * 100).round(1)
    ch_summary["광고비(억)"]   = (ch_summary["광고비"] / 1e8).round(1)

    display_cols = ["channel","광고비(억)","회원가입","계좌개설","CTR(%)","CAC(₩)","CPA계좌(₩)","CVR가입(%)","CVR계좌(%)","CVR첫거래(%)"]
    st.dataframe(ch_summary[display_cols].rename(columns={"channel":"채널"}),
                 hide_index=True, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(ch_summary, x="channel", y="CAC(₩)",
                     color="channel", color_discrete_map=CHANNEL_COLORS,
                     title="채널별 CAC (회원가입당 비용, 낮을수록 효율적)",
                     text="CAC(₩)")
        fig.update_traces(texttemplate="₩%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="#0f1117",
                          paper_bgcolor="#0f1117", font_color="#e8eaf6",
                          yaxis_title="CAC (₩)")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig2 = px.bar(ch_summary, x="channel", y="광고비(억)",
                      color="channel", color_discrete_map=CHANNEL_COLORS,
                      title="채널별 광고비 집행액 (억원)",
                      text="광고비(억)")
        fig2.update_traces(texttemplate="%{text}억", textposition="outside")
        fig2.update_layout(showlegend=False, plot_bgcolor="#0f1117",
                           paper_bgcolor="#0f1117", font_color="#e8eaf6")
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — 월별 추이
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("월별 주요 지표 추이")

    monthly = fdf.groupby(["month","month_label","channel"]).agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"),
        광고노출=("광고노출","sum"), 앱설치=("앱설치","sum"),
        회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum")
    ).reset_index().sort_values("month")
    monthly["CAC"]         = monthly["광고비"] / monthly["회원가입"].replace(0,np.nan)
    monthly["CTR"]         = monthly["광고클릭"] / monthly["광고노출"].replace(0,np.nan) * 100
    monthly["CVR_signup"]  = monthly["회원가입"] / monthly["앱설치"].replace(0,np.nan) * 100
    monthly["CVR_account"] = monthly["계좌개설"] / monthly["회원가입"].replace(0,np.nan) * 100

    monthly_total = fdf.groupby(["month","month_label"]).agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"),
        계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum"),
        광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"), 앱설치=("앱설치","sum")
    ).reset_index().sort_values("month")
    monthly_total["CAC"]         = monthly_total["광고비"] / monthly_total["회원가입"].replace(0,np.nan)
    monthly_total["CTR"]         = monthly_total["광고클릭"] / monthly_total["광고노출"].replace(0,np.nan) * 100
    monthly_total["CVR_signup"]  = monthly_total["회원가입"] / monthly_total["앱설치"].replace(0,np.nan) * 100
    monthly_total["CVR_account"] = monthly_total["계좌개설"] / monthly_total["회원가입"].replace(0,np.nan) * 100

    metric_choice = st.selectbox(
        "지표 선택",
        ["CAC (회원가입당 비용)", "광고비", "회원가입", "계좌개설", "CTR (%)", "CVR_signup (%)", "CVR_account (%)"],
    )
    metric_map = {
        "CAC (회원가입당 비용)": "CAC",
        "광고비": "광고비",
        "회원가입": "회원가입",
        "계좌개설": "계좌개설",
        "CTR (%)": "CTR",
        "CVR_signup (%)": "CVR_signup",
        "CVR_account (%)": "CVR_account",
    }
    chosen = metric_map[metric_choice]

    fig = px.line(monthly, x="month_label", y=chosen, color="channel",
                  color_discrete_map=CHANNEL_COLORS,
                  markers=True,
                  title=f"월별 채널별 {metric_choice} 추이")
    fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                      font_color="#e8eaf6", xaxis_title="월", yaxis_title=metric_choice)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.bar(monthly_total, x="month_label", y="광고비",
                      title="월별 총 광고비 (원)",
                      color_discrete_sequence=["#5c6bc0"],
                      text_auto=False)
        fig2.update_traces(
            text=[f"₩{v/1e8:.1f}억" for v in monthly_total["광고비"]],
            textposition="outside"
        )
        fig2.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = px.line(monthly_total, x="month_label", y="CAC",
                       title="월별 전체 CAC 추이 (원)",
                       color_discrete_sequence=["#ff7043"], markers=True)
        fig3.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6")
        st.plotly_chart(fig3, use_container_width=True)

    st.info("💡 3월·9월·12월에 광고비가 급등하면서 CAC도 동반 상승합니다. 예산 확대가 효율 저하로 이어지는 패턴을 확인할 수 있습니다.")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — 채널 분석
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("채널별 심층 분석")

    ch_det = fdf.groupby("channel").agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"),
        광고노출=("광고노출","sum"), 앱설치=("앱설치","sum"),
        회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum")
    ).reset_index()
    for col in ["CTR","CVR_signup","CVR_account","CVR_trade"]:
        pass
    ch_det["CTR"]          = ch_det["광고클릭"] / ch_det["광고노출"] * 100
    ch_det["CVR_signup"]   = ch_det["회원가입"] / ch_det["앱설치"] * 100
    ch_det["CVR_account"]  = ch_det["계좌개설"] / ch_det["회원가입"] * 100
    ch_det["CVR_trade"]    = ch_det["첫거래"] / ch_det["계좌개설"] * 100
    ch_det["CAC"]          = ch_det["광고비"] / ch_det["회원가입"]
    ch_det["CPA_account"]  = ch_det["광고비"] / ch_det["계좌개설"]
    ch_det["광고비_비율"]   = ch_det["광고비"] / ch_det["광고비"].sum() * 100
    ch_det["회원가입_비율"] = ch_det["회원가입"] / ch_det["회원가입"].sum() * 100

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(ch_det, names="channel", values="광고비",
                     title="채널별 광고비 분배",
                     color="channel", color_discrete_map=CHANNEL_COLORS,
                     hole=0.4)
        fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                          font_color="#e8eaf6")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.pie(ch_det, names="channel", values="회원가입",
                      title="채널별 회원가입 기여",
                      color="channel", color_discrete_map=CHANNEL_COLORS,
                      hole=0.4)
        fig2.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("채널별 CVR 단계 비교")
    cvr_melt = ch_det[["channel","CVR_signup","CVR_account","CVR_trade"]].melt(
        id_vars="channel", var_name="단계", value_name="전환율(%)")
    cvr_melt["단계"] = cvr_melt["단계"].map({
        "CVR_signup":"앱설치→회원가입",
        "CVR_account":"회원가입→계좌개설",
        "CVR_trade":"계좌개설→첫거래"
    })
    fig3 = px.bar(cvr_melt, x="단계", y="전환율(%)", color="channel",
                  barmode="group", color_discrete_map=CHANNEL_COLORS,
                  title="채널별 단계별 전환율 비교")
    fig3.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                       font_color="#e8eaf6")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("채널 × 광고그룹 CAC 비교")
    ch_group = fdf.groupby(["channel","ad_group"]).agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum")
    ).reset_index()
    ch_group["CAC"] = ch_group["광고비"] / ch_group["회원가입"].replace(0,np.nan)
    fig4 = px.bar(ch_group, x="channel", y="CAC", color="ad_group",
                  barmode="group",
                  color_discrete_sequence=["#5c6bc0","#26d07c"],
                  title="채널 × 광고그룹별 CAC")
    fig4.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                       font_color="#e8eaf6")
    st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — 캠페인·그룹·소재
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("캠페인별 성과")

    camp = fdf.groupby(["channel","campaign_id","campaign_objective"]).agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"),
        계좌개설=("계좌개설","sum"), 첫거래=("첫거래","sum"),
        광고클릭=("광고클릭","sum"), 광고노출=("광고노출","sum"), 앱설치=("앱설치","sum")
    ).reset_index()
    camp["CAC"]          = camp["광고비"] / camp["회원가입"].replace(0,np.nan)
    camp["CVR_account"]  = camp["계좌개설"] / camp["회원가입"].replace(0,np.nan) * 100
    camp["CVR_trade"]    = camp["첫거래"] / camp["계좌개설"].replace(0,np.nan) * 100
    camp["CTR"]          = camp["광고클릭"] / camp["광고노출"].replace(0,np.nan) * 100
    camp["광고비(억)"]   = (camp["광고비"] / 1e8).round(2)

    top_n = st.slider("TOP N 캠페인", 5, 20, 10)
    sort_metric = st.selectbox("정렬 기준", ["CAC", "광고비", "회원가입", "CVR_account"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**효율 상위 캠페인 (CAC 낮은 순)**")
        top_camp = camp.sort_values("CAC").head(top_n)
        fig = px.bar(top_camp, x="CAC", y="campaign_id", orientation="h",
                     color="channel", color_discrete_map=CHANNEL_COLORS,
                     title=f"CAC 상위 {top_n} 캠페인 (낮을수록 효율적)")
        fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                          font_color="#e8eaf6", yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**비효율 하위 캠페인 (CAC 높은 순)**")
        bot_camp = camp.sort_values("CAC", ascending=False).head(top_n)
        fig2 = px.bar(bot_camp, x="CAC", y="campaign_id", orientation="h",
                      color="channel", color_discrete_map=CHANNEL_COLORS,
                      title=f"CAC 하위 {top_n} 캠페인 (높을수록 비효율)")
        fig2.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6", yaxis={"categoryorder":"total descending"})
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("소재 포맷별 성과")

    creative = fdf.groupby(["channel","creative_format"]).agg(
        광고비=("광고비","sum"), 광고클릭=("광고클릭","sum"),
        광고노출=("광고노출","sum"), 앱설치=("앱설치","sum"),
        회원가입=("회원가입","sum"), 계좌개설=("계좌개설","sum")
    ).reset_index()
    creative["CTR"]         = creative["광고클릭"] / creative["광고노출"] * 100
    creative["CAC"]         = creative["광고비"] / creative["회원가입"].replace(0,np.nan)
    creative["CVR_signup"]  = creative["회원가입"] / creative["앱설치"].replace(0,np.nan) * 100
    creative["CVR_account"] = creative["계좌개설"] / creative["회원가입"].replace(0,np.nan) * 100

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(creative, x="creative_format", y="CAC",
                      color="channel", barmode="group",
                      color_discrete_map=CHANNEL_COLORS,
                      title="소재 포맷 × 채널별 CAC")
        fig3.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6")
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        fig4 = px.bar(creative, x="creative_format", y="CTR",
                      color="channel", barmode="group",
                      color_discrete_map=CHANNEL_COLORS,
                      title="소재 포맷 × 채널별 CTR (%)")
        fig4.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6")
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.subheader("광고그룹별 성과")

    adgrp = fdf.groupby(["channel","ad_group"]).agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"),
        계좌개설=("계좌개설","sum"), 광고클릭=("광고클릭","sum"),
        광고노출=("광고노출","sum"), 앱설치=("앱설치","sum")
    ).reset_index()
    adgrp["CAC"]        = adgrp["광고비"] / adgrp["회원가입"].replace(0,np.nan)
    adgrp["CVR_signup"] = adgrp["회원가입"] / adgrp["앱설치"].replace(0,np.nan) * 100
    adgrp_total = fdf.groupby("ad_group").agg(
        광고비=("광고비","sum"), 회원가입=("회원가입","sum"),
        계좌개설=("계좌개설","sum"), 앱설치=("앱설치","sum")
    ).reset_index()
    adgrp_total["CAC"]       = adgrp_total["광고비"] / adgrp_total["회원가입"]
    adgrp_total["CVR_signup"]= adgrp_total["회원가입"] / adgrp_total["앱설치"] * 100

    col5, col6 = st.columns(2)
    with col5:
        fig5 = px.bar(adgrp_total, x="ad_group", y="CAC",
                      color="ad_group", color_discrete_sequence=["#5c6bc0","#26d07c"],
                      title="광고그룹별 전체 CAC", text="CAC")
        fig5.update_traces(texttemplate="₩%{text:,.0f}", textposition="outside")
        fig5.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6", showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)
    with col6:
        fig6 = px.scatter(adgrp, x="CAC", y="CVR_signup", color="channel",
                          size="광고비", symbol="ad_group",
                          color_discrete_map=CHANNEL_COLORS,
                          title="CAC vs CVR_signup (버블 = 광고비)")
        fig6.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                           font_color="#e8eaf6")
        st.plotly_chart(fig6, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — 퍼널 분석
# ════════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("전체 퍼널 전환율 분석")

    funnel_cols = ["광고노출","광고클릭","앱설치","앱실행","회원가입","계좌개설","첫거래","반복사용","자동이체설정","추천완료"]
    totals = fdf[funnel_cols].sum()

    rates = []
    for i in range(1, len(funnel_cols)):
        prev = totals.iloc[i-1]
        curr = totals.iloc[i]
        rates.append({
            "단계": f"{funnel_cols[i-1]} → {funnel_cols[i]}",
            "전환율(%)": round(curr/prev*100, 2) if prev else 0,
            "이탈율(%)": round((1-curr/prev)*100, 2) if prev else 0,
            "모수": int(prev),
            "전환수": int(curr),
        })
    rate_df = pd.DataFrame(rates)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_cols,
            x=[int(totals[c]) for c in funnel_cols],
            textinfo="value+percent previous",
            marker_color=["#5c6bc0","#7986cb","#9fa8da","#c5cae9",
                          "#26d07c","#43a047","#ffa726","#ef5350","#ab47bc","#7e57c2"],
        ))
        fig_funnel.update_layout(
            title="전체 퍼널 (전체 기간)",
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e8eaf6"
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col2:
        st.markdown("**단계별 전환율 & 이탈율**")
        colored_rates = rate_df.style.background_gradient(
            subset=["전환율(%)"], cmap="RdYlGn", vmin=0, vmax=100
        ).background_gradient(
            subset=["이탈율(%)"], cmap="RdYlGn_r", vmin=0, vmax=100
        )
        st.dataframe(rate_df, hide_index=True, use_container_width=True)
        st.warning("⚠️ 반복사용 → 자동이체설정 전환율 **21.9%** — 가장 큰 병목")
        st.warning("⚠️ 계좌개설 → 첫거래 전환율 **51.2%** — 두 번째 병목")

    st.divider()
    st.subheader("채널별 퍼널 비교")

    ch_funnel = fdf.groupby("channel")[funnel_cols].sum().reset_index()
    funnel_stage = st.selectbox(
        "비교할 퍼널 단계 선택",
        ["앱설치→회원가입 CVR", "회원가입→계좌개설 CVR", "계좌개설→첫거래 CVR"]
    )
    stage_map = {
        "앱설치→회원가입 CVR": ("앱설치","회원가입"),
        "회원가입→계좌개설 CVR": ("회원가입","계좌개설"),
        "계좌개설→첫거래 CVR": ("계좌개설","첫거래"),
    }
    num, denom = stage_map[funnel_stage]
    ch_funnel["선택CVR"] = ch_funnel[denom] / ch_funnel[num].replace(0,np.nan) * 100

    fig_ch = px.bar(ch_funnel, x="channel", y="선택CVR",
                    color="channel", color_discrete_map=CHANNEL_COLORS,
                    title=f"채널별 {funnel_stage}", text="선택CVR")
    fig_ch.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_ch.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                         font_color="#e8eaf6", showlegend=False, yaxis_range=[0,100])
    st.plotly_chart(fig_ch, use_container_width=True)

    st.info("💡 채널과 관계없이 CVR이 거의 동일합니다 (앱설치→회원가입 약 69.5%, 회원가입→계좌개설 약 76.9%).\n"
            "즉, 채널 광고 최적화보다 **앱 내 UX/온보딩 개선**이 전환율 향상에 더 직접적입니다.")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 6 — 인사이트 (메트릭 하이어라키)
# ════════════════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("💡 핵심 인사이트 & 메트릭 하이어라키")

    st.markdown("### 메트릭 하이어라키 — 비용 효율 진단")
    with st.expander("▶ CAC 분해 트리 보기", expanded=True):
        st.markdown("""
```
전체 CAC ₩1,595 (높음)
│
├─ 구글  CAC ₩900  ✅  (38.8% 비용, 41.1% 회원가입)
│   ├─ 영상 소재  CAC ₩862  ← 최고 효율
│   └─ 이미지 소재 CAC ₩949
│
├─ 페이스북  CAC ₩1,429  🟡  (43.0% 비용, 44.1% 회원가입)
│   ├─ 영상 소재  CAC ₩1,371
│   └─ 이미지 소재 CAC ₩1,506
│
└─ 네이버검색  CAC ₩3,280  🔴  (33.1% 비용, 14.8% 회원가입)
    ├─ 브랜드KW  CAC ₩2,978  ← 비용 대비 성과 저조
    └─ 일반KW   CAC ₩3,870  ← 전체 최악
```
        """)
        st.error("🔴 **핵심 문제**: 네이버검색이 전체 광고비의 33%를 소비하지만 회원가입 기여는 14.8%에 불과. CAC가 구글 대비 3.6배.")

    with st.expander("▶ 퍼널 병목 트리 보기"):
        st.markdown("""
```
광고노출 4.55B
  → 광고클릭 47M     CTR 1.03%
    → 앱설치 26.4M  설치율 56.2%
      → 앱실행 23.8M  실행율 90.0%  (약 10% 미실행 이탈)
        → 회원가입 18.4M  CVR 77.3%
          → 계좌개설 14.2M  CVR 76.9%
            → 첫거래 7.2M   CVR 51.2%  ⚠️ 병목 2
              → 반복사용 4.6M  CVR 63.7%
                → 자동이체설정 1.0M  CVR 21.9%  ⚠️ 최대 병목
                  → 추천완료 0.5M  CVR 50.0%
```
        """)

    st.divider()
    st.markdown("### 발견된 주요 인사이트 15개")

    insights = [
        ("danger", "1. 네이버검색 CAC 구글 대비 3.6배",
         "네이버검색 CAC ₩3,280 vs 구글 ₩900. 광고비 33% 투입 → 회원가입 기여 14.8% 불과. 예산 재배분 검토 필요."),
        ("danger", "2. 일반키워드 CAC ₩3,870 — 전체 최하위",
         "네이버 일반키워드의 CAC가 전체 소재 포맷 중 가장 높음. 즉각적인 입찰가 낮추기 또는 중단 검토."),
        ("warning", "3. 예산 급등 월(3·9·12월)에 CAC도 동반 상승",
         "3월 CAC ₩1,601, 9월 ₩1,664, 12월 ₩1,820으로 연간 최고 수준. 예산 증액이 효율 저하를 동반함 — 매체 경쟁 심화 시기 집행 전략 재검토."),
        ("danger", "4. 계좌개설 → 첫거래 전환율 51.2% — 두 번째 병목",
         "계좌를 개설한 사람의 절반 가까이가 첫 거래 없이 이탈. 온보딩 후 첫거래 유도 인앱 메시지/리마케팅 캠페인 필요."),
        ("danger", "5. 자동이체설정 전환율 21.9% — 최대 병목",
         "반복사용 고객 중 78.1%가 자동이체를 설정하지 않음. 자동이체 설정 유도 CRM 시퀀스 강화 필요."),
        ("success", "6. 구글 영상 소재 CAC ₩862 — 전체 최우수",
         "구글 영상 소재의 CAC가 전체에서 가장 낮음. 해당 소재 포맷 증량 및 유사 크리에이티브 확대 권장."),
        ("success", "7. 리타겟팅 CAC가 논타겟 대비 23% 낮음",
         "리타겟 CAC ₩1,336 vs 논타겟 ₩1,735. 리타겟팅 예산 비율 확대 검토."),
        ("warning", "8. 채널 관계없이 CVR(앱설치→회원가입)은 69.5%로 동일",
         "채널이 달라도 CVR이 동일하다는 것은 광고 소재/채널 최적화보다 앱 내 UX 개선이 더 큰 효과를 낼 수 있음을 시사."),
        ("warning", "9. 앱설치 → 앱실행 10% 이탈",
         "설치 후 미실행 이탈 10% 존재. 설치 직후 푸시 알림 또는 딥링크 온보딩 시퀀스로 실행 유도 필요."),
        ("danger", "10. 네이버검색 계좌개설 캠페인 CVR_account ≈ 99%",
         "회원가입 후 계좌개설 전환율이 비정상적으로 높음 — 데이터 품질 이슈(어트리뷰션 오류 또는 이중 집계) 의심, 실제 로그와 교차검증 필요."),
        ("success", "11. 영상 > 이미지 소재 전반적 CAC 우위",
         "전체 소재 포맷 중 영상(CAC ₩1,126)이 이미지(₩1,236) 대비 9% 낮음. 디스플레이 채널에서 영상 소재 비중 확대 권장."),
        ("warning", "12. 12월 CAC ₩1,820 — 연간 최고점",
         "연말 광고 경쟁 심화로 12월 CAC가 연간 최고. 1·7월 CAC ₩1,250~1,254로 최저. 비수기 집중 집행으로 CAC 최적화 가능."),
        ("success", "13. 페이스북 > 네이버검색 효율, 구글 최우수",
         "채널 효율 순위: 구글(₩900) > 페이스북(₩1,429) > 네이버검색(₩3,280). 예산 배분 재조정 시 구글 우선."),
        ("warning", "14. 추천완료 전환율 50% (자동이체설정자 대상)",
         "자동이체 설정자 중 50%가 추천을 완료함. 자동이체 설정률 개선 시 추천 바이럴 효과가 배가됨."),
        ("danger", "15. 전체 광고비 대비 하위 퍼널(반복사용 이후) 수치 급락",
         "첫거래 이후 반복사용(63.7%)은 양호하나, 자동이체설정(21.9%)이 급락. 제품 기능 노출 및 이점 전달 강화 필요."),
    ]

    for kind, title, body in insights:
        st.markdown(f"""
<div class="insight-card {kind}">
  <div class="insight-title">{title}</div>
  <div class="insight-body">{body}</div>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 우선순위별 액션 플랜")

    actions = pd.DataFrame({
        "우선순위": ["🔴 즉시","🔴 즉시","🔴 즉시","🟡 1개월","🟡 1개월","🟢 3개월"],
        "액션": [
            "네이버 일반KW 캠페인 예산 50% 삭감",
            "계좌개설 후 첫거래 유도 인앱 메시지 시퀀스 신설",
            "구글 영상 소재 예산 30% 증량",
            "자동이체설정 유도 CRM 캠페인 강화",
            "3·9·12월 예산 급등 기간 효율 임계 CAC 설정",
            "앱설치 → 앱실행 개선을 위한 딥링크 푸시 온보딩",
        ],
        "예상 임팩트": [
            "CAC ₩200~400 절감",
            "첫거래 CVR 10%p 향상 목표",
            "회원가입 +15% 동일 예산",
            "자동이체 CVR 5%p 향상",
            "계절성 CAC 편차 축소",
            "설치→실행 이탈 5%p 감소",
        ]
    })
    st.dataframe(actions, hide_index=True, use_container_width=True)
