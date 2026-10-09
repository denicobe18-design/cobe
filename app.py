from typing import Any

import streamlit as st

from ui.styles import apply_brutal_styles

st.set_page_config(
    page_title="Luma Living | Oprema za svaki dan",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_brutal_styles()

PRODUCTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Aero Buds Pro",
        "category": "Audio",
        "price": 129.0,
        "old_price": 179.0,
        "rating": 4.9,
        "badge": "NOVO",
        "emoji": "🎧",
        "tone": "lavender",
        "description": "Bežične slušalice s aktivnim poništavanjem buke i baterijom do 30 sati.",
    },
    {
        "id": 2,
        "name": "Luma Smart Watch",
        "category": "Pametni dodaci",
        "price": 199.0,
        "old_price": 249.0,
        "rating": 4.8,
        "badge": "HIT",
        "emoji": "⌚",
        "tone": "mint",
        "description": "Prati san, puls i treninge uz elegantan dizajn za svaki dan.",
    },
    {
        "id": 3,
        "name": "Volt Power Bank",
        "category": "Dodaci",
        "price": 59.0,
        "old_price": 89.0,
        "rating": 4.7,
        "badge": "BESTSELLER",
        "emoji": "🔋",
        "tone": "peach",
        "description": "Kompaktna prijenosna baterija od 20.000 mAh s brzim punjenjem.",
    },
    {
        "id": 4,
        "name": "Nova Mini projektor",
        "category": "Dom",
        "price": 349.0,
        "old_price": 429.0,
        "rating": 4.9,
        "badge": "OMILJENO",
        "emoji": "📽️",
        "tone": "blue",
        "description": "Pretvori dnevni boravak u kino uz sliku do 120 inča.",
    },
    {
        "id": 5,
        "name": "Flex stalak za laptop",
        "category": "Radni prostor",
        "price": 79.0,
        "old_price": 109.0,
        "rating": 4.6,
        "badge": "PAMETAN IZBOR",
        "emoji": "💻",
        "tone": "sand",
        "description": "Podesivi aluminijski stalak za udobniji rad i uredniji stol.",
    },
    {
        "id": 6,
        "name": "Hush slušalice",
        "category": "Audio",
        "price": 149.0,
        "old_price": 199.0,
        "rating": 4.9,
        "badge": "TOP OCJENA",
        "emoji": "🎵",
        "tone": "rose",
        "description": "Udobne naglavne slušalice koje pomažu da se fokusiraš na ono važno.",
    },
]

def get_cart() -> dict[str, int]:
    cart = st.session_state.get("cart")
    if not isinstance(cart, dict):
        cart = {}
        st.session_state["cart"] = cart
    return cart


def update_cart(product_id: int, change: int) -> None:
    cart = get_cart().copy()
    key = str(product_id)
    quantity = cart.get(key, 0) + change
    if quantity > 0:
        cart[key] = quantity
    else:
        cart.pop(key, None)
    st.session_state["cart"] = cart


def get_cart_items() -> list[dict[str, Any]]:
    cart = get_cart()
    return [
        {**product, "quantity": cart[str(product["id"])]}
        for product in PRODUCTS
        if cart.get(str(product["id"]), 0) > 0
    ]


