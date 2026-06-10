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

    _, col, _ = st.columns([1, 4, 1])
    with col:
        st.markdown("## About")
        st.markdown(
            '<p style="font-size:1.1rem;color:#6b7280;line-height:1.7;max-width:640px;">'
            "Fintell turns 8 years of banking app reviews into competitive intelligence. "
            "Built by a team of 5 at Le Wagon Paris — Data Science &amp; AI Bootcamp, June 2026."
            "</p>",
            unsafe_allow_html=True,
        )

        st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)

        st.markdown("### Team")
        cols = st.columns(5, gap="medium")
        for col_item, (initials, name, role) in zip(cols, _TEAM):
            with col_item:
                st.markdown(_avatar(initials, name, role), unsafe_allow_html=True)

    footer()


if __name__ == "__main__":
    main()
