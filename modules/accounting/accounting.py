import streamlit as st
from datetime import date
from database.db import get_connection


def initialize_accounting_table():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounting_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_code TEXT,
            asset_name TEXT,
            department TEXT,
            purchase_value REAL,
            salvage_value REAL,
            useful_life INTEGER,
            purchase_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_accounting_record(
    project_code, asset_name, department,
    purchase_value, salvage_value,
    useful_life, purchase_date
):

    conn = get_connection()

    conn.execute("""
        INSERT INTO accounting_records (
            project_code, asset_name, department,
            purchase_value, salvage_value,
            useful_life, purchase_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        project_code, asset_name, department,
        purchase_value, salvage_value,
        useful_life, str(purchase_date)
    ))

    conn.commit()
    conn.close()


def get_accounting_records():

    conn = get_connection()

    records = conn.execute("""
        SELECT * FROM accounting_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return records


def calculate_depreciation(
    purchase_value,
    salvage_value,
    useful_life,
    purchase_date,
    calculation_date
):

    annual_depreciation = (
        purchase_value - salvage_value
    ) / useful_life

    days_used = max(
        (calculation_date - purchase_date).days, 0
    )

    years_used = days_used / 365.25

    accumulated_depreciation = min(
        annual_depreciation * years_used,
        purchase_value - salvage_value
    )

    book_value = (
        purchase_value - accumulated_depreciation
    )

    return (
        annual_depreciation,
        accumulated_depreciation,
        book_value
    )


def accounting_page():

    initialize_accounting_table()

    st.title("Accounting & Depreciation")

    st.write(
        "Manage capital expenditure purchase records, "
        "project codes and asset depreciation."
    )

    tab1, tab2, tab3 = st.tabs([
        "Record Purchase",
        "Accounting Records",
        "Depreciation Tracking"
    ])

    departments = [
        "R&D",
        "IT",
        "Operations",
        "Administration",
        "Other"
    ]

    # RECORD PURCHASE

    with tab1:

        st.subheader("Record Capital Expenditure Purchase")

        with st.form("accounting_form"):

            project_code = st.text_input("Project Code")

            asset_name = st.text_input("Asset Name")

            department = st.selectbox(
                "Department", departments
            )

            purchase_value = st.number_input(
                "Purchase Value (₹)",
                min_value=0.0,
                step=10000.0
            )

            salvage_value = st.number_input(
                "Salvage Value (₹)",
                min_value=0.0,
                step=1000.0
            )

            useful_life = st.number_input(
                "Useful Life (Years)",
                min_value=1,
                max_value=100,
                value=5
            )

            purchase_date = st.date_input(
                "Purchase Date",
                value=date.today(),
                max_value=date.today()
            )

            submit = st.form_submit_button(
                "Save Purchase Record"
            )

            if submit:

                if not project_code.strip():
                    st.error("Enter a project code.")

                elif not asset_name.strip():
                    st.error("Enter an asset name.")

                elif purchase_value <= 0:
                    st.error("Enter a valid purchase value.")

                elif salvage_value > purchase_value:
                    st.error(
                        "Salvage value cannot exceed purchase value."
                    )

                else:

                    save_accounting_record(
                        project_code,
                        asset_name,
                        department,
                        purchase_value,
                        salvage_value,
                        useful_life,
                        purchase_date
                    )

                    st.success("Purchase record saved successfully!")

                    st.rerun()

    records = get_accounting_records()

    # ACCOUNTING RECORDS

    with tab2:

        st.subheader("Accounting & Depreciation Records")

        if records:

            for record in records:

                record_id = record[0]
                project_code = record[1]
                asset_name = record[2]
                department = record[3]
                purchase_value = record[4]
                salvage_value = record[5]
                useful_life = record[6]
                purchase_date = date.fromisoformat(record[7])

                annual_dep, accumulated_dep, book_value = (
                    calculate_depreciation(
                        purchase_value,
                        salvage_value,
                        useful_life,
                        purchase_date,
                        date.today()
                    )
                )

                with st.expander(
                    f"{asset_name} - {project_code}"
                ):

                    st.write(f"**Record ID:** {record_id}")
                    st.write(f"**Project Code:** {project_code}")
                    st.write(f"**Department:** {department}")
                    st.write(f"**Purchase Date:** {purchase_date}")

                    st.write(
                        f"**Purchase Value:** ₹{purchase_value:,.2f}"
                    )

                    st.write(
                        f"**Salvage Value:** ₹{salvage_value:,.2f}"
                    )

                    st.write(f"**Useful Life:** {useful_life} years")

                    st.divider()

                    st.write(
                        f"**Annual Depreciation:** ₹{annual_dep:,.2f}"
                    )

                    st.write(
                        f"**Accumulated Depreciation:** ₹{accumulated_dep:,.2f}"
                    )

                    st.write(
                        f"**Current Book Value:** ₹{book_value:,.2f}"
                    )

        else:
            st.info("No accounting records have been added yet.")

    # DEPRECIATION TRACKING

    with tab3:

        st.subheader("Asset Depreciation Tracking")

        if records:

            calculation_date = st.date_input(
                "Calculate Depreciation As Of",
                value=date.today(),
                max_value=date.today(),
                key="depreciation_date"
            )

            st.write(
                "View accumulated depreciation and remaining "
                "book value for each recorded asset."
            )

            st.divider()

            for record in records:

                record_id = record[0]
                project_code = record[1]
                asset_name = record[2]
                department = record[3]
                purchase_value = record[4]
                salvage_value = record[5]
                useful_life = record[6]
                purchase_date = date.fromisoformat(record[7])

                annual_dep, accumulated_dep, book_value = (
                    calculate_depreciation(
                        purchase_value,
                        salvage_value,
                        useful_life,
                        purchase_date,
                        calculation_date
                    )
                )

                with st.expander(
                    f"{asset_name} - {project_code}"
                ):

                    st.write(f"**Department:** {department}")

                    st.write(
                        f"**Purchase Value:** ₹{purchase_value:,.2f}"
                    )

                    st.write(
                        f"**Annual Depreciation:** ₹{annual_dep:,.2f}"
                    )

                    st.write(
                        f"**Accumulated Depreciation:** ₹{accumulated_dep:,.2f}"
                    )

                    st.write(
                        f"**Remaining Book Value:** ₹{book_value:,.2f}"
                    )

                    st.write(
                        f"**Calculation Date:** {calculation_date}"
                    )

                    st.progress(
                        min(
                            accumulated_dep /
                            max(purchase_value - salvage_value, 1),
                            1.0
                        )
                    )

        else:

            st.info(
                "Add purchase records to start depreciation tracking."
            )