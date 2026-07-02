from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


class ReportGenerator:

    def create_pdf(self, filename, campaign, results):

        doc = SimpleDocTemplate(filename)

        styles = getSampleStyleSheet()

        story = []

        story.append(Paragraph("<b>AutoFuzzLLM Report</b>", styles["Heading1"]))

        story.append(Paragraph(f"Campaign : {campaign}", styles["Normal"]))

        story.append(Paragraph("<br/>", styles["Normal"]))

        for index, result in enumerate(results, start=1):

            story.append(
                Paragraph(
                    f"<b>Test {index}</b>",
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    f"Prompt : {result['prompt']}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"Response : {result['response']}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph("<br/>", styles["Normal"])
            )

        doc.build(story)
        