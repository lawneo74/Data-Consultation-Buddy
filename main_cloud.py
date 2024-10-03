__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Set up and run this Streamlit App
import streamlit as st
from helper_functions.ps_user_interface import render_user_interface
from helper_functions.utility import check_password
from logics.ps_clarifier import ProblemClarifier
from helper_functions.threat_detector import ThreatDetector
from helper_functions.pdf_generator import PDFGenerator
from config import load_config

# from helper_functions.user_interface import render_user_interface
from helper_functions.utility import check_password

# Do not continue if check_password is not True.
if not check_password():
    st.stop()

# region <--------- Streamlit App Configuration --------->
st.set_page_config(layout="wide", page_title="Data Consultancy Buddy")
# # endregion <--------- Streamlit App Configuration --------->

# Load configuration
config = load_config()

with st.expander("Warning", expanded=False):
    st.warning(
        """
:red[IMPORTANT NOTICE]: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.
""",
        icon="⚠️",
    )

st.divider()

st.title("MOE Data Consultancy Buddy")

tab1, tab2, tab3 = st.tabs(
    [
        "Clarify Problem Statement",
        "Refine Research Questions",
        "Search for Existing Data",
    ]
)


@st.cache_resource
def create_threat_detector(config):
    threat_detector = ThreatDetector(config)
    return threat_detector


threat_detector = create_threat_detector(config)


with tab1:
    st.subheader("Clarify Problem Statement")

    # Initialize session state variables
    if "ps_process_started" not in st.session_state:
        st.session_state.ps_process_started = False

    if "ps_clarifications" not in st.session_state:
        st.session_state.ps_clarifications = []

    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    if "broad_issues" not in st.session_state:
        st.session_state.broad_issues = []

    if "focused_issues" not in st.session_state:
        st.session_state.focused_issues = []

    if "manual_issues" not in st.session_state:
        st.session_state.manual_issues = []

    # with problem_statement_clarifier tab:
    clarifier = ProblemClarifier(config)
    pdf_gen = PDFGenerator()

    # # Render the User Interface
    render_user_interface(clarifier, threat_detector, pdf_gen)

with tab2:
    st.subheader("Research Questions")

with tab3:
    st.subheader("Search for Existing Data in MOE")
