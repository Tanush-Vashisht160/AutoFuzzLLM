import time
from fuzzing.executor import FuzzExecutor
from fuzzing.mutator import PromptMutator


class FuzzCampaign:

    def __init__(self, provider):
        self.mutator = PromptMutator()
        self.executor = FuzzExecutor(provider)

    def run(self, seed_prompt, max_tests):

        print("=" * 60)
        print("NEW CAMPAIGN STARTED")
        print("=" * 60)

        # Generate all mutations from the seed prompt
        mutated_prompts = self.mutator.generate_mutations(seed_prompt)

        # Limit the number of tests based on the slider
        mutated_prompts = mutated_prompts[:max_tests]

        results = []

        # Execute each mutated prompt
        for i, attack in enumerate(mutated_prompts, start=1):

            print(f"Running Test {i}/{len(mutated_prompts)}")

            # Returns a dictionary: {"response": text, "response_time": float}
            response = self.executor.run_prompt(attack["prompt"])

            # Extract text and compute length inline
            response_text = response["response"]

            results.append({
                "provider": self.executor.router.provider,
                "category": attack["category"],
                "prompt": attack["prompt"],
                "response": response_text,
                "response_time": response["response_time"],
                "response_length": len(response_text.split())
            })

            # Delay to reduce API rate-limit issues
            time.sleep(4)

        return results

    def run_conversation_campaign(self, conversation_turns, max_tests):
        """
        Handles multi-turn conversation campaigns and tracks the final 
        response metrics for downstream aggregate calculations.
        """
        results = []
        
        for i in range(min(len(conversation_turns), max_tests)):
            messages = conversation_turns[i]
            
            responses = self.executor.run_conversation(messages)
            
            # Extract the final AI assistant text from the full turn array
            final_response = responses[-1]["response"] if isinstance(responses, list) else responses
            
            results.append({
                "provider": self.executor.router.provider,
                "category": "Multi-Turn",
                "conversation": messages,
                "responses": responses,
                "response_length": len(str(final_response).split())
            })
            
            time.sleep(4)
            
        return results

