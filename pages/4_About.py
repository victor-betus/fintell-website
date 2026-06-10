"""Fintell — About page."""

import streamlit as st
from utils import inject_css, nav, footer


_TEAM = [
    ("V", "Victor",  "Product & Lead"),
    ("H", "Hélène",  "ML Models"),
    ("T", "Thomas",  "Model Optimization"),
    ("K", "Kassim",  "Model Comparison"),
    ("G", "Gerardo", "Visualization"),
]

_MARKET_STATS = [
    ("1,000+", "reviews per day",  "UK banking apps alone"),
    ("8 years", "of data",         "2018 to 2026"),
    ("6 banks", "tracked",         "and benchmarked"),
]


def _avatar(initials: str, name: str, role: str) -> str:
    return f"""
    <div style="text-align:center;padding:1.25rem 1rem;
                border:1px solid #e5e7eb;border-radius:12px;background:white;">
        <div style="width:48px;height:48px;background:#0a0a0a;color:white;
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    font-size:1.1rem;font-weight:600;margin:0 auto 0.75rem;">{initials}</div>
        <div style="font-weight:600;font-size:0.95rem;color:#0a0a0a;">{name}</div>
        <div style="font-size:0.8rem;color:#9ca3af;margin-top:2px;">{role}</div>
    </div>
    """


def main() -> None:
    st.set_page_config(
        page_title="Fintell — About",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    nav()

    st.markdown("## About")
    st.markdown("""
    <p style="font-size:1.3rem;font-weight:500;line-height:1.7;color:#0a0a0a;max-width:720px;">
        Every day, thousands of users leave unfiltered feedback about your competitors' apps.
        Most teams never read them. The ones that do spend days doing it manually.
        By then, it's too late.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)

    st.markdown("### The vision")
    st.write(
        "Fintell was built to give every product team the competitive intelligence "
        "that only the best-resourced teams used to have. Automated. Real-time. Actionable."
    )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)

    st.markdown("### The market")
    cols = st.columns(3)
    for col, (num, label, sub) in zip(cols, _MARKET_STATS):
        with col:
            st.markdown(
                f'<div class="ft-stat" style="text-align:left;">'
                f'<div class="ft-stat-num">{num}</div>'
                f'<div class="ft-stat-lbl">{label}<br>'
                f'<span style="color:#d1d5db;">{sub}</span></div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)

    st.markdown("### Built by")
    st.write(
        "Fintell was built by a team of 5 at Le Wagon Paris Data Science & AI Bootcamp, June 2026. "
        "We combined 8 years of banking app review data, state-of-the-art NLP, and a product "
        "obsession to build something we wished existed."
    )
    st.markdown(
        '<p class="ft-muted">Le Wagon Paris · Data Science & AI #2271 · June 2026</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)

    st.markdown("### Team")
    cols = st.columns(5, gap="medium")
    for col, (initials, name, role) in zip(cols, _TEAM):
        with col:
            st.markdown(_avatar(initials, name, role), unsafe_allow_html=True)

    footer()


if __name__ == "__main__":
    main()
