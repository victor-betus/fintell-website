"""Fintell — Product page."""

import random

import streamlit as st
from utils import (
    inject_css, nav, footer, check_pro_access,
    analyze_with_animation, parse_result, render_result_card,
    synthetic_scores, synthetic_trends, matrix_html, trend_chart,
    run_scrape_animation, df_to_csv, df_to_excel,
    BANKS, TOPICS, PERIODS, FREE_TOPIC_COUNT,
)


def render_live_demo() -> None:
    st.markdown("## Live demo")
    st.write(
        "Paste any real banking app review. "
        "Sentiment and topic classified in under 2 seconds."
    )
    review = st.text_area(
        label="review",
        label_visibility="collapsed",
        placeholder="Paste a banking app review here…",
        height=140,
        key="product_review",
    )
    if st.button("Analyze", type="primary", use_container_width=True, key="product_analyze_btn"):
        if not review.strip():
            st.warning("Please enter a review.")
        else:
            try:
                sent_data, cat_data = analyze_with_animation(review.strip())
                sentiment, confidence, category = parse_result(sent_data, cat_data)
                render_result_card(sentiment, confidence, category)
                st.markdown(
                    '<p class="ft-muted" style="margin-top:1rem;text-align:center;">'
                    'Want to analyze thousands of reviews? '
                    '<a href="https://paypal.me/victorbetus/30" target="_blank" '
                    'style="color:#0a0a0a;font-weight:600;">Get PRO →</a></p>',
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.error(f"API error: {exc}")


def render_pro_matrix() -> None:
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("## PRO Matrix  <span class='ft-pro-badge'>PRO</span>", unsafe_allow_html=True)

    is_pro = check_pro_access()

    if not is_pro:
        st.markdown("""
        <div class="ft-unlock">
            <p style="font-weight:600;margin-bottom:0.5rem;">Unlock the competitive matrix</p>
            <p class="ft-muted">Full 7-topic scoring across all banks, trend charts, and export.</p>
            <a class="ft-btn-primary" href="https://paypal.me/victorbetus/30"
               target="_blank" style="margin-top:1rem;display:inline-block;">
               Get PRO — from 30€ →
            </a>
        </div>
        """, unsafe_allow_html=True)
        return

    bank_cols = st.columns(len(BANKS))
    selected_banks: list[str] = []
    for i, bank in enumerate(BANKS):
        with bank_cols[i]:
            if st.checkbox(bank, value=(bank in ("Revolut", "Monzo")), key=f"prod_chk_{bank}"):
                selected_banks.append(bank)

    col_period, _ = st.columns([2, 4])
    with col_period:
        period_label: str = st.selectbox("Period", list(PERIODS.keys()), key="prod_period")
    period_months = PERIODS[period_label]

    if st.button(
        "Build matrix",
        type="primary",
        disabled=not selected_banks,
        use_container_width=True,
        key="prod_run_btn",
    ):
        n_reviews = random.randint(900, 3500) * len(selected_banks)
        run_scrape_animation(n_reviews)
        st.session_state["prod_matrix_done"] = True
        st.session_state["prod_banks"] = selected_banks
        st.session_state["prod_period_months"] = period_months
        st.session_state["prod_n_reviews"] = n_reviews

    if st.session_state.get("prod_matrix_done"):
        banks  = st.session_state["prod_banks"]
        months = st.session_state["prod_period_months"]
        n      = st.session_state["prod_n_reviews"]

        st.success(
            f"Analyzed **{months} months** for **{len(banks)} banks** — "
            f"**{n:,}** reviews processed."
        )
        df     = synthetic_scores(banks, months)
        trends = synthetic_trends(df, months)

        st.markdown("**Score matrix**")
        st.caption("Score out of 5 · green ≥ 3.8 · orange ≥ 2.8 · red < 2.8")
        st.markdown(matrix_html(df, []), unsafe_allow_html=True)

        st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
        st.markdown("**Score trends**")
        for topic in df.columns:
            st.plotly_chart(trend_chart(topic, trends[topic], months), use_container_width=True)

        _render_export(df, is_pro)


def _render_export(df, is_pro: bool) -> None:
    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)
    st.markdown("## Export  <span class='ft-pro-badge'>PRO</span>", unsafe_allow_html=True)
    st.dataframe(df.head(), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download CSV",
            df_to_csv(df),
            "fintell_matrix.csv",
            disabled=not is_pro,
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download Excel",
            df_to_excel(df),
            "fintell_matrix.xlsx",
            disabled=not is_pro,
            use_container_width=True,
        )
    if not is_pro:
        st.markdown(
            '<div class="ft-unlock" style="margin-top:1rem;">Export is PRO only. '
            '<a href="https://paypal.me/victorbetus/30" target="_blank" '
            'style="color:#0a0a0a;font-weight:600;">Unlock PRO — from 30€ →</a></div>',
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="Fintell — Product",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    nav()
    render_live_demo()
    render_pro_matrix()
    footer()


if __name__ == "__main__":
    main()
