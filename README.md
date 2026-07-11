# AutoFuzzLLM

AutoFuzzLLM is an automated evolutionary-inspired fuzzing framework for Large Language Models (LLMs). It applies fuzzing concepts to natural language by generating adversarial prompt variations, executing them against target LLMs, and analyzing model behavior.
The framework treats jailbreak discovery as a guided search problem over semantic prompt space. It combines mutation-based fuzzing, adaptive seed selection, rule-based detection, AI-assisted evaluation, novelty tracking, and structured reporting into a single pipeline.

## Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Workflow](#workflow)
- [Repository Structure](#repository-structure)
- [Core Concepts](#core-concepts)
- [Mathematical Foundations](#mathematical-foundations)
- [Evaluation Pipeline](#evaluation-pipeline)
- [Evolutionary Fuzzing](#evolutionary-fuzzing)
- [Fitness and Novelty](#fitness-and-novelty)
- [Behaviour Tracking](#behaviour-tracking)
- [Risk Scoring](#risk-scoring)
- [Benchmarks](#benchmarks)
- [Reporting](#reporting)
- [UI and Dashboards](#ui-and-dashboards)
- [Current Limitations](#current-limitations)
- [Future Work](#future-work)
- [Research Motivation](#research-motivation)

## Overview

AutoFuzzLLM applies classical fuzzing principles to natural language systems. Instead of mutating binary inputs or structured files, it mutates prompts, executes them against target LLMs, and evaluates the resulting responses using a hybrid oracle.

The system is built to:
- Generate adversarial prompt variants.
- Detect unsafe behaviors and policy violations.
- Track lineage across generations.
- Score and prioritize effective mutations.
- Produce dashboards and reports for analysis.

Supported capabilities include: - 
-	Multi-model testing through Gemini, Groq, Ollama, and OpenRouter. 
-	15+ prompt mutation operators. 
-	Hybrid evaluation using rule-based oracle detection and AI-based judging. 
-	Campaign-based fuzzing execution. 
-	SQLite-based result storage. 
-	Automated PDF security reports. 
-	Streamlit dashboard visualization.

## Architecture

AutoFuzzLLM is organized as a modular pipeline with distinct components for fuzzing, analysis, model routing, benchmarking, reporting, and visualization.

```text
Seed Pool
   │
   ▼
Seed Selection
   │
   ▼
Mutation Engine
   │
   ▼
Target LLM Execution
   │
   ▼
Oracle + AI Judge
   │
   ▼
Fusion + Risk Scoring
   │
   ▼
Behaviour Analysis
   │
   ▼
Fitness calculation
   │
   ▼
Seed Pool Update
   │
   ▼
Next Generation
```

This architecture allows the system to evolve prompts iteratively while preserving observability and reproducibility.

## Workflow

1. Load baseline prompts from the dataset or user configuration.
2. Select seeds from the adaptive seed pool.
3. Mutate prompts using predefined or AI-assisted operators.
4. Route prompts to the configured target LLM.
5. Evaluate outputs with rule-based detectors and semantic judgment.
6. Compute fitness, novelty, reward, and risk.
7. Update the seed pool and lineage metadata.
8. Repeat for the next generation or campaign cycle.

## Repository Structure

```text
AutoFuzzLLM
├── analysis
│   ├── __init__.py
│   ├── insights.py
│   ├── owasp_mapper.py
│   ├── prompt_detector.py
│   ├── response_classifier.py		# Response categorization
│   ├── risk_score.py				# Severity calculation
│   └── rule_engine.py			# Rule based vulnerability detection
├── benchmark
│   ├── benchmark_loader.py
│   ├── benchmark_metrics.py
│   └── benchmark_runner.py
├── config
│   ├── __init__.py
│   └── settings.py
├── database
│   ├── __init__.py
│   └── database.py
├── datasets
│   ├── seed_prompts.json
│   └── test.json
├── fuzzing
│   ├── attacks
│   │   └── base_attacks.py
│   ├── mcts
│   │   └── ucb1.py
│   ├── mutations
│   │   ├── operators
│   │   │   ├── __init__.py
│   │   │   ├── authority.py
│   │   │   ├── base64.py
│   │   │   ├── base_operator.py
│   │   │   ├── chain_of_thought.py
│   │   │   ├── context_switch.py
│   │   │   ├── indirect.py
│   │   │   ├── json_operator.py
│   │   │   ├── markdown.py
│   │   │   ├── operator_manager.py
│   │   │   ├── persona.py
│   │   │   ├── prompt_leakage.py
│   │   │   ├── roleplay.py
│   │   │   ├── rot13.py
│   │   │   ├── translation.py
│   │   │   ├── typoglycemia.py
│   │   │   ├── unicode.py
│   │   │   └── xml.py
│   │   ├── __init__.py
│   │   ├── ai_mutator.py
│   │   └── template_mutator.py
│   ├── oracle
│   │   ├── detectors
│   │   │   ├── cot_detector.py
│   │   │   ├── data_exfiltration.py
│   │   │   ├── hallucination.py
│   │   │   ├── instruction_override.py
│   │   │   ├── jailbreak_detector.py
│   │   │   ├── override_detector.py
│   │   │   ├── policy_detector.py
│   │   │   ├── prompt_injection.py
│   │   │   ├── prompt_leakage.py
│   │   │   ├── refusal.py
│   │   │   ├── refusal_detector.py
│   │   │   ├── roleplay.py
│   │   │   ├── system_prompt.py
│   │   │   └── tool_abuse.py
│   │   ├── __init__.py
│   │   ├── ai_judge.py
│   │   ├── attack_categories.py
│   │   ├── fusion.py
│   │   └── oracle.py
│   ├── seed_pool
│   │   ├── seed.py
│   │   └── seed_pool.py
│   ├── __init__.py
│   ├── adaptive_campaign.py
│   ├── behavior_tracker.py
│   ├── campaign.py
│   ├── executor.py
│   ├── fitness.py
│   ├── mutation_strategies.py
│   ├── mutator.py
│   ├── novelty.py
│   └── operator_statistics.py
├── llm
│   ├── __init__.py
│   ├── gemini_client.py
│   ├── groq_client.py
│   ├── llm_router.py
│   ├── ollama_client.py
│   └── openrouter_client.py
├── pages
│   └── 1_Campaign_History.py
├── reports
│   ├── __init__.py
│   └── report_generator.py
├── tabs
│   ├── __init__.py
│   ├── batch_campaign.py
│   └── live_fuzzer.py
├── ui
│   ├── assets
│   │   ├── loader.css
│   │   ├── loader.html
│   │   └── loader.js
│   ├── __init__.py
│   ├── charts.py
│   ├── dynamic_insights.py
│   ├── explanations.py
│   ├── insights.py
│   ├── loader.py
│   ├── report_view.py
│   └── styles.css
├── utils
│   ├── __init__.py
│   └── response_summary.py
├── .env
├── .gitignore
├── app.py
├── autofuzz.db
├── campaign_report.pdf
├── core_state.py
├── fuzz_runner.py
├── generate_structure.py
├── llm_mutator.py
├── README.md
├── requirements.txt
├── scorer.py
├── test_adaptive.py
├── test_ai_mutator.py
├── test_benchmark.py
├── test_campaign.py
├── test_database.py
├── test_groq.py
├── test_loader.py
├── test_mutator.py
├── test_openrouter.py
├── test_operator_manager.py
├── test_oracle.py
└── test_seed_pool.py
```

## Core Concepts

AutoFuzzLLM uses the following core concepts:

- **Seed Pool**: A collection of initial attack prompts stored in datasets/seed_prompts.json. These prompts act as starting points for generating mutated adversarial variants.
- **Mutation Operator**: A transformation technique that modifies an existing prompt using strategies such as roleplay, encoding, context switching, translation, and prompt leakage manipulation.
- **Oracle**: A detector that evaluates whether the response indicates unsafe behavior.
- **AI Judge**: A secondary LLM-based evaluator that analyzes whether the target model response represents successful jailbreak, leakage, unsafe compliance, or safe refusal.
- **Fusion Engine**: A component that combines oracle and judge outputs into a final verdict.
- **Fitness**: A score measuring how useful a prompt is for future fuzzing.
- **Novelty**: A measure of behavioral diversity.
- **Behaviour Tracker**: A record of distinct model outputs and defense states.
- **Lineage**: Parent-child relationships between generated prompts.

## Mutation Operators

AutoFuzzLLM contains multiple mutation strategies inspired by adversarial testing techniques.

Implemented operators include:

| Operator | Purpose |
|---|---|
| Persona | Changes model identity/context |
| Roleplay | Creates fictional scenarios |
| Authority | Adds fake authority instructions |
| Context Switch | Changes conversation context |
| Prompt Leakage | Attempts system instruction extraction |
| Base64 | Encodes instructions |
| ROT13 | Character transformation |
| Translation | Multilingual transformation |
| Unicode | Character manipulation |
| Typoglycemia | Word scrambling |
| JSON/XML | Structured prompt wrapping |

These operators generate diverse adversarial prompts for testing LLM robustness.

## Mathematical Foundations

### Fitness Function

The fitness of a prompt is calculated using a heuristic scoring approach:

\[
Fitness(x)=Success(x)+Confidence(x)+Novelty(x)+Risk(x)
\]

Where:

- Success(x) represents whether the attack was confirmed.
- Confidence(x) represents evaluator confidence.
- Novelty(x) represents prompt diversity compared with previous mutations.
- Risk(x) represents detected vulnerability severity.

Currently AutoFuzzLLM uses heuristic optimization to prioritize useful prompts for future mutation cycles.
### Selection Probability

Prompts with higher fitness are more likely to be selected:

\[
P(x) = \frac{F(x)}{\sum_{j=1}^{N} F(j)}
\]

Where:
- \(P(x)\) is the selection probability for seed \(x\).
- \(N\) is the number of seeds in the pool.

### Average Risk

\[
\text{Average Risk} = \frac{\sum_{i=1}^{n} \text{Risk Score}_i}{n}
\]

Where \(n\) is the number of tests in the campaign.

## Evaluation Pipeline

AutoFuzzLLM uses a two-stage evaluation mechanism instead of relying only on keyword matching.

```text
Mutated Prompt
      │
      ▼
Target LLM Response
      │
 ┌────┴─────┐
 ▼          ▼
Rule-Based  AI Judge
Oracle      (LLM)
      │          │
      └────┬─────┘
           ▼
      Result Fusion
           │
           ▼
     Final Verdict
```

### Rule-Based Oracle

The rule-based oracle performs deterministic checks for known unsafe patterns.

Checks include:
- Prompt leakage.
- Jailbreak indicators.
- Malware patterns.
- Credential leakage.
- Refusal detection.
- Dangerous keywords.

Outputs:
- `success`
- `confidence`
- `severity`
- `reason`
- `matched_indicators`

### AI Judge

The AI Judge evaluates the full response semantically using a separate LLM backend such as Groq. It determines whether the model truly leaked sensitive information, complied with the attack, or refused safely.

Outputs:
- `success`
- `confidence`
- `reason`

### Result Fusion

The fusion layer combines both signals into a single verdict shown to the user. This keeps the interface simple while preserving internal evaluation detail.

Example:
- Oracle: Safe
- AI Judge: Safe
- Final Verdict: Safe

Example:
- Oracle: Warning
- AI Judge: Safe
- Final Verdict: Warning

## Evolutionary Fuzzing

The fuzzing engine follows an iterative search process inspired by evolutionary algorithms. High-performing prompts are prioritized for further mutation in future campaign cycles.
```text
Seed Prompt
    │
    ▼
Mutation Engine
    │
    ▼
Mutated Prompts
    │
    ▼
Execute on LLM
    │
    ▼
Oracle + AI Judge
    │
    ▼
Fitness Calculation
    │
    ▼
Seed Pool Update
    │
    ▼
Next Generation
```

Each campaign cycle uses scored prompts to guide future mutation attempts and improve the discovery of effective adversarial variations.

## Multi-Model LLM Support

AutoFuzzLLM supports testing across multiple LLM providers through a unified routing layer.

Supported providers:

- Google Gemini
- Groq hosted models
- Ollama local models
- OpenRouter models

The LLM router allows switching between models without modifying the fuzzing pipeline.

## Fitness and Novelty

### Fitness Calculation

A practical fitness formulation is:

\[
\text{Fitness} = \text{Attack Success} + \text{Confidence} + \text{Novelty} + \text{Oracle Score}
\]

### Novelty Search

Novelty search prevents the system from repeatedly generating nearly identical prompts.
The current implementation uses similarity-based comparison. Future versions can integrate embedding-based semantic distance for improved novelty estimation.

\[
\text{Novelty}(p) = \frac{1}{k}\sum_{i=1}^{k} d(p, p_i)
\]

Where:
- \(p\) is the current prompt.
- \(p_i\) are the nearest previously observed prompts.
- \(d(\cdot)\) is the similarity distance.

Higher novelty increases the chance that a prompt survives into the next generation.

## Behaviour Tracking

Traditional fuzzers look for crashes. AutoFuzzLLM tracks unique LLM behaviors instead.

Tracked behaviors may include:
- Standard refusal.
- Partial compliance.
- Information leakage.
- Role confusion.
- System prompt disclosure.
- Policy bypass.
- Hallucinated authority.
- Context manipulation.

Each new behavior helps the system understand how the target model responds under pressure.

## Risk Scoring

AutoFuzzLLM calculates risk dynamically based on detected vulnerability indicators.

The RiskScorer analyzes LLM responses for security-sensitive keywords and behaviors.

Each detected risk indicator contributes to the final risk score.

Example:

- Malware keyword detection = +15
- Credential keyword detection = +15
- API key detection = +15
- System prompt detection = +15
- Password detection = +15

Additional scoring factors:

- Large responses (>1000 characters) increase risk score by +10.
- Safe refusal responses reduce the score using refusal modifiers.

Severity mapping:

- 0–34 : Low
- 35–69 : Medium
- 70+ : Critical

## Benchmarks

The `benchmark` module provides support for structured evaluation and comparison across campaigns and models.

It includes:
- Benchmark loading.
- Metric computation.
- Benchmark execution.

This makes it easier to compare target models, mutation strategies, and attack performance under consistent conditions.

## Reporting

AutoFuzzLLM generates a PDF report for documentation, sharing, and audit use.

The report can include:
- Executive summary.
- Campaign overview.
- Tested models.
- Final verdicts.
- Mutated prompts.
- Model responses.
- Risk scores.
- Severity distribution.
- Charts.
- Recommendations.

## UI and Dashboards

The `ui` and `tabs` modules provide both live and batch interfaces for campaign monitoring.

Key UI elements include:
- Live campaign execution views.
- Batch campaign views.
- Historical campaign pages.
- Charts and summaries.
- Dynamic insights.
- Report preview components.

The `pages/1_Campaign_History.py` file supports campaign history browsing inside the app.

## Current Limitations

Current known limitations include:
- Evolution strategy is currently heuristic-based rather than a complete genetic algorithm.
- Novelty calculation is similarity-based and can be improved with embeddings.
- Mutation effectiveness depends on the target model and dataset quality.
- AI Judge accuracy depends on the evaluator model capability.
## Future Work

Planned improvements include:
- More robust MCTS-based selection.
- Stronger semantic novelty search.
- Multi-objective fitness optimization.
- Expanded benchmark coverage.
- Additional oracle detectors.
- More detailed automated explanations.
- Better cross-model campaign comparisons.

## Research Motivation

Large Language Models are increasingly used in sensitive applications, making systematic security evaluation essential.

AutoFuzzLLM aims to bridge the gap between traditional fuzzing and modern LLM security research by combining evolutionary optimization, automated evaluation, and structured reporting into a reproducible framework for adversarial testing.
