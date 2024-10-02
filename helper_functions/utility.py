# filename: utility.py
import streamlit as st
import random
import hmac

# """
# This file contains the common components used in the Streamlit App.
# This includes the sidebar, the title, the footer, and the password check.
# """


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True
    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


### Returns random quotations on data ###

quote_dict = {
    "Without data, you'e just another person with an opinion.": "W. Edwards Deming, American statistician.",
    "In God we trust. All others must bring data.": "W. Edwards Deming, American statistician.",
    "The goal is to turn data into information, and information into insight.": "Carly Fiorina, former CEO of Hewlett-Packard.",
}


def select_quote():
    quote_selected = random.choice(list(quote_dict.keys()))
    return quote_selected, quote_dict[quote_selected]
