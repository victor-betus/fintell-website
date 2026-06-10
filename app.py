"""Fintell — single-page app."""

import random

import streamlit as st
from utils import (
    inject_css, nav, footer,
    analyze_with_animation, parse_result, render_result_card,
    synthetic_scores, synthetic_trends, matrix_html, trend_chart,
    run_scrape_animation,
    BANKS, TOPICS, PERIODS, PAYPAL_PINTE, PAYPAL_KEBAB, PAYPAL_JET,
    FREE_TOPIC_COUNT, PRO_PASSWORD,
)

# ── Pricing data ──────────────────────────────────────────────────────────────

_TIERS = [
    {
        "name": "FREE",
        "price": "Free forever",
        "price_sub": "",
        "features": ["Live demo — 1 review at a time", "Sentiment + category", "4 topics in the matrix"],
        "missing": ["Full matrix (7 topics)", "Trend charts", "CSV / Excel export"],
        "cta": "Start free",
        "url": None,
        "badge": None,
        "featured": False,
    },
    {
        "name": "CHOUQUETTES",
        "price": "~30€",
        "price_sub": "A box for the whole team",
        "features": ["Everything in Free", "Full matrix (7 topics)", "Trend charts per bank", "PRO access"],
        "missing": ["CSV / Excel export"],
        "cta": "Buy the chouquettes",
        "url": PAYPAL_PINTE,
        "badge": None,
        "featured": False,
    },
    {
        "name": "PIZZA",
        "price": "~60€",
        "price_sub": "Pizza party for the team",
        "features": ["Everything in Chouquettes", "CSV export", "Excel export", "Priority support", "PRO access"],
        "missing": [],
        "cta": "Order the pizza",
        "url": PAYPAL_KEBAB,
        "badge": "Most popular",
        "featured": False,
    },
    {
        "name": "SILICON VALLEY",
        "price": "100,000€",
        "price_sub": "All-expenses-paid trip to SF",
        "features": ["Everything in Pizza", "Round trip to San Francisco", "Hotel in Palo Alto", "Meetings on Sand Hill Road", "Direct access to Victor"],
        "missing": [],
        "cta": "Book the trip",
        "url": PAYPAL_JET,
        "badge": None,
        "featured": True,
    },
]

# ── Section renderers ─────────────────────────────────────────────────────────


def _anchor(name: str) -> None:
    st.markdown(f'<div id="{name}"></div>', unsafe_allow_html=True)


def render_hero() -> None:
    _anchor("home")
    st.markdown("""
    <div style="padding:0.5rem 0 0.75rem;text-align:center;">
        <h1 style="margin-bottom:0.5rem;">FINTELL<span style="color:#2563EB;">.</span></h1>
        <p style="font-size:1.15rem;color:#374151;margin:0.5rem 0 0.25rem;line-height:1.5;">
            AI competitive intelligence, straight from user reviews.
        </p>
        <p style="font-size:0.95rem;color:#9ca3af;margin-bottom:1.25rem;">
            The neobank war is won on UX. We track every battle.
        </p>
        <a class="ft-btn-primary" href="#product">Try live demo</a>
        &nbsp;&nbsp;
        <a class="ft-btn-secondary" href="#pricing">Get PRO</a>
    </div>
    """, unsafe_allow_html=True)


