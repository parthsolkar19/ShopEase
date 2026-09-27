import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO

from database import (
    get_products,
    add_product,
    delete_product,
    update_product,
    get_bills,
    get_dashboard_stats,
    save_bill,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ShopEase",
    page_icon="🛒",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def go_to(page):
    st.session_state.page = page

def create_invoice_pdf(
    bill_id,
    customer_name,
    cart,
    subtotal,
    gst,
    discount,
    total
):
    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    # Header
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(
        25 * mm,
        height - 25 * mm,
        "ShopEase"
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        25 * mm,
        height - 32 * mm,
        "Shopping & Billing Management System"
    )

    # Invoice details
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(
        25 * mm,
        height - 50 * mm,
        f"Invoice #{bill_id}"
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        25 * mm,
        height - 58 * mm,
        f"Customer: {customer_name}"
    )

    # Table header
    y = height - 78 * mm

    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(25 * mm, y, "Product")
    pdf.drawString(105 * mm, y, "Qty")
    pdf.drawString(130 * mm, y, "Price")
    pdf.drawString(160 * mm, y, "Total")

    y -= 8 * mm

    pdf.setFont("Helvetica", 10)

    for item in cart:

        pdf.drawString(
            25 * mm,
            y,
            item["name"][:30]
        )

        pdf.drawString(
            105 * mm,
            y,
            str(item["quantity"])
        )

        pdf.drawString(
            130 * mm,
            y,
            f"Rs.{item['price']:,.2f}"
        )

        pdf.drawString(
            160 * mm,
            y,
            f"Rs.{item['total']:,.2f}"
        )

        y -= 7 * mm

    # Summary
    y -= 8 * mm

    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(
        120 * mm,
        y,
        f"Subtotal: Rs.{subtotal:,.2f}"
    )

    y -= 7 * mm

    pdf.drawString(
        120 * mm,
        y,
        f"GST: Rs.{gst:,.2f}"
    )

    y -= 7 * mm

    pdf.drawString(
        120 * mm,
        y,
        f"Discount: Rs.{discount:,.2f}"
    )

    y -= 9 * mm

    pdf.setFont("Helvetica-Bold", 13)

    pdf.drawString(
        120 * mm,
        y,
        f"Grand Total: Rs.{total:,.2f}"
    )

    # Footer
    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        25 * mm,
        20 * mm,
        "Thank you for shopping with ShopEase!"
    )

    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()
def add_to_cart(product):
    product_id = product[0]
    product_name = product[1]
    category = product[2]
    price = product[3]
    stock = product[4]

    for item in st.session_state.cart:
        if item["id"] == product_id:

            if item["quantity"] < stock:
                item["quantity"] += 1
                item["total"] = item["quantity"] * item["price"]

            return

    st.session_state.cart.append(
        {
            "id": product_id,
            "name": product_name,
            "category": category,
            "price": price,
            "quantity": 1,
            "total": price,
        }
    )


def remove_from_cart(product_id):
    st.session_state.cart = [
        item
        for item in st.session_state.cart
        if item["id"] != product_id
    ]

# ============================================================
# LOGIN
# ============================================================

if not st.session_state.logged_in:

    st.title("🛒 ShopEase")
    st.subheader("Login to continue")

    with st.form("login_form"):

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "🔐 Login",
            use_container_width=True
        )

        if login_button:

            if username == "admin" and password == "shopease123":

                st.session_state.logged_in = True
                st.success("Login successful!")

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    st.info(
        "Demo Username: admin | Password: shopease123"
    )

    st.stop()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🛒 ShopEase")
    st.caption("Shopping & Billing Management System")

    st.divider()

    if st.button("📊 Dashboard", use_container_width=True):
        go_to("Dashboard")

    if st.button("📦 Products", use_container_width=True):
        go_to("Products")

    if st.button("🛒 Billing", use_container_width=True):
        go_to("Billing")

    if st.button("📜 Sales History", use_container_width=True):
        go_to("Sales History")

    st.divider()

    st.caption("Python • Streamlit • SQLite")
    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.cart = []

        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.title("📊 Dashboard")
    st.write("Welcome to ShopEase Management System")

    stats = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Products",
            stats["products"]
        )

    with col2:
        st.metric(
            "Total Stock",
            stats["stock"]
        )

    with col3:
        st.metric(
            "Total Bills",
            stats["bills"]
        )

    with col4:
        st.metric(
            "Total Sales",
            f"₹{stats['sales']:,.2f}"
        )

    bills = get_bills()

    if bills:

        df = pd.DataFrame(
            bills,
            columns=[
                "id",
                "customer",
                "subtotal",
                "gst",
                "discount",
                "total",
                "created_at"
            ]
        )

        df["created_at"] = pd.to_datetime(
            df["created_at"]
        )

        current_month = pd.Timestamp.now().to_period("M")

        monthly_bills = df[
            df["created_at"].dt.to_period("M")
            == current_month
        ]

        monthly_sales = monthly_bills["total"].sum()

        average_bill = df["total"].mean()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "📅 This Month Sales",
                f"₹{monthly_sales:,.2f}"
            )

        with col2:
            st.metric(
                "🧾 Average Bill",
                f"₹{average_bill:,.2f}"
            )

        st.subheader("📈 Monthly Sales")

        df["month"] = df["created_at"].dt.strftime(
            "%b %Y"
        )

        monthly_data = (
            df.groupby("month")["total"]
            .sum()
            .reset_index()
        )

        st.line_chart(
            monthly_data.set_index("month")
        )

    st.divider()

    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "📦 Manage Products",
            use_container_width=True
        ):
            go_to("Products")

    with col2:
        if st.button(
            "🛒 Create New Bill",
            use_container_width=True
        ):
            go_to("Billing")

    with col3:
        if st.button(
            "📜 View Sales",
            use_container_width=True
        ):
            go_to("Sales History")


