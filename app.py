"""Fintell — single-page app."""

import random
import threading

import streamlit as st
from utils import (
    inject_css, nav, footer, _logo_b64,
    analyze_with_animation, parse_result, render_result_card, log_review_to_sheet,
    real_scores, real_trends, matrix_html, trend_chart,
    run_scrape_animation, translate_to_english,
    BANKS, TOPICS, PERIODS, PAYPAL_CHOUQUETTES, PAYPAL_DYSON, PAYPAL_SF, API_BASE,
    FREE_TOPIC_COUNT, PRO_PASSWORD,
)

# ── Pricing data ──────────────────────────────────────────────────────────────

_TIERS = [
    {
        "name": "🧀 MICE IN LEARNING",
        "price": "2€",
        "price_sub": "A piece of cheese",
        "features": ["Live demo — 1 review at a time", "Sentiment + category", "4 topics in the matrix"],
        "missing": ["Full matrix (7 topics)", "Trend charts", "CSV / Excel export"],
        "cta": "Feed the rat",
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHYycW1vcDl6aXd5NXR3MWJtbnd2b3I2bnpqdWh3aTRld3prbzY1ciZlcD12MV9naWZzX3NlYXJjaCZjdD1n/JyF7YMCmCZqxoN3sb7/giphy.gif",
        "badge": None,
        "featured": False,
    },
    {
        "name": "🍰 CHOUQUETTES",
        "price": "~30€",
        "price_sub": "A box for the whole team",
        "features": ["Everything in Mice in Learning", "Full matrix (7 topics)", "Trend charts per bank", "PRO access"],
        "missing": ["CSV / Excel export"],
        "cta": "Buy the chouquettes",
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3g2OXVmdGp6NmNzMTAxazM4eWN2MGk3dGcxaGYxazd3dHI5NHdoaiZlcD12MV9naWZzX3JlbGF0ZWQmY3Q9Zw/1Z02vuppxP1Pa/giphy.gif",
        "badge": None,
        "featured": False,
    },
    {
        "name": "🌀 DYSON",
        "price": "349,99€",
        "price_sub": "A fan for each desk",
        "features": ["Everything in Chouquettes", "CSV export", "Excel export", "Priority support", "PRO access"],
        "missing": [],
        "cta": "Cool down the team",
        "url": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWk5eHY4b2VuZGQ4d2U3ZnI1bzVvNjNtaXA4ZzJuMTUyYml0MDBqbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ToMjGppLes0ENI5osCc/giphy.gif",
        "badge": "Most popular",
        "featured": False,
    },
    {
        "name": "✈️ SILICON VALLEY",
        "price": "100 000€",
        "price_sub": "Pay our trip to SF, we go launch the business",
        "features": ["Everything in Dyson", "Round trip to San Francisco", "Hotel in Palo Alto", "Meetings on Sand Hill Road", "You fund us, we build the future"],
        "missing": [],
        "cta": "Pay for our trip",
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnpnMXZ5Nm1oZTJ3dHM5MGdud2t3aG11cXZjNmowYnE4NHpmaWs3eCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lOadmkNRWkO3jITOpe/giphy.gif",
        "badge": None,
        "featured": True,
    },
]

# ── Section renderers ─────────────────────────────────────────────────────────


def _anchor(name: str) -> None:
    st.markdown(f'<div id="{name}"></div>', unsafe_allow_html=True)


