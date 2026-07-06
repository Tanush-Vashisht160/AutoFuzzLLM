from llm.llm_router import LLMRouter

router = LLMRouter("OpenRouter")

response = router.generate("Say hello in one sentence.")

print(response)