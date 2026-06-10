"""Fintell — Research page."""

import streamlit as st
from utils import inject_css, nav, footer


_STACK = [
    ("Classical ML",       "TF-IDF + LinearSVC. Fast, interpretable, production baseline."),
    ("Deep Learning",      "Word2Vec embeddings + BiGRU. Captures sequential context and domain-specific semantics."),
    ("Transformer-ready",  "Architecture designed to integrate transformer models. We know where the ceiling is."),
]

_REFS = [
    ("Pang & Lee (2002)",                     "Thumbs Up? Sentiment Classification using Machine Learning"),
    ("Guzman & Maalej (2014)",                "Fine-Grained Sentiment Analysis of App Reviews"),
    ("Systematic Literature Review (2022)",   "Opinion Mining for Software Development"),
]

_METRICS = [
    ("87%",  "validation accuracy"),
    ("0.80", "F1-macro score"),
    ("181K", "training reviews"),
]


def main() -> None:
    st.set_page_config(
        page_title="Fintell — Research",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    nav()

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
    for col, (title, desc) in zip(cols, _STACK):
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
    for col, (num, label) in zip(cols, _METRICS):
        with col:
            st.markdown(
                f'<div class="ft-stat" style="text-align:left;">'
                f'<div class="ft-stat-num">{num}</div>'
                f'<div class="ft-stat-lbl">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)

    st.markdown("### Academic references")
    for author, title in _REFS:
        st.markdown(
            f'<p style="margin:0.5rem 0;"><span style="font-weight:600;">{author}</span>'
            f' <span class="ft-muted">— {title}</span></p>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="ft-divider"/>', unsafe_allow_html=True)

    st.markdown("### What we don't share")
    st.write(
        "The exact architecture, hyperparameters, and training recipe are proprietary. "
        "What we can say: we tested every major approach, measured everything rigorously, "
        "and found what works specifically for the banking domain."
    )

    footer()


if __name__ == "__main__":
    main()
