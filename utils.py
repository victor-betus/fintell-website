"""Shared utilities: CSS, navigation, API helpers, data generators, rendering."""

import concurrent.futures
import io
import random
import time

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ── Constants ─────────────────────────────────────────────────────────────────

API_BASE = st.secrets.get("API_URL", "https://fintell-852162571474.europe-west1.run.app")

BANK_LOGOS = {
    "Revolut":  "https://logo.clearbit.com/revolut.com",
    "Monzo":    "https://logo.clearbit.com/monzo.com",
    "Barclays": "https://logo.clearbit.com/barclays.co.uk",
    "HSBC":     "https://logo.clearbit.com/hsbc.com",
    "Lloyds":   "https://logo.clearbit.com/lloydsbank.com",
    "Starling": "https://logo.clearbit.com/starlingbank.com",
}

BANKS = ["Revolut", "Monzo", "Barclays", "HSBC", "Lloyds", "Starling"]
TOPICS = [
    "App Experience",
    "Customer Service",
    "Fees & Pricing",
    "Security & Trust",
    "Onboarding",
    "Card & Limits",
    "Transfers",
]
PERIODS: dict[str, int] = {"3 months": 3, "6 months": 6, "1 year": 12}
PAYPAL_URL   = "https://paypal.me/victorbetus"
PAYPAL_PINTE = "https://paypal.me/victorbetus/30"
PAYPAL_KEBAB = "https://paypal.me/victorbetus/60"
PAYPAL_JET   = "https://paypal.me/victorbetus/1500"
PRO_PASSWORD     = "fintell2026"
FREE_TOPIC_COUNT = 4

_SCRAPE_STEPS = [
    (0.10, "Connecting to App Store & Google Play scrapers…"),
    (0.22, "Fetching reviews — Revolut, Monzo…"),
    (0.36, "Fetching reviews — Barclays, HSBC, Lloyds, Starling…"),
    (0.50, "Deduplicating & cleaning {n:,} raw reviews…"),
    (0.64, "Running Fintell NLP sentiment analysis…"),
    (0.78, "Classifying reviews by topic…"),
    (0.90, "Aggregating scores per bank × topic…"),
    (1.00, "Analysis complete."),
]

_ANALYSIS_STEPS = [
    (0.20, "Reading review content…"),
    (0.42, "Detecting language patterns…"),
    (0.63, "Running Fintell sentiment model…"),
    (0.83, "Classifying topic and intent…"),
]

_PALETTE = ["#2563EB", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]

# ── CSS & navigation ──────────────────────────────────────────────────────────