# ============================================================
# PRODUCTS
# ============================================================

elif st.session_state.page == "Products":

    st.title("📦 Product Management")

    tab1, tab2 = st.tabs(
        [
            "Product List",
            "Add Product"
        ]
    )

    # --------------------------------------------------------
    # PRODUCT LIST
    # --------------------------------------------------------

    with tab1:

        products = get_products()

        if not products:

            st.info("No products added yet.")

        else:

            search = st.text_input(
                "🔍 Search Product",
                placeholder="Enter product name..."
            )

            filtered_products = products

            if search:

                filtered_products = [
                    product
                    for product in products
                    if search.lower() in product[1].lower()
                ]

            if not filtered_products:

                st.warning("No matching products found.")

            else:

                for product in filtered_products:

                    col1, col2, col3, col4, col5 = st.columns(
                        [2, 1.5, 1, 1, 1.5]
                    )

                    with col1:
                        st.write(f"**{product[1]}**")

                    with col2:
                        st.write(product[2])

                    with col3:
                        st.write(f"₹{product[3]:,.2f}")

                    with col4:
                        if product[4] <= 5:
                            st.warning(f"{product[4]} left")
                        else:
                            st.write(f"{product[4]} units")

                    with col5:

                        if st.button(
                            "✏️ Edit",
                            key=f"edit_{product[0]}"
                        ):
                            st.session_state.edit_product = product
                            st.rerun()

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{product[0]}"
                        ):
                            delete_product(product[0])
                            st.rerun()

                    if (
                        "edit_product" in st.session_state
                        and st.session_state.edit_product[0] == product[0]
                    ):

                        st.subheader("✏️ Edit Product")

                        new_name = st.text_input(
                            "Product Name",
                            value=product[1],
                            key=f"edit_name_{product[0]}"
                        )

                        categories = [
                            "Electronics",
                            "Clothing",
                            "Food",
                            "Grocery",
                            "Home",
                            "Beauty",
                            "Other"
                        ]

                        new_category = st.selectbox(
                            "Category",
                            categories,
                            index=categories.index(product[2]),
                            key=f"edit_category_{product[0]}"
                        )

                        new_price = st.number_input(
                            "Price (₹)",
                            min_value=0.0,
                            value=float(product[3]),
                            step=10.0,
                            key=f"edit_price_{product[0]}"
                        )

                        new_stock = st.number_input(
                            "Stock",
                            min_value=0,
                            value=int(product[4]),
                            step=1,
                            key=f"edit_stock_{product[0]}"
                        )

                        col_edit1, col_edit2 = st.columns(2)

                        with col_edit1:

                            if st.button(
                                "💾 Update Product",
                                key=f"update_{product[0]}",
                                use_container_width=True
                            ):

                                if not new_name.strip():

                                    st.error(
                                        "Product name is required."
                                    )

                                elif new_price <= 0:

                                    st.error(
                                        "Price must be greater than 0."
                                    )

                                else:

                                    update_product(
                                        product[0],
                                        new_name.strip(),
                                        new_category,
                                        new_price,
                                        new_stock
                                    )

                                    del st.session_state.edit_product

                                    st.success(
                                        "Product updated successfully!"
                                    )

                                    st.rerun()

                        with col_edit2:

                            if st.button(
                                "❌ Cancel",
                                key=f"cancel_{product[0]}",
                                use_container_width=True
                            ):

                                del st.session_state.edit_product

                                st.rerun()

    # --------------------------------------------------------
    # ADD PRODUCT
    # --------------------------------------------------------

    with tab2:

        st.subheader("Add New Product")

        with st.form("add_product_form"):

            name = st.text_input(
                "Product Name"
            )

            category = st.selectbox(
                "Category",
                [
                    "Electronics",
                    "Clothing",
                    "Food",
                    "Grocery",
                    "Home",
                    "Beauty",
                    "Other"
                ]
            )

            col1, col2 = st.columns(2)

            with col1:

                price = st.number_input(
                    "Price (₹)",
                    min_value=0.0,
                    step=10.0
                )

            with col2:

                stock = st.number_input(
                    "Stock",
                    min_value=0,
                    step=1
                )

            submitted = st.form_submit_button(
                "➕ Add Product",
                use_container_width=True
            )

            if submitted:

                if not name.strip():

                    st.error(
                        "Product name is required."
                    )

                elif price <= 0:

                    st.error(
                        "Price must be greater than 0."
                    )

                else:

                    add_product(
                        name.strip(),
                        category,
                        price,
                        stock
                    )

                    st.success(
                        f"{name} added successfully!"
                    )

                    st.rerun()


