import streamlit as st
import duckdb
import pandas as pd
import altair as alt

# ============================================================
#  Page config
# ============================================================
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

# ---- Light custom styling ----
st.markdown(
    """
    <style>
        .main { background-color: #fafafa; }
        h1, h2, h3 { color: #1a1a2e; font-family: 'Helvetica Neue', sans-serif; }
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #ececec;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        [data-testid="stMetricLabel"] { color: #6b7280; font-weight: 500; }
        [data-testid="stMetricValue"] { color: #1a1a2e; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  Data loading (cached, read-only to avoid dbt lock)
# ============================================================
DB_PATH = "retail.duckdb"

@st.cache_data
def load_data():
    con = duckdb.connect(DB_PATH, read_only=True)
    rfm = con.execute("select * from rfm_scores").df()
    cohort = con.execute("select * from cohort_retention").df()
    con.close()
    return rfm, cohort

rfm, cohort = load_data()

# ============================================================
#  Header
# ============================================================
st.title("Customer Analytics")
st.caption(
    "RFM segmentation & cohort retention · UCI Online Retail II (2009–2011) · "
    "Built with DuckDB + dbt + Streamlit"
)
st.divider()

# ============================================================
#  Headline metrics
# ============================================================
total_customers = rfm["customer_id"].nunique()
total_revenue = rfm["monetary"].sum()
avg_spend = rfm["monetary"].mean()
champions_share = (rfm["segment"].eq("Champions").mean()) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers", f"{total_customers:,}")
c2.metric("Total Revenue", f"£{total_revenue/1_000_000:,.1f}M")
c3.metric("Avg Spend / Customer", f"£{avg_spend:,.0f}")
c4.metric("Champions", f"{champions_share:.0f}%")

st.divider()

# ============================================================
#  Segment breakdown
# ============================================================
st.subheader("Customer Segments")

seg = (
    rfm.groupby("segment")
    .agg(customers=("customer_id", "count"),
         avg_spend=("monetary", "mean"),
         total_revenue=("monetary", "sum"))
    .reset_index()
    .sort_values("customers", ascending=False)
)
seg["avg_spend"] = seg["avg_spend"].round(0)

segment_colors = {
    "Champions": "#2e7d32",
    "Loyal": "#66bb6a",
    "At Risk": "#f9a825",
    "New": "#42a5f5",
    "Lost / Hibernating": "#c62828",
}

left, right = st.columns([1.1, 1])

with left:
    chart = (
        alt.Chart(seg)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("segment:N", sort="-y", title=None,
                    axis=alt.Axis(labelAngle=-30)),
            y=alt.Y("customers:Q", title="Customers"),
            color=alt.Color("segment:N",
                            scale=alt.Scale(
                                domain=list(segment_colors.keys()),
                                range=list(segment_colors.values())),
                            legend=None),
            tooltip=["segment", "customers", "avg_spend", "total_revenue"],
        )
        .properties(height=340)
    )
    st.altair_chart(chart, use_container_width=True)

with right:
    display = seg.rename(columns={
        "segment": "Segment",
        "customers": "Customers",
        "avg_spend": "Avg Spend (£)",
        "total_revenue": "Total Revenue (£)",
    })
    st.dataframe(
        display.style.format({
            "Avg Spend (£)": "{:,.0f}",
            "Total Revenue (£)": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ============================================================
#  Cohort retention heatmap
# ============================================================
st.subheader("Cohort Retention")
st.caption("Each row is a monthly acquisition cohort; values are the % of that "
           "cohort still active in each subsequent month.")

pivot = cohort.pivot_table(
    index="cohort_month", columns="month_offset",
    values="active_customers", aggfunc="sum",
)
retention_pct = pivot.divide(pivot[0], axis=0) * 100
retention_pct.index = pd.to_datetime(retention_pct.index).strftime("%Y-%m")

styled = (
    retention_pct
    .style
    .background_gradient(cmap="RdYlGn", axis=None, vmin=0, vmax=100)
    .format(lambda v: "" if pd.isna(v) else f"{v:.0f}")
)

st.dataframe(styled, use_container_width=True)

# ============================================================
#  Key takeaways  --  TODO: write these in your own words
# ============================================================
st.divider()
st.subheader("Key Takeaways")

# Facts to build from (all from your own data):
#  - Champions: 1,544 customers (26%), £12.4M of £17.7M total revenue (~70%)
#  - Lost/Hibernating: 2,792 customers (~47%), only £1.9M revenue (~11%), £688 avg
#  - At Risk: 430 customers, £1,217 avg spend, recency dropping (win-back target)
#  - Retention: 100% month 0 -> ~20-35% month 1; 2009-12 cohort holds 30-50% for a year

st.markdown(
    """
- **Champions drive most of the revenue.** They're 1,544 customers (26% of the base)
  but account for £12.4M of £17.7M total revenue — roughly 70% of revenue from about
  a quarter of customers.
- **Nearly half the base has gone quiet.** 2,792 customers (about 47%) fall into
  Lost / Hibernating, contributing only £1.9M (~11%) of revenue at £688 average spend.
- **At Risk is the win-back target.** 430 customers with £1,217 average spend and
  declining recency — recent enough to re-engage, valuable enough to be worth it.
    """
)