def inject_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }

    [data-testid="stSidebar"]       { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarNav"]    { display: none !important; }

    .block-container {
        padding-top: 0 !important;
        max-width: 100% !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse 600px 400px at 0% 0%,    rgba(147,112,219,0.12) 0%, transparent 70%),
            radial-gradient(ellipse 500px 350px at 100% 0%,  rgba(37,99,235,0.10)   0%, transparent 70%),
            radial-gradient(ellipse 400px 300px at 100% 100%, rgba(147,112,219,0.08) 0%, transparent 70%),
            #ffffff;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
    }
    [data-testid="block-container"] { background: transparent !important; }
    [data-testid="stMain"]          { background: transparent !important; }
    .block-container                 { background: transparent !important; }

    h1 { font-size: 3rem !important; font-weight: 600 !important; letter-spacing: -2px !important; line-height: 1.1 !important; color: #0a0a0a !important; }
    h2 { font-size: 1.6rem !important; font-weight: 600 !important; letter-spacing: -0.5px !important; color: #0a0a0a !important; }
    h3 { font-size: 1.1rem !important; font-weight: 500 !important; color: #0a0a0a !important; }
    p  { font-size: 1rem; color: #374151; line-height: 1.7; }

    /* ── Navigation ── */
    .ft-nav {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 0; border-bottom: 1px solid #f0f0f0; margin-bottom: 0.75rem;
        min-height: 64px;
    }
    .ft-logo     { font-size: 1.3rem; font-weight: 600; letter-spacing: -1px; color: #0a0a0a; }
    .ft-logo-dot { color: #2563EB; }
    .ft-nav-links { display: flex; gap: 2rem; }
    .ft-nav-link  { font-size: 0.9rem; color: #0a0a0a; text-decoration: none !important; }
    .ft-nav-link:hover { color: #6b7280; }

    /* ── Buttons ── */
    .ft-btn-primary {
        background: #0a0a0a; color: white !important; padding: 0.6rem 1.4rem;
        border-radius: 8px; font-size: 0.9rem; font-weight: 500;
        text-decoration: none !important; display: inline-block;
    }
    .ft-btn-secondary {
        background: white; color: #0a0a0a !important; padding: 0.6rem 1.4rem;
        border-radius: 8px; font-size: 0.9rem; font-weight: 500;
        border: 1px solid #e5e7eb; text-decoration: none !important; display: inline-block;
    }

    /* Streamlit primary button — fix black-on-black text */
    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"]:focus,
    .stButton > button[kind="primary"]:active {
        background-color: #0a0a0a !important; color: #ffffff !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; font-size: 15px !important; box-shadow: none !important;
    }
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] div { color: #ffffff !important; }
    .stButton > button[kind="primary"]:hover { background-color: #222222 !important; }

    /* ── Tabs — centered sliding pill ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #f0f0f0;
        padding: 4px;
        border-radius: 12px;
        gap: 0;
        border-bottom: none !important;
        width: fit-content;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 9px !important;
        padding: 0.35rem 1.2rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #9ca3af !important;
        border: none !important;
        transition: color 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0a0a0a !important;
        box-shadow: 0 1px 6px rgba(0,0,0,0.08) !important;
        transition: background 0.2s ease, color 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"]    { display: none !important; }

    /* ── Inputs ── */
    .stTextArea textarea {
        background: #ffffff !important; border: 1.5px solid #d1d5db !important;
        border-radius: 8px !important; font-size: 15px !important; color: #0a0a0a !important;
    }
    .stTextArea textarea:focus { border-color: #0a0a0a !important; box-shadow: none !important; }
    .stTextInput input {
        background: #ffffff !important; border: 1.5px solid #d1d5db !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus { border-color: #0a0a0a !important; box-shadow: none !important; }

    /* ── Cards & layout helpers ── */
    .ft-card { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem 2rem; }
    .ft-tag {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.8rem; background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; margin: 4px;
    }
    .ft-muted   { color: #9ca3af; font-size: 0.875rem; }
    .ft-divider { border: none; border-top: 1px solid #f0f0f0; margin: 3rem 0; }

    /* ── PRO gate ── */
    .ft-pro-badge {
        background: #0a0a0a; color: white; padding: 3px 10px;
        border-radius: 6px; font-size: 0.72rem; font-weight: 600;
        letter-spacing: 1px; vertical-align: middle; margin-left: 8px;
    }
    .ft-unlock {
        background: white; border-radius: 16px; padding: 2rem;
        text-align: center; border: 1px solid #e5e7eb; margin: 1rem auto; max-width: 440px;
    }

    /* ── Result card ── */
    .ft-result {
        border: 1px solid #e5e7eb; border-radius: 12px;
        padding: 1.5rem 2rem; background: #ffffff;
        display: flex; align-items: center; gap: 2rem; margin-top: 1rem;
    }
    .ft-result-pos { border-left: 4px solid #2563EB; }
    .ft-result-neg { border-left: 4px solid #ef4444; }
    .ft-result-left  { flex: 1; }
    .ft-result-right { flex-shrink: 0; }
    .ft-sentiment  { font-size: 1.8rem; font-weight: 700; letter-spacing: -1px; color: #0a0a0a; margin: 0 0 0.25rem; }
    .ft-confidence { font-size: 0.88rem; color: #6b7280; }
    .ft-cat-pill {
        display: inline-block; padding: 0.4rem 1rem; border-radius: 6px;
        background: #0a0a0a; color: #ffffff; font-size: 0.85rem; font-weight: 600;
    }

    /* ── Stats ── */
    .ft-stats    { display: flex; margin: 2rem 0; }
    .ft-stat     { flex: 1; text-align: center; }
    .ft-stat-num { font-size: 2rem; font-weight: 700; letter-spacing: -1px; color: #0a0a0a; }
    .ft-stat-lbl { font-size: 0.75rem; color: #9ca3af; margin-top: 0.2rem; line-height: 1.5; }

    /* ── Pricing CTA buttons ── */
    a.ft-pricing-btn,
    a.ft-pricing-btn:visited,
    a.ft-pricing-btn:hover,
    a.ft-pricing-btn:active {
        color: #ffffff !important;
        text-decoration: none !important;
    }

    /* ── Contact form submit button ── */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stFormSubmitButton"] > button p,
    [data-testid="stFormSubmitButton"] > button span {
        color: #ffffff !important;
    }

    /* ── Mobile ── */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        h1 { font-size: 2.2rem !important; }
        .ft-pricing-grid-inner { grid-template-columns: 1fr !important; }
        [data-testid="stColumns"] { flex-direction: column !important; }
        .ft-stats { flex-direction: column; gap: 1.5rem; }
        .ft-nav { padding: 0.75rem 0; }
    }

    /* ── Footer ── */
    .ft-footer {
        margin-top: 6rem; padding: 2rem 0; border-top: 1px solid #f0f0f0;
        display: flex; justify-content: space-between; align-items: center;
    }
    .ft-footer-logo { font-size: 1rem; font-weight: 600; letter-spacing: -0.5px; color: #0a0a0a; }
    .ft-footer-right { font-size: 0.8rem; color: #9ca3af; }
    .ft-footer-right a { color: #9ca3af; text-decoration: none; margin-left: 1rem; }
    .ft-footer-right a:hover { color: #374151; }
    </style>
    """, unsafe_allow_html=True)


def nav() -> None:
    st.markdown("""
    <div class="ft-nav">
        <span class="ft-logo">FINTELL<span class="ft-logo-dot">.</span></span>
        <a class="ft-btn-primary" href="#pricing">Get PRO</a>
    </div>
    """, unsafe_allow_html=True)


def footer() -> None:
    st.markdown("""
    <div class="ft-footer">
        <span class="ft-footer-logo">FINTELL<span style="color:#2563EB;">.</span></span>
        <div class="ft-footer-right">
            <a href="/Product">Product</a>
            <a href="/Research">Research</a>
            <a href="/Pricing">Pricing</a>
            <a href="/About">About</a>
            <a href="/Contact">Contact</a>
            <span style="margin-left:2rem;">Built at Le Wagon Paris · Data Science & AI #2271 · June 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def check_pro_access() -> bool:
    if st.session_state.get("pro"):
        return True
    with st.expander("Enter PRO access code"):
        pwd = st.text_input("Access code", type="password", key="pro_pwd_gate")
        if st.button("Unlock", key="unlock_btn_gate"):
            if pwd == PRO_PASSWORD:
                st.session_state["pro"] = True
                st.rerun()
            else:
                st.error("Invalid code.")
    return False


# ── API calls ─────────────────────────────────────────────────────────────────


def _fetch_sentiment(review: str) -> dict:
    resp = requests.get(
        f"{API_BASE}/predict_sentiment",
        params={"review": review},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def _fetch_category(review: str) -> dict:
    resp = requests.get(
        f"{API_BASE}/predict_category",
        params={"review": review},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def analyze_with_animation(review: str) -> tuple[dict, dict]:
    bar = st.progress(0, text="Starting Fintell AI…")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        f_sent = pool.submit(_fetch_sentiment, review)
        f_cat  = pool.submit(_fetch_category, review)
        for pct, msg in _ANALYSIS_STEPS:
            time.sleep(0.45)
            if f_sent.done() and f_cat.done():
                break
            bar.progress(pct, text=msg)
        sent = f_sent.result()
        cat  = f_cat.result()
    bar.progress(1.0, text="Analysis complete.")
    time.sleep(0.15)
    bar.empty()
    return sent, cat


def parse_result(sent_data: dict, cat_data: dict) -> tuple[str, float, str]:
    sentiment = (
        sent_data.get("sentiment") or sent_data.get("label")
        or sent_data.get("prediction") or "unknown"
    ).lower()
    raw_conf = (
        sent_data.get("confidence") or sent_data.get("score")
        or sent_data.get("probability") or 0
    )
    confidence = float(raw_conf) if float(raw_conf) <= 1 else float(raw_conf) / 100
    category = (
        cat_data.get("category") or cat_data.get("label")
        or cat_data.get("prediction") or "Unknown"
    )
    return sentiment, confidence, category


def render_result_card(sentiment: str, confidence: float, category: str) -> None:
    is_pos = sentiment == "positive"
    cls = "ft-result ft-result-pos" if is_pos else "ft-result ft-result-neg"
    st.markdown(f"""
    <div class="{cls}">
        <div class="ft-result-left">
            <div class="ft-sentiment">{sentiment.upper()}</div>
            <div class="ft-confidence">Confidence {confidence:.1%}</div>
        </div>
        <div class="ft-result-right">
            <span class="ft-cat-pill">{category}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Synthetic data ────────────────────────────────────────────────────────────


def synthetic_scores(banks: list[str], period_months: int) -> pd.DataFrame:
    rng = random.Random(sum(ord(c) for c in "".join(sorted(banks))) + period_months * 7)
    return pd.DataFrame(
        {topic: [round(rng.uniform(1.8, 4.9), 1) for _ in banks] for topic in TOPICS},
        index=banks,
    )


def synthetic_trends(df: pd.DataFrame, period_months: int) -> dict[str, dict[str, list[float]]]:
    rng = random.Random(42)
    trends: dict[str, dict[str, list[float]]] = {}
    for topic in df.columns:
        trends[topic] = {}
        for bank in df.index:
            base = df.loc[bank, topic]
            trends[topic][bank] = [
                round(max(1.0, min(5.0, base + rng.uniform(-0.5, 0.5))), 2)
                for _ in range(period_months)
            ]
    return trends


# ── Matrix rendering ──────────────────────────────────────────────────────────


def score_colors(score: float) -> tuple[str, str]:
    if score >= 3.8:
        return "#d1fae5", "#065f46"
    if score >= 2.8:
        return "#fef3c7", "#92400e"
    return "#fee2e2", "#991b1b"


def matrix_html(df: pd.DataFrame, blur_topics: list[str]) -> str:
    visible = [t for t in df.columns if t not in blur_topics]
    blurred = [t for t in df.columns if t in blur_topics]
    th = "padding:10px 14px;font-weight:600;color:#374151;white-space:nowrap;font-size:0.88rem;"
    out = [
        '<div style="overflow-x:auto;">',
        '<table style="width:100%;border-collapse:separate;border-spacing:4px 6px;font-size:0.88rem;">',
        "<thead><tr>",
        f'<th style="{th}text-align:left;">Bank</th>',
    ]
    for t in visible:
        out.append(f'<th style="{th}text-align:center;">{t}</th>')
    for t in blurred:
        out.append(
            f'<th style="{th}text-align:center;filter:blur(5px);'
            f'color:#9ca3af;user-select:none;">{t}</th>'
        )
    out.append("</tr></thead><tbody>")
    for bank in df.index:
        out.append("<tr>")
        out.append(f'<td style="{th}font-weight:600;color:#0a0a0a;">{bank}</td>')
        for t in visible:
            s = df.loc[bank, t]
            bg, fg = score_colors(s)
            out.append(
                f'<td style="background:{bg};color:{fg};font-weight:600;'
                f'text-align:center;padding:10px 14px;border-radius:8px;">{s:.1f}</td>'
            )
        for t in blurred:
            s = df.loc[bank, t]
            bg, fg = score_colors(s)
            out.append(
                f'<td style="background:{bg};color:{fg};font-weight:600;'
                f'text-align:center;padding:10px 14px;border-radius:8px;'
                f'filter:blur(7px);user-select:none;">{s:.1f}</td>'
            )
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def trend_chart(topic: str, bank_series: dict[str, list[float]], period_months: int) -> go.Figure:
    labels = [f"M-{period_months - i}" for i in range(period_months)]
    fig = go.Figure()
    for idx, (bank, series) in enumerate(bank_series.items()):
        fig.add_trace(go.Scatter(
            x=labels, y=series, mode="lines+markers", name=bank,
            line=dict(width=2.5, color=_PALETTE[idx % len(_PALETTE)]),
            marker=dict(size=5),
        ))
    fig.update_layout(
        title=dict(text=f"<b>{topic}</b>", font=dict(size=14, family="Inter")),
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=-0.28, font=dict(size=11)),
        yaxis=dict(range=[0, 5.5], title="Score /5", gridcolor="#f3f4f6"),
        xaxis=dict(gridcolor="#f3f4f6"),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def run_scrape_animation(n_reviews: int) -> None:
    bar = st.progress(0, text="Initializing…")
    for pct, msg in _SCRAPE_STEPS:
        time.sleep(0.55)
        bar.progress(pct, text=msg.format(n=n_reviews))
    time.sleep(0.25)
    bar.empty()


# ── Export helpers ────────────────────────────────────────────────────────────


def df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv().encode("utf-8")


def df_to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Fintell Matrix")
    return buf.getvalue()
