from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate


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
                Paragraph(f"<b>Test {index}</b>", styles["Heading2"])
            )

            if "prompt" in result:
                story.append(
                    Paragraph(
                        f"Prompt : {result['prompt']}", styles["Normal"]
                    )
                )
                story.append(
                    Paragraph(
                        f"Response : {result['response']}", styles["Normal"]
                    )
                )

            elif "conversation" in result:
                story.append(
                    Paragraph(
                        "<b>Multi-Turn Conversation</b>", styles["Heading3"]
                    )
                )
                for turn, item in enumerate(result["responses"], start=1):
                    story.append(
                        Paragraph(
                            f"<b>User {turn}</b>: {item['prompt']}",
                            styles["Normal"],
                        )
                    )
                    story.append(
                        Paragraph(
                            f"<b>Assistant {turn}</b>: {item['response']}",
                            styles["Normal"],
                        )
                    )
                story.append(Paragraph("<br/>", styles["Normal"]))

            story.append(Paragraph("<br/>", styles["Normal"]))

        doc.build(story)