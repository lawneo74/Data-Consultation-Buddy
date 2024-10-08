import streamlit as st
import re
from config import HUMAN_ICON, AI_ICON
import time


def render_user_interface(clarifier, threat_detector, pdf_gen):
    st.subheader("AI Problem Statement Clarifier")

    left_column, right_column = st.columns([3, 1])

    with right_column:
        render_instructions()

    with left_column:
        if "initial_statement" not in st.session_state:
            st.session_state.initial_statement = ""
        if "ps_process_started" not in st.session_state:
            st.session_state.ps_process_started = False

        initial_statement = st.text_area(
            "Enter your initial problem statement:",
            value=st.session_state.initial_statement,
            height=150,
            key="initial_statement_input",
        )
        st.session_state.initial_statement = initial_statement

        start_button = st.button("Start Clarification Process", key="start_button")
        if start_button:

            ## Detect Prompt Hijacking
            is_threat = threat_detector.detect_threat(
                st.session_state.initial_statement
            )

            if is_threat == True:
                st.warning(
                    "Prompt hijacking/malicious intent detected! \
                        Please re-write the problem statement.",
                    icon="🚨",
                )
                time.sleep(2)
                st.session_state.initial_statement = ""
                st.rerun()

            else:
                st.session_state.ps_process_started = True
                initialize_session_state()
                process_initial_statement(clarifier, st.session_state.initial_statement)
                st.rerun()

        if st.session_state.ps_process_started:
            render_clarification_process(
                clarifier, threat_detector, pdf_gen, st.session_state.initial_statement
            )


def render_instructions():
    with st.expander("Instructions", expanded=False):
        st.write(
            """
            1. Enter your initial problem statement.
            2. Click 'Start Clarification Process'.
            3. Select focus areas from the AI-generated list.
            4. Optionally add your own focus area(s).
            5. Confirm selected focus area(s) to proceed.
            6. Respond to AI's clarifying questions or leave blank to skip.
            7. Edit previous responses if needed.
            8. Click 'Continue Clarification' for more questions.
            9. Click 'End Clarification' when finished.
            10. Review the summary and refined problem statement.
            11. Download the PDF summary.
            12. Click 'Restart Problem Clarification' to begin anew.
            """
        )


def initialize_session_state():
    st.session_state.ps_clarifications = []
    st.session_state.current_question = None
    st.session_state.broad_issues = []
    st.session_state.focused_issues = []
    st.session_state.manual_issues = []
    st.session_state.issues_confirmed = False
    st.session_state.selected_issues = []


def process_initial_statement(clarifier, initial_statement):
    broad_issues = clarifier.generate_broad_issues(initial_statement)
    st.session_state.broad_issues = broad_issues


def render_clarification_process(
    clarifier, threat_detector, pdf_gen, initial_statement
):
    st.subheader("Clarification Process Started")

    if not st.session_state.issues_confirmed:
        issues_confirmed = render_issue_selection(clarifier, threat_detector)
        if issues_confirmed:
            st.session_state.issues_confirmed = True
            st.rerun()
    else:
        st.write("Selected Focus Areas:")
        for issue in st.session_state.selected_issues:
            st.write(f"- {issue}")
        user_response = render_clarification_interactions(
            clarifier, threat_detector, initial_statement
        )
        render_process_buttons(clarifier, pdf_gen, initial_statement, user_response)


def render_issue_selection(clarifier, threat_detector):
    st.write("Please enter the issue(s) that you want to focus on:")

    new_issue = st.text_input("Enter an issue (optional):", key="new_issue", value="")

    if st.button("Add Issue", key="add_manual_issue"):
        if new_issue:

            ## Detect Prompt Hijacking
            is_threat = threat_detector.detect_threat(new_issue)

            if is_threat == True:
                st.warning(
                    "Prompt hijacking/malicious intent detected! \
                        Please re-write the entry.",
                    icon="🚨",
                )
                time.sleep(2)
                st.rerun()

            else:
                rephrased_issue = clarifier.rephrase_issue(new_issue)
                st.session_state.manual_issues.append(rephrased_issue)
                st.session_state.selected_issues.append(rephrased_issue)
                st.success(f"Added: {rephrased_issue}")
                st.rerun()
        else:
            st.warning("Please enter an issue before adding.")

    st.write(
        "Below are some potential issue(s) generated by AI. Please select additional issues you may want to focus on:"
    )

    all_issues = st.session_state.broad_issues + st.session_state.manual_issues
    for issue in all_issues:
        if issue not in st.session_state.manual_issues:
            if st.checkbox(
                issue,
                key=f"checkbox_{issue}",
                value=issue in st.session_state.selected_issues,
            ):
                if issue not in st.session_state.selected_issues:
                    st.session_state.selected_issues.append(issue)
            elif issue in st.session_state.selected_issues:
                st.session_state.selected_issues.remove(issue)

    if st.session_state.selected_issues:
        st.write("Selected Issues to Focus on:")
        for issue in st.session_state.selected_issues:
            st.write(f"- {issue}")

    confirm_button = st.button("Confirm Selected Issues", key="confirm_issues")
    return confirm_button


