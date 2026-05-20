import streamlit as st
import pandas as pd
import altair as alt
from utils.ui_helpers import css_style, render_sidebar, render_page_header
from services import dashboard_service as dash_srv

st.set_page_config(page_title="LTO Dashboard", layout="wide", initial_sidebar_state="expanded")
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
        "trend_data": dash_srv.get_monthly_registration_trend()
    }

data = load_dashboard_data()

render_page_header(
    title="📊 System Overview",
    subtitle="Real-time performance metrics for the Land Transportation Office",
)

st.markdown("---")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; border-top: 5px solid #1f77b4; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2); border-bottom: 1px solid rgba(128,128,128,0.2);">
        <p style="margin: 0; font-size: 12px; font-weight: 600; text-transform: uppercase; opacity: 0.7;">👥 Vehicle Owners </p>
        <h2 style="margin: 5px 0 0 0; font-size: 2rem;">{data['total_drivers']:,}</h2>
        <p style="margin: 5px 0 0 0; font-size: 13px; color: #2e8b57; font-weight: 600;">↑ Registered Drivers</p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; border-top: 5px solid #17becf; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2); border-bottom: 1px solid rgba(128,128,128,0.2);">
        <p style="margin: 0; font-size: 12px; font-weight: 600; text-transform: uppercase; opacity: 0.7;">📝 Active Registrations</p>
        <h2 style="margin: 5px 0 0 0; font-size: 2rem;">{data['active_regs']:,}</h2>
        <p style="margin: 5px 0 0 0; font-size: 13px; color: #2e8b57; font-weight: 600;">↑ Registered Vehicles</p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; border-top: 5px solid #ff7f0e; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2); border-bottom: 1px solid rgba(128,128,128,0.2);">
        <p style="margin: 0; font-size: 12px; font-weight: 600; text-transform: uppercase; opacity: 0.7;">💰 Total Revenue</p>
        <h2 style="margin: 5px 0 0 0; font-size: 2rem;">₱{data['revenue']:,.2f}</h2>
        <p style="margin: 5px 0 0 0; font-size: 13px; color: #2e8b57; font-weight: 600;">↑ Collected Fines</p>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; border-top: 5px solid #d62728; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2); border-bottom: 1px solid rgba(128,128,128,0.2);">
        <p style="margin: 0; font-size: 12px; font-weight: 600; text-transform: uppercase; opacity: 0.7;">⚠️ Pending Violations</p>
        <h2 style="margin: 5px 0 0 0; font-size: 2rem;">{data['pending_vios']:,}</h2>
        <p style="margin: 5px 0 0 0; font-size: 13px; color: #ff4b4b; font-weight: 600;">↑ Unpaid Tickets</p>
    </div>
    """, unsafe_allow_html=True)

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
        
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        chart = alt.Chart(df_trend).mark_bar().encode(
            x=alt.X('month', sort=month_order, title="Month"),
            y=alt.Y('Registrations', title="Registrations")
        ).properties(height=420)
        
        st.altair_chart(chart, use_container_width=True)

with col_cards:
    st.subheader("System Insights")
    
    # CARD 1: Expiring Licenses (Red Border)
    html_card_1 = f"""
    <div style="padding: 15px; border-radius: 8px; border-top: 5px solid #ff4b4b; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2); border-bottom: 1px solid rgba(128,128,128,0.2); margin-bottom: 15px;">
        <p style="margin: 0; font-size: 14px; font-weight: 600; text-transform: uppercase; opacity: 0.7;">Licenses Expiring Soon</p>
        <h2 style="margin: 5px 0 0 0; font-size: 2rem;">{data['expiring_licenses']:,}</h2>
        <p style="margin: 0; font-size: 12px; opacity: 0.6;">Within 30 days</p>
    </div>
    """
    st.markdown(html_card_1, unsafe_allow_html=True)
    
    # CARD 2: Violations Resolved (Green Border)
    html_card_2 = f"""
    <div style="padding: 15px; border-radius: 8px; border-top: 5px solid #2e8b57; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2); border-bottom: 1px solid rgba(128,128,128,0.2); margin-bottom: 15px;">
        <p style="margin: 0; font-size: 14px; font-weight: 600; text-transform: uppercase; opacity: 0.7;">Violations Resolved</p>
        <h2 style="margin: 5px 0 0 0; font-size: 2rem;">{data['resolved_vios']:,}</h2>
        <p style="margin: 0; font-size: 12px; opacity: 0.6;">Paid/Settled</p>
    </div>
    """
    st.markdown(html_card_2, unsafe_allow_html=True)

    # CARD 3: Average Fine Amount (Blue Border)
    html_card_3 = f"""
    <div style="padding: 15px; border-radius: 8px; border-top: 5px solid #1f77b4; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2); border-bottom: 1px solid rgba(128,128,128,0.2); margin-bottom: 15px;">
        <p style="margin: 0; font-size: 14px; font-weight: 600; text-transform: uppercase; opacity: 0.7;">Average Fine Amount</p>
        <h2 style="margin: 5px 0 0 0; font-size: 2rem;">₱{data['avg_fine']:,.2f}</h2>
        <p style="margin: 0; font-size: 12px; opacity: 0.6;">Per violation</p>
    </div>
    """
    st.markdown(html_card_3, unsafe_allow_html=True)