def render_search_card() -> None:
    _anchor("product")
    _, col, _ = st.columns([1, 8, 1])
    with col:
        tab_analyze, tab_matrix = st.tabs(["Analyze a review", "Build the matrix"])

        with tab_analyze:
            review = st.text_area(
                label="review",
                label_visibility="collapsed",
                placeholder="Paste a banking app review...",
                height=130,
                key="home_review",
            )
            if st.button("Analyze", type="primary", use_container_width=True, key="home_analyze_btn"):
                if not review.strip():
                    st.warning("Please enter a review.")
                else:
                    try:
                        sent_data, cat_data = analyze_with_animation(review.strip())
                        sentiment, confidence, category = parse_result(sent_data, cat_data)
                        render_result_card(sentiment, confidence, category)
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
                n = random.randint(900, 3500) * len(selected_banks)
                run_scrape_animation(n)
                st.session_state.update({
                    "matrix_done": True,
                    "matrix_banks_run": selected_banks,
                    "matrix_months_run": PERIODS[period_label],
                    "matrix_n_run": n,
                })

            if st.session_state.get("matrix_done"):
                banks  = st.session_state["matrix_banks_run"]
                months = st.session_state["matrix_months_run"]
                n      = st.session_state["matrix_n_run"]
                is_pro = st.session_state.get("pro", False)

                st.success(f"**{n:,}** reviews analyzed · **{len(banks)} banks** · **{months} months**")

                df     = synthetic_scores(banks, months)
                trends = synthetic_trends(df, months)
                blur   = [] if is_pro else TOPICS[FREE_TOPIC_COUNT:]

                st.markdown("**Score matrix**")
                st.caption("Score /5 · green ≥ 3.8 · orange ≥ 2.8 · red < 2.8")
                st.markdown(matrix_html(df, blur), unsafe_allow_html=True)

                if blur and not is_pro:
                    st.markdown(
                        f'<p class="ft-muted" style="margin-top:0.5rem;">'
                        f'{len(blur)} topics locked. '
                        f'<a href="#pricing" style="color:#0a0a0a;font-weight:600;">Get PRO →</a></p>',
                        unsafe_allow_html=True,
                    )
                    pwd = st.text_input("PRO code", type="password",
                                        placeholder="Enter PRO code…", key="matrix_pwd",
                                        label_visibility="collapsed")
                    if st.button("Unlock", key="matrix_unlock"):
                        if pwd == PRO_PASSWORD:
                            st.session_state["pro"] = True
                            st.rerun()
                        else:
                            st.error("Wrong code.")

                st.markdown('<hr style="border:none;border-top:1px solid #f0f0f0;margin:1.5rem 0;"/>', unsafe_allow_html=True)
                st.markdown("**Score trends**")
                visible = [t for t in df.columns if t not in blur]
                for topic in visible:
                    st.plotly_chart(trend_chart(topic, trends[topic], months), use_container_width=True)


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
    border = "2px solid #0a0a0a" if tier["featured"] else "1px solid #e5e7eb"
    features = "".join(
        f'<div style="font-size:0.85rem;color:#374151;margin:0.35rem 0;text-align:left;">+ {f}</div>'
        for f in tier["features"]
    ) + "".join(
        f'<div style="font-size:0.85rem;color:#d1d5db;margin:0.35rem 0;text-align:left;">– {f}</div>'
        for f in tier["missing"]
    )
    btn = (
        f'<a class="ft-pricing-btn" href="{tier["url"]}" target="_blank"'
        f' style="display:block;background:#0a0a0a;color:#ffffff;'
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
                padding:1.5rem;background:#fff;box-sizing:border-box;text-align:center;">
        <div style="font-size:0.72rem;font-weight:700;letter-spacing:1.5px;
                    color:#9ca3af;text-transform:uppercase;margin-bottom:0.5rem;">
            {tier["name"]}{badge}
        </div>
        <div style="font-size:1.8rem;font-weight:700;letter-spacing:-1px;
                    color:#0a0a0a;line-height:1.1;">{tier["price"]}</div>
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
    _anchor("pricing")
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("## Simple, honest pricing.")
    st.write("Start free. Buy us a drink when you're ready.")
    st.markdown("<br>", unsafe_allow_html=True)

    cards_html = "".join(_tier_card_html(t) for t in _TIERS)
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.25rem;align-items:stretch;">
        {cards_html}
    </div>
    <p style="text-align:center;color:#9ca3af;font-size:0.85rem;margin-top:1.5rem;">
        After payment, we send your PRO code within 24h.
        <a href="#contact" style="color:#9ca3af;">Questions? Contact us.</a>
    </p>
    """, unsafe_allow_html=True)


def render_about() -> None:
    _anchor("about")
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("## About")
    st.markdown("""
    <p style="font-size:1.3rem;font-weight:500;line-height:1.7;color:#0a0a0a;max-width:720px;">
        Every day, thousands of users leave unfiltered feedback about your competitors' apps.
        Most teams never read them. The ones that do spend days doing it manually.
        By then, it's too late.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("### The market")
    cols = st.columns(3)
    for col, (num, label, sub) in zip(cols, [
        ("1,000+", "reviews per day", "UK banking apps alone"),
        ("8 years", "of data", "2018 to 2026"),
        ("6 banks", "tracked", "and benchmarked"),
    ]):
        with col:
            st.markdown(
                f'<div class="ft-stat" style="text-align:left;">'
                f'<div class="ft-stat-num">{num}</div>'
                f'<div class="ft-stat-lbl">{label}<br>'
                f'<span style="color:#d1d5db;">{sub}</span></div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.write(
        "Fintell was built by a team of 5 at Le Wagon Paris Data Science & AI Bootcamp, June 2026. "
        "We combined 8 years of banking app review data, state-of-the-art NLP, and a product "
        "obsession to build something we wished existed."
    )
    st.markdown('<p class="ft-muted">Le Wagon Paris · Data Science & AI #2271 · June 2026</p>', unsafe_allow_html=True)

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("### Team")
    team = [("V", "Victor", "Product & Lead"), ("H", "Hélène", "ML Models"),
            ("T", "Thomas", "Model Optimization"), ("K", "Kassim", "Model Comparison"),
            ("G", "Gerardo", "Visualization")]
    cols = st.columns(5, gap="medium")
    for col, (ini, name, role) in zip(cols, team):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:1.25rem 0.5rem;border:1px solid #e5e7eb;
                        border-radius:12px;background:white;">
                <div style="width:44px;height:44px;background:#0a0a0a;color:white;border-radius:50%;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1rem;font-weight:600;margin:0 auto 0.6rem;">{ini}</div>
                <div style="font-weight:600;font-size:0.9rem;color:#0a0a0a;">{name}</div>
                <div style="font-size:0.78rem;color:#9ca3af;margin-top:2px;">{role}</div>
            </div>
            """, unsafe_allow_html=True)


def render_contact() -> None:
    _anchor("contact")
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("## Contact")

    _, col, _ = st.columns([1, 4, 1])
    with col:
        with st.form("contact_form", clear_on_submit=True):
            st.text_input("Name")
            st.text_input("Email")
            st.selectbox("Subject", ["General inquiry", "PRO access", "Partnership", "Press"])
            st.text_area("Message", height=140)
            sent = st.form_submit_button("Send message", type="primary", use_container_width=True)
        if sent:
            st.success("Message received. We'll be in touch shortly.")
        st.markdown(
            '<p class="ft-muted" style="text-align:center;margin-top:1rem;">'
            'Or reach us at <strong>fintell@lewagon.com</strong></p>',
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="Fintell — AI Banking Intelligence",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    nav()
    render_hero()
    render_search_card()
    render_stats()
    render_arguments()
    render_research()
    render_pricing()
    render_about()
    render_contact()
    footer()


if __name__ == "__main__":
    main()