def format_price(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def render_header() -> None:
    st.markdown(
        "<div class='announcement'>DEMO TRGOVINA <span>✦</span> "
        "Proizvodi i cijene su ogledni · kupnja i plaćanje nisu aktivni.</div>",
        unsafe_allow_html=True,
    )
    brand_col, nav_col, cart_col = st.columns([1.2, 2.2, 1], vertical_alignment="center")
    with brand_col:
        st.markdown(
            "<a class='brand' href='#top'>luma living<span>.</span></a>",
            unsafe_allow_html=True,
        )
    with nav_col:
        st.markdown(
            "<nav class='main-nav'><a href='#katalog'>Proizvodi</a>"
            "<a href='#prednosti'>Zašto mi</a><a href='#kontakt'>Kontakt</a></nav>",
            unsafe_allow_html=True,
        )
    with cart_col:
        item_count = sum(get_cart().values())
        st.markdown(
            f"<div class='cart-summary'>🛍️ <span>Košarica</span> "
            f"<b>{item_count}</b></div>",
            unsafe_allow_html=True,
        )


def render_hero() -> None:
    st.markdown(
        """
        <section id="top" class="hero">
            <div class="hero-copy">
                <div class="eyebrow"><span></span> DOBRE STVARI ZA SVAKI DAN</div>
                <h1>Mali upgrade.<br><em>Velika razlika.</em></h1>
                <p>Pažljivo odabrani gadgeti koji ti olakšaju dan, uljepšaju prostor
                i izmame ono: „Ovo mi je baš trebalo.”</p>
                <a class="hero-cta" href="#katalog">Istraži ponudu <span>↘</span></a>
                <div class="hero-proof">✦ Dobra oprema, bez kompliciranja</div>
            </div>
            <div class="hero-art">
                <div class="hero-orbit orbit-one"></div>
                <div class="hero-orbit orbit-two"></div>
                <div class="hero-product">🎧</div>
                <div class="hero-sticker">DOBAR<br>ODABIR</div>
                <div class="hero-note">sitnice koje<br>čine razliku ↗</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_cart() -> None:
    items = get_cart_items()
    count = sum(item["quantity"] for item in items)
    with st.expander(f"🛍️  Tvoja košarica · {count} artikala", expanded=False):
        if not items:
            st.markdown(
                "<div class='empty-cart'>Košarica je zasad prazna. "
                "Pronađi nešto što ti se sviđa u katalogu. ♡</div>",
                unsafe_allow_html=True,
            )
            return

        subtotal = 0.0
        for item in items:
            line_total = item["price"] * item["quantity"]
            subtotal += line_total
            name_col, qty_col, price_col = st.columns([3, 2, 1])
            with name_col:
                st.markdown(
                    f"**{item['emoji']} {item['name']}**  \n"
                    f"<span class='muted'>{format_price(item['price'])} / kom</span>",
                    unsafe_allow_html=True,
                )
            with qty_col:
                minus_col, number_col, plus_col = st.columns([1, 1, 1])
                with minus_col:
                    st.button(
                        "−",
                        key=f"minus_{item['id']}",
                        on_click=update_cart,
                        args=(item["id"], -1),
                    )
                with number_col:
                    st.markdown(
                        f"<div class='quantity'>{item['quantity']}</div>",
                        unsafe_allow_html=True,
                    )
                with plus_col:
                    st.button(
                        "+",
                        key=f"plus_{item['id']}",
                        on_click=update_cart,
                        args=(item["id"], 1),
                    )
            with price_col:
                st.markdown(f"**{format_price(line_total)}**")

        st.markdown("---")
        summary_col, amount_col = st.columns([3, 1])
        with summary_col:
            st.markdown("Ogledni međuzbroj")
        with amount_col:
            st.markdown(f"**{format_price(subtotal)}**")
        st.info(
            "Ovo je javni demo: cijene i proizvodi su ogledni, dostava nije "
            "izračunata, a kupnja i plaćanje nisu omogućeni. Nemoj unositi "
            "osobne ili platne podatke."
        )


def render_catalog() -> None:
    st.markdown(
        "<div id='katalog' class='section-heading'>"
        "<div><div class='eyebrow'>MALI IZBOR, DOBRE STVARI</div>"
        "<h2>Pronađi svog favorita<span>.</span></h2></div>"
        "<div class='section-aside'>Odabrano s razlogom. Namijenjeno svakodnevici.</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    controls = st.columns([2, 1])
    with controls[0]:
        query = st.text_input(
            "Pretraži katalog",
            placeholder="🔎  Što tražiš?",
            label_visibility="collapsed",
        ).strip().casefold()
    with controls[1]:
        categories = ["Sve kategorije", *sorted({item["category"] for item in PRODUCTS})]
        category = st.selectbox(
            "Kategorija",
            categories,
            label_visibility="collapsed",
        )

    filtered_products = [
        product
        for product in PRODUCTS
        if (category == "Sve kategorije" or product["category"] == category)
        and (
            not query
            or query in product["name"].casefold()
            or query in product["description"].casefold()
            or query in product["category"].casefold()
        )
    ]
    st.markdown(
        f"<div class='result-count'>{len(filtered_products)} proizvoda za otkriti</div>",
        unsafe_allow_html=True,
    )

    if not filtered_products:
        st.info("Nismo pronašli proizvode za tu pretragu. Probaj drugi pojam ili kategoriju.")
        return

    columns = st.columns(3, gap="large")
    for index, product in enumerate(filtered_products):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="product-visual {product['tone']}">
                        <span class="product-badge">{product['badge']}</span>
                        <span class="product-emoji">{product['emoji']}</span>
                        <span class="visual-sparkle">✳</span>
                    </div>
                    <div class="product-category">{product['category']}</div>
                    <div class="product-name">{product['name']}</div>
                    <div class="product-description">{product['description']}</div>
                    <div class="product-rating">★★★★★ <span>{product['rating']:.1f}</span></div>
                    <div class="product-prices">
                        <span class="current-price">{format_price(product['price'])}</span>
                        <span class="old-price">{format_price(product['old_price'])}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.button(
                    "Dodaj u košaricu  +",
                    key=f"add_{product['id']}",
                    type="primary",
                    use_container_width=True,
                    on_click=update_cart,
                    args=(product["id"], 1),
                )


def render_benefits() -> None:
    st.markdown(
        """
        <section id="prednosti" class="benefits">
            <div class="eyebrow">MALO VIŠE PAŽNJE U SVAKOM KORAKU</div>
            <h2>Online kupnja, ali ljudski<span>.</span></h2>
            <div class="benefit-grid">
                <div><span>01</span><b>Pažljiv odabir</b><p>Biramo korisne stvari koje bismo i sami rado koristili.</p></div>
                <div><span>02</span><b>Jednostavna kupnja</b><p>Jasan katalog i košarica bez nepotrebnih koraka.</p></div>
                <div><span>03</span><b>Podrška kad zatreba</b><p>Tu smo za pitanja prije i nakon tvoje kupnje.</p></div>
            </div>
        </section>
        <footer id="kontakt" class="store-footer">
            <div><a class="brand footer-brand" href="#top">luma living<span>.</span></a>
            <p>Dobre sitnice za svaki dan.</p></div>
            <div class="footer-contact"><b>Demonstracijska trgovina</b><br>
            Ovdje se ne zaprimaju stvarne narudžbe.</div>
            <div class="footer-small">© 2026 Luma Living · ogledni sadržaj</div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    render_header()
    render_hero()
    render_cart()
    render_catalog()
    render_benefits()


if __name__ == "__main__":
    main()
