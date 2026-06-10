"""Fintell — Contact page."""

import streamlit as st
from utils import inject_css, nav, footer

_SUBJECTS = ["General inquiry", "PRO access", "Partnership", "Press"]


def main() -> None:
    st.set_page_config(
        page_title="Fintell — Contact",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    nav()

    _, col, _ = st.columns([1, 4, 1])
    with col:
        st.markdown("## Contact")

        with st.form("contact_form", clear_on_submit=True):
            st.text_input("Name")
            st.text_input("Email")
            st.selectbox("Subject", _SUBJECTS)
            st.text_area("Message", height=160)
            sent = st.form_submit_button("Send message", type="primary", use_container_width=True)

        if sent:
            st.success("Message received. We'll be in touch shortly.")

        st.markdown(
            '<p class="ft-muted" style="text-align:center;margin-top:1.5rem;">'
            'Or reach us at <strong>fintell@lewagon.com</strong></p>',
            unsafe_allow_html=True,
        )

    footer()


if __name__ == "__main__":
    main()
