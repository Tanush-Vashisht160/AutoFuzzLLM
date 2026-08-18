import time
import requests


class OllamaClient:
    """
    Client for communicating with a local Ollama server.

    Ollama failures such as connection errors, HTTP errors, invalid
    responses, and request timeouts are returned as structured
    infrastructure errors so the fuzzing campaign can skip Oracle,
    fitness, novelty, and seed-pool processing for failed executions.
    """

    def __init__(self, model="llama2"):
        self.url = "http://localhost:11434/api/chat"
        self.model = model

    def generate_response(self, prompt):
        """
        Generate a response from the Ollama target model.

        Returns
        -------
        dict
            Successful response:

            {
                "success": True,
                "response": "...",
                "response_time": 1.23
            }

            Infrastructure failure:

            {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": "...",
                "response_time": 120.0
            }

        Notes
        -----
        The timeout remains at 120 seconds intentionally. A timeout is
        treated as an infrastructure failure rather than as an LLM
        response that should enter Oracle evaluation.
        """

        MAX_PROMPT_LENGTH = 10000

        # ------------------------------------------------------------
        # Validate prompt
        # ------------------------------------------------------------

        if not isinstance(prompt, str):

            raise TypeError(
                "Ollama prompt must be string."
            )

        if len(prompt) > MAX_PROMPT_LENGTH:

            raise ValueError(
                f"Prompt length "
                f"{len(prompt)} "
                f"exceeds limit "
                f"{MAX_PROMPT_LENGTH}"
            )

        # ------------------------------------------------------------
        # Build Ollama request payload
        # ------------------------------------------------------------

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        # ------------------------------------------------------------
        # Execute Ollama request
        # ------------------------------------------------------------

        try:

            print("\n" + "=" * 60)
            print("OLLAMA REQUEST STARTED")
            print("=" * 60)

            print(
                f"Model : {self.model}"
            )

            print(
                f"Prompt Length : "
                f"{len(prompt)} characters"
            )

            print(
                "Sending request to Ollama..."
            )

            start = time.time()

            # Keep the existing 120-second timeout.
            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )

            end = time.time()

            response_time = round(
                end - start,
                2
            )

            print(
                "HTTP Request Finished"
            )

            print(
                "Status Code :",
                response.status_code
            )

            # --------------------------------------------------------
            # HTTP error handling
            # --------------------------------------------------------

            response.raise_for_status()

            # --------------------------------------------------------
            # Parse JSON response
            # --------------------------------------------------------

            data = response.json()

            print(
                "Received JSON from Ollama"
            )

            print(
                "Response Time :",
                response_time,
                "seconds"
            )

            # --------------------------------------------------------
            # Validate Ollama response structure
            # --------------------------------------------------------

            if "message" not in data:

                print(
                    "Unexpected Response:"
                )

                print(
                    data
                )

                # The server responded, but it did not return the
                # expected Ollama message structure. Treat this as an
                # infrastructure/model-server failure rather than
                # sending the raw server response to the Oracle.

                return {
                    "success": False,
                    "response": "",
                    "error_type": "INFRASTRUCTURE_ERROR",
                    "error": (
                        "Unexpected Ollama response: "
                        f"{data}"
                    ),
                    "response_time": response_time
                }

            # --------------------------------------------------------
            # Extract generated content
            # --------------------------------------------------------

            message = data.get(
                "message",
                {}
            )

            response_content = message.get(
                "content"
            )

            # Missing/invalid content is also considered an
            # infrastructure/model-server failure.

            if not isinstance(
                response_content,
                str
            ):

                print(
                    "Invalid Ollama message content:"
                )

                print(
                    data
                )

                return {
                    "success": False,
                    "response": "",
                    "error_type": "INFRASTRUCTURE_ERROR",
                    "error": (
                        "Ollama response did not contain "
                        "valid message content."
                    ),
                    "response_time": response_time
                }

            print(
                "Response successfully extracted."
            )

            print("=" * 60)

            # --------------------------------------------------------
            # Successful response
            # --------------------------------------------------------

            return {
                "success": True,
                "response": response_content,
                "response_time": response_time
            }

        # ------------------------------------------------------------
        # Explicit timeout handling
        # ------------------------------------------------------------

        except requests.exceptions.Timeout as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA TIMEOUT"
            )

            print(
                "Ollama request exceeded "
                "the 120-second timeout."
            )

            print(
                "Error :",
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # Connection-related errors
        # ------------------------------------------------------------

        except requests.exceptions.ConnectionError as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA CONNECTION ERROR"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # HTTP errors
        # ------------------------------------------------------------

        except requests.exceptions.HTTPError as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA HTTP ERROR"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # Invalid JSON / response parsing errors
        # ------------------------------------------------------------

        except requests.exceptions.JSONDecodeError as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA RESPONSE PARSE ERROR"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # Catch-all infrastructure failure
        # ------------------------------------------------------------

        except Exception as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA ERROR"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

    def generate_conversation(self, messages):
        """
        Generate a response for a multi-message conversation.

        Successful calls return the generated text.

        Infrastructure failures return a structured error dictionary,
        matching the format used by generate_response().
        """

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:

            print(
                "\nSending conversation request to Ollama..."
            )

            start = time.time()

            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )

            end = time.time()

            response_time = round(
                end - start,
                2
            )

            response.raise_for_status()

            data = response.json()

            print(
                "Conversation response received."
            )

            # --------------------------------------------------------
            # Validate response structure
            # --------------------------------------------------------

            if "message" not in data:

                print(
                    "Unexpected Ollama conversation response:"
                )

                print(
                    data
                )

                return {
                    "success": False,
                    "response": "",
                    "error_type": "INFRASTRUCTURE_ERROR",
                    "error": (
                        "Unexpected Ollama conversation "
                        f"response: {data}"
                    ),
                    "response_time": response_time
                }

            message = data.get(
                "message",
                {}
            )

            response_content = message.get(
                "content"
            )

            if not isinstance(
                response_content,
                str
            ):

                print(
                    "Invalid Ollama conversation content:"
                )

                print(
                    data
                )

                return {
                    "success": False,
                    "response": "",
                    "error_type": "INFRASTRUCTURE_ERROR",
                    "error": (
                        "Ollama conversation response "
                        "did not contain valid content."
                    ),
                    "response_time": response_time
                }

            return {
                "success": True,
                "response": response_content,
                "response_time": response_time
            }

        # ------------------------------------------------------------
        # Explicit timeout handling
        # ------------------------------------------------------------

        except requests.exceptions.Timeout as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA CONVERSATION TIMEOUT"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # Connection error
        # ------------------------------------------------------------

        except requests.exceptions.ConnectionError as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA CONVERSATION CONNECTION ERROR"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # HTTP error
        # ------------------------------------------------------------

        except requests.exceptions.HTTPError as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA CONVERSATION HTTP ERROR"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # JSON parsing error
        # ------------------------------------------------------------

        except requests.exceptions.JSONDecodeError as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nOLLAMA CONVERSATION RESPONSE PARSE ERROR"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }

        # ------------------------------------------------------------
        # Catch-all infrastructure failure
        # ------------------------------------------------------------

        except Exception as e:

            elapsed = round(
                time.time() - start,
                2
            ) if "start" in locals() else 0

            print(
                "\nConversation Error"
            )

            print(
                e
            )

            return {
                "success": False,
                "response": "",
                "error_type": "INFRASTRUCTURE_ERROR",
                "error": str(e),
                "response_time": elapsed
            }