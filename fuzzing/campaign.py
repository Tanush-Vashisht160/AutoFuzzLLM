import time

from fuzzing.executor import FuzzExecutor
from fuzzing.mutator import PromptMutator
from fuzzing.mutations.ai_mutator import AIMutator

from fuzzing.seed_pool.seed_pool import SeedPool
from fuzzing.oracle.oracle import Oracle
from fuzzing.fitness import FitnessCalculator
from fuzzing.behavior_tracker import BehaviorTracker
from fuzzing.operator_statistics import OperatorStatistics
# ======================================
# Evolution Parameters
# ======================================

SEED_THRESHOLD = 30
NOVELTY_BONUS = 20

class FuzzCampaign:

    def __init__(
        self,
        provider,
        mutation_engine="AI Generated Mutations (Recommended)"
    ):

        self.executor = FuzzExecutor(provider)
        self.template_mutator = PromptMutator()
        self.ai_mutator = AIMutator()
        self.mutation_engine = mutation_engine

        # New components for adaptive fuzzing
        self.seed_pool = SeedPool()
        self.oracle = Oracle()
        self.fitness = FitnessCalculator()
        self.behavior_tracker = BehaviorTracker()
        self.operator_stats = OperatorStatistics()

    def run(self, seed_prompt, max_tests, generations=3):

        print("=" * 60)
        print("NEW CAMPAIGN STARTED")
        print("=" * 60)

        # Add the original prompt to the Seed Pool
        self.seed_pool.add_prompt(prompt=seed_prompt, generation=0, operator="Original")
        print()
        print("Seed Pool Size :", self.seed_pool.size())
        print("Current Seeds:")
        for seed in self.seed_pool.get_all():
            print(seed)

        results = []

        # ---------------------------------------
        # Evolutionary Generation Loop
        # ---------------------------------------
        for generation in range(generations):
            print()
            print("=" * 60)
            print(f"GENERATION {generation}")
            print("=" * 60)

            # Adaptive seed selection
            selected_seed = self.seed_pool.get_weighted_seed()
            if selected_seed is None:
                current_seed = None
                current_prompt = seed_prompt
            else:
                current_seed = selected_seed
                current_prompt = selected_seed.prompt

            # ---------------------------------------
            # Generate Mutations
            # ---------------------------------------
            if self.mutation_engine == "AI Generated Mutations (Recommended)":

                print(f"\nGenerating AI Mutations for Gen {generation}...\n")

                mutated_prompts = self.ai_mutator.generate(
                    current_prompt,
                    count=max_tests
                )

                # Fallback to template mutations
                if not mutated_prompts:

                    print("AI mutation generation failed.")
                    print("Falling back to Template Mutations...\n")

                    mutated_prompts = (
                        self.template_mutator.generate_mutations(current_prompt)
                    )[:max_tests]

                else:

                    print(f"Generated {len(mutated_prompts)} AI mutations.\n")

            else:

                print(f"\nGenerating Template Mutations for Gen {generation}...\n")

                mutated_prompts = (
                    self.template_mutator.generate_mutations(current_prompt)
                )[:max_tests]

            generation_results = []

            # ---------------------------------------
            # Execute Mutations
            # ---------------------------------------
            for i, attack in enumerate(mutated_prompts, start=1):

                print("=" * 60)
                print(f"Running Gen {generation} | Test {i}/{len(mutated_prompts)}")
                print("Category :", attack["category"])
                print("Prompt   :", attack["prompt"])
                print("=" * 60)

                response = self.executor.run_prompt(
                    attack["prompt"]
                )

                response_text = response["response"]

                ####################################################
