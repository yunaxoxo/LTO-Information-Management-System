import pandas as pd
import streamlit as st

from services import dashboard_service as dash_srv
from utils.ui_helpers import css_style

# ── Page Configuration ──────────────────────────────────────────────────── #
st.set_page_config(
    page_title="LTO Dashboard", layout="wide", initial_sidebar_state="expanded"
)
css_style(__file__)


# ── Data Fetching (Cached for 60 seconds for performance) ───────────────── #
@st.cache_data(ttl=60)
def load_dashboard_data():
    return {
        "total_drivers": dash_srv.get_total_drivers(),
        "active_regs": dash_srv.get_active_registrations(),
        "revenue": dash_srv.get_total_revenue(),
        "pending_vios": dash_srv.get_pending_violations(),
        "expiring_licenses": dash_srv.get_expiring_licenses(),
        "resolved_vios": dash_srv.get_resolved_violations(),
        "avg_fine": dash_srv.get_average_fine(),
        "trend_data": dash_srv.get_monthly_registration_trend(),
    }


# Fetch the live data
data = load_dashboard_data()

# ── TOP NAVIGATION ──────────────────────────────────────────────────────── #
col_title, col_profile = st.columns([8, 1])
with col_title:
    st.title("System Overview")
    st.markdown("Real-time performance metrics for the Land Transportation Office")

st.markdown("---")

# ── ROW 1: KPI METRICS ──────────────────────────────────────────────────── #
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        label="TOTAL REGISTERED DRIVERS",
        value=f"{data['total_drivers']:,}",
        delta="Live Data",
    )
with m2:
    st.metric(
        label="ACTIVE REGISTRATIONS",
        value=f"{data['active_regs']:,}",
        delta="Stable",
        delta_color="off",
    )
with m3:
    st.metric(
        label="TOTAL REVENUE (PHP)",
        value=f"₱{data['revenue']:,.2f}",
        delta="Collected Fines",
        delta_color="off",
    )
with m4:
    st.metric(
        label="PENDING VIOLATIONS",
        value=f"{data['pending_vios']:,}",
        delta="Unpaid Tickets",
        delta_color="inverse",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── ROW 2: CHART & STACKED CARDS ────────────────────────────────────────── #
col_chart, col_cards = st.columns([2.5, 1])

with col_chart:
    st.subheader("Monthly Registration Trend (Current Year)")

    # Process chart data
    trend_records = data["trend_data"]
    if not trend_records:
        st.info("No registration data available for the current year.")
    else:
        # Convert DB dicts to a pandas DataFrame and set the month as the index
        df_trend = pd.DataFrame(trend_records)
        df_trend.set_index("month", inplace=True)
        # Rename column for a cleaner chart legend
        df_trend.rename(columns={"count": "Registrations"}, inplace=True)

        st.line_chart(df_trend, use_container_width=True, height=420)

with col_cards:
    st.subheader("System Insights")

    with st.container(border=True):
        st.metric(
            label="Licenses Expiring Soon",
            value=f"{data['expiring_licenses']:,}",
            delta="Within 30 days",
            delta_color="inverse" if data["expiring_licenses"] > 0 else "off",
        )

    with st.container(border=True):
        st.metric(
            label="Violations Resolved",
            value=f"{data['resolved_vios']:,}",
            delta="Paid/Settled",
        )

    with st.container(border=True):
        st.metric(
            label="Average Fine Amount",
            value=f"₱{data['avg_fine']:,.2f}",
            delta="Per violation",
            delta_color="off",
        )
