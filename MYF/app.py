import streamlit as st
import pandas as pd
import json
import urllib.request
from datetime import datetime, date

# ==========================================
# WEB PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Taytay Methodist Church",
    layout="wide"
)


# ==========================================
# GOOGLE SHEETS URL CLEANER
# ==========================================
def get_clean_url(url_string):
    if "/edit" in url_string:
        return url_string.split("/edit")[0] + "/export?format=csv"
    return url_string


# ==========================================
# DAILY BIBLE VERSE
# ==========================================
verses_list = [
    '"The Lord is a stronghold for the oppressed, a stronghold in times of trouble." — Psalm 9:9',
    '"Trust in the Lord with all your heart, and do not lean on your own understanding." — Proverbs 3:5',
    '"I can do all things through him who strengthens me." — Philippians 4:13',
    '"For God gave us a spirit not of fear but of power and love and self-control." — 2 Timothy 1:7',
    '"Be strong and courageous. Do not be frightened, and do not be dismayed." — Joshua 1:9',
    '"The Lord is my shepherd; I shall not want." — Psalm 23:1',
    '"But seek first the kingdom of God and his righteousness." — Matthew 6:33'
]

today_index = date.today().day % len(verses_list)


# ==========================================
# VERSE OF THE DAY
# ==========================================
st.subheader("📖 Verse of the Day")
st.markdown(f"## **{verses_list[today_index]}**")
st.write("---")


# ==========================================
# WELCOME MESSAGE
# ==========================================
st.title("Welcome to our Youth Fellowship Portal!")

st.write(
    "We are glad you are here! Please take a moment "
    "to fill out the form below so we can stay connected."
)

st.write("---")


# ==========================================
# REGISTRATION FORM
# ==========================================
st.subheader("✝️ New Registration Form")

with st.form("registration_form", clear_on_submit=True):

    col1, col2 = st.columns(2)

    # --------------------------------------
    # LEFT COLUMN
    # --------------------------------------
    with col1:

        full_name = st.text_input(
            "Full Name:",
            placeholder="e.g., John Doe"
        )

        birthday = st.date_input(
            "Birthday:",
            value=date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="MM/DD/YYYY"
        )

        gender = st.selectbox(
            "Gender:",
            ["Male", "Female", "Other"]
        )

        membership_status = st.selectbox(
            "Membership Status:",
            ["Active Member", "First-Time Visitor"]
        )

        church = st.text_input(
            "Church:",
            placeholder="e.g., Taytay Methodist Church"
        )

    # --------------------------------------
    # RIGHT COLUMN
    # --------------------------------------
    with col2:

        parent_name = st.text_input(
            "Parent's / Guardian's Name:",
            placeholder="e.g., Mary Doe"
        )

        fb_profile = st.text_input(
            "Facebook Profile Link or Name:",
            placeholder="e.g., https://facebook.com/username"
        )

        contact_number = st.text_input(
            "Contact Number:",
            placeholder="e.g., 09123456789"
        )

        address = st.text_area(
            "Complete Address:",
            height=100,
            placeholder="e.g., 123 Street Name, Barangay, City"
        )

    # --------------------------------------
    # SUBMIT BUTTON
    # --------------------------------------
    submit_button = st.form_submit_button(
        "Save Registration Details"
    )


# ==========================================
# SAVE REGISTRATION
# ==========================================
if submit_button:

    if full_name.strip() == "":
        st.error("Full Name is a required field!")

    else:

        # Keep contact number as TEXT
        contact_number = contact_number.strip()

        bday_str = (
            birthday.strftime("%m/%d/%Y")
            if birthday
            else ""
        )

        current_now = datetime.now().strftime(
            "%m/%d/%Y %H:%M:%S"
        )

        # ----------------------------------
        # DATA TO SEND
        # ----------------------------------
        payload = {
            "fullName": full_name.strip(),
            "birthday": bday_str,
            "gender": gender,
            "status": membership_status,
            "church": church.strip(),
            "parentName": parent_name.strip(),
            "fbProfile": fb_profile.strip(),

            # IMPORTANT:
            # Contact number is sent as TEXT
            "contactNumber": str(contact_number),

            "address": address.strip(),
            "registrationDate": current_now
        }

        # ----------------------------------
        # SEND TO GOOGLE APPS SCRIPT
        # ----------------------------------
        try:

            script_url = st.secrets["SCRIPT_URL"]

            req = urllib.request.Request(
                script_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode("utf-8")

            st.success(
                f"Successfully registered {full_name}!"
            )

        except Exception as e:

            st.error(
                "The registration could not be sent to "
                "the online database. Please check the "
                "Google Apps Script connection."
            )


st.write("---")


# ==========================================
# ADMIN SIDEBAR
# ==========================================
st.sidebar.title("🔐 Admin")

admin_password = st.sidebar.text_input(
    "Enter Password:",
    type="password",
    key="final_sidebar_admin_password"
)


# ==========================================
# ADMIN PANEL
# ==========================================
if admin_password:

    if admin_password == st.secrets["ADMIN_PASSWORD"]:

        st.sidebar.success("Correct Password!")

        st.write("---")

        st.subheader(
            "Saved Members List (Live Cloud Data Feed)"
        )

        # ----------------------------------
        # LOAD GOOGLE SHEETS DATA
        # ----------------------------------
        try:

            raw_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

            csv_url = get_clean_url(raw_url)

            # IMPORTANT:
            # Read EVERYTHING as text.
            # This prevents contact numbers from
            # becoming mathematical numbers.
            df_clean = pd.read_csv(
                csv_url,
                dtype=str,
                keep_default_na=False
            )

            # ----------------------------------
            # CLEAN CONTACT NUMBERS
            # ----------------------------------
            if "Contact Number" in df_clean.columns:

                df_clean["Contact Number"] = (
                    df_clean["Contact Number"]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("'", "", regex=False)
                    .str.strip()
                )

        except Exception as e:

            df_clean = pd.DataFrame()


        # ==================================
        # DISPLAY DATA
        # ==================================
        if not df_clean.empty:

            # Add Row Number
            if "Row No." not in df_clean.columns:

                df_clean.insert(
                    0,
                    "Row No.",
                    range(1, 1 + len(df_clean))
                )


            # ----------------------------------
            # SEARCH
            # ----------------------------------
            search_col, _ = st.columns(2)

            with search_col:

                search_query = st.text_input(
                    "Search list by name:",
                    value=""
                )


            if (
                search_query
                and "Full Name" in df_clean.columns
            ):

                df_clean = df_clean[
                    df_clean["Full Name"]
                    .astype(str)
                    .str.contains(
                        search_query,
                        case=False,
                        na=False
                    )
                ]


            # ----------------------------------
            # MEMBER TABLE
            # ----------------------------------
            st.dataframe(
                df_clean,
                use_container_width=True,
                hide_index=True
            )


            # ----------------------------------
            # DOWNLOAD CSV
            # ----------------------------------
            csv_data = df_clean.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download List as Excel / CSV file",
                data=csv_data,
                file_name=(
                    f"registered_members_"
                    f"{date.today().strftime('%m_%d_%Y')}.csv"
                ),
                mime="text/csv"
            )


        else:

            st.info(
                "The database is currently loading or empty."
            )


    else:

        st.sidebar.error("Wrong Password")