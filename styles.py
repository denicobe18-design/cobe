import streamlit as st


def apply_brutal_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --ink: #20251e;
                --muted: #777b72;
                --paper: #faf9f5;
                --green: #285b3b;
                --lime: #d9ef9b;
                --line: #e8e7df;
            }

            .stApp {
                background: var(--paper);
                color: var(--ink);
                font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                    BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

            [data-testid="stHeader"] { background: transparent; }
            #MainMenu, footer { visibility: hidden; }
            .block-container {
                max-width: 1240px;
                padding: 0.5rem 2.5rem 3rem;
            }
            a { color: inherit; text-decoration: none; }
            h1, h2, h3, p { color: var(--ink); }

            .announcement {
                margin: -0.5rem calc((100vw - min(100vw, 1240px)) / -2)
                    1.25rem;
                padding: 0.65rem 1rem;
                background: var(--green);
                color: #fff;
                text-align: center;
                font-size: 0.72rem;
                font-weight: 650;
                letter-spacing: 0.08em;
            }
            .announcement span { color: var(--lime); padding: 0 0.5rem; }
            .brand {
                color: var(--ink);
                font-size: 1.65rem;
                font-weight: 850;
                letter-spacing: -0.09em;
            }
            .brand span { color: #83a94e; }
            .main-nav {
                display: flex;
                justify-content: center;
                gap: clamp(1rem, 4vw, 3rem);
                font-size: 0.9rem;
                font-weight: 550;
            }
            .main-nav a:hover, .footer-contact a:hover { color: var(--green); }
            .cart-summary {
                display: flex;
                align-items: center;
                justify-content: flex-end;
                gap: 0.5rem;
                font-size: 0.9rem;
            }
            .cart-summary b {
                display: inline-grid;
                place-items: center;
                width: 1.55rem;
                height: 1.55rem;
                border-radius: 50%;
                background: var(--lime);
                font-size: 0.78rem;
            }

            .hero {
                position: relative;
                display: grid;
                grid-template-columns: 1.05fr 0.95fr;
                min-height: 440px;
                margin: 1.25rem 0 5.5rem;
                overflow: hidden;
                border-radius: 1.5rem;
                background: #e9eddf;
            }
            .hero-copy {
                z-index: 1;
                align-self: center;
                padding: clamp(2rem, 5vw, 4.5rem);
            }
            .eyebrow {
                color: var(--green);
                font-size: 0.72rem;
                font-weight: 750;
                letter-spacing: 0.14em;
            }
            .eyebrow span {
                display: inline-block;
                width: 0.55rem;
                height: 0.55rem;
                margin-right: 0.45rem;
                border-radius: 50%;
                background: #8eae5e;
            }
            .hero h1 {
                margin: 1.2rem 0 1rem;
                font-size: clamp(2.8rem, 5.1vw, 4.7rem);
                line-height: 0.99;
                letter-spacing: -0.075em;
                font-weight: 780;
            }
            .hero h1 em { color: var(--green); font-style: normal; }
            .hero-copy > p {
                max-width: 450px;
                margin: 0;
                color: #5f655a;
                font-size: 1.04rem;
                line-height: 1.75;
            }
            .hero-cta {
                display: inline-flex;
                align-items: center;
                gap: 1.1rem;
                margin-top: 1.6rem;
                padding: 0.85rem 1.2rem;
                border-radius: 0.5rem;
                background: var(--green);
                color: #fff !important;
                font-size: 0.9rem;
                font-weight: 650;
            }
            .hero-cta span { color: var(--lime); font-size: 1.2rem; }
            .hero-proof { margin-top: 1.5rem; color: #74796f; font-size: 0.8rem; }
            .hero-art {
                position: relative;
                display: grid;
                place-items: center;
                min-height: 360px;
                overflow: hidden;
                background: #dce5ce;
            }
            .hero-orbit {
                position: absolute;
                width: min(74%, 370px);
                aspect-ratio: 1;
                border: 1px solid rgba(40, 91, 59, 0.2);
                border-radius: 50%;
            }
            .orbit-two { width: min(58%, 290px); }
            .hero-product {
                z-index: 1;
                display: grid;
                place-items: center;
                width: clamp(160px, 22vw, 270px);
                aspect-ratio: 1;
                border-radius: 50%;
                background: linear-gradient(145deg, #f7f5ed, #d4d7cb);
                box-shadow: 0 32px 60px rgba(55, 68, 49, 0.16);
                font-size: clamp(5rem, 10vw, 8.5rem);
                transform: rotate(-9deg);
            }
            .hero-sticker {
                position: absolute;
                top: 15%;
                right: 13%;
                display: grid;
                place-content: center;
                width: 76px;
                height: 76px;
                border-radius: 50%;
                background: var(--lime);
                color: var(--green);
                font-size: 0.66rem;
                font-weight: 850;
                line-height: 1.15;
                text-align: center;
                transform: rotate(10deg);
            }
            .hero-note {
                position: absolute;
                right: 8%;
                bottom: 12%;
                color: var(--green);
                font-size: 0.85rem;
                font-weight: 650;
                line-height: 1.45;
                transform: rotate(-5deg);
            }

            .section-heading {
                display: flex;
                align-items: end;
                justify-content: space-between;
                gap: 1rem;
                margin: 0 0 1.5rem;
            }
            .section-heading h2, .benefits h2 {
                margin: 0.5rem 0 0;
                font-size: clamp(1.8rem, 3.3vw, 2.7rem);
                letter-spacing: -0.06em;
                line-height: 1.1;
            }
            .section-heading h2 span, .benefits h2 span { color: #83a94e; }
            .section-aside { color: var(--muted); font-size: 0.85rem; }
            [data-testid="stTextInput"] input,
            [data-testid="stSelectbox"] [data-baseweb="select"] > div {
                min-height: 46px;
                border: 1px solid var(--line);
                border-radius: 0.55rem;
                background: #fff;
                color: var(--ink);
            }
            [data-testid="stTextInput"] input:focus {
                border-color: #799b5b;
                box-shadow: 0 0 0 1px #799b5b;
            }
            .result-count {
                margin: 0.35rem 0 1rem;
                color: var(--muted);
                font-size: 0.8rem;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                margin-bottom: 1.1rem;
                border: 1px solid var(--line) !important;
                border-radius: 0.85rem !important;
                background: #fff;
                box-shadow: 0 5px 20px rgba(40, 44, 34, 0.035);
                overflow: hidden;
            }
            [data-testid="stVerticalBlockBorderWrapper"] > div {
                gap: 0.35rem;
                padding: 0.8rem 0.85rem 1rem;
            }
            .product-visual {
                position: relative;
                display: grid;
                place-items: center;
                height: 210px;
                margin: -0.8rem -0.85rem 0.65rem;
                overflow: hidden;
            }
            .product-visual::before {
                position: absolute;
                width: 150px;
                height: 150px;
                border: 1px solid rgba(32, 37, 30, 0.1);
                border-radius: 50%;
                content: "";
            }
            .product-visual::after {
                position: absolute;
                width: 112px;
                height: 112px;
                border: 1px solid rgba(32, 37, 30, 0.09);
                border-radius: 50%;
                content: "";
            }
            .product-visual.lavender { background: #eeebf5; }
            .product-visual.mint { background: #e4eee4; }
            .product-visual.peach { background: #f5e9dc; }
            .product-visual.blue { background: #e4edf0; }
            .product-visual.sand { background: #efeee7; }
            .product-visual.rose { background: #f1e5e4; }
            .product-emoji {
                z-index: 1;
                display: grid;
                place-items: center;
                width: 112px;
                height: 112px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.66);
                box-shadow: 0 13px 32px rgba(42, 49, 38, 0.1);
                font-size: 4.2rem;
                transform: rotate(-8deg);
            }
            .product-badge {
                position: absolute;
                z-index: 2;
                top: 14px;
                left: 14px;
                padding: 0.35rem 0.55rem;
                border-radius: 99px;
                background: rgba(255, 255, 255, 0.82);
                color: var(--green);
                font-size: 0.61rem;
                font-weight: 750;
                letter-spacing: 0.04em;
            }
            .visual-sparkle {
                position: absolute;
                right: 16%;
                bottom: 15%;
                color: rgba(40, 91, 59, 0.35);
                font-size: 1.3rem;
            }
            .product-category {
                margin-top: 0.2rem;
                color: var(--muted);
                font-size: 0.72rem;
            }
            .product-name {
                margin-top: 0.1rem;
                color: var(--ink);
                font-size: 1.12rem;
                font-weight: 700;
                letter-spacing: -0.025em;
            }
            .product-description {
                min-height: 48px;
                margin-top: 0.25rem;
                color: #696e65;
                font-size: 0.79rem;
                line-height: 1.55;
            }
            .product-rating {
                margin-top: 0.35rem;
                color: #cf9a3a;
                font-size: 0.8rem;
                letter-spacing: 0.06em;
            }
            .product-rating span {
                margin-left: 0.3rem;
                color: var(--muted);
                letter-spacing: 0;
            }
            .product-prices {
                display: flex;
                align-items: baseline;
                gap: 0.55rem;
                margin: 0.15rem 0 0.5rem;
            }
            .current-price {
                color: var(--ink);
                font-size: 1.25rem;
                font-weight: 750;
            }
            .old-price {
                color: #9a9d96;
                font-size: 0.8rem;
                text-decoration: line-through;
            }
            .stButton > button {
                min-height: 42px;
                border: 1px solid var(--green);
                border-radius: 0.5rem;
                background: var(--green);
                color: #fff;
                font-size: 0.83rem;
                font-weight: 650;
                transition: background 120ms ease, transform 120ms ease;
            }
            .stButton > button:hover {
                border-color: #1d472d;
                background: #1d472d;
                color: #fff;
                transform: translateY(-1px);
            }
            .stButton > button:focus:not(:active) {
                border-color: var(--green);
                color: #fff;
            }

            [data-testid="stExpander"] {
                margin: 0 0 3rem;
                border: 1px solid var(--line);
                border-radius: 0.8rem;
                background: #fff;
            }
            [data-testid="stExpander"] summary { color: var(--ink); font-weight: 650; }
            .empty-cart {
                padding: 1rem 0;
                color: var(--muted);
                line-height: 1.6;
            }
            .muted { color: var(--muted); font-size: 0.8rem; }
            .quantity {
                padding-top: 0.55rem;
                text-align: center;
                font-weight: 650;
            }
            [data-testid="stForm"] {
                padding: 1rem;
                border: 1px solid var(--line);
                border-radius: 0.75rem;
                background: #fafaf7;
            }
            [data-testid="stForm"] h3 {
                margin-top: 0;
                font-size: 1.05rem;
            }
            [data-testid="stAlert"] {
                border-radius: 0.65rem;
            }

            .benefits {
                margin-top: 5rem;
                padding: 3rem clamp(1.5rem, 4vw, 3.5rem);
                border-radius: 1.25rem;
                background: #eff1e9;
            }
            .benefits h2 { margin-bottom: 2rem; }
            .benefit-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 2rem;
            }
            .benefit-grid > div { display: flex; flex-direction: column; }
            .benefit-grid span {
                margin-bottom: 1rem;
                color: #88a66b;
                font-size: 0.75rem;
                font-weight: 750;
            }
            .benefit-grid b { font-size: 1rem; }
            .benefit-grid p {
                margin: 0.45rem 0 0;
                color: #6d7269;
                font-size: 0.83rem;
                line-height: 1.6;
            }
            .store-footer {
                display: grid;
                grid-template-columns: 1fr 1fr auto;
                align-items: end;
                gap: 2rem;
                margin-top: 3rem;
                padding: 1.5rem 0 0.5rem;
                border-top: 1px solid var(--line);
            }
            .footer-brand { font-size: 1.35rem; }
            .store-footer p, .footer-contact, .footer-small {
                color: var(--muted);
                font-size: 0.8rem;
                line-height: 1.7;
            }
            .store-footer p { margin: 0.25rem 0 0; }
            .footer-contact b { color: var(--ink); }
            .footer-contact a { color: var(--green); }
            .footer-small { text-align: right; }

            @media (max-width: 760px) {
                .block-container { padding: 0.5rem 1rem 2rem; }
                .announcement { font-size: 0.61rem; }
                .main-nav { display: none; }
                .hero {
                    grid-template-columns: 1fr;
                    margin-bottom: 3.5rem;
                }
                .hero-copy { padding: 2rem 1.5rem 1rem; }
                .hero-art { min-height: 270px; }
                .section-heading { align-items: start; flex-direction: column; }
                .section-aside { font-size: 0.78rem; }
                .product-visual { height: 175px; }
                .product-emoji { width: 95px; height: 95px; font-size: 3.5rem; }
                .benefit-grid { grid-template-columns: 1fr; gap: 1.5rem; }
                .store-footer { grid-template-columns: 1fr; gap: 1rem; }
                .footer-small { text-align: left; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