def render_hero() -> None:
    _anchor("home")
    st.markdown(f"""
    <div style="padding:0.5rem 0 0.75rem;text-align:center;">
        <img src="data:image/png;base64,{_logo_b64()}" style="height:72px;width:auto;margin-bottom:0.25rem;" />
        <p style="font-size:1.15rem;color:#374151;margin:0.25rem 0 0.15rem;line-height:1.5;">
            AI competitive intelligence,<br class="ft-mobile-br" /> straight from user reviews.
        </p>
        <p style="font-size:0.95rem;color:#9ca3af;margin-bottom:1.25rem;">
            Turn thousands of customer reviews<br class="ft-mobile-br" /> into strategic decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_search_card() -> None:
    _anchor("product")
    _, col, _ = st.columns([1, 8, 1])
    with col:
        tab_analyze, tab_matrix = st.tabs(["Analyze a review", "Competitive Matrix"])

        with tab_analyze:
            _, inner, _ = st.columns([1, 3, 1])
            with inner:
                st.markdown('<p style="text-align:center;font-size:0.72rem;color:#9ca3af;margin:0 0 0.25rem;">✏️ Example review · feel free to edit or replace it.</p>', unsafe_allow_html=True)
                review = st.text_area(
                    label="review",
                    label_visibility="collapsed",
                    placeholder="e.g. The app is great overall but customer support takes forever to respond.",
                    value="Great app, support fixed my issue in 10 min. Highly recommend! 😉",
                    height=130,
                    key="home_review",
                )
                if st.button("Analyze", type="primary", use_container_width=True, key="home_analyze_btn"):
                    if not review.strip():
                        st.warning("Please enter a review.")
                    else:
                        try:
                            review_en = translate_to_english(review.strip())
                            if review_en != review.strip():
                                st.caption("Translated to English for analysis.")
                            sent_data, cat_data = analyze_with_animation(review_en)
                            sentiment, confidence, category, cat_confidence = parse_result(sent_data, cat_data)
                            render_result_card(sentiment, confidence, category, cat_confidence)
                            log_review_to_sheet(review_en, review.strip(), sentiment, confidence, category)
                        except Exception as exc:
                            st.error(f"API error: {exc}")

        with tab_matrix:
            selected_banks: list[str] = st.pills(
                "Banks",
                BANKS,
                selection_mode="multi",
                default=["Revolut", "Monzo"],
                key="matrix_banks",
                label_visibility="collapsed",
            ) or []

            period_label: str = st.pills(
                "Period",
                list(PERIODS.keys()),
                selection_mode="single",
                default="3 months",
                key="matrix_period",
                label_visibility="collapsed",
            ) or "3 months"

            if st.button(
                "Build matrix",
                type="primary",
                use_container_width=True,
                disabled=not selected_banks,
                key="matrix_run_btn",
            ):
                months_val = PERIODS[period_label]
                n = random.randint(900, 3500) * len(selected_banks)
                run_scrape_animation(n)
                df_run = real_scores(selected_banks, months_val)
                trends_run, labels_run = real_trends(df_run, months_val)
                st.session_state.update({
                    "matrix_done": True,
                    "matrix_banks_run": selected_banks,
                    "matrix_months_run": months_val,
                    "matrix_n_run": n,
                    "matrix_df": df_run,
                    "matrix_trends": trends_run,
                    "matrix_labels": labels_run,
                })

            if st.session_state.get("matrix_done"):
                banks        = st.session_state["matrix_banks_run"]
                months       = st.session_state["matrix_months_run"]
                n            = st.session_state["matrix_n_run"]
                df           = st.session_state["matrix_df"]
                trends       = st.session_state["matrix_trends"]
                trend_labels = st.session_state["matrix_labels"]
                is_pro       = st.session_state.get("pro", False)

                st.success(f"**{n:,}** reviews scraped & analyzed · **{len(banks)} banks** · **{months} months**")

                st.markdown("**Score matrix**")
                st.caption("Score /10 · green ≥ 7.5 · orange ≥ 5.5 · red < 5.5")
                st.markdown(matrix_html(df, []), unsafe_allow_html=True)

                st.markdown('<hr style="border:none;border-top:1px solid #f0f0f0;margin:1.5rem 0;"/>', unsafe_allow_html=True)
                st.markdown("**Score trends**")
                preview_topic = "Support & Access"
                st.plotly_chart(trend_chart(preview_topic, trends[preview_topic], months, trend_labels), use_container_width=True)

                st.markdown("""
                <div style="border:1px solid #e5e7eb;border-radius:12px;padding:1.5rem 2rem;
                            background:#fafafa;text-align:center;margin-top:0.5rem;">
                    <div style="font-weight:600;font-size:1rem;color:#0a0a0a;margin-bottom:0.4rem;">
                        Get full access
                    </div>
                    <div style="font-size:0.88rem;color:#6b7280;margin-bottom:1rem;">
                        All years of data · All 7 topics · Trend charts · CSV &amp; Excel export
                    </div>
                    <a href="#pricing" style="background:#0a0a0a;color:#fff;padding:0.55rem 1.5rem;
                       border-radius:8px;text-decoration:none;font-weight:600;font-size:0.88rem;">
                       See pricing →
                    </a>
                </div>
                """, unsafe_allow_html=True)


def render_stats() -> None:
    st.markdown("""
    <hr class="ft-divider"/>
    <div class="ft-stats">
        <div class="ft-stat"><div class="ft-stat-num">181,000</div><div class="ft-stat-lbl">reviews<br>analyzed</div></div>
        <div class="ft-stat"><div class="ft-stat-num">6</div><div class="ft-stat-lbl">banks<br>tracked</div></div>
        <div class="ft-stat"><div class="ft-stat-num">99.4%</div><div class="ft-stat-lbl">model<br>accuracy</div></div>
    </div>
    <hr class="ft-divider"/>
    """, unsafe_allow_html=True)


def render_arguments() -> None:
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown('<p class="ft-muted">Product Managers</p>', unsafe_allow_html=True)
        st.markdown("### Stop reading reviews manually")
        st.write("1,000+ new reviews per day. Fintell reads them all, classifies by sentiment and topic, surfaces what matters. Voice of customer at scale.")
    with col2:
        st.markdown('<p class="ft-muted">UX & Design</p>', unsafe_allow_html=True)
        st.markdown("### Speak your users' language")
        st.write("Extract the exact words real users use. Build your copy, flows, research from real voice of customer data. Competitive UX benchmarking in 30 seconds.")
    with col3:
        st.markdown('<p class="ft-muted">Strategy & C-suite</p>', unsafe_allow_html=True)
        st.markdown("### Know when a competitor is bleeding")
        st.write("Track sentiment trends across all major neobanks. Know which competitor is losing ground on crashes, fees, or support — before they announce it.")


def render_research() -> None:
    _anchor("research")
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("## Research")
    st.markdown("### Our approach")
    st.write(
        "Fintell is not a wrapper around a generic sentiment API. We built a custom NLP "
        "pipeline trained specifically on banking app reviews — a domain with unique "
        "language, specific pain points, and distinct user behavior patterns."
    )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("### Stack")
    cols = st.columns(3, gap="large")
    stack = [
        ("Classical ML", "TF-IDF + LinearSVC. Fast, interpretable, production baseline."),
        ("Deep Learning", "Word2Vec + BiGRU. Sequential context, domain semantics."),
        ("Transformer-ready", "Architecture ready for transformer integration."),
    ]
    for col, (title, desc) in zip(cols, stack):
        with col:
            st.markdown(
                f'<div class="ft-card"><p style="font-weight:600;margin-bottom:0.5rem;">'
                f'{title}</p><p style="font-size:0.9rem;">{desc}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:1.3rem;font-weight:500;line-height:1.7;color:#0a0a0a;max-width:720px;">
        "Banking app reviews are not like Amazon reviews. Users write about trust, money, and anxiety.
        Generic models fail here. We trained on 181K labeled reviews across 6 UK banks over 8 years."
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("### Performance")
    cols = st.columns(3)
    metrics = [("87%", "validation accuracy"), ("0.80", "F1-macro score"), ("181K", "training reviews")]
    for col, (num, label) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="ft-stat" style="text-align:left;">'
                f'<div class="ft-stat-num">{num}</div>'
                f'<div class="ft-stat-lbl">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("### Academic references")
    refs = [
        ("Pang & Lee (2002)", "Thumbs Up? Sentiment Classification using Machine Learning"),
        ("Guzman & Maalej (2014)", "Fine-Grained Sentiment Analysis of App Reviews"),
        ("Systematic Literature Review (2022)", "Opinion Mining for Software Development"),
    ]
    for author, title in refs:
        st.markdown(
            f'<p style="margin:0.5rem 0;"><span style="font-weight:600;">{author}</span>'
            f' <span class="ft-muted">— {title}</span></p>',
            unsafe_allow_html=True,
        )


def _tier_card_html(tier: dict) -> str:
    badge = (
        f'<span style="display:inline-block;background:#0a0a0a;color:#fff;'
        f'font-size:0.65rem;font-weight:700;letter-spacing:1px;padding:2px 8px;'
        f'border-radius:4px;margin-left:6px;text-transform:uppercase;">{tier["badge"]}</span>'
        if tier["badge"] else ""
    )
    border = "2px solid transparent" if tier["featured"] else "1px solid #e5e7eb"
    outline = 'background: linear-gradient(white,white) padding-box, linear-gradient(135deg,#2563EB,#7c3aed) border-box;' if tier["featured"] else ""
    price_color = "background:linear-gradient(135deg,#2563EB,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;" if tier["featured"] else "color:#0a0a0a;"
    btn_style = "background:linear-gradient(135deg,#2563EB,#7c3aed);" if tier["featured"] else "background:#0a0a0a;"
    features = "".join(
        f'<div style="font-size:0.85rem;color:#374151;margin:0.35rem 0;text-align:left;">+ {f}</div>'
        for f in tier["features"]
    ) + "".join(
        f'<div style="font-size:0.85rem;color:#d1d5db;margin:0.35rem 0;text-align:left;">– {f}</div>'
        for f in tier["missing"]
    )
    btn = (
        f'<a class="ft-pricing-btn" href="{tier["url"]}" target="_blank"'
        f' style="display:block;{btn_style}color:#ffffff;'
        f'text-align:center;padding:0.6rem 1rem;border-radius:8px;'
        f'text-decoration:none;font-weight:600;font-size:0.88rem;">'
        f'{tier["cta"]}</a>'
        if tier["url"] else
        f'<div style="background:#f3f4f6;color:#9ca3af;text-align:center;'
        f'padding:0.6rem 1rem;border-radius:8px;font-weight:600;font-size:0.88rem;">'
        f'{tier["cta"]}</div>'
    )
    return f"""
    <div style="display:flex;flex-direction:column;border:{border};border-radius:12px;
                padding:1.5rem;background:#fff;box-sizing:border-box;text-align:center;{outline}">
        <div style="font-size:0.72rem;font-weight:700;letter-spacing:1.5px;
                    color:#9ca3af;text-transform:uppercase;margin-bottom:0.5rem;">
            {tier["name"]}{badge}
        </div>
        <div style="font-size:1.8rem;font-weight:700;letter-spacing:-1px;
                    line-height:1.1;{price_color}">{tier["price"]}</div>
        <div style="font-size:0.78rem;color:#9ca3af;margin-bottom:1rem;min-height:1.2rem;">
            {tier["price_sub"] or "&nbsp;"}
        </div>
        <div style="border-top:1px solid #f3f4f6;padding-top:1rem;flex:1;">
            {features}
        </div>
        <div style="margin-top:1.25rem;">{btn}</div>
    </div>
    """


def render_pricing() -> None:
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    _anchor("pricing")
    st.markdown("## Simple, honest pricing.")
    st.write("Start free. Buy us a fan, some chouquettes, or a trip to SF when you're ready.")
    st.markdown("<br>", unsafe_allow_html=True)

    cards_html = "".join(_tier_card_html(t) for t in _TIERS)
    st.markdown(f"""
    <style>
    .ft-pricing-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1.25rem; align-items:stretch; }}
    @media(max-width:900px) {{ .ft-pricing-grid {{ grid-template-columns:repeat(2,1fr); }} }}
    @media(max-width:500px) {{ .ft-pricing-grid {{ grid-template-columns:1fr; }} }}
    </style>
    <div class="ft-pricing-grid">
        {cards_html}
    </div>
    <p style="text-align:center;color:#9ca3af;font-size:0.85rem;margin-top:1.5rem;">
        After payment, we send your PRO code within 24h.
    </p>
    """, unsafe_allow_html=True)


_TEAM = [
    ("Victor",  "Sith Lord du Produit · Packager de l'Empire · ML/DL",          "https://github.com/victor-betus",  "https://avatars.githubusercontent.com/u/260678422?v=4"),
    ("Hélène",  "Pâtissière du ML · Exploratrice de Modèles · Reine du Streamlit", "https://github.com/LeleneTian",     "https://avatars.githubusercontent.com/u/275649394?v=4"),
    ("Thomas",  "Hantavirus Engineer · Patient 0 · Créateur de Clusters · Architecte API",   "https://github.com/Elyokle",        "https://avatars.githubusercontent.com/u/272031024?v=4"),
    ("Kassim",  "Sensei Guru des Endpoints · Maître Incontesté de l'API",        "https://github.com/ksa2003",        "https://avatars.githubusercontent.com/u/188040760?v=4"),
    ("Gerardo", "Félin du ML · Seigneur GCS · Dompteur de BiGRU · MLOps Master", "https://github.com/LordGER2024",    "https://avatars.githubusercontent.com/u/179365933?v=4"),
]


def render_about() -> None:
    _anchor("about")
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("## About")
    st.markdown(
        '<p style="font-size:1.05rem;color:#6b7280;line-height:1.7;">'
        "Fintell was built as a final project at <strong>Le Wagon Paris, Data Science &amp; AI Bootcamp #2271</strong>, June 2026. "
        "We trained a custom NLP pipeline on 181K banking app reviews across 6 UK neobanks, "
        "and turned it into a competitive intelligence tool for product teams. "
        "Every team member benchmarked and compared models end-to-end."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("""
    <style>
    [data-testid="stMarkdown"]:has(#ft-team-marker) + [data-testid="stHorizontalBlock"] { align-items: stretch !important; }
    [data-testid="stMarkdown"]:has(#ft-team-marker) + [data-testid="stHorizontalBlock"] [data-testid="stColumn"] { display: flex !important; flex-direction: column !important; }
    [data-testid="stMarkdown"]:has(#ft-team-marker) + [data-testid="stHorizontalBlock"] [data-testid="stVerticalBlock"] { flex: 1 !important; display: flex !important; flex-direction: column !important; }
    [data-testid="stMarkdown"]:has(#ft-team-marker) + [data-testid="stHorizontalBlock"] [data-testid="stMarkdown"] { flex: 1 !important; display: flex !important; flex-direction: column !important; }
    [data-testid="stMarkdown"]:has(#ft-team-marker) + [data-testid="stHorizontalBlock"] [data-testid="stMarkdown"] > div { flex: 1 !important; display: flex !important; flex-direction: column !important; }
    [data-testid="stMarkdown"]:has(#ft-team-marker) + [data-testid="stHorizontalBlock"] .ft-team-card { flex: 1 !important; }
    </style>
    <div id="ft-team-marker"></div>
    """, unsafe_allow_html=True)
    cols = st.columns(5, gap="medium")
    for col, (name, role, github_url, avatar_url) in zip(cols, _TEAM):
        with col:
            st.markdown(f"""
            <a href="{github_url}" target="_blank" style="text-decoration:none;">
            <div class="ft-team-card" style="display:flex;flex-direction:column;align-items:center;
                        text-align:center;padding:1.25rem 0.5rem;min-height:210px;
                        border:1px solid #e5e7eb;border-radius:12px;background:white;
                        transition:border-color 0.2s;"
                 onmouseover="this.style.borderColor='#9ca3af'"
                 onmouseout="this.style.borderColor='#e5e7eb'">
                <img src="{avatar_url}" style="width:48px;height:48px;border-radius:50%;
                     object-fit:cover;margin:0 auto 0.6rem;display:block;" />
                <div style="font-weight:600;font-size:0.9rem;color:#0a0a0a;">{name}</div>
                <div style="font-size:0.78rem;color:#9ca3af;margin-top:2px;flex:1;">{role}</div>
                <div style="font-size:0.72rem;color:#2563EB;margin-top:6px;">GitHub ↗</div>
            </div>
            </a>
            """, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="Fintell — AI Banking Intelligence",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    nav()
    if not st.session_state.get("api_warmed"):
        threading.Thread(
            target=lambda: __import__("requests").get(
                f"{API_BASE}/predict_sentiment", params={"review": "ok"}, timeout=30
            ),
            daemon=True,
        ).start()
        st.session_state["api_warmed"] = True
    render_hero()
    render_search_card()
    render_about()
    render_pricing()
    footer()


if __name__ == "__main__":
    main()
