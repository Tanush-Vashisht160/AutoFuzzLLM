from llm.llm_router import LLMRouter

router = LLMRouter("Groq")

response = router.generate("Say hello in one sentence.")

print(response)