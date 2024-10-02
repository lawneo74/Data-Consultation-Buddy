from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from crewai import Agent, Task, Crew, Process
import re


class ProblemClarifier:
    def __init__(self, config):
        self.chat_model = ChatOpenAI(model=config["OPENAI_MODEL"])
        self.clarification_agent = self._create_clarification_agent()
        self.problem_statement_analyzer_agent = (
            self._create_problem_statement_analyzer_agent()
        )
        self.refinement_agent = self._create_refinement_agent()
        self.research_advisor_agent = self._create_research_advisor_agent()

    def _create_clarification_agent(self):
        return Agent(
            role="Clarification Specialist",
            goal="Elicit detailed information to enhance understanding of the problem, but do not ask for any possible solution",
            backstory="You are an AI assistant specialized in asking insightful questions to clarify problem statements.",
            allow_delegation=False,
            llm=self.chat_model,
        )

    def _create_research_advisor_agent(self):
        return Agent(
            role="Research Advisor",
            goal="Suggest good responses to the questions posed to the users for clarification. Do not suggest any possible solution.",
            backstory="You are an AI assistant specialized in providing good, coherent and trust-worthy responses to questions. \
                        You are also a renowned researcher with 20 years of experience in various contexts and a track record of \
                        influential publications. Committed to rigorous, ethical, and impactful research.",
            allow_delegation=False,
            llm=self.chat_model,
        )

    def _create_problem_statement_analyzer_agent(self):
        return Agent(
            role="Problem Statement Analyzer",
            goal="Analyze problem statements for completeness and quality. Do not offer any possible solutions.",
            backstory="You are skilled in evaluating problem statements against key criteria.",
            allow_delegation=False,
            llm=self.chat_model,
        )

    def _create_refinement_agent(self):
        return Agent(
            role="Problem Statement Refiner",
            goal="Refine the problem statement based on clarifications to ensure they meet all necessary criteria. \
            Stop the process when the problem statement can be clearly addressed.",
            backstory="You are an AI assistant specialized in synthesizing information to create clear and actionable \
                    problem statements. You are also a former policy analyst with a PhD in Systems Thinking, known for \
                    breaking down complex societal and educational issues",
            allow_delegation=False,
            llm=self.chat_model,
        )

    def generate_broad_issues(self, problem_statement):
        broad_issues_template = PromptTemplate(
            input_variables=["problem_statement"],
            template="""
            Ruminate on the following problem statement.
            <problem_statement>
            {problem_statement}
            </problem_statement>
            Analyze the problem statement and identify a broad range of potential issues:
            List at least 12 potential issues or areas of concern related to this problem statement.
            Format your response as a numbered list, with each issue on a new line, like this:
            1. Issue one
            2. Issue two
            3. Issue three
            ...and so on.
            """,
        )

        broad_issues_task = Task(
            description=broad_issues_template.format(
                problem_statement=problem_statement
            ),
            expected_output="A list of at least 12 potential issues or areas of concern related to the \
                problem statement that are useful to investigate.",
            agent=self.clarification_agent,
        )

        crew = Crew(
            agents=[self.clarification_agent],
            tasks=[broad_issues_task],
            process=Process.sequential,
        )

        broad_issues_result = crew.kickoff()
        return self._parse_issues(str(broad_issues_result))

    def ask_clarifying_question(
        self, problem_statement, previous_clarifications, current_issue, focused_issues
    ):
        clarification_template = PromptTemplate(
            input_variables=[
                "problem_statement",
                "previous_questions",
                "current_issue",
                "focused_issues",
                "previous_responses",
            ],
            template="""
            Ruminate and analyze the following problem statement and generate one clarifying question:
            Problem Statement:
            <problem_statement>
            {problem_statement}
            </problem_statement>
            Current Issue: 
            <current_issue>
            {current_issue}
            </current_issue>
            Focused issues:
            <focused_issues>
            {focused_issues}
            </focused_issues>
            Previous questions and responses: 
            <previous_questions>
            {previous_questions}
            </previous_questions>
            Your task is to ask a single clarifying question that helps gather more specific information about the problem to better understand why it is problem, focusing on the current issue.
            Ensure that the question is:
                1. Open-ended
                2. Neutral and unbiased
                3. Specific to key aspects needing clarification
                4. Relevant to the problem
                5. Clear and easily understood
                6. Constructive for problem refinement
                
            The goal is to use the information to clarify the problem statement and NOT to generate any research question. 
            Provide useful suggestions that users provide to provide more clarity on the problem statement. 
            Use a header to separate the question from the suggestions.

            Important guidelines:
            1. Maintain context consistency with previous questions unless the user's responses clearly indicate a need to change direction.
            2. Do not repeat any previous questions.
            3. If a user's response suggests a new important area of inquiry, you may explore that, but generally try to deepen understanding of the current issue.
            4. Ask only one question at a time.
            5. Ensure your question is specific and targeted to gather actionable information. 
            6. Take the responses to the previous questions into account when asking the next question.
            7. MUST not ask questions that are very similar to previous questions that the user leave as blank or did not answer.
            Based on these guidelines and the information provided, generate your next clarifying question:
            """,
        )

        previous_questions = [
            q["text"] for q in previous_clarifications if q["role"] == "AI"
        ]
        previous_responses = [
            r["text"] for r in previous_clarifications if r["role"] == "Human"
        ]

        clarification_task = Task(
            description=clarification_template.format(
                problem_statement=problem_statement,
                previous_questions=previous_questions,
                current_issue=current_issue,
                focused_issues=focused_issues,
                previous_responses=previous_responses,
            ),
            expected_output="A single clarifying question based on the problem statement, current issue, and previous interactions. \
            The clarifying question cannot be too similar to any of the previous questions.",
            agent=self.clarification_agent,
        )

        crew = Crew(
            agents=[self.clarification_agent, self.problem_statement_analyzer_agent],
            tasks=[clarification_task],
            process=Process.sequential,
        )

        clarification_result = crew.kickoff()
        return str(clarification_result)

    def refine_problem_statement(self, original_statement, clarifications):
        refinement_template = PromptTemplate(
            input_variables=["original_statement", "clarifications"],
            template="""
            Based on the original problem statement and the clarifications provided, provide a refined problem statement:
            Original Statement: 
            <original_statement>
            {original_statement}
            </original_statement>
            Clarifications: 
            <clarifications>
            {clarifications}
            </clarifications>
            Ensure it is:
                1. Clear and specific
                2. Relevant and significant
                3. Well-scoped with defined boundaries
                4. Measurable
                5. Contextualized
                6. Objective
                7. Actionable
                8. Timely
            Provide a refined version of the problem statement that incorporates new information gathered during the clarification process.
            Output the refined problem statement text.
            Add a paragraph to explain the new information that have been included in the refned problem statement, but were not provided by the user.
            """,
        )

        refinement_task = Task(
            description=refinement_template.format(
                original_statement=original_statement,
                clarifications="\n".join(
                    f"{c['role']}: {c['text']}" for c in clarifications
                ),
            ),
            expected_output="A refined problem statement that incorporates the clarifications provided.",
            agent=self.refinement_agent,
            delegations=True,
        )

        crew = Crew(
            agents=[self.refinement_agent, self.problem_statement_analyzer_agent],
            tasks=[refinement_task],
            process=Process.sequential,
        )

        refinement_result = crew.kickoff()
        return str(refinement_result)

    def generate_title(self, problem_statement):
        title_template = PromptTemplate(
            input_variables=["problem_statement"],
            template="""
            Based on the following problem statement, generate a concise and descriptive title \
                that reflects the nature of the problem:
            Problem Statement:
            <problem_statement>
            {problem_statement}
            </problem_statement>
            The title should be:
            1. No more than 10 words long
            2. Capture the essence of the problem
            3. Professional and clear
            Generate the title:
            """,
        )

        title_task = Task(
            description=title_template.format(problem_statement=problem_statement),
            expected_output="A title for a problem statement that is clear and concise.",
            agent=self.refinement_agent,
        )

        crew = Crew(
            agents=[self.refinement_agent, self.problem_statement_analyzer_agent],
            tasks=[title_task],
            process=Process.sequential,
        )

        title_result = crew.kickoff()
        return str(title_result).strip()

    def rephrase_issue(self, issue):
        rephrase_template = PromptTemplate(
            input_variables=["issue"],
            template="""
            Rephrase the following issue to make it more clear, concise, and professional:
            Issue:
            <issue>
            {issue}
            </issue>
            Rephrased issue:
            """,
        )

        rephrase_task = Task(
            description=rephrase_template.format(issue=issue),
            expected_output="A rephrased version of the issue that is clear, concise, and professional.",
            agent=self.refinement_agent,
        )

        crew = Crew(
            agents=[self.refinement_agent, self.problem_statement_analyzer_agent],
            tasks=[rephrase_task],
            process=Process.sequential,
        )

        rephrase_result = crew.kickoff()
        return str(rephrase_result).strip()

    def generate_feedback_problem_statement(self, refined_statement):
        analyze_problem_statement_template = PromptTemplate(
            input_variables=["refined_statement"],
            template="""
            Analyze the problem statement below and provide constructive and professional feedback for users to consider to make it even better:
            Refined problem statement:
            <refined_problem_statement>
            {refined_statement}
            </refined_problem_statement>
            Evaluate the refined problem statement using the criteria below: 
            <criteria>
                1. Clear and specific
                2. Relevant and significant
                3. Well-scoped with defined boundaries
                4. Measurable
                5. Contextualized
                6. Objective
                7. Actionable
                8. Timely
            </criteria>
            Provide a concise and succinct report on the evaluation of the refined problem statement \
            and feedback for the refined problem statement. A paragraph for evaluation and another paragraph for feedback.
            """,
        )

        analyze_problem_statement_task = Task(
            description=analyze_problem_statement_template.format(
                refined_statement=refined_statement,
            ),
            expected_output="A rephrased version of the issue that is clear, concise, and professional.",
            agent=self.refinement_agent,
        )

        crew = Crew(
            agents=[self.problem_statement_analyzer_agent, self.research_advisor_agent],
            tasks=[analyze_problem_statement_task],
            process=Process.sequential,
        )

        feedback_problem_statement = crew.kickoff()
        return str(feedback_problem_statement).strip()

    def _parse_issues(self, issues_text):
        return re.findall(r"\d+\.\s*(.*)", issues_text)
