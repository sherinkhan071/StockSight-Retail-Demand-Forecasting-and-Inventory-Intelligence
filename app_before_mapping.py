import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="StockSight | Retail Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px;}
    [data-testid="stMetric"] {
        background: #f6f8fc; border: 1px solid #e5eaf3;
        padding: 16px 18px; border-radius: 14px;
    }
    [data-testid="stMetricLabel"] p {font-size: .88rem; color: #526079;}
    [data-testid="stMetricValue"] {font-size: clamp(1.2rem, 2vw, 2rem);}
    .hero {
        padding: 1.5rem 1.7rem; border-radius: 18px;
        background: linear-gradient(120deg,#101d3b,#2457a7);
        color: white; margin-bottom: 1.1rem;
    }
    .hero h1 {color:white; margin:0; font-size:2.1rem;}
    .hero p {color:#e4ebff; margin:.45rem 0 0 0;}
    .eyebrow {text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; color:#8ba7d8; font-weight:700;}
    div[data-testid="stTabs"] button {font-weight:600;}
    .hint {color:#667085; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def norm_col(value):
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")

def find_col(df, candidates):
    if df is None:
        return None
    lookup = {norm_col(c): c for c in df.columns}
    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]
    return None

def numeric(df, col):
    if df is None or col is None or col not in df.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(df[col], errors="coerce")

def money(value):
    if pd.isna(value):
        return "—"
    value = float(value)
    absolute = abs(value)
    if absolute >= 10_000_000:
        return f"₹{value / 10_000_000:,.2f} Cr"
    if absolute >= 100_000:
        return f"₹{value / 100_000:,.2f} L"
    return f"₹{value:,.0f}"

def display_name(col):
    return str(col).replace("_", " ").strip().title()

def read_uploads(files):
    tables = {}
    for file in files or []:
        try:
            file.seek(0)
            df = pd.read_csv(file, low_memory=False)
            # Remove blank rows/columns and normalize headers without changing originals too aggressively.
            df = df.dropna(how="all").dropna(axis=1, how="all")
            df.columns = [str(c).strip() for c in df.columns]
            tables[Path(file.name).stem.lower()] = df
        except Exception as exc:
            st.error(f"Could not read {file.name}: {exc}")
    return tables

def pick_table(tables, keywords):
    for name, df in tables.items():
        if any(word in name for word in keywords):
            return df
    return None

def choose_table(tables, label, keywords):
    if not tables:
        return None
    options = ["— Not selected —"] + list(tables.keys())
    default = next((name for name in tables if any(k in name for k in keywords)), "— Not selected —")
    selected = st.selectbox(label, options, index=options.index(default))
    return tables.get(selected)

def safe_date_range(series):
    parsed = pd.to_datetime(series, errors="coerce").dropna()
    if parsed.empty:
        return None
    return parsed.min().date(), parsed.max().date()

def filter_options(df, col, label):
    if df is None or col is None:
        return None
    values = sorted(df[col].dropna().astype(str).unique().tolist())
    if not values:
        return None
    selected = st.multiselect(label, values, default=[], help="Leave empty to include every value.")
    return selected or None

def filtered_by_values(df, filters):
    result = df.copy()
    for col, values in filters.items():
        if col and values and col in result.columns:
            result = result[result[col].astype(str).isin(values)]
    return result

def show_empty_state(message, detail=None):
    st.info(message)
    if detail:
        st.caption(detail)

# ---------- Header ----------
with st.sidebar:
    st.title("📦 StockSight")
    st.caption("Retail Demand & Inventory Intelligence")
    page = st.radio(
        "Workspace",
        ["Overview", "Sales Analysis", "Inventory Health", "Demand Forecast", "Data Explorer"],
        index=0,
    )
    st.divider()
    st.markdown("**Your workspace**")
    st.caption("Upload a dataset, then use filters to explore it.")
    st.caption("Tip: upload multiple CSVs together.")

st.markdown("""
<div class="hero">
  <div class="eyebrow">Retail intelligence workspace</div>
  <h1>StockSight</h1>
  <p>Explore performance, spot risks, and make more confident stocking decisions.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Bring your retail data")
st.write("Upload one or more CSV files. StockSight detects common fields and lets you explore the data interactively.")
uploads = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True, help="Files can have different names and column formats.")
uploaded = read_uploads(uploads) if uploads else {}

if not uploaded:
    st.info("Upload one or more CSV files to begin.")
    st.markdown("**What you can do here**")
    a, b, c = st.columns(3)
    a.markdown("#### 📈 Explore sales\nFilter dates and products, compare revenue, and inspect trends.")
    b.markdown("#### 📦 Review inventory\nFind rows at or below a detected reorder point when those fields exist.")
    c.markdown("#### 🔎 Understand your data\nInspect columns, missing values, data types, and download filtered rows.")
    with st.expander("Supported column examples"):
        st.markdown("""
        - **Date:** `date`, `sale_date`, `order_date`, `transaction_date`
        - **Revenue:** `revenue`, `sales`, `sales_amount`, `total_amount`
        - **Quantity:** `quantity`, `qty`, `units_sold`, `sold_quantity`
        - **Product:** `product`, `product_id`, `sku`, `product_name`, `item`
        - **Category:** `category`, `product_category`, `department`
        - **Inventory:** `closing_stock`, `stock_on_hand`, `current_stock`, `available_stock`
        - **Reorder point:** `reorder_point`, `reorder_level`, `minimum_stock`, `min_stock`
        """)
    st.stop()

st.success(f"Loaded {len(uploaded)} file(s): " + ", ".join(uploaded.keys()))

# ---------- Let the user explicitly map files ----------
with st.expander("Dataset setup — check which file is which", expanded=False):
    table_names = list(uploaded.keys())
    sales_default = next((n for n in table_names if any(k in n for k in ["sales", "transaction", "order"])), "— Not selected —")
    inventory_default = next((n for n in table_names if any(k in n for k in ["inventory", "stock", "health"])), "— Not selected —")
    product_default = next((n for n in table_names if any(k in n for k in ["product", "catalog"])), "— Not selected —")
    options = ["— Not selected —"] + table_names
    sales_name = st.selectbox("Sales dataset", options, index=options.index(sales_default), key="sales_table")
    inventory_name = st.selectbox("Inventory dataset", options, index=options.index(inventory_default), key="inventory_table")
    product_name = st.selectbox("Product catalogue (optional)", options, index=options.index(product_default), key="product_table")

sales = uploaded.get(sales_name) if 'sales_name' in locals() and sales_name != "— Not selected —" else pick_table(uploaded, ["sales", "transaction", "order"])
inventory = uploaded.get(inventory_name) if 'inventory_name' in locals() and inventory_name != "— Not selected —" else pick_table(uploaded, ["inventory", "stock", "health"])
products = uploaded.get(product_name) if 'product_name' in locals() and product_name != "— Not selected —" else pick_table(uploaded, ["product", "catalog"])

# If the user explicitly selected "not selected", don't silently re-assign that role.
if 'sales_name' in locals() and sales_name == "— Not selected —":
    sales = None
if 'inventory_name' in locals() and inventory_name == "— Not selected —":
    inventory = None

# ---------- Flexible field detection ----------
date_candidates = ["sale_date", "date", "transaction_date", "order_date", "created_at", "datetime", "timestamp", "day"]
qty_candidates = ["quantity", "units_sold", "qty", "sold_quantity", "units", "sales_quantity", "demand"]
revenue_candidates = ["revenue", "sales_amount", "total_amount", "net_sales", "total_sales", "sales", "amount", "line_total"]
price_candidates = ["unit_price", "selling_price", "price", "sale_price", "unit_selling_price"]
discount_candidates = ["discount", "discount_amount", "discount_rate"]
product_candidates = ["product_id", "product", "sku", "product_name", "item", "item_name", "stock_code"]
store_candidates = ["store_id", "store", "location_id", "store_name", "branch", "location"]
category_candidates = ["category", "product_category", "department", "product_type", "class"]
stock_candidates = ["closing_stock", "stock_on_hand", "current_stock", "available_stock", "quantity_on_hand", "ending_inventory", "stock"]
reorder_candidates = ["reorder_point", "reorder_level", "minimum_stock", "min_stock", "safety_stock"]
inv_date_candidates = ["inventory_date", "snapshot_date", "date", "as_of_date", "last_updated"]

sales_date = find_col(sales, date_candidates)
sales_qty = find_col(sales, qty_candidates)
sales_revenue = find_col(sales, revenue_candidates)
sales_product = find_col(sales, product_candidates)
sales_store = find_col(sales, store_candidates)
sales_category = find_col(sales, category_candidates)
inv_close = find_col(inventory, stock_candidates)
inv_reorder = find_col(inventory, reorder_candidates)
inv_product = find_col(inventory, product_candidates)
inv_store = find_col(inventory, store_candidates)
inv_date = find_col(inventory, inv_date_candidates)

# ---------- Global interactive filters ----------
st.markdown("### Filters")
filter_note = st.caption("Filters affect the selected analysis where matching fields are available.")
f1, f2, f3 = st.columns([1.25, 1, 1])
sales_filtered = sales.copy() if sales is not None else None
with f1:
    date_bounds = safe_date_range(sales[sales_date]) if sales is not None and sales_date else None
    if date_bounds:
        date_range = st.date_input("Sales date range", value=date_bounds, min_value=date_bounds[0], max_value=date_bounds[1], key="global_date_range")
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            parsed = pd.to_datetime(sales_filtered[sales_date], errors="coerce")
            sales_filtered = sales_filtered[parsed.dt.date.between(date_range[0], date_range[1])]
    else:
        st.text_input("Sales date range", value="No usable date column", disabled=True)
with f2:
    product_filter = filter_options(sales_filtered, sales_product, "Products") if sales_filtered is not None else None
with f3:
    category_filter = filter_options(sales_filtered, sales_category, "Categories") if sales_filtered is not None else None

if sales_filtered is not None:
    sales_filtered = filtered_by_values(sales_filtered, {sales_product: product_filter, sales_category: category_filter})

with st.expander("More filters", expanded=False):
    g1, g2 = st.columns(2)
    with g1:
        store_filter = filter_options(sales_filtered, sales_store, "Stores / locations") if sales_filtered is not None else None
    with g2:
        st.caption("Inventory filters are available in Inventory Health.")
if sales_filtered is not None:
    sales_filtered = filtered_by_values(sales_filtered, {sales_store: store_filter if 'store_filter' in locals() else None})

# ---------- Overview ----------
if page == "Overview":
    st.header("Business overview")
    if sales_filtered is None and inventory is None:
        show_empty_state("Choose a sales or inventory dataset in Dataset setup to see business metrics.")
        st.stop()

    total_revenue = numeric(sales_filtered, sales_revenue).sum(min_count=1) if sales_filtered is not None and sales_revenue else np.nan
    total_units = numeric(sales_filtered, sales_qty).sum(min_count=1) if sales_filtered is not None and sales_qty else np.nan
    sales_records = len(sales_filtered) if sales_filtered is not None else np.nan
    low_stock_count = np.nan
    valid_inventory = 0
    if inventory is not None and inv_close:
        closing = numeric(inventory, inv_close)
        valid_inventory = int(closing.notna().sum())
        if inv_reorder:
            reorder = numeric(inventory, inv_reorder)
            low_stock_count = int(((closing <= reorder) & closing.notna() & reorder.notna()).sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total revenue", money(total_revenue), help="Sum of the detected revenue column after filters.")
    m2.metric("Units sold", f"{total_units:,.0f}" if pd.notna(total_units) else "—", help="Sum of the detected quantity column.")
    m3.metric("Sales records", f"{sales_records:,}" if pd.notna(sales_records) else "—")
    m4.metric("At/below reorder point", f"{low_stock_count:,}" if pd.notna(low_stock_count) else "Unavailable", help="Only calculated when both stock and reorder-point columns are detected.")

    left, right = st.columns(2)
    with left:
        st.subheader("Revenue trend")
        if sales_filtered is not None and sales_date and sales_revenue:
            trend_df = sales_filtered.copy()
            trend_df["_date"] = pd.to_datetime(trend_df[sales_date], errors="coerce")
            trend_df["_revenue"] = numeric(trend_df, sales_revenue)
            trend = trend_df.dropna(subset=["_date"]).groupby(trend_df["_date"].dt.to_period("ME").astype(str))["_revenue"].sum()
            if not trend.empty:
                st.line_chart(trend, x_label="Month", y_label="Revenue")
            else:
                show_empty_state("No valid dates in the selected sales data.")
        else:
            show_empty_state("A date and revenue column are needed for this chart.")
    with right:
        st.subheader("Inventory status")
        if inventory is not None and inv_close and inv_reorder:
            closing = numeric(inventory, inv_close)
            reorder = numeric(inventory, inv_reorder)
            status = pd.Series({
                "At/below reorder point": int(((closing <= reorder) & closing.notna() & reorder.notna()).sum()),
                "Above reorder point": int(((closing > reorder) & closing.notna() & reorder.notna()).sum()),
                "Needs data review": int((closing.isna() | reorder.isna()).sum()),
            })
            st.bar_chart(status, y_label="Inventory records")
        elif inventory is not None and inv_close:
            st.metric("Inventory records with usable stock", f"{valid_inventory:,}")
            show_empty_state("Stock column detected, but no reorder-point column was recognized.", "Inventory status can still be explored in Inventory Health.")
        else:
            show_empty_state("Upload/select inventory data with a recognizable stock column to view inventory status.")

    st.subheader("Explore the filtered sales")
    if sales_filtered is not None:
        st.caption(f"Showing {len(sales_filtered):,} sales rows after filters.")
        st.dataframe(sales_filtered.head(500), use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download filtered sales CSV", sales_filtered.to_csv(index=False).encode("utf-8"), "stocksight_filtered_sales.csv", "text/csv", key="overview_download")

# ---------- Sales analysis ----------
elif page == "Sales Analysis":
    st.header("Sales analysis")
    if sales_filtered is None:
        show_empty_state("Select a sales dataset in Dataset setup.")
        st.stop()
    st.caption(f"{len(sales_filtered):,} records match the current filters.")
    if sales_revenue:
        rev = numeric(sales_filtered, sales_revenue)
        a, b = st.columns(2)
        a.metric("Revenue in selection", money(rev.sum(min_count=1)))
        a.metric("Average revenue per record", money(rev.mean()))
        if sales_product:
            product_perf = sales_filtered.assign(_revenue=rev).groupby(sales_product, dropna=False)["_revenue"].sum().sort_values(ascending=False).head(10)
            st.subheader("Top 10 products by revenue")
            st.bar_chart(product_perf, horizontal=True, x_label="Revenue", y_label="Product")
        if sales_date:
            trend_df = sales_filtered.copy()
            trend_df["_date"] = pd.to_datetime(trend_df[sales_date], errors="coerce")
            trend_df["_revenue"] = rev
            freq = st.segmented_control("Trend granularity", options=["Daily", "Weekly", "Monthly"], default="Monthly", key="sales_granularity")
            freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}
            valid = trend_df.dropna(subset=["_date"])
            if not valid.empty:
                trend = valid.set_index("_date")["_revenue"].resample(freq_map[freq]).sum()
                st.subheader(f"{freq} revenue trend")
                st.line_chart(trend, x_label="Date", y_label="Revenue")
    else:
        show_empty_state("No recognized revenue column found.", "Open Data Explorer to inspect columns; column mapping can be added next.")
    if sales_qty:
        st.metric("Units sold in selection", f"{numeric(sales_filtered, sales_qty).sum():,.0f}")
    with st.expander("View sales records", expanded=False):
        st.dataframe(sales_filtered.head(2000), use_container_width=True, hide_index=True)
        st.download_button("Download sales CSV", sales_filtered.to_csv(index=False).encode("utf-8"), "stocksight_sales_filtered.csv", "text/csv", key="sales_download")

# ---------- Inventory health ----------
elif page == "Inventory Health":
    st.header("Inventory health")
    if inventory is None:
        show_empty_state("Select an inventory dataset in Dataset setup.", "If your file has an unusual name, you can select it manually above.")
        st.stop()
    st.caption(f"{len(inventory):,} inventory records loaded.")
    if not inv_close:
        show_empty_state("StockSight could not identify a stock-on-hand column.", "Open Data Explorer to inspect your column names.")
        st.dataframe(inventory.head(500), use_container_width=True, hide_index=True)
        st.stop()

    health = inventory.copy()
    health["_stock_numeric"] = numeric(health, inv_close)
    if inv_reorder:
        health["_reorder_numeric"] = numeric(health, inv_reorder)
        health["Stock status"] = np.select(
            [
                health["_stock_numeric"].isna() | health["_reorder_numeric"].isna(),
                health["_stock_numeric"] <= health["_reorder_numeric"],
            ],
            ["Needs data review", "At/below reorder point"],
            default="Above reorder point",
        )
    else:
        health["Stock status"] = np.where(health["_stock_numeric"].isna(), "Needs data review", "Stock available; reorder point unknown")

    h1, h2, h3 = st.columns(3)
    h1.metric("Inventory records", f"{len(health):,}")
    h2.metric("Valid stock values", f"{health['_stock_numeric'].notna().sum():,}")
    if inv_reorder:
        h3.metric("At/below reorder point", f"{(health['Stock status'] == 'At/below reorder point').sum():,}")
    else:
        h3.metric("Reorder analysis", "Needs reorder column")

    st.subheader("Stock status distribution")
    st.bar_chart(health["Stock status"].value_counts(), y_label="Records")
    if inv_product:
        product_search = st.text_input("Search product / SKU", placeholder="Type a product name or SKU…")
        if product_search:
            health = health[health[inv_product].astype(str).str.contains(product_search, case=False, na=False)]
    status_options = health["Stock status"].dropna().unique().tolist()
    chosen_status = st.multiselect("Show stock statuses", status_options, default=status_options)
    health_view = health[health["Stock status"].isin(chosen_status)]
    st.subheader("Inventory records")
    st.dataframe(health_view.drop(columns=["_stock_numeric", "_reorder_numeric"], errors="ignore").head(2000), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download inventory review CSV", health_view.to_csv(index=False).encode("utf-8"), "stocksight_inventory_review.csv", "text/csv", key="inventory_download")

# ---------- Demand forecast ----------
elif page == "Demand Forecast":
    st.header("Demand forecast")
    if sales_filtered is None or not sales_date or not sales_qty:
        show_empty_state("A sales dataset with a recognizable date and quantity column is needed for forecasting.")
        st.stop()
    forecast_df = sales_filtered.copy()
    forecast_df["_date"] = pd.to_datetime(forecast_df[sales_date], errors="coerce")
    forecast_df["_qty"] = numeric(forecast_df, sales_qty)
    series = forecast_df.dropna(subset=["_date"]).groupby(forecast_df["_date"].dt.date)["_qty"].sum().sort_index()
    series.index = pd.to_datetime(series.index)
    series = series.asfreq("D", fill_value=0)
    if len(series) < 14:
        show_empty_state("At least 14 days of dated sales are recommended for this baseline forecast.")
        st.stop()
    horizon = st.slider("Forecast horizon (days)", 7, 60, 14, key="forecast_horizon")
    window = min(7, len(series))
    daily_mean = float(series.tail(window).mean())
    future_dates = pd.date_range(series.index.max() + pd.Timedelta(days=1), periods=horizon, freq="D")
    forecast = pd.Series([daily_mean] * horizon, index=future_dates, name="Forecast units")
    f1, f2, f3 = st.columns(3)
    f1.metric(f"Estimated units next {horizon} days", f"{forecast.sum():,.0f}")
    f2.metric("Recent daily average", f"{daily_mean:,.1f}")
    f3.metric("Forecast method", "7-day mean")
    st.caption("This is a simple baseline forecast, not a validated production model. Accuracy evaluation is a future improvement.")
    chart_history = series.tail(60).rename("Actual units")
    st.subheader("Historical demand and forecast")
    st.line_chart(pd.concat([chart_history, forecast]), x_label="Date", y_label="Units")
    out = forecast.rename_axis("date").reset_index()
    out.columns = ["date", "forecast_units"]
    st.download_button("⬇️ Download forecast CSV", out.to_csv(index=False).encode("utf-8"), "stocksight_demand_forecast.csv", "text/csv", key="forecast_download")

# ---------- Data explorer ----------
elif page == "Data Explorer":
    st.header("Data Explorer")
    st.write("Inspect any uploaded file, understand its quality, and download the rows you need.")
    selected_file = st.selectbox("Choose a dataset", list(uploaded.keys()), key="explorer_file")
    df = uploaded[selected_file].copy()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", f"{len(df.columns):,}")
    c3.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")
    c4.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

    st.subheader("Column quality")
    profile = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Detected type": [str(df[c].dtype) for c in df.columns],
        "Missing values": [int(df[c].isna().sum()) for c in df.columns],
        "Missing %": [round(float(df[c].isna().mean() * 100), 2) for c in df.columns],
        "Unique values": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    st.dataframe(profile, use_container_width=True, hide_index=True)
    st.subheader("Filter and inspect rows")
    search = st.text_input("Search across all columns", placeholder="Enter a product, category, store, or value…", key="explorer_search")
    view = df
    if search:
        mask = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        view = view[mask]
    column_choice = st.multiselect("Columns to display", df.columns.tolist(), default=df.columns.tolist(), key="explorer_columns")
    if column_choice:
        st.dataframe(view[column_choice].head(3000), use_container_width=True, hide_index=True)
    else:
        st.warning("Select at least one column to display.")
    st.download_button("⬇️ Download current rows as CSV", view.to_csv(index=False).encode("utf-8"), f"{Path(selected_file).stem}_filtered.csv", "text/csv", key="explorer_download")
    with st.expander("Raw data preview"):
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)

st.divider()
st.caption("StockSight · Interactive retail analytics starter. Validate data definitions before making purchasing decisions.")
