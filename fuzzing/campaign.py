import json
import os
import time
from datetime import datetime

from datasets.artifact_loader import ArtifactLoader
from fuzzing.behavior_tracker import BehaviorTracker
from fuzzing.executor import FuzzExecutor
from fuzzing.fitness import FitnessCalculator
from fuzzing.mutations.ai_mutator import AIMutator
from fuzzing.mutator import PromptMutator
from fuzzing.novelty import NoveltySearch
from fuzzing.operator_statistics import OperatorStatistics
from fuzzing.oracle.ai_judge import AIJudge
from fuzzing.oracle.fusion import ResultFusion
from fuzzing.oracle.oracle import Oracle
from fuzzing.seed_pool.seed_pool import SeedPool
from analysis.lvi import LVI
from ui.evolution_tree import show_evolution_tree
from utils.checkpoint import CampaignCheckpoint
from utils.response_summary import summarize_response
from utils.seed_history import SeedHistory

# ======================================
# Evolution Parameters
# ======================================
fitness_threshold = 30
NOVELTY_BONUS = 20


class FuzzCampaign:

    def __init__(
        self, provider, mutation_engine="AI Generated Mutations (Recommended)"
    ):
        self.executor = FuzzExecutor(provider)
        self.template_mutator = PromptMutator()
        self.ai_mutator = AIMutator()
        self.mutation_engine = mutation_engine
        self.ai_judge = AIJudge()

        # New components for adaptive fuzzing
        self.seed_pool = SeedPool()
        self.oracle = Oracle()
        self.fitness = FitnessCalculator()
        self.behavior_tracker = BehaviorTracker()
        self.operator_stats = OperatorStatistics()
        self.fusion = ResultFusion()
        self.novelty = NoveltySearch()

    def save_checkpoint(self, results):
        """Saves campaign progress after every completed test."""
        os.makedirs("checkpoints", exist_ok=True)
        filename = datetime.now().strftime("campaign_%Y%m%d_%H%M%S.json")
        path = os.path.join("checkpoints", filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        return path

    def run(
        self,
        seed_prompt,
        max_tests,
        generations=3,
        dataset_name=None,
        initial_seed_count=100,
        seed_source="Custom Prompt",
        seed_pool_size=100,
        fitness_threshold=30,
        resume_data=None,
        progress_bar=None,
        status_text=None,
        completed_tests=0,
        total_tests=1,
    ):
        print("=" * 60)
        print("NEW CAMPAIGN STARTED")
        os.makedirs("checkpoints", exist_ok=True)

        checkpoint_file = os.path.join(
            "checkpoints",
            datetime.now().strftime("campaign_%Y%m%d_%H%M%S.json"),
        )
        print(f"Seed Source      : {seed_source}")
        print(f"Dataset          : {dataset_name}")
        print(f"Initial Seeds    : {initial_seed_count}")
        print(f"Max Pool Size    : {seed_pool_size}")
        print(f"Fitness Threshold: {fitness_threshold}")
        print()
        print("=" * 60)

        # ---------------------------------------
        # Initialize Seed Pool
        # ---------------------------------------
        benchmark_prompts = []
        previous_prompts = []

        # Built-in Dataset Ingestion
        if seed_source in ["Built-in Dataset", "Hybrid Mode ⭐"]:
            loader = ArtifactLoader(dataset_name)
            benchmark_prompts = loader.load()
            benchmark_prompts = benchmark_prompts[:initial_seed_count]
            print(f"Loaded {len(benchmark_prompts)} benchmark prompts.")

            if seed_source == "Hybrid Mode ⭐":
                previous_prompts = SeedHistory.get_best_prompts(
                    limit=20, minimum_fitness=60
                )
                print(
                    f"Loaded {len(previous_prompts)} prompts from previous campaigns."
                )

            for item in benchmark_prompts:
                self.seed_pool.add_prompt(
                    prompt=item["prompt"],
                    attack_category=item["category"],
                    generation=0,
                    operator=item["attack_method"],
                    fitness=1,
                    score=0,
                    confidence=0,
                    success=False,
                )

            for item in previous_prompts:
                self.seed_pool.add_prompt(
                    prompt=item["prompt"],
                    attack_category=item["attack_category"],
                    generation=0,
                    operator="Previous Campaign",
                    fitness=item["fitness"],
                    score=item["oracle_score"],
                    confidence=item["confidence"],
                    success=item["success"],
                )

        # Custom Prompt Ingestion
        if seed_source in ["Custom Prompt", "Hybrid Mode ⭐"]:
            self.seed_pool.add_prompt(
                prompt=seed_prompt,
                attack_category="User Prompt",
                generation=0,
                operator="User",
                fitness=5,
                score=0,
                confidence=0,
                success=False,
            )
            print("Custom prompt added to Seed Pool.\n")

            print("=" * 60)
            print("INITIAL SEED POOL")
            print("=" * 60)
            print(f"Total Initial Seeds : {self.seed_pool.size()}\n")

            for index, seed in enumerate(self.seed_pool.get_all(), start=1):
                print(
                    f"{index:03d} | "
                    f"Source={seed.operator:<20} "
                    f"Generation={seed.generation:<2} "
                    f"Fitness={seed.fitness:<5} "
                    f"Category={seed.attack_category}"
                )
            print("=" * 60)

        results = []
        checkpoint_name = "current_campaign.json"

        # ---------------------------------------
        # Dynamic Planned Test Counter
        # ---------------------------------------
        planned_tests = 0

        # ---------------------------------------
        # Evolutionary Generation Loop
        # ---------------------------------------
        start_generation = 0
        if resume_data is not None:
            start_generation = resume_data["generation"]

        for generation in range(start_generation, generations):
            print()
            print("=" * 60)
            print(f"GENERATION {generation}")
            print("=" * 60)

            generation_results = []

            # =====================================================
            # Evaluate EVERY seed in the current seed pool
            # =====================================================

            current_population = list(self.seed_pool.get_all())

            # ---------------------------------------
            # Count planned tests for THIS generation
            # ---------------------------------------
            planned_tests += len(current_population) * max_tests

            print(f"Processing {len(current_population)} seeds")

            for seed_index, current_seed in enumerate(current_population, start=1):

                current_prompt = current_seed.prompt

                print()
                print("-" * 60)
                print(
                    f"Seed {seed_index}/{len(current_population)} "
                    f"| Fitness={current_seed.fitness} "
                    f"| Operator={current_seed.operator}"
                )

                # ---------------------------------------
                # Generate mutations
                # ---------------------------------------

                if self.mutation_engine == "AI Generated Mutations (Recommended)":

                    mutated_prompts = self.ai_mutator.generate(
                        current_prompt,
                        count=max_tests
                    )

                    if not mutated_prompts:

                        print("AI mutation failed.")
                        print("Using template mutations.")

                        mutated_prompts = (
                            self.template_mutator.generate_mutations(
                                current_prompt
                            )
                        )[:max_tests]

                else:

                    mutated_prompts = (
                        self.template_mutator.generate_mutations(
                            current_prompt
                        )
                    )[:max_tests]

            # ---------------------------------------
            # Execute Mutations
            # ---------------------------------------
                for i, attack in enumerate(mutated_prompts, start=1):
                    print("=" * 60)
                    print(
                        f"Running Gen {generation} | Test {i}/{len(mutated_prompts)}"
                    )
                    print("Category :", attack["category"])
                    print("Prompt   :", attack["prompt"])
                    print("=" * 60)

                    response = self.executor.run_prompt(attack["prompt"])

                    if isinstance(response, dict):
                        response_text = response.get("response", "")
                    else:
                        response_text = str(response)
                    response_summary = summarize_response(response_text)

                    # Infrastructure Error Handling
                    if response_text.startswith("OLLAMA ERROR"):
                        print("Infrastructure Error Detected")
                        failed_result = {
                            "provider": self.executor.router.provider,
                            "generation": generation,
                            "mutation_category": attack["category"],
                            "attack_category": attack["category"],
                            "prompt": attack["prompt"],
                            "response": response_text,
                            "response_summary": response_text,
                            "response_time": 0,
                            "response_length": 0,
                            "fitness": 0,
                            "novelty": 0,
                            "success": False,
                            "severity": "Failed",
                            "confidence": 0,
                            "reason": "Infrastructure Error",
                            "status": "Infrastructure Error",
                            "oracle_keywords": [],
                            "oracle_refusals": [],
                            "oracle_score": 0,
                            "oracle_success": False,
                            "oracle_confidence": 0,
                            "oracle_reason": "Infrastructure Error",
                        }
                        results.append(failed_result)
                        generation_results.append(failed_result)
                        completed_tests += 1

                        if progress_bar:
                            progress_bar.progress(completed_tests / total_tests)
                        continue

                    # Response Preview Display
                    print("\nResponse Preview")
                    print("-" * 40)
                    preview = response_text[:600]
                    print(preview)
                    if len(response_text) > 400:
                        print("...")
                    print("-" * 40)

                    # Oracles & Evaluators Pipeline
                    attack_category = attack["category"]
                    oracle_result = self.oracle.evaluate(response_text)
                    oracle_result["attack_category"] = attack_category
                    ai_result = self.ai_judge.evaluate(
                        attack["prompt"], response_text
                    )

                    fused_result = self.fusion.fuse(oracle_result, ai_result)

                    # Compute Novelty and Fitness Metrics
                    population = [seed.prompt for seed in self.seed_pool.get_all()]
                    novelty_score = self.novelty.score(
                        attack["prompt"], population
                    )
                    attack["novelty"] = novelty_score

                    fitness = self.fitness.calculate(
                        fused_result, response_text, novelty_score
                    )
                    # ---------------------------------------
                    # Reproducibility Score
                    # ---------------------------------------

                    reproducibility = {
                        "success": 1 if fused_result["success"] else 0,
                        "attempts": 1
                    }

                    # ---------------------------------------
                    # LLM Vulnerability Index
                    # ---------------------------------------

                    lvi = LVI.calculate(
                        severity=fused_result["severity"],
                        attack_category=fused_result["attack_category"],
                        confidence=fused_result["confidence"],
                        novelty=novelty_score,
                        reproducibility=reproducibility
                    )

                    print("\n========== LVI ==========")
                    print(lvi)
                    print("=========================\n")
                    
                    # Update Global Statistics & Internal Mutation Operators
                    self.operator_stats.update(attack["category"], fitness)
                    for operator in self.ai_mutator.manager.get_all():
                        if operator.category == attack["category"]:
                            operator.update(fitness)
                            break

                    new_behavior = self.behavior_tracker.is_new_behavior(
                        fused_result
                    )
                    if new_behavior:
                        print("⭐ New Behaviour Discovered!")
                        fitness += NOVELTY_BONUS

                    if current_seed is not None:
                        current_seed.visit()
                        current_seed.update_reward(fitness)

                    print(f"Fitness : {fitness}")
                    print(f"Novelty Score: {novelty_score}")

                    print("\nOracle Evaluation")
                    print("-" * 40)
                    print("Attack Success :", oracle_result["success"])
                    print("Score          :", oracle_result["score"])
                    print("Confidence     :", oracle_result["confidence"])
                    print("Category       :", oracle_result["attack_category"])
                    print(
                        "Refused        :",
                        oracle_refused := oracle_result.get("refused", False),
                    )
                    print("Matched Keywords :", oracle_result["matched_keywords"])
                    print("Matched Refusals :", oracle_result["matched_refusals"])
                    print("Reason :", oracle_result["reason"])
                    print()

                    print("AI Judge")
                    print("-" * 40)
                    print("Success    :", ai_result["success"])
                    print("Confidence :", ai_result["confidence"])
                    print("Reason     :", ai_result["reason"])
                    print()

                    print("Fusion")
                    print("-" * 40)
                    print("Success        :", fused_result["success"])
                    print("Attack Type    :", fused_result["attack_category"])
                    print("Severity       :", fused_result["severity"])
                    print("Confidence     :", fused_result["confidence"])
                    print("Reason         :", fused_result["reason"])
                    print("-" * 40)

                    # Pack Execution Summary Payload
                    result_payload = {
                        "provider": self.executor.router.provider,
                        "generation": generation,
                        "mutation_category": attack["category"],
                        "prompt": attack["prompt"],
                        "response": response_text,
                        "response_summary": response_summary,
                        "response_time": (
                            response["response_time"]
                            if isinstance(response, dict)
                            else 0
                        ),
                        "response_length": len(response_text.split()),
                        "fitness": fitness,
                        "novelty": novelty_score,
                        "new_behavior": new_behavior,
                        "oracle_success": oracle_result["success"],
                        "oracle_score": oracle_result["score"],
                        "oracle_confidence": oracle_result["confidence"],
                        "oracle_attack_category": oracle_result["attack_category"],
                        "oracle_severity": oracle_result.get(
                            "severity", fused_result["severity"]
                        ),
                        "oracle_refused": oracle_result.get("refused", False),
                        "oracle_reason": oracle_result["reason"],
                        "oracle_keywords": oracle_result.get(
                            "matched_keywords", []
                        ),
                        "oracle_refusals": oracle_result.get(
                            "matched_refusals", []
                        ),
                        "judge_success": ai_result["success"],
                        "judge_confidence": ai_result["confidence"],
                        "judge_reason": ai_result["reason"],
                        "success": fused_result["success"],
                        "category": fused_result[
                            "attack_category"
                        ],  # compatibility
                        "attack_category": fused_result["attack_category"],
                        "severity": fused_result["severity"],
                        "confidence": fused_result["confidence"],
                        "reason": fused_result["reason"],
                        "fused_reason": fused_result["reason"],
                        # ---------------------------------------
                        # LVI Metrics
                        # ---------------------------------------
                        "lvi_score": lvi["lvi_score"],
                        "lvi_level": lvi["level"],
                        "lvi_rating": lvi["rating"],
                        "lvi_formula": lvi["formula"],

                        # Component Scores
                        "lvi_severity": lvi["severity"],
                        "lvi_exploitability": lvi["exploitability"],
                        "lvi_confidence": lvi["confidence"],
                        "lvi_novelty": lvi["novelty"],
                        "lvi_reproducibility": lvi["reproducibility"],
                        "lvi_impact": lvi["impact"],
                        "status": (
                            "Refused"
                            if oracle_result.get("refused", False)
                            else "Success"
                            if fused_result["success"]
                            else "Failed"
                        ),
                    }
                    print(result_payload.keys())
                    print("\nLVI Score :", result_payload["lvi_score"])
                    print("Risk Level :", result_payload["lvi_level"])
                    print("Rating :", result_payload["lvi_rating"])
                    results.append(result_payload)
                    generation_results.append(result_payload)

                    # Update Campaign Tracking Progress
                    completed_tests += 1
                    if progress_bar:
                        progress = min(
                            completed_tests / max(total_tests, 1),
                            0.999
                        )

                        progress_bar.progress(progress)

                    if status_text:
                        status_text.markdown(
                            f"""
                            **Running Campaign**
                            Provider : {self.executor.router.provider}
                            Generation : {generation + 1}/{generations}
                            Mutation : {i}/{len(mutated_prompts)}
                            Completed : {completed_tests}/{total_tests}
                            """
                        )

                    with open(checkpoint_file, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=4, ensure_ascii=False)

                    # Adaptive Feedback Loop: Conditional Seed Pool Ingestion
                    if (
                        fitness >= fitness_threshold
                        and self.seed_pool.size() < seed_pool_size
                    ):
                        self.seed_pool.add_prompt(
                            prompt=attack["prompt"],
                            parent=current_seed,
                            score=oracle_result["score"],
                            fitness=fitness,
                            confidence=fused_result["confidence"],
                            success=fused_result["success"],
                            attack_category=fused_result["attack_category"],
                            generation=generation + 1,
                            operator=attack["category"],
                        )
                        print("Added to Seed Pool")

                    # Throttling to prevent API rate limits
                    time.sleep(1)

            # End of Generation Logging
            gen_best_fitness = (
                max([r["fitness"] for r in generation_results])
                if generation_results
                else 0
            )
            print("\n" + "=" * 40)
            print("Generation Finished")
            print(f"Best Fitness   : {gen_best_fitness}")
            print(f"Seed Pool Size : {self.seed_pool.size()}\n")
            print(f"Seeds Evaluated : {len(current_population)}")
            print(f"Mutations/Seed : {max_tests}")
            print(f"Executed Tests : {len(current_population) * max_tests}")

            checkpoint_data = {
                "generation": generation + 1,
                "results": results,
                "seed_source": seed_source,
                "dataset_name": dataset_name,
                "seed_prompt": seed_prompt,
                "max_tests": max_tests,
                "generations": generations,
                "seed_pool_size": seed_pool_size,
                "fitness_threshold": fitness_threshold,
                "initial_seed_count": initial_seed_count,
            }

            CampaignCheckpoint.save(checkpoint_name, checkpoint_data)
            top = sorted(
                self.seed_pool.get_all(),
                key=lambda x: x.fitness,
                reverse=True,
            )[:5]

            print("Top Seeds")
            for seed in top:
                print(
                    f"Fitness={seed.fitness} | "
                    f"Generation={seed.generation} | "
                    f"{seed.operator}"
                )
            print("=" * 40)

        # ---------------------------------------
        # Campaign Summary Terminal Reporting
        # ---------------------------------------
        print("\n")
        print("=" * 60)
        print("CAMPAIGN SUMMARY")
        print("=" * 60)

        successful = sum(
            1 for r in results
            if r.get("oracle_success", False)
        )

        refused = sum(
            1 for r in results
            if r.get("oracle_refused", False)
        )

        failed = len(results) - successful

        print(f"Total Tests : {len(results)}")
        print(f"Successful Attacks : {successful}")
        print(f"Failed Attacks : {failed}")
        print(f"Refused Responses : {refused}")

        if results:
            avg_score = sum(
                r.get("oracle_score", 0) for r in results
            ) / len(results)
            avg_confidence = sum(r["confidence"] for r in results) / len(
                results
            )
        else:
            avg_score = 0
            avg_confidence = 0

        print(f"Average Oracle Score : {avg_score:.2f}")
        print(f"Average Confidence   : {avg_confidence:.2f}")
        print("=" * 60)

        # Current Seed Pool Reporting
        print("\n")
        print("=" * 60)
        print("CURRENT SEED POOL")
        print("=" * 60)
        for seed in sorted(
            self.seed_pool.get_all(), key=lambda s: s.fitness, reverse=True
        ):
            print(seed)
        print("=" * 60)

        # Seed Pool Analytical Statistics
        print("\nSeed Pool Statistics")
        print("-" * 40)

        if self.seed_pool.size() > 0:
            best = self.seed_pool.get_best_seed()
            avg = (
                sum(s.fitness for s in self.seed_pool.get_all())
                / self.seed_pool.size()
            )

            print(f"Pool Size       : {self.seed_pool.size()}")
            if best:
                print(f"Best Fitness    : {best.fitness}")
            else:
                print("Best Fitness    : 0")
            print(f"Average Fitness : {avg:.2f}")

            # Top 5 Seeds Display
            print("\n")
            print("=" * 60)
            print("TOP 5 SEEDS")
            print("=" * 60)

            top = sorted(
                self.seed_pool.get_all(), key=lambda s: s.fitness, reverse=True
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
                self.behavior_tracker.total_behaviors(),
            )
            print("=" * 60)

        # Top Mutations Performance Details
        if results:
            ranked = sorted(
                results,
                key=lambda x: x.get("fitness", 0),
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
                    f"{item['mutation_category']} | "
                    f"Fitness={item['fitness']} | "
                    f"Success={item['success']}"
                )
            print("=" * 60)

            best = ranked[0]
            print()
            print("=" * 60)
            print("BEST MUTATION DETAILS")
            print("=" * 60)
            print("Generation   :", best["generation"])
            print("Category     :", best["mutation_category"])
            print("Fitness      :", best["fitness"])
            print("Oracle Score :", best["oracle_score"])
            print("Oracle Confidence :", best["oracle_confidence"])
            print("Attack Type  :", best["attack_category"])
            print("Severity     :", best["severity"])
            print("Fusion Reason :", best["reason"])
            print("Oracle Reason :", best["oracle_reason"])

            print("\nPrompt Preview:")
            print(best["prompt"][:300])
            if len(best["prompt"]) > 300:
                print("...")
            print("=" * 60)

            # Verification: Seed Pool Lineage & Ancestry relationships
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

        # Operator Statistics Performance Breakdown
        print()
        print("=" * 60)
        print("OPERATOR STATISTICS")
        print("=" * 60)
        for operator, info in self.operator_stats.summary().items():
            print(
                f"{operator:<20}"
                f"Runs={info['runs']:<5}"
                f"Avg Fitness={info['average_fitness']:.2f}"
            )
        print()
        print("=" * 60)
        print("CHECKPOINT SAVED")
        print(checkpoint_file)
        print("=" * 60)
        CampaignCheckpoint.delete(checkpoint_name)

        # Final Terminal Output: Evolution Ancestry Tree Structure
        print("\nEvolution Tree")
        for seed in self.seed_pool.get_all():
            parent = seed.parent.operator if seed.parent else "ROOT"
            print(f"{parent} -> {seed.operator}")

        return results, completed_tests, planned_tests

    def run_conversation_campaign(self, conversation_turns, max_tests):
        """Temporary multi-turn conversation pipeline execution.

        Executes interactions sequentially without applying evaluating oracles,
        judges, or fitness scores.
        """
        results = []

        for i in range(min(len(conversation_turns), max_tests)):
            messages = conversation_turns[i]
            responses = self.executor.run_conversation(messages)

            results.append({"messages": messages, "responses": responses})
            time.sleep(1)

        return results