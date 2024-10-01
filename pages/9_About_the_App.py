import streamlit as st
import random
from helper_functions.utility import select_quote

# region <--------- Streamlit App Configuration --------->
# st.set_page_config(layout="centered", page_title="MOE Data Consultancy Buddy")

st.set_page_config(
    page_title="MOE Data Consultancy Buddy", page_icon="🧭", layout="wide"
)
# endregion <--------- Streamlit App Configuration --------->

# st.image("data-scout-logo.png", width=200)

st.title("Welcome to MOE Data Consultancy Buddy App")

st.header("Your Intelligent Data Companion at MOE")

st.markdown("---")

st.subheader("WARNING!")
st.write(
    """
:red[IMPORTANT NOTICE]: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice."""
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("What is MOE Data Consultancy Buddy?")
    st.write(
        """MOE Data Consultancy Buddy is a LLM-powered AI assistant, designed to 
        simplify data exploration and facilitate decision-making at MOE HQ."""
    )

    st.subheader("How Can MOE Data Consultancy Buddy Help You?")
    st.write("🎯 **Refine Your Questions**")
    st.write(
        "Transform vague ideas into clear research questions that can be addressed with data."
    )

    st.write("🔍 **Discover Hidden Data**")
    st.write("Uncover relevant data sources in MOE HQ for your data use case.")

    st.write("💡 **Generate Quick Insights**")
    st.write("Get preliminary analysis to kickstart your projects.")

    st.write("🧭 **Navigate Expert Resources**")
    st.write("Find the right specialists for in-depth consultations.")

with col2:
    st.subheader("Why Use MOE Data Consultancy Buddy?")
    st.write("- **Save Time**: Cut hours off your initial data exploration.")
    st.write("- **Enhance Collaboration**: Break down data silos across MOE HQ.")
    st.write(
        "- **Optimise Resources**: Engage with RMID's specialists more effectively."
    )

    st.subheader("Getting Started is Easy!")
    st.write("1. **Log In**: Use your credentials.")
    st.write("2. **Ask Away**: Type your question or topic.")
    st.write("3. **Explore**: Follow MOE Data Consultancy Buddy's guided journey.")


st.divider()

quote_selected_output = select_quote()
st.markdown(f'> "{quote_selected_output[0]}" - {quote_selected_output[1]}')
st.markdown("---")

# col3, col4 = st.columns(2)
# with col3:
#     if st.button("FAQs"):
#         st.info("FAQ section is under construction.")
# with col4:
#     if st.button("Contact Support"):
#         st.info("Support contact information will be available soon.")