# Skip infrastructure errors
####################################################

                if response_text.startswith("OLLAMA ERROR"):

                    print("Skipping timeout/error response.")

                    continue

                # --- Response Preview Block ---
                print("\nResponse Preview")
                print("-" * 40)
                preview = response_text[:400]
                print(preview)
                if len(response_text) > 400:
                    print("...")
                print("-" * 40)
                # ------------------------------------

                # Oracle evaluation
                oracle_result = self.oracle.evaluate(response_text)

                fitness = self.fitness.calculate(oracle_result, response_text)
                self.operator_stats.update(attack["category"],fitness)
                
                new_behavior= self.behavior_tracker.is_new_behavior(oracle_result)
                if new_behavior:
                    print("⭐ New Behaviour Discovered!")
                    fitness += NOVELTY_BONUS
                
                if current_seed is not None:
                    current_seed.visit()
                    current_seed.update_reward(fitness)
                print(f"Fitness : {fitness}")

                print("\nOracle Evaluation")
                print("-" * 40)

                print("Attack Success :", oracle_result["success"])
                print("Score          :", oracle_result["score"])
                print("Confidence     :", oracle_result["confidence"])
                print("Category       :", oracle_result["attack_category"])
                print("Refused        :", oracle_result["refused"])

                print("Matched Keywords :", oracle_result["matched_keywords"])
                print("Matched Refusals :", oracle_result["matched_refusals"])

                print("Reason :", oracle_result["reason"])

                print("-" * 40)

                result_payload = {
                    "provider": self.executor.router.provider,
                    "generation": generation,
                    "category": attack["category"],
                    "prompt": attack["prompt"],
                    "response": response_text,
                    "response_time": response["response_time"],
                    "response_length": len(response_text.split()),
                    "oracle_success": oracle_result["success"],
                    "oracle_score": oracle_result["score"],
                    "oracle_confidence": oracle_result["confidence"],
                    "oracle_attack_category": oracle_result["attack_category"],
                    "oracle_refused": oracle_result["refused"],
                    "oracle_matched_keywords": oracle_result["matched_keywords"],
                    "oracle_matched_refusals": oracle_result["matched_refusals"],
                    "oracle_reason": oracle_result["reason"],
                    "fitness": fitness,
                    "new_behavior": new_behavior
                }

                results.append(result_payload)
                generation_results.append(result_payload)

                # --- Adaptive Feedback Loop: Conditional Seed Pool Ingestion ---
                SEED_THRESHOLD=30
                if fitness >= SEED_THRESHOLD:
                    self.seed_pool.add_prompt(
                        prompt=attack["prompt"],
                        parent=current_seed,
                        score=oracle_result["score"],
                        fitness=fitness,
                        confidence=oracle_result["confidence"],
                        success=oracle_result["success"],
                        attack_category=oracle_result["attack_category"],
                        generation=generation + 1,
                        operator=attack["category"]
                    )
                    print("Added to Seed Pool")

                # Helps avoid API rate limits
                time.sleep(4)

            # --- End of Generation Logging ---
            gen_best_fitness = max([r["fitness"] for r in generation_results]) if generation_results else 0
            print("\n" + "=" * 40)
            print("Generation Finished")
            print(f"Best Fitness   : {gen_best_fitness}")
            print(f"Seed Pool Size : {self.seed_pool.size()}")
            print("=" * 40)
            
        print("\n")
        print("=" * 60)
        print("CAMPAIGN SUMMARY")
        print("=" * 60)

        successful = sum(
            1 for r in results if r["oracle_success"]
        )

        refused = sum(
            1 for r in results if r["oracle_refused"]
        )

        failed = len(results) - successful

        print(f"Total Tests : {len(results)}")
        print(f"Successful Attacks : {successful}")
        print(f"Failed Attacks : {failed}")
        print(f"Refused Responses : {refused}")

        if len(results) > 0:

            avg_score = (
                sum(r["oracle_score"] for r in results)
                / len(results)
            )

            avg_confidence = (
                sum(r["oracle_confidence"] for r in results)
                / len(results)
            )

            print(f"Average Oracle Score : {avg_score:.2f}")
            print(f"Average Confidence   : {avg_confidence:.2f}")

        print("=" * 60)

        # --- Current Seed Pool Reporting Block ---
        print("\n")
        print("=" * 60)
        print("CURRENT SEED POOL")
        print("=" * 60)
        for seed in sorted(
            self.seed_pool.get_all(),
            key=lambda s: s.fitness,
            reverse=True
        ):
            print(seed)
        print("=" * 60)

        # --- Seed Pool Statistics Block ---
        print("\nSeed Pool Statistics")
        print("-" * 40)
        if self.seed_pool.size() > 0:
            best = max(
                self.seed_pool.get_all(),
                key=lambda s: s.fitness
            )
            avg = (
                sum(s.fitness for s in self.seed_pool.get_all())
                / self.seed_pool.size()
            )
            print(f"Pool Size       : {self.seed_pool.size()}")
            print(f"Best Fitness    : {best.fitness}")
            print(f"Average Fitness : {avg:.2f}")

        #####################################################
