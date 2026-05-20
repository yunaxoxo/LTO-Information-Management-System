import pandas as pd
import streamlit as st

from controllers import vehicle_controller as vc
from utils.ui_helpers import (
    apply_styler,
    color_vehicle_type,
    css_style,
    paginate_df,
    render_pagination_controls,
    safe_str,
)

st.set_page_config(page_title="Vehicle Registry", layout="wide")
css_style(__file__)

st.title("Vehicle Registry")
st.markdown(
    "Manage and monitor all registered vehicles, including ownership, type, and technical details."
)
st.markdown("---")

#  Filter option constants  #
VEHICLE_TYPE_OPTIONS = [
    "All Types",
    "Sedan",
    "SUV",
    "Hatchback",
    "MPV",
    "Pickup",
    "Van",
    "Coupe",
    "Convertible",
    "Commercial Truck",
    "Bus",
    "Light Truck",
    "Motorcycle",
    "Other",
]
TYPE_OPTS = [t for t in VEHICLE_TYPE_OPTIONS if t != "All Types"]

#  Session state  #
if "vehicle_filters" not in st.session_state:
    st.session_state.vehicle_filters = {"vehicle_type": "All Types"}
if "vehicle_page" not in st.session_state:
    st.session_state.vehicle_page = 1


def _vtype_to_backend(label: str) -> str:
    return "ALL" if label == "All Types" else label


#  DIALOGS  #


@st.dialog("Filter Vehicles")
def filter_dialog():
    st.write("Narrow results by vehicle type:")
    cur = st.session_state.vehicle_filters
    vt_idx = (
        VEHICLE_TYPE_OPTIONS.index(cur["vehicle_type"])
        if cur["vehicle_type"] in VEHICLE_TYPE_OPTIONS
        else 0
    )
    vehicle_type = st.selectbox("Vehicle Type", VEHICLE_TYPE_OPTIONS, index=vt_idx)
    if st.button("Apply Filters", use_container_width=True, type="primary"):
        st.session_state.vehicle_filters["vehicle_type"] = vehicle_type
        st.session_state.vehicle_page = 1
        st.rerun()


