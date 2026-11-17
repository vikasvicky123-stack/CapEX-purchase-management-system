
import streamlit as st
import pandas as pd

from database.db import initialize_database, get_connection
from modules.purchase_request.pr import purchase_request_page
from modules.budgeting.budget import budget_management_page


st.set_page_config(
    page_title="CapEx Management System",
    page_icon="📊",
    layout="wide"
)

initialize_database()


# ---------------- DATABASE DASHBOARD FUNCTIONS ----------------

def get_table_names(conn):
    result = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    return [row[0] for row in result]


def get_table_columns(conn, table_name):
    result = conn.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()

    return [row[1] for row in result]


def get_table_count(conn, table_name):
    return conn.execute(
        f'SELECT COUNT(*) FROM "{table_name}"'
    ).fetchone()[0]


def get_dashboard_data():

    conn = get_connection()

    try:
        tables = get_table_names(conn)

        # Total Purchase Requests
        total_requests = 0

        if "purchase_requests" in tables:
            total_requests = get_table_count(
                conn, "purchase_requests"
            )

        # Pending Approvals
        pending_approvals = 0
        approval_column_found = False

        if "purchase_requests" in tables:

            columns = get_table_columns(
                conn, "purchase_requests"
            )

            status_column = next(
                (
                    col for col in columns
                    if col.lower() in [
                        "status",
                        "approval_status",
                        "request_status"
                    ]
                ),
                None
            )

            if status_column:
                approval_column_found = True

                pending_approvals = conn.execute(
                    f'''
                    SELECT COUNT(*)
                    FROM purchase_requests
                    WHERE LOWER("{status_column}") IN
                    ('pending', 'submitted', 'awaiting approval')
                    '''
                ).fetchone()[0]

        # Total Budget
        total_budget = 0

        if "budgets" in tables:

            budget_columns = get_table_columns(
                conn, "budgets"
            )

            amount_column = next(
                (
                    col for col in budget_columns
                    if col.lower() in [
                        "amount",
                        "budget_amount",
                        "allocated_amount"
                    ]
                ),
                None
            )

            if amount_column:
                total_budget = conn.execute(
                    f'SELECT COALESCE(SUM("{amount_column}"), 0) FROM budgets'
                ).fetchone()[0]

        # Total Expenditure
        total_expenditure = 0

        if "budget_transactions" in tables:

            transaction_columns = get_table_columns(
                conn, "budget_transactions"
            )

            expenditure_column = next(
                (
                    col for col in transaction_columns
                    if col.lower() in [
                        "amount",
                        "expenditure",
                        "expense_amount"
                    ]
                ),
                None
            )

            if expenditure_column:
                total_expenditure = conn.execute(
                    f'''
                    SELECT COALESCE(SUM("{expenditure_column}"), 0)
                    FROM budget_transactions
                    '''
                ).fetchone()[0]

        # Budget Utilisation
        if total_budget > 0:
            budget_utilised = (
                total_expenditure / total_budget
            ) * 100
        else:
            budget_utilised = 0

        # Total Assets
        total_assets = 0

        asset_tables = [
            table for table in tables
            if table.lower() in [
                "assets",
                "asset_inventory",
                "asset_register"
            ]
        ]

        if asset_tables:
            total_assets = get_table_count(
                conn, asset_tables[0]
            )

        return (
            total_requests,
            pending_approvals,
            budget_utilised,
            total_assets,
            approval_column_found,
            total_budget,
            total_expenditure
        )

    finally:
        conn.close()


# ---------------- SIDEBAR NAVIGATION ----------------

st.sidebar.title("CAPEX MANAGEMENT")
st.sidebar.caption("Purchase Management System")

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Purchase Requests",
        "Budget Management",
        "Accounting & Depreciation",
        "Asset Inventory",
        "AI Processing"
    ]
)


# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.title("CapEx Management Dashboard")

    st.write(
        "Centralised management of capital expenditure requests, "
        "budgets, purchases and assets."
    )

    (
        total_requests,
        pending_approvals,
        budget_utilised,
        total_assets,
        approval_column_found,
        total_budget,
        total_expenditure
    ) = get_dashboard_data()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Requests",
        total_requests
    )

    col2.metric(
        "Pending Approvals",
        pending_approvals
    )

    col3.metric(
        "Budget Utilised",
        f"{budget_utilised:.1f}%"
    )

    col4.metric(
        "Total Assets",
        total_assets
    )

    st.divider()

    st.subheader("Budget Summary")

    budget_col1, budget_col2, budget_col3 = st.columns(3)

    budget_col1.metric(
        "Total Allocated Budget",
        f"₹{total_budget:,.2f}"
    )

    budget_col2.metric(
        "Total Expenditure",
        f"₹{total_expenditure:,.2f}"
    )

    available_budget = total_budget - total_expenditure

    budget_col3.metric(
        "Available Budget",
        f"₹{available_budget:,.2f}"
    )

    st.divider()

    st.subheader("System Information")

    st.success(
        "Dashboard data is retrieved from the application database."
    )

    if not approval_column_found:
        st.info(
            "Pending approval count is shown as 0 because "
            "the current purchase request database does not "
            "contain a recognised approval status field."
        )

    if not total_budget:
        st.info(
            "Allocate a budget in Budget Management "
            "to view budget utilisation."
        )


# ---------------- PURCHASE REQUESTS ----------------

elif page == "Purchase Requests":

    purchase_request_page()


# ---------------- BUDGET MANAGEMENT ----------------

elif page == "Budget Management":

    budget_management_page()


# ---------------- ACCOUNTING ----------------

elif page == "Accounting & Depreciation":

    from modules.accounting.accounting import accounting_page

    accounting_page()


# ---------------- ASSET INVENTORY ----------------

elif page == "Asset Inventory":

    from modules.asset_inventory.assets import asset_inventory_page

    asset_inventory_page()


# ---------------- AI PROCESSING ----------------

elif page == "AI Processing":

    from modules.ai_features.classification import classification_page
    from modules.ai_features.invoice_ocr import invoice_ocr_page

    tab1, tab2 = st.tabs(
        [
            "CapEx Classification",
            "Invoice OCR & JSON"
        ]
    )

    with tab1:
        classification_page()

    with tab2:
        invoice_ocr_page()
