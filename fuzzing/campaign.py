import time
from fuzzing.executor import FuzzExecutor
from fuzzing.mutator import PromptMutator
from fuzzing.conversation_fuzzer import ConversationFuzzer


class FuzzCampaign:

    def __init__(self):
        self.conversation = ConversationFuzzer()
        self.mutator = PromptMutator()
        self.executor = FuzzExecutor()

    def run(self, seed_prompt, max_tests):
        print("=" * 60)
        print("NEW CAMPAIGN STARTED")
        print("=" * 60)
        
        # 1. Generate mutations from the initial seed prompt
        mutated_prompts = self.mutator.generate_mutations(seed_prompt)
        
        # Enforce maximum test limit by slicing the list
        mutated_prompts = mutated_prompts[:max_tests]
        results = []

        # 2. Iterate through each limited unique prompt attack object
        for i, attack in enumerate(mutated_prompts, start=1):
            print(f"Running Test {i}/{len(mutated_prompts)}")

            # EXACTLY ONE CALL to Gemini per prompt mapping
            response = self.executor.run_prompt(attack["prompt"])

            # Store the individual run results including the attack category metadata
            results.append({
                "category": attack["category"],
                "prompt": attack["prompt"],
                "response": response
            })

            # Campaign delay (rate limiting) applied once per loop iteration
            time.sleep(4)

        # 3. Run Multi-Turn Conversation Fuzzing Mode
        print("\n" + "=" * 40)
        print("RUNNING MULTI-TURN CONVERSATION FUZZING")
        print("=" * 40)
        
        conversations = self.conversation.generate_conversations()

        for conversation in conversations:
            # Executes the conversation array sequentially through the client
            result = self.executor.run_conversation(conversation)

            # Package and append the dialogue chain state
            results.append({
                "category": "Multi-Turn",
                "conversation": conversation,
                "responses": result
            })

            # Respect rate limit buffers between conversation chains
            time.sleep(4)

        # 4. Return the cumulative single-turn and multi-turn results
        return results