def render_clarification_interactions(clarifier, threat_detector, initial_statement):
    for i, interaction in enumerate(st.session_state.ps_clarifications):
        if interaction["role"] == HUMAN_ICON:
            edited_response = st.text_area(
                f"Edit response {i//2 + 1}:",
                value=interaction["text"],
                key=f"edit_{i}",
                height=100,
            )
            if edited_response != interaction["text"]:
                st.session_state.ps_clarifications[i]["text"] = edited_response
        else:
            st.write(f"{interaction['role']}: {interaction['text']}")

    if st.session_state.current_question is None:
        st.session_state.current_question = clarifier.ask_clarifying_question(
            initial_statement,
            st.session_state.ps_clarifications,
            st.session_state.selected_issues,
            st.session_state.focused_issues,
        )

    st.write(f"{AI_ICON}: {st.session_state.current_question}")

    user_response = st.text_area(
        "Your response (leave blank to skip):",
        key=f"response_{len(st.session_state.ps_clarifications)}",
        height=100,
        value="leave blank to skip",
    )

    if user_response:

        ## Detect Prompt Hijacking
        is_threat = threat_detector.detect_threat(user_response)
        if is_threat == True:
            st.warning(
                "Prompt hijacking/malicious intent detected! \
                    Please re-write the entry.",
                icon="🚨",
            )
            time.sleep(2)
            # st.rerun()

    return user_response


def render_process_buttons(clarifier, pdf_gen, initial_statement, user_response):
    col1, col2, col3 = st.columns(3)

    with col1:
        continue_button = st.button("Continue Clarification", key="continue_button")
    with col2:
        end_button = st.button("End Clarification", key="end_button")
    with col3:
        restart_button = st.button(
            "Restart Clarification Process", key="restart_button"
        )

    if continue_button:
        process_continue(clarifier, initial_statement, user_response)
    elif end_button:
        process_end_clarification(clarifier, pdf_gen, initial_statement, user_response)
    elif restart_button:
        restart_process()


def process_continue(clarifier, initial_statement, user_response):
    st.session_state.ps_clarifications.append(
        {"role": AI_ICON, "text": st.session_state.current_question}
    )

    if user_response:
        st.session_state.ps_clarifications.append(
            {"role": HUMAN_ICON, "text": user_response}
        )
    else:
        st.session_state.ps_clarifications.append(
            {"role": HUMAN_ICON, "text": "Question skipped."}
        )

    st.session_state.current_question = None
    st.rerun()


def process_end_clarification(clarifier, pdf_gen, initial_statement, user_response):
    # if user_response:
    st.session_state.ps_clarifications.append(
        {"role": AI_ICON, "text": st.session_state.current_question}
    )
    st.session_state.ps_clarifications.append(
        {"role": HUMAN_ICON, "text": user_response}
    )

    refined_statement = clarifier.refine_problem_statement(
        initial_statement, st.session_state.ps_clarifications
    )

    display_summary(clarifier, pdf_gen, initial_statement, refined_statement)


def display_summary(clarifier, pdf_gen, initial_statement, refined_statement):
    st.divider()
    st.subheader("Summary of Clarifications:")

    st.write("Initial Problem Statement:")
    st.write(initial_statement)
    st.write("---")
    st.write("Selected Focus Areas:")
    for issue in st.session_state.selected_issues:
        st.write(f"- {issue}")
    st.write("---")
    for clarification in st.session_state.ps_clarifications:
        st.write(f"{clarification['role']}: {clarification['text']}")

    problem_statement_title = clarifier.generate_title(initial_statement)
    st.subheader(
        f"Suggested Problem Statement (for consideration): {problem_statement_title}"
    )
    st.write(refined_statement)

    st.warning(
        "Please revise the problem statement to ensure that it accurately reflects the problem",
        icon="⚠️",
    )

    feedback_refined_statement = clarifier.generate_feedback_problem_statement(
        refined_statement
    )
    st.divider()
    st.subheader("Feedback for the Refined Statement")
    st.write(feedback_refined_statement)

    print(st.session_state.ps_clarifications)
    pdf_buffer = pdf_gen.create_pdf(
        initial_statement,
        st.session_state.selected_issues,
        st.session_state.ps_clarifications,
        refined_statement,
        problem_statement_title,
        feedback_refined_statement,
    )
    pdf_filename = extract_pdf_name(initial_statement)

    st.subheader("Download summary")
    st.markdown(
        pdf_gen.get_pdf_download_link(pdf_buffer, pdf_filename), unsafe_allow_html=True
    )

    restart_button_last = st.button(
        "Restart Clarification Process", key="restart_button_last"
    )

    if restart_button_last:
        restart_process()


def extract_pdf_name(problem_statement):
    name = problem_statement.strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return f"problem_statement_{name[:50]}.pdf"


def restart_process():
    st.session_state.issues_confirmed = False
    st.session_state.selected_issues = []
    st.session_state.manual_issues = []
    st.session_state.ps_clarifications = []
    st.session_state.current_question = None
    st.rerun()


# Add automatic scrolling
st.markdown(
    "<script>window.scrollTo(0, document.body.scrollHeight);</script>",
    unsafe_allow_html=True,
)
