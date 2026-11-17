import streamlit as st
import pytesseract
import json
import re
from PIL import Image

# Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_invoice_text(image):
    return pytesseract.image_to_string(image, config="--psm 6")


def extract_invoice_details(text):

    details = {
        "invoice_number": None,
        "invoice_date": None,
        "supplier_name": None,
        "total_amount": None
    }

    # Extract invoice number
    match = re.search(
        r"Invoice\s*(?:No|Number)\s*[:.]?\s*([A-Z0-9/-]+)",
        text,
        re.IGNORECASE
    )

    if match:
        details["invoice_number"] = match.group(1).strip()

    # Extract invoice date
    match = re.search(
        r"Invoice\s*Date\s*[:.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        text,
        re.IGNORECASE
    )

    if match:
        details["invoice_date"] = match.group(1).strip()

    # Extract supplier name
    match = re.search(
        r"Supplier\s*:\s*(.*?)(?=\s+Invoice\s*(?:No|Number)|\n|$)",
        text,
        re.IGNORECASE
    )

    if match:
        supplier = match.group(1).strip()
        supplier = re.sub(r"[^A-Za-z0-9&.,() -]", "", supplier)
        details["supplier_name"] = supplier.strip()

    # Extract total amount
    match = re.search(
        r"Total\s*Amount[^\d]{0,30}([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )

    if match:
        amount = match.group(1).replace(",", "")
        details["total_amount"] = float(amount)

    return details


def invoice_ocr_page():

    st.title("Invoice OCR & JSON Extraction")

    st.write(
        "Upload a purchase invoice to extract information "
        "and convert it into structured JSON format."
    )

    st.info(
        "OCR extracts text from invoice images. "
        "Extracted information must be manually verified."
    )

    st.subheader("Upload Purchase Invoice")

    uploaded_file = st.file_uploader(
        "Choose an invoice image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Invoice",
            use_container_width=True
        )

        if st.button("Process Invoice"):

            try:

                with st.spinner("Processing invoice..."):

                    extracted_text = extract_invoice_text(image)

                    details = extract_invoice_details(extracted_text)

                    details["extracted_text"] = extracted_text

                st.success("Invoice text extraction completed!")

                st.subheader("Extracted Invoice Details")

                st.write("**Invoice Number:**",
                         details["invoice_number"] or "Not detected")

                st.write("**Invoice Date:**",
                         details["invoice_date"] or "Not detected")

                st.write("**Supplier Name:**",
                         details["supplier_name"] or "Not detected")

                if details["total_amount"] is not None:
                    st.write(
                        "**Total Amount:** ₹{:,.2f}".format(
                            details["total_amount"]
                        )
                    )
                else:
                    st.write("**Total Amount:** Not detected")

                st.subheader("Extracted Text")

                st.text_area(
                    "OCR Output",
                    extracted_text,
                    height=250
                )

                st.subheader("Structured JSON Output")

                json_output = json.dumps(
                    details,
                    indent=4,
                    ensure_ascii=False
                )

                st.code(json_output, language="json")

                st.download_button(
                    label="Download JSON",
                    data=json_output,
                    file_name="invoice_data.json",
                    mime="application/json"
                )

                st.warning(
                    "Please verify all extracted invoice fields "
                    "before using them for accounting or procurement."
                )

            except Exception as e:

                st.error(f"OCR processing failed: {e}")