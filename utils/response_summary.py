def summarize_response(response: str) -> str:
    """
    Creates a short summary of the model response.
    """

    if not response:
        return "The model did not generate a response."

    words = response.split()

    if len(words) <= 35:
        return response

    return " ".join(words[:35]) + "..."