# Top Seeds
#####################################################

            print("\n")
            print("=" * 60)
            print("TOP 5 SEEDS")
            print("=" * 60)

            top = sorted(
                self.seed_pool.get_all(),
                key=lambda s: s.fitness,
                reverse=True
            )

            for i, seed in enumerate(top[:5], start=1):

                print(
                    f"{i}. "
                    f"Generation={seed.generation} | "
                    f"Operator={seed.operator} | "
                    f"Fitness={seed.fitness} | "
                    f"Visits={seed.visits} | "
                    f"Reward={seed.reward:.2f} | "
                    f"AvgReward={seed.average_reward():.2f}"
                )

            print("=" * 60)

            print("\n")
            print("=" * 60)
            print("BEHAVIOUR STATISTICS")
            print("=" * 60)

            print(
                "Unique Behaviours :",
                self.behavior_tracker.total_behaviors()
            )

            print("=" * 60)
        #####################################################
        # Top & Best Mutations Summary
        #####################################################

        if results:
            ranked = sorted(
                results,
                key=lambda x: x["fitness"],
                reverse=True
            )

            print("\n")
            print("=" * 60)
            print("TOP MUTATIONS")
            print("=" * 60)
            for i, item in enumerate(ranked[:5], start=1):
                print(
                    f"{i}. "
                    f"Gen {item['generation']} | "
                    f"{item['category']} | "
                    f"Fitness={item['fitness']} | "
                    f"Success={item['oracle_success']}"
                )
            print("=" * 60)

            # Detail the single best mutation out of the ranked list
            best = ranked[0]

            print()
            print("=" * 60)
            print("BEST MUTATION DETAILS")
            print("=" * 60)

            print("Generation   :", best["generation"])
            print("Category     :", best["category"])
            print("Fitness      :", best["fitness"])
            print("Oracle Score :", best["oracle_score"])
            print("Confidence   :", best["oracle_confidence"])
            print("Attack Type  :", best["oracle_attack_category"])
            print("Reason       :", best["oracle_reason"])
            
            print("\nPrompt Preview:")
            print(best["prompt"][:300])
            if len(best["prompt"]) > 300:
                print("...")

            print("=" * 60)

            #####################################################
            # Seed Relationship Verification (Temporary)
            #####################################################

            print("\n")
            print("=" * 60)
            print("SEED RELATIONSHIPS")
            print("=" * 60)

            for seed in self.seed_pool.get_all():

                parent = "None"

                if seed.parent:
                    parent = seed.parent.operator

                print(
                    f"Generation={seed.generation} | "
                    f"Operator={seed.operator} | "
                    f"Parent={parent} | "
                    f"Fitness={seed.fitness}"
                )

            print("=" * 60)

        return results

    def run_conversation_campaign(self, conversation_turns, max_tests):

        results = []

        for i in range(min(len(conversation_turns), max_tests)):

            messages = conversation_turns[i]

            responses = self.executor.run_conversation(messages)

            final_response = (
                responses[-1]["response"]
                if isinstance(responses, list)
                else responses
            )

            results.append({
                "provider": self.executor.router.provider,
                "category": "Multi-Turn",
                "conversation": messages,
                "responses": responses,
                "response_length": len(str(final_response).split()),
                })

            time.sleep(4)

            print("\nOperator Statistics")
            print("-" * 40)

            for operator, info in self.operator_stats.summary().items():
                print(
                    f"{operator} | "
                    f"Runs={info['runs']} | "
                    f"Avg Fitness={info['average_fitness']:.2f}"
    )

        return results