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

            # Single Prompt Attack Processing
            if "prompt" in result:
                story.append(
                    Paragraph(
                        f"Category : {result.get('category', 'N/A')}", styles["Normal"]
                    )
                )
                # Embedded new OWASP classification field safely
                story.append(
                    Paragraph(
                        f"OWASP : {result.get('owasp', 'Unknown')}", styles["Normal"]
                    )
                )
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

            # Multi-Turn Conversation Processing
            elif "conversation" in result:
                story.append(
                    Paragraph(
                        "<b>Multi-Turn Conversation</b>", styles["Heading3"]
                    )
                )
                for turn, item in enumerate(result["responses"], start=1):
                    story.append(
                        Paragraph(
                            f"<b>User {turn}</b>: {item.get('prompt', '')}",
                            styles["Normal"],
                        )
                    )
                    story.append(
                        Paragraph(
                            f"<b>Assistant {turn}</b>: {item.get('response', '')}",
                            styles["Normal"],
                        )
                    )
                story.append(Paragraph("<br/>", styles["Normal"]))

            story.append(Paragraph("<br/>", styles["Normal"]))

        doc.build(story)