# ============================================================
# BILLING
# ============================================================

elif st.session_state.page == "Billing":

    st.title("🛒 Billing")

    products = get_products()

    if not products:

        st.warning(
            "No products available. Add products first."
        )

    else:

        st.subheader("Select Products")

        # ----------------------------------------------------
        # PRODUCT SELECTION
        # ----------------------------------------------------

        for product in products:

            col1, col2, col3, col4 = st.columns(
                [3, 1, 1, 1]
            )

            with col1:

                st.write(
                    f"**{product[1]}**"
                )

                st.caption(
                    product[2]
                )

            with col2:

                st.write(
                    f"₹{product[3]:,.2f}"
                )

            with col3:

                st.write(
                    f"Stock: {product[4]}"
                )

            with col4:

                if product[4] > 0:

                    if st.button(
                        "Add",
                        key=f"add_{product[0]}"
                    ):

                        add_to_cart(product)
                        st.rerun()

                else:

                    st.error(
                        "Out of stock"
                    )

        st.divider()

        # ----------------------------------------------------
        # CART
        # ----------------------------------------------------

        st.subheader("🛒 Current Cart")

        if not st.session_state.cart:

            st.info(
                "Cart is empty."
            )

        else:

            for item in st.session_state.cart:

                col1, col2, col3, col4 = st.columns(
                    [3, 1, 1, 1]
                )

                with col1:

                    st.write(
                        f"**{item['name']}**"
                    )

                with col2:

                    st.write(
                        f"₹{item['price']:,.2f}"
                    )

                with col3:

                    st.write(
                        f"Qty: {item['quantity']}"
                    )

                with col4:

                    if st.button(
                        "Remove",
                        key=f"remove_{item['id']}"
                    ):

                        remove_from_cart(
                            item["id"]
                        )

                        st.rerun()

            st.divider()

            # ------------------------------------------------
            # BILL CALCULATIONS
            # ------------------------------------------------

            subtotal = sum(
                item["total"]
                for item in st.session_state.cart
            )

            col1, col2 = st.columns(2)

            with col1:

                discount_percent = st.number_input(
                    "Discount (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0
                )

            discount = subtotal * (
                discount_percent / 100
            )

            taxable_amount = subtotal - discount

            gst = taxable_amount * 0.18

            total = (
                taxable_amount
                + gst
            )

            col1, col2 = st.columns(2)

            with col1:

                customer_name = st.text_input(
                    "Customer Name",
                    value="Walk-in Customer"
                )

            with col2:

                st.write(
                    f"Discount ({discount_percent:.0f}%): "
                    f"₹{discount:,.2f}"
                )

                st.write(
                    f"GST (18%): ₹{gst:,.2f}"
                )

                st.write(
                    f"Discount: ₹{discount:,.2f}"
                )

                st.subheader(
                    f"Grand Total: ₹{total:,.2f}"
                )

            if st.button(
                "🧾 Generate Bill",
                type="primary",
                use_container_width=True
            ):

                if not customer_name.strip():

                    st.error(
                        "Please enter customer name."
                    )

                else:

                    bill_id = save_bill(
                        customer_name.strip(),
                        subtotal,
                        gst,
                        discount,
                        total,
                        st.session_state.cart
                    )

                    # Create PDF before clearing cart
                    pdf_data = create_invoice_pdf(
                        bill_id,
                        customer_name.strip(),
                        st.session_state.cart,
                        subtotal,
                        gst,
                        discount,
                        total
                    )

                    st.success(
                        f"✅ Bill #{bill_id} generated successfully!"
                    )

                    st.info(
                        f"Customer: {customer_name} | "
                        f"Total: ₹{total:,.2f}"
                    )

                    st.download_button(
                        label="📄 Download Invoice",
                        data=pdf_data,
                        file_name=f"ShopEase_Invoice_{bill_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                    st.session_state.cart = []

                    st.balloons()


# ============================================================
# SALES HISTORY
# ============================================================

elif st.session_state.page == "Sales History":

    st.title("📜 Sales History")

    bills = get_bills()

    if not bills:

        st.info(
            "No sales recorded yet."
        )

    else:

        for bill in bills:

            st.subheader(
                f"Bill #{bill[0]}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    f"**Customer:** {bill[1]}"
                )

            with col2:

                st.write(
                    f"**Total:** ₹{bill[5]:,.2f}"
                )

            with col3:

                st.write(
                    f"**Date:** {bill[6]}"
                )

            st.write(
                f"Subtotal: ₹{bill[2]:,.2f}"
            )

            st.write(
                f"GST: ₹{bill[3]:,.2f}"
            )

            st.write(
                f"Discount: ₹{bill[4]:,.2f}"
            )

            st.divider()