import streamlit as st
import pandas as pd
import uuid

from database.db import save_request, get_requests


def purchase_request_page():

    st.title("Purchase Request Management")

    st.write("Create and manage capital expenditure purchase requests.")

    tab1, tab2 = st.tabs([
        "Create Purchase Request",
        "View Requests"
    ])

    with tab1:

        st.subheader("New Purchase Request")

        with st.form("purchase_request_form"):

            col1, col2 = st.columns(2)

            with col1:
                requester = st.text_input("Requester Name")

                department = st.selectbox(
                    "Department",
                    ["R&D", "IT", "Operations", "Administration", "Other"]
                )

                item_name = st.text_input("Item Name")

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    step=1
                )

            with col2:
                category = st.selectbox(
                    "Purchase Category",
                    [
                        "Computer / Laptop",
                        "Hardware Components",
                        "Software",
                        "Machinery / Equipment",
                        "Office Equipment",
                        "Other"
                    ]
                )

                estimated_cost = st.number_input(
                    "Estimated Total Cost (₹)",
                    min_value=0.0,
                    step=1000.0
                )

                description = st.text_area("Purchase Description")

            submitted = st.form_submit_button(
                "Submit Purchase Request",
                use_container_width=True
            )

            if submitted:

                if not requester.strip() or not item_name.strip():
                    st.error("Please enter requester name and item name.")

                elif estimated_cost <= 0:
                    st.error("Please enter a valid estimated cost.")

                else:

                    request_data = {
                        "request_id": "PR-" + uuid.uuid4().hex[:6].upper(),
                        "department": department,
                        "requester": requester.strip(),
                        "item_name": item_name.strip(),
                        "description": description.strip(),
                        "quantity": quantity,
                        "estimated_cost": estimated_cost,
                        "category": category,
                        "capex_status": "Pending Classification"
                    }

                    try:
                        save_request(request_data)

                        st.success(
                            f"Request {request_data['request_id']} submitted successfully!"
                        )

                    except Exception as e:
                        st.error(f"Unable to save request: {e}")

    with tab2:

        st.subheader("Submitted Purchase Requests")

        requests = get_requests()

        if requests:

            columns = [
                "Database ID",
                "Request ID",
                "Department",
                "Requester",
                "Item",
                "Description",
                "Quantity",
                "Estimated Cost",
                "Category",
                "CapEx Classification",
                "Status",
                "Created At"
            ]

            df = pd.DataFrame(requests, columns=columns)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.metric("Total Purchase Requests", len(requests))

        else:
            st.info("No purchase requests submitted yet.")