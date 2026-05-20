import altair as alt
import pandas as pd
import streamlit as st

from services import dashboard_service as dash_srv
from utils.ui_helpers import css_style, metric_card, render_sidebar

st.set_page_config(
    page_title="LTO Dashboard", layout="wide", initial_sidebar_state="expanded"
)
css_style(__file__)
render_sidebar()


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


data = load_dashboard_data()

st.title("System Overview")
st.markdown("Real-time performance metrics for the Land Transportation Office")

st.markdown("---")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        metric_card(
            "Vehicle Owners",
            f"{data['total_drivers']:,}",
            "↑ Registered Drivers",
            "#1f77b4",
            "#2e8b57",
        ),
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        metric_card(
            "Active Registrations",
            f"{data['active_regs']:,}",
            "↑ Registered Vehicles",
            "#17becf",
            "#2e8b57",
        ),
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        metric_card(
            "Total Revenue",
            f"₱{data['revenue']:,.2f}",
            "↑ Collected Fines",
            "#ff7f0e",
            "#2e8b57",
        ),
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        metric_card(
            "Pending Violations",
            f"{data['pending_vios']:,}",
            "↑ Unpaid Tickets",
            "#d62728",
            "#ff4b4b",
        ),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

col_chart, col_cards = st.columns([2.5, 1])

with col_chart:
    st.subheader("Monthly Registration Trend (Current Year)")

    trend_records = data["trend_data"]
    if not trend_records:
        st.info("No registration data available for the current year.")
    else:
        df_trend = pd.DataFrame(trend_records)
        df_trend.rename(columns={"count": "Registrations"}, inplace=True)

        month_order = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        chart = (
            alt.Chart(df_trend)
            .mark_bar()
            .encode(
                x=alt.X("month", sort=month_order, title="Month"),
                y=alt.Y("Registrations", title="Registrations"),
            )
            .properties(height=420)
        )

        st.altair_chart(chart, use_container_width=True)

with col_cards:
    st.subheader("System Insights")

    # CARD 1: Expiring Licenses (Red Border)
    st.markdown(
        metric_card(
            "Licenses Expiring Soon",
            f"{data['expiring_licenses']:,}",
            "Within 30 days",
            "#ff4b4b",
        ),
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    # CARD 2: Violations Resolved (Green Border)
    st.markdown(
        metric_card(
            "Violations Resolved",
            f"{data['resolved_vios']:,}",
            "Paid/Settled",
            "#2e8b57",
        ),
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    # CARD 3: Average Fine Amount (Blue Border)
    st.markdown(
        metric_card(
            "Average Fine Amount",
            f"₱{data['avg_fine']:,.2f}",
            "Per violation",
            "#1f77b4",
        ),
        unsafe_allow_html=True,
    )
