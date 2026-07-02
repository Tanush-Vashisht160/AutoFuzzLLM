import random
import base64


class MutationStrategies:

    def uppercase(self, text):
        return text.upper()

    def lowercase(self, text):
        return text.lower()

    def extra_spaces(self, text):
        return text.replace(" ", "   ")

    def exclamation(self, text):
        return text + "!!!"

    def question(self, text):
        return text + "???"

    def emoji(self, text):
        return text + " 😊"

    def quotes(self, text):
        return '"' + text + '"'

    def newline(self, text):
        return text.replace(" ", "\n")

    def leetspeak(self, text):

        table = {
            "o": "0",
            "a": "4",
            "e": "3",
            "i": "1",
            "s": "5"
        }

        result = ""

        for c in text:

            result += table.get(c.lower(), c)

        return result

    def base64_encode(self, text):

        return base64.b64encode(
            text.encode()
        ).decode()

    def reverse(self, text):

        return text[::-1]

    def duplicate(self, text):

        return text + " " + text

    def random_case(self, text):

        output = ""

        for c in text:

            if random.choice([True, False]):
                output += c.upper()
            else:
                output += c.lower()

        return output