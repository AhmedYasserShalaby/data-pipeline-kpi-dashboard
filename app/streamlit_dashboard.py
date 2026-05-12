from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from pipeline.bootstrap import ensure_demo_outputs


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "data" / "processed" / "dashboard_exports"


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(EXPORTS / name)


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def metric_delta(value: float | None) -> str | None:
    if pd.isna(value):
        return None
    return percent(value)


st.set_page_config(page_title="Retail KPI Dashboard", layout="wide")
generated_demo_outputs = ensure_demo_outputs()
st.title("Retail KPI Dashboard")
st.caption("Python + SQL data pipeline with validation, incremental loading, KPI exports, and executive reporting.")
if generated_demo_outputs:
    st.toast("Demo data prepared")

overview = load_csv("executive_overview.csv").iloc[0]
monthly = load_csv("monthly_revenue.csv")
products = load_csv("product_performance.csv")
customers = load_csv("customer_analysis.csv")
returns = load_csv("returns_quality.csv")
quality = load_csv("data_quality_summary.csv")
issues = load_csv("data_quality_issues.csv")
run_summary = load_csv("pipeline_run_summary.csv").iloc[0]

tab_executive, tab_sales, tab_products, tab_customers, tab_quality = st.tabs(
    ["Executive", "Sales", "Products", "Customers", "Data Quality"]
)

with tab_executive:
    metric_cols = st.columns(5)
    metric_cols[0].metric("Total Revenue", money(overview["total_revenue"]))
    metric_cols[1].metric("Orders", f"{int(overview['total_orders']):,}")
    metric_cols[2].metric("Avg Order Value", money(overview["average_order_value"]))
    metric_cols[3].metric("Gross Margin", percent(overview["gross_margin"]))
    metric_cols[4].metric("Return Rate", percent(overview["return_rate"]))

    left, right = st.columns(2)
    with left:
        st.subheader("Revenue Trend")
        st.plotly_chart(
            px.line(
                monthly,
                x="order_month",
                y="revenue",
                markers=True,
                labels={"order_month": "Month", "revenue": "Revenue"},
            ),
            width="stretch",
        )

    with right:
        st.subheader("Revenue by Category")
        category_revenue = (
            products.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        )
        st.plotly_chart(
            px.bar(
                category_revenue,
                x="revenue",
                y="category",
                orientation="h",
                labels={"revenue": "Revenue", "category": "Category"},
                color="category",
            ),
            width="stretch",
        )

with tab_sales:
    st.subheader("Monthly Sales Performance")
    month_cols = st.columns(3)
    best_month = monthly.sort_values("revenue", ascending=False).iloc[0]
    latest_month = monthly.sort_values("order_month").iloc[-1]
    month_cols[0].metric("Best Month", best_month["order_month"], money(best_month["revenue"]))
    month_cols[1].metric(
        "Latest Month Revenue", money(latest_month["revenue"]), metric_delta(latest_month["monthly_growth"])
    )
    month_cols[2].metric("Latest Month Orders", f"{int(latest_month['orders']):,}")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.bar(
                monthly,
                x="order_month",
                y="revenue",
                labels={"order_month": "Month", "revenue": "Revenue"},
            ),
            width="stretch",
        )
    with right:
        growth = monthly.dropna(subset=["monthly_growth"]).copy()
        growth["monthly_growth_pct"] = growth["monthly_growth"] * 100
        st.plotly_chart(
            px.line(
                growth,
                x="order_month",
                y="monthly_growth_pct",
                markers=True,
                labels={"order_month": "Month", "monthly_growth_pct": "Growth %"},
            ),
            width="stretch",
        )

    st.dataframe(monthly, width="stretch", hide_index=True)

