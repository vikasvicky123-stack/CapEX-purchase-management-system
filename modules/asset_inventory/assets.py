import streamlit as st
from database.db import get_connection


def initialize_asset_table():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS asset_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code TEXT UNIQUE,
            asset_name TEXT,
            category TEXT,
            department TEXT,
            project_code TEXT,
            purchase_value REAL,
            location TEXT,
            status TEXT DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_asset(data):

    conn = get_connection()

    conn.execute("""
        INSERT INTO asset_inventory (
            asset_code,
            asset_name,
            category,
            department,
            project_code,
            purchase_value,
            location,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["asset_code"],
        data["asset_name"],
        data["category"],
        data["department"],
        data["project_code"],
        data["purchase_value"],
        data["location"],
        data["status"]
    ))

    conn.commit()
    conn.close()


def get_assets():

    conn = get_connection()

    assets = conn.execute("""
        SELECT * FROM asset_inventory
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return assets


def update_asset_status(asset_id, status):

    conn = get_connection()

    conn.execute("""
        UPDATE asset_inventory
        SET status = ?
        WHERE id = ?
    """, (status, asset_id))

    conn.commit()
    conn.close()


def asset_inventory_page():

    initialize_asset_table()

    st.title("Asset Inventory")

    st.write(
        "Register, monitor and manage capital expenditure assets."
    )

    tab1, tab2, tab3 = st.tabs([
        "Asset Overview",
        "Add Asset",
        "Asset Register"
    ])

    # ASSET OVERVIEW

    assets = get_assets()

    with tab1:

        st.subheader("Asset Overview")

        total_assets = len(assets)

        available = sum(
            1 for asset in assets if asset[8] == "Available"
        )

        in_use = sum(
            1 for asset in assets if asset[8] == "In Use"
        )

        maintenance = sum(
            1 for asset in assets
            if asset[8] == "Under Maintenance"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Assets", total_assets)
        col2.metric("Available Assets", available)
        col3.metric("Assets In Use", in_use)
        col4.metric("Under Maintenance", maintenance)

        st.divider()

        if assets:

            st.subheader("Department-wise Asset Summary")

            departments = {}

            for asset in assets:

                department = asset[4]

                departments[department] = (
                    departments.get(department, 0) + 1
                )

            for department, count in departments.items():

                st.write(f"**{department}:** {count} assets")

        else:

            st.info("No assets have been registered yet.")

    # ADD ASSET

    with tab2:

        st.subheader("Register New Asset")

        with st.form("add_asset_form"):

            asset_code = st.text_input("Asset ID")

            asset_name = st.text_input("Asset Name")

            category = st.selectbox(
                "Asset Category",
                [
                    "Computer/Laptop",
                    "Hardware Components",
                    "Software",
                    "Machinery/Equipment",
                    "Office Equipment",
                    "Other"
                ]
            )

            department = st.selectbox(
                "Department",
                [
                    "R&D",
                    "IT",
                    "Operations",
                    "Administration",
                    "Other"
                ]
            )

            project_code = st.text_input("Project Code")

            purchase_value = st.number_input(
                "Purchase Value (₹)",
                min_value=0.0,
                step=1000.0
            )

            location = st.text_input("Asset Location")

            status = st.selectbox(
                "Asset Status",
                ["Available", "In Use", "Under Maintenance"]
            )

            submit = st.form_submit_button("Register Asset")

            if submit:

                if not asset_code.strip():

                    st.error("Enter an Asset ID.")

                elif not asset_name.strip():

                    st.error("Enter an Asset Name.")

                elif purchase_value <= 0:

                    st.error("Enter a valid purchase value.")

                else:

                    try:

                        save_asset({
                            "asset_code": asset_code.strip(),
                            "asset_name": asset_name.strip(),
                            "category": category,
                            "department": department,
                            "project_code": project_code.strip(),
                            "purchase_value": purchase_value,
                            "location": location.strip(),
                            "status": status
                        })

                        st.success("Asset registered successfully!")

                        st.rerun()

                    except Exception as error:

                        if "UNIQUE constraint failed" in str(error):

                            st.error(
                                "This Asset ID already exists. "
                                "Enter a different Asset ID."
                            )

                        else:

                            st.error(f"Unable to register asset: {error}")

    # ASSET REGISTER

    with tab3:

        st.subheader("Asset Register")

        assets = get_assets()

        if assets:

            for asset in assets:

                with st.expander(
                    f"{asset[2]} - {asset[1]}"
                ):

                    st.write(f"**Asset ID:** {asset[1]}")
                    st.write(f"**Asset Name:** {asset[2]}")
                    st.write(f"**Category:** {asset[3]}")
                    st.write(f"**Department:** {asset[4]}")
                    st.write(f"**Project Code:** {asset[5]}")

                    st.write(
                        f"**Purchase Value:** ₹{asset[6]:,.2f}"
                    )

                    st.write(f"**Location:** {asset[7]}")
                    st.write(f"**Current Status:** {asset[8]}")

                    st.divider()

                    new_status = st.selectbox(
                        "Update Asset Status",
                        [
                            "Available",
                            "In Use",
                            "Under Maintenance"
                        ],
                        index=[
                            "Available",
                            "In Use",
                            "Under Maintenance"
                        ].index(asset[8]),
                        key=f"status_{asset[0]}"
                    )

                    if st.button(
                        "Update Status",
                        key=f"update_{asset[0]}"
                    ):

                        update_asset_status(
                            asset[0],
                            new_status
                        )

                        st.success("Asset status updated!")

                        st.rerun()

        else:

            st.info("No assets have been registered yet.")