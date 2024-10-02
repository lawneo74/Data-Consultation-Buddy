import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import base64


class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.normal_style = ParagraphStyle(
            "Normal",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=14,
        )
        self.bold_style = ParagraphStyle(
            "Bold",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=14,
            fontName="Helvetica-Bold",
        )

    def create_pdf(
        self,
        initial_statement,
        focused_issues,
        clarifications,
        refined_statement,
        title,
        feedback_refined_statement,
    ):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        story = []

        # Title
        story.append(Paragraph(title, self.styles["Title"]))
        story.append(Spacer(1, 12))

        # Subtitle
        story.append(
            Paragraph(
                "Problem Statement Clarification Summary", self.styles["Heading1"]
            )
        )
        story.append(Spacer(1, 12))

        # Initial Problem Statement
        story.append(Paragraph("Initial Problem Statement:", self.styles["Heading2"]))
        story.append(Paragraph(initial_statement, self.normal_style))
        story.append(Spacer(1, 12))

        # Focused Issues
        story.append(Paragraph("Focused Issues:", self.styles["Heading2"]))
        for issue in focused_issues:
            story.append(Paragraph(f"• {issue}", self.normal_style))
        story.append(Spacer(1, 12))

        # Clarification Process
        story.append(Paragraph("Clarification Process:", self.styles["Heading2"]))
        for clarification in clarifications:
            role = "AI" if clarification["role"] == "🤖" else "Human"
            text = clarification["text"]
            story.append(Paragraph(f"{role}: {text}", self.normal_style))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        # Refined Problem Statement
        story.append(Paragraph("Refined Problem Statement:", self.styles["Heading2"]))

        # Split the input text into paragraphs
        paragraphs = refined_statement.strip().split("\n\n")

        # Add each paragraph to the story
        for para in paragraphs:
            story.append(Paragraph(para.strip(), self.normal_style))
            story.append(Spacer(1, 12))

        # Feedback on Refined Problem Statement
        story.append(
            Paragraph("Feedback on Refined Problem Statement:", self.styles["Heading2"])
        )

        # Split the input text into paragraphs
        paragraphs = feedback_refined_statement.strip().split("\n\n")

        # Add each paragraph to the story
        for para in paragraphs:
            story.append(Paragraph(para.strip(), self.normal_style))
            story.append(Spacer(1, 12))

        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def get_pdf_download_link(self, pdf_buffer, filename):
        b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF</a>'
