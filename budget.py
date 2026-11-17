import streamlit as st

from database.db import (
    save_budget,
    get_budgets,
    record_expenditure,
    save_budget_exception,
    get_budget_exceptions,
    update_exception_status
)


def budget_management_page():

    st.title("Budget Management")
    st.write(
        "Allocate, monitor and manage departmental "
        "capital expenditure budgets."
    )

    departments = [
        "R&D",
        "IT",
        "Operations",
        "Administration",
        "Other"
    ]

    tab1, tab2, tab3, tab4 = st.tabs([
        "Budget Overview",
        "Allocate Budget",
        "Record Expenditure",
        "Budget Exceptions"
    ])

    # --------------------------------
    # TAB 1: BUDGET OVERVIEW
    # --------------------------------

    with tab1:

        st.subheader("Department-wise Budget Overview")

        budgets = get_budgets()

        if budgets:

            total_allocated = sum(row[1] for row in budgets)
            total_utilised = sum(row[2] for row in budgets)
            available = total_allocated - total_utilised

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Allocated",
                f"₹{total_allocated:,.2f}"
            )

            col2.metric(
                "Total Utilised",
                f"₹{total_utilised:,.2f}"
            )

            col3.metric(
                "Available Budget",
                f"₹{available:,.2f}"
            )

            st.divider()

            for department, allocated, utilised in budgets:

                remaining = allocated - utilised

                st.write(f"### {department}")

                col1, col2, col3 = st.columns(3)

                col1.write(f"Allocated: ₹{allocated:,.2f}")
                col2.write(f"Utilised: ₹{utilised:,.2f}")
                col3.write(f"Available: ₹{remaining:,.2f}")

                if allocated > 0:
                    progress = min(utilised / allocated, 1.0)
                    st.progress(progress)

        else:
            st.info(
                "No departmental budgets have been allocated yet."
            )

    # --------------------------------
    # TAB 2: ALLOCATE BUDGET
    # --------------------------------

    with tab2:

        st.subheader("Allocate Departmental Budget")

        with st.form("allocate_budget_form"):

            department = st.selectbox(
                "Select Department",
                departments
            )

            amount = st.number_input(
                "Budget Allocation Amount (₹)",
                min_value=0.0,
                step=10000.0
            )

            submit = st.form_submit_button(
                "Allocate Budget"
            )

            if submit:

                if amount > 0:

                    save_budget(department, amount)

                    st.success(
                        f"Budget of ₹{amount:,.2f} "
                        f"allocated to {department}."
                    )

                    st.rerun()

                else:
                    st.error("Enter a valid budget amount.")

    # --------------------------------
    # TAB 3: RECORD EXPENDITURE
    # --------------------------------

    with tab3:

        st.subheader("Record Departmental Expenditure")

        budgets = get_budgets()

        if budgets:

            with st.form("record_expenditure_form"):

                department = st.selectbox(
                    "Select Department",
                    [row[0] for row in budgets]
                )

                description = st.text_input(
                    "Expenditure Description"
                )

                amount = st.number_input(
                    "Expenditure Amount (₹)",
                    min_value=0.0,
                    step=1000.0
                )

                submit = st.form_submit_button(
                    "Record Expenditure"
                )

                if submit:

                    selected_budget = next(
                        row for row in budgets
                        if row[0] == department
                    )

                    available = selected_budget[1] - selected_budget[2]

                    if not description.strip():
                        st.error("Enter an expenditure description.")

                    elif amount <= 0:
                        st.error("Enter a valid expenditure amount.")

                    elif amount > available:
                        st.error(
                            "Insufficient available budget. "
                            "Use Budget Exceptions for additional funding."
                        )

                    else:

                        record_expenditure(
                            department,
                            description,
                            amount
                        )

                        st.success(
                            f"Expenditure of ₹{amount:,.2f} "
                            f"recorded for {department}."
                        )

                        st.rerun()

        else:
            st.info(
                "Allocate a departmental budget before recording expenditure."
            )

    # --------------------------------
    # TAB 4: BUDGET EXCEPTIONS
    # --------------------------------

    with tab4:

        st.subheader("Budget Exception Management")

        budgets = get_budgets()

        if budgets:

            st.write(
                "Submit a budget exception when a purchase "
                "requirement exceeds the available departmental budget."
            )

            with st.form("budget_exception_form"):

                department = st.selectbox(
                    "Select Department",
                    [row[0] for row in budgets],
                    key="exception_department"
                )

                description = st.text_input(
                    "Purchase Requirement Description"
                )

                requested_amount = st.number_input(
                    "Requested Amount (₹)",
                    min_value=0.0,
                    step=10000.0
                )

                submit = st.form_submit_button(
                    "Submit Budget Exception"
                )

                if submit:

                    selected_budget = next(
                        row for row in budgets
                        if row[0] == department
                    )

                    available_amount = (
                        selected_budget[1] - selected_budget[2]
                    )

                    if not description.strip():
                        st.error(
                            "Enter the purchase requirement description."
                        )

                    elif requested_amount <= 0:
                        st.error(
                            "Enter a valid requested amount."
                        )

                    elif requested_amount <= available_amount:
                        st.warning(
                            "The requested amount is within the available "
                            "budget. A budget exception is not required."
                        )

                    else:

                        save_budget_exception(
                            department,
                            description,
                            requested_amount,
                            available_amount
                        )

                        st.success(
                            "Budget exception submitted successfully "
                            "for review."
                        )

                        st.rerun()

        else:

            st.info(
                "Allocate a departmental budget before creating "
                "a budget exception."
            )

        st.divider()

        st.subheader("Recorded Budget Exceptions")

        exceptions = get_budget_exceptions()

        if exceptions:

            for exception in exceptions:

                exception_id = exception[0]
                department = exception[1]
                description = exception[2]
                requested = exception[3]
                available = exception[4]
                status = exception[5]
                created_at = exception[6]

                with st.expander(
                    f"{department} - Exception #{exception_id}"
                ):

                    st.write(f"**Description:** {description}")

                    st.write(
                        f"**Requested Amount:** ₹{requested:,.2f}"
                    )

                    st.write(
                        f"**Available Budget:** ₹{available:,.2f}"
                    )

                    st.write(f"**Status:** {status}")

                    st.write(f"**Created At:** {created_at}")

                    if status == "Pending":

                        new_status = st.selectbox(
                            "Review Status",
                            ["Pending", "Under Review", "Approved", "Rejected"],
                            key=f"status_{exception_id}"
                        )

                        if st.button(
                            "Update Status",
                            key=f"update_{exception_id}"
                        ):

                            update_exception_status(
                                exception_id,
                                new_status
                            )

                            st.success("Exception status updated.")

                            st.rerun()

        else:

            st.info("No budget exceptions recorded.")