@st.dialog("Add New Vehicle", width="large")
def add_vehicle_dialog():
    with st.form("add_vehicle_form"):
        col1, col2 = st.columns(2)
        with col1:
            plate_number = st.text_input("Plate Number *", placeholder="ABC1234")
            engine_number = st.text_input("Engine Number *", placeholder="ENG-XXXXXXX")
            chassis_number = st.text_input(
                "Chassis Number *", placeholder="CHA-XXXXXXXXX"
            )
            make = st.text_input("Make *", placeholder="Toyota")
            model = st.text_input("Model *", placeholder="Vios")
        with col2:
            year = st.number_input(
                "Year *", min_value=1900, max_value=2027, value=2024, step=1
            )
            color = st.text_input("Color *", placeholder="Midnight Black")
            vehicle_type = st.selectbox("Vehicle Type *", TYPE_OPTS)
            license_number = st.text_input(
                "Owner License Number *", placeholder="A01-15-100001"
            )
        if st.form_submit_button(
            "Add Vehicle", use_container_width=True, type="primary"
        ):
            if not all(
                [
                    plate_number,
                    engine_number,
                    chassis_number,
                    make,
                    model,
                    color,
                    license_number,
                ]
            ):
                st.error("All fields marked with * are required.")
            else:
                try:
                    vc.create_vehicle(
                        {
                            "plate_number": plate_number.strip().upper(),
                            "engine_number": engine_number.strip().upper(),
                            "chassis_number": chassis_number.strip().upper(),
                            "make": make.strip(),
                            "model": model.strip(),
                            "year": int(year),
                            "color": color.strip(),
                            "vehicle_type": vehicle_type,
                            "license_number": license_number.strip().upper(),
                        }
                    )
                    st.success(
                        f"✅ Vehicle '{plate_number.upper()}' added successfully!"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding vehicle: {e}")


@st.dialog("Confirm Deletion")
def delete_vehicle_dialog(v):
    st.warning(
        f"This will permanently delete vehicle **{v['Plate Number']}** "
        f"({v.get('make', '')} {v.get('model', '')}) and all linked records."
    )
    if st.button("Confirm Delete", type="primary", use_container_width=True):
        try:
            vc.delete_vehicle(v["Plate Number"])
            st.success("Vehicle deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting record: {e}")


@st.dialog("Edit Vehicle Data", width="large")
def edit_vehicle_dialog(v):
    cur_type = v.get("Vehicle Type", TYPE_OPTS[0])
    type_idx = TYPE_OPTS.index(cur_type) if cur_type in TYPE_OPTS else 0
    with st.form("edit_vehicle_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Plate Number (read-only)",
                value=v.get("Plate Number", ""),
                disabled=True,
            )
            new_engine = st.text_input(
                "Engine Number", value=v.get("engine_number", "")
            )
            new_chassis = st.text_input(
                "Chassis Number", value=v.get("chassis_number", "")
            )
            new_make = st.text_input("Make", value=v.get("make", ""))
            new_model = st.text_input("Model", value=v.get("model", ""))
        with col2:
            raw_year = v.get("year", 2024)
            try:
                cur_year = int(raw_year) if raw_year else 2024
            except (ValueError, TypeError):
                cur_year = 2024
            new_year = st.number_input(
                "Year", min_value=1900, max_value=2027, value=cur_year, step=1
            )
            new_color = st.text_input("Color", value=v.get("color", ""))
            new_type = st.selectbox("Vehicle Type", TYPE_OPTS, index=type_idx)
            new_license = st.text_input(
                "Owner License Number", value=v.get("license_number", "")
            )
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                vc.update_vehicle(
                    {
                        "plate_number": v["Plate Number"],
                        "engine_number": new_engine,
                        "chassis_number": new_chassis,
                        "make": new_make,
                        "model": new_model,
                        "year": int(new_year),
                        "color": new_color,
                        "vehicle_type": new_type,
                        "license_number": new_license.strip().upper(),
                    }
                )
                st.success("✅ Vehicle updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating record: {e}")


#  Top nav bar  #
col_search, empty_space, col_filter, col_add = st.columns([4, 1.5, 1.5, 2])
with col_search:
    search_query = st.text_input(
        "Search",
        placeholder="Search by plate, make, model, or type...",
        label_visibility="collapsed",
    )
with col_filter:
    if st.button("Filter", use_container_width=True):
        filter_dialog()
with col_add:
    if st.button("Add Vehicle", use_container_width=True):
        add_vehicle_dialog()


#  Fetch data  #
f = st.session_state.vehicle_filters
try:
    vehicles = vc.get_vehicles_by_criteria(
        {
            "vehicle_type": _vtype_to_backend(f["vehicle_type"]),
        }
    )
except Exception as e:
    st.error(f"Error loading vehicles: {e}")
    vehicles = []

action_bar = st.empty()

#  Build dataframe  #
if not vehicles:
    st.info("No vehicles found matching the current filters or search query.")
else:
    df = pd.DataFrame(vehicles)

    # Rename primary display columns
    df.rename(
        columns={
            "plate_number": "Plate Number",
            "vehicle_type": "Vehicle Type",
            "engine_number": "Engine Number",
            "chassis_number": "Chassis Number",
            "license_number": "Owner License No.",
        },
        inplace=True,
    )

    # Stacked combined columns for compact display
    df["MAKE / MODEL"] = safe_str(df["make"]) + "\n" + safe_str(df["model"])
    year_str = df["year"].apply(
        lambda x: str(int(x)) if pd.notna(x) and str(x) != "" else ""
    )
    df["YEAR / COLOR"] = year_str + "\n" + safe_str(df["color"])

    if search_query:
        sq = search_query.lower()
        mask = (
            df["Plate Number"].str.lower().str.contains(sq, na=False)
            | df["make"].str.lower().str.contains(sq, na=False)
            | df["model"].str.lower().str.contains(sq, na=False)
            | df["Vehicle Type"].str.lower().str.contains(sq, na=False)
            | df["Owner License No."].str.lower().str.contains(sq, na=False)
        )
        df = df[mask]

    if df.empty:
        st.info("No vehicles found matching the current filters or search query.")
    else:
        display_cols = [
            "Plate Number",
            "Owner License No.",
            "Vehicle Type",
            "MAKE / MODEL",
            "YEAR / COLOR",
            "Engine Number",
            "Chassis Number",
        ]
        df_display = df[[c for c in display_cols if c in df.columns]].copy()

        paginated_df, start_idx, total_pages = paginate_df(
            df_display, "vehicle_page", rows_per_page=10
        )

        styler = paginated_df.style
        styler = apply_styler(styler, color_vehicle_type, subset=["Vehicle Type"])
        styled_df = styler.set_properties(
            **{"text-align": "center", "white-space": "pre-wrap"}
        )

        selection_event = st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        render_pagination_controls("vehicle_page", total_pages, paginated_df)

        selected_rows = selection_event.selection.rows
        if selected_rows:
            full_row = df.iloc[start_idx + selected_rows[0]].to_dict()

            with action_bar.container():
                with st.container(border=True):
                    c_text, c_edit, c_del = st.columns([6, 1.5, 1.5])
                    with c_text:
                        st.markdown(
                            f"**Active Record:** {full_row.get('make', '')} {full_row.get('model', '')} "
                            f"(`{full_row['Plate Number']}`)"
                        )
                    with c_edit:
                        if st.button(
                            "Edit", use_container_width=True, key="edit_vehicle"
                        ):
                            edit_vehicle_dialog(full_row)
                    with c_del:
                        if st.button(
                            "Delete",
                            type="primary",
                            use_container_width=True,
                            key="del_vehicle",
                        ):
                            delete_vehicle_dialog(full_row)
