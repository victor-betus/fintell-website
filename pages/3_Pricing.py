"""Fintell — Pricing page."""

import streamlit as st
from utils import inject_css, nav, footer, PAYPAL_PINTE, PAYPAL_KEBAB, PAYPAL_JET

_TIERS = [
    {
        "name": "FREE",
        "price": "Free forever",
        "price_sub": "",
        "features": [
            "Live demo — 1 review at a time",
            "Sentiment + category",
            "4 topics in the matrix",
        ],
        "missing": [
            "Full matrix (7 topics)",
            "Trend charts",
            "CSV / Excel export",
            "PRO access",
        ],
        "cta_label": "Start free",
        "cta_url": None,
        "badge": None,
        "featured": False,
    },
    {
        "name": "LA PINTE",
        "price": "~30€",
        "price_sub": "The price of a round for the team",
        "features": [
            "Everything in Free",
            "Full matrix (7 topics)",
            "Trend charts per bank",
            "PRO access (password)",
        ],
        "missing": [
            "CSV / Excel export",
        ],
        "cta_label": "Buy the round",
        "cta_url": PAYPAL_PINTE,
        "badge": None,
        "featured": False,
    },
    {
        "name": "LE KEBAB",
        "price": "~60€",
        "price_sub": "Kebabs for the whole team",
        "features": [
            "Everything in La Pinte",
            "CSV export",
            "Excel export",
            "Priority support",
            "PRO access (password)",
        ],
        "missing": [],
        "cta_label": "Feed the team",
        "cta_url": PAYPAL_KEBAB,
        "badge": "Most popular",
        "featured": False,
    },
    {
        "name": "FINTELL JET",
        "price": "1 500€",
        "price_sub": "5× GCP credit or one jet charter",
        "features": [
            "Everything in Le Kebab",
            "Fuel for 5 data scientists",
            "GCP credit that actually matters",
            "We integrate on your infra",
            "Weekly strategy call",
            "Direct access to Victor",
        ],
        "missing": [],
        "cta_label": "Book the jet",
        "cta_url": PAYPAL_JET,
        "badge": None,
        "featured": True,
    },
]


def _tier_card(tier: dict) -> str:
    border = "border: 2px solid #0a0a0a;" if tier["featured"] else "border: 1px solid #e5e7eb;"
    badge_html = ""
    if tier["badge"]:
        badge_html = (
            f'<span style="display:inline-block;background:#0a0a0a;color:#fff;'
            f'font-size:0.65rem;font-weight:700;letter-spacing:1px;padding:3px 8px;'
            f'border-radius:4px;margin-left:8px;text-transform:uppercase;">'
            f'{tier["badge"]}</span>'
        )

    rows = "".join(
        f'<div style="font-size:0.88rem;color:#374151;margin:0.4rem 0;">+ {f}</div>'
        for f in tier["features"]
    ) + "".join(
        f'<div style="font-size:0.88rem;color:#d1d5db;margin:0.4rem 0;">– {f}</div>'
        for f in tier["missing"]
    )

    if tier["cta_url"]:
        btn = (
            f'<a href="{tier["cta_url"]}" target="_blank"'
            f' style="display:block;margin-top:1.5rem;background:#0a0a0a;color:#fff;'
            f'text-align:center;padding:0.65rem 1rem;border-radius:8px;'
            f'text-decoration:none;font-weight:600;font-size:0.9rem;">'
            f'{tier["cta_label"]}</a>'
        )
    else:
        btn = (
            f'<div style="margin-top:1.5rem;background:#f3f4f6;color:#6b7280;'
            f'text-align:center;padding:0.65rem 1rem;border-radius:8px;'
            f'font-weight:600;font-size:0.9rem;">{tier["cta_label"]}</div>'
        )

    return f"""
    <div style="{border}border-radius:12px;padding:1.75rem 1.5rem;
                background:#ffffff;height:100%;box-sizing:border-box;">
        <div style="font-size:0.75rem;font-weight:700;letter-spacing:1.5px;
                    color:#9ca3af;text-transform:uppercase;margin-bottom:0.5rem;">
            {tier["name"]}{badge_html}
        </div>
        <div style="font-size:2rem;font-weight:700;letter-spacing:-1.5px;
                    color:#0a0a0a;line-height:1.1;">{tier["price"]}</div>
        <div style="font-size:0.8rem;color:#9ca3af;margin-bottom:1.25rem;">
            {tier["price_sub"] or "&nbsp;"}
        </div>
        <div style="border-top:1px solid #f3f4f6;padding-top:1rem;">
            {rows}
        </div>
        {btn}
    </div>
    """


def main() -> None:
    st.set_page_config(
        page_title="Fintell — Pricing",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    nav()

    st.markdown("## Simple, honest pricing.")
    st.write("Start free. Buy us a drink when you're ready.")
    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns(4, gap="medium")
    for col, tier in zip(cols, _TIERS):
        with col:
            st.markdown(_tier_card(tier), unsafe_allow_html=True)

    st.markdown(
        '<p style="text-align:center;color:#9ca3af;font-size:0.85rem;margin-top:2rem;">'
        'After payment, we send your PRO code within 24h. '
        '<a href="/Contact" style="color:#9ca3af;">Questions? Contact us.</a></p>',
        unsafe_allow_html=True,
    )

    footer()


if __name__ == "__main__":
    main()
