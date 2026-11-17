import streamlit as st


def classify_capex(item_name, category, purpose, useful_life):

    item = item_name.lower()
    purpose_text = purpose.lower()

    non_capex_keywords = [
        "repair",
        "maintenance",
        "replacement part",
        "stationery",
        "consumable",
        "cleaning",
        "office supplies"
    ]

    for keyword in non_capex_keywords:

        if keyword in item or keyword in purpose_text:

            return (
                "Potential Non-CapEx",
                "The description suggests a routine expense, "
                "repair, maintenance or consumable purchase."
            )

    asset_keywords = [
        "computer",
        "laptop",
        "printer",
        "scanner",
        "machinery",
        "equipment",
        "server",
        "furniture",
        "hardware",
        "production machine"
    ]

    if any(keyword in item for keyword in asset_keywords):

        if useful_life >= 1:

            return (
                "Potential CapEx",
                "The item appears to be a long-term asset "
                "that may provide benefits over multiple periods."
            )

    if useful_life >= 2:

        return (
            "Potential CapEx",
            "The stated useful life suggests a possible "
            "long-term asset."
        )

    return (
        "Requires Further Review",
        "There is insufficient information to classify "
        "this purchase confidently."
    )


def classification_page():

    st.title("AI-Assisted CapEx Classification")

    st.write(
        "Analyse purchase requirements and generate "
        "a preliminary CapEx classification recommendation."
    )

    st.info(
        "This prototype uses predefined classification rules. "
        "Recommendations require authorised human verification."
    )

    st.divider()

    st.subheader("Purchase Request Details")

    with st.form("capex_classification_form"):

        item_name = st.text_input(
            "Item Name",
            placeholder="Example: Dell Laptop"
        )

        category = st.selectbox(
            "Purchase Category",
            [
                "Computer/Laptop",
                "Hardware Components",
                "Software",
                "Machinery/Equipment",
                "Office Equipment",
                "Other"
            ]
        )

        purpose = st.text_area(
            "Purpose of Purchase",
            placeholder="Explain why this item is required."
        )

        useful_life = st.number_input(
            "Expected Useful Life (Years)",
            min_value=0,
            max_value=100,
            value=5
        )

        submit = st.form_submit_button(
            "Analyse Purchase"
        )

    if submit:

        if not item_name.strip():

            st.error("Please enter the item name.")

        elif not purpose.strip():

            st.error("Please enter the purchase purpose.")

        elif useful_life <= 0:

            st.error("Please enter a valid useful life.")

        else:

            result, reason = classify_capex(
                item_name,
                category,
                purpose,
                useful_life
            )

            st.divider()

            st.subheader("Classification Result")

            if result == "Potential CapEx":

                st.success(result)

            elif result == "Potential Non-CapEx":

                st.warning(result)

            else:

                st.info(result)

            st.write("**Reason for Recommendation:**")

            st.write(reason)

            st.warning(
                "Final classification must be verified "
                "by an authorised person based on the "
                "organisation's accounting policy."
            )