with tab_products:
    categories = sorted(products["category"].unique())
    selected_categories = st.multiselect("Category", categories, default=categories)
    product_view = products[products["category"].isin(selected_categories)].copy()

    metric_cols = st.columns(3)
    metric_cols[0].metric("Selected Revenue", money(product_view["revenue"].sum()))
    metric_cols[1].metric("Units Sold", f"{int(product_view['units_sold'].sum()):,}")
    metric_cols[2].metric("Avg Gross Margin", percent(product_view["gross_margin"].mean()))

    left, right = st.columns(2)
    with left:
        st.subheader("Top Products")
        st.plotly_chart(
            px.bar(
                product_view.head(12),
                x="revenue",
                y="product_name",
                color="category",
                orientation="h",
                labels={"revenue": "Revenue", "product_name": "Product"},
            ),
            width="stretch",
        )
    with right:
        st.subheader("Margin by Category")
        margin_view = (
            product_view.groupby("category", as_index=False)["gross_margin"]
            .mean()
            .sort_values("gross_margin", ascending=False)
        )
        st.plotly_chart(
            px.bar(
                margin_view,
                x="category",
                y="gross_margin",
                labels={"category": "Category", "gross_margin": "Gross Margin"},
            ),
            width="stretch",
        )

    st.dataframe(
        product_view[["product_name", "category", "units_sold", "revenue", "gross_profit", "gross_margin"]],
        width="stretch",
        hide_index=True,
    )

with tab_customers:
    segments = sorted(customers["segment"].unique())
    countries = sorted(customers["country"].unique())
    left_filter, right_filter = st.columns(2)
    selected_segments = left_filter.multiselect("Segment", segments, default=segments)
    selected_countries = right_filter.multiselect("Country", countries, default=countries)
    customer_view = customers[
        customers["segment"].isin(selected_segments) & customers["country"].isin(selected_countries)
    ].copy()

    metric_cols = st.columns(4)
    metric_cols[0].metric("Customers", f"{customer_view['customer_id'].nunique():,}")
    metric_cols[1].metric("Revenue", money(customer_view["revenue"].sum()))
    metric_cols[2].metric("Repeat Customers", f"{int(customer_view['repeat_customer'].sum()):,}")
    metric_cols[3].metric("Avg Order Value", money(customer_view["average_order_value"].mean()))

    left, right = st.columns(2)
    with left:
        st.subheader("Revenue by Segment")
        segment_revenue = (
            customer_view.groupby("segment", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        )
        st.plotly_chart(
            px.bar(
                segment_revenue,
                x="segment",
                y="revenue",
                color="segment",
                labels={"segment": "Segment", "revenue": "Revenue"},
            ),
            width="stretch",
        )
    with right:
        st.subheader("Top Customers")
        st.dataframe(
            customer_view[["customer_name", "segment", "country", "city", "orders", "revenue", "repeat_customer"]].head(
                12
            ),
            width="stretch",
            hide_index=True,
        )

with tab_quality:
    st.subheader("Pipeline Health")
    quality_score = quality["quality_score"].mean()
    quality_cols = st.columns(5)
    quality_cols[0].metric("Quality Score", percent(quality_score))
    quality_cols[1].metric("Rows Read", f"{int(run_summary['rows_read']):,}")
    quality_cols[2].metric("Rows Cleaned", f"{int(run_summary['rows_cleaned']):,}")
    quality_cols[3].metric("Rows Rejected", f"{int(run_summary['rows_rejected']):,}")
    quality_cols[4].metric("Loaded Rows", f"{int(run_summary['loaded_rows']):,}")

    left, right = st.columns(2)
    with left:
        st.subheader("Clean Rate by Table")
        st.plotly_chart(
            px.bar(
                quality,
                x="table_name",
                y="clean_rate",
                color="table_name",
                labels={"table_name": "Table", "clean_rate": "Clean Rate"},
            ),
            width="stretch",
        )
    with right:
        st.subheader("Refund Exposure by Reason")
        reason_refunds = (
            returns.groupby("reason", as_index=False)["refunded_amount"]
            .sum()
            .sort_values("refunded_amount", ascending=False)
        )
        st.plotly_chart(
            px.bar(
                reason_refunds,
                x="refunded_amount",
                y="reason",
                orientation="h",
                labels={"refunded_amount": "Refunded Amount", "reason": "Reason"},
            ),
            width="stretch",
        )

    issue_breakdown = issues.groupby(["issue_source", "table_name", "issue_type"], as_index=False).size()
    st.subheader("Issue Breakdown")
    st.dataframe(issue_breakdown, width="stretch", hide_index=True)

    st.subheader("Table Quality Summary")
    st.dataframe(quality, width="stretch", hide_index=True)
