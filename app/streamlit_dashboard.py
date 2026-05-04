from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "data" / "processed" / "dashboard_exports"


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(EXPORTS / name)


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


st.set_page_config(page_title="Retail KPI Dashboard", layout="wide")
st.title("Retail KPI Dashboard")
st.caption("Executive view powered by the Python, SQL, and SQLite retail data pipeline.")

overview = load_csv("executive_overview.csv").iloc[0]
monthly = load_csv("monthly_revenue.csv")
products = load_csv("product_performance.csv")
customers = load_csv("customer_analysis.csv")
returns = load_csv("returns_quality.csv")
quality = load_csv("data_quality_summary.csv")

metric_cols = st.columns(5)
metric_cols[0].metric("Total Revenue", money(overview["total_revenue"]))
metric_cols[1].metric("Orders", f"{int(overview['total_orders']):,}")
metric_cols[2].metric("Avg Order Value", money(overview["average_order_value"]))
metric_cols[3].metric("Gross Margin", percent(overview["gross_margin"]))
metric_cols[4].metric("Return Rate", percent(overview["return_rate"]))

left, right = st.columns(2)
with left:
    st.subheader("Monthly Revenue")
    st.plotly_chart(
        px.line(monthly, x="order_month", y="revenue", markers=True, labels={"order_month": "Month", "revenue": "Revenue"}),
        use_container_width=True,
    )

with right:
    st.subheader("Revenue by Category")
    category_revenue = products.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    st.plotly_chart(
        px.bar(category_revenue, x="revenue", y="category", orientation="h", labels={"revenue": "Revenue", "category": "Category"}),
        use_container_width=True,
    )

left, right = st.columns(2)
with left:
    st.subheader("Top Products")
    st.dataframe(
        products[["product_name", "category", "units_sold", "revenue", "gross_margin"]].head(10),
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("Refund Exposure by Reason")
    reason_refunds = returns.groupby("reason", as_index=False)["refunded_amount"].sum().sort_values("refunded_amount", ascending=False)
    st.plotly_chart(
        px.bar(reason_refunds, x="refunded_amount", y="reason", orientation="h", labels={"refunded_amount": "Refunded Amount", "reason": "Reason"}),
        use_container_width=True,
    )

st.subheader("Customer Segments")
segment_revenue = customers.groupby("segment", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
st.plotly_chart(
    px.bar(segment_revenue, x="segment", y="revenue", labels={"segment": "Segment", "revenue": "Revenue"}),
    use_container_width=True,
)

st.subheader("Data Quality Summary")
st.dataframe(quality, use_container_width=True, hide_index=True)
