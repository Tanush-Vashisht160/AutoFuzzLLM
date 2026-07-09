# AutoFuzzLLM: Automated Evolutionary Fuzzing Framework for Large Language Models

AutoFuzzLLM is an open-source, automated evolutionary fuzzing framework engineered to systematically discover, track, and evaluate safety vulnerabilities, alignment regressions, and adversarial prompt vulnerabilities in Large Language Models (LLMs). By treating jailbreak generation as a directed grey-box optimization problem, the system uses genetic algorithms and automated feedback loops to mutate prompt spaces, evaluate target boundaries, and map semantic vulnerabilities.

---

## 1. System Architecture & Workflow

AutoFuzzLLM applies traditional software mutation-based fuzzing paradigms to non-deterministic, natural language interfaces. The framework orchestrates a continuous feedback loop spanning seed selection, semantic mutation, target inference, evaluation, and adaptive reward propagation.

### Pipeline Schematic

```
  [ User Input / Configuration ]
                │
                ▼
        ┌──────────────┐
        │  Seed Pool   │◄──────────────────────────────┐
        └──────┬───────┘                               │
               │ (Selection Strategy)                  │
               ▼                                       │
        ┌──────────────┐                               │
        │Seed Selection│                               │
        └──────┬───────┘                               │
               │                                       │
               ▼                                       │
        ┌──────────────┐                               │
        │ AI Mutation  │ (Groq / OpenRouter API)       │
        └──────┬───────┘                               │
               │ (Mutated Prompt Variants)             │
               ▼                                       │
        ┌──────────────┐                               │
        │  Target LLM  │ (Ollama / Local / Remote)     │
        └──────┬───────┘                               │
               │ (Raw Response Generation)             │
               ▼                                       │
        ┌──────────────┐                               │
        │Oracle Engine │ (LLM-as-a-Judge / Policies)   │
        └──────┬───────┘                               │
               │ (Classification & Scores)             │
               ▼                                       │
        ┌──────────────┐                               │
        │ Fitness / BM │ (Behavior Tracking)           │
        └──────┬───────┘                               │
               │                                       │
               ▼                                       │
        ┌──────────────┐                               │
        │  Reward &    │───────────────────────────────┘
        │ Parent/Child │ (Metric Updates & Realignment)
        └──────────────┘

```

### Operational Workflow Steps

1. **Initialization**: An initial corpus of baseline prompt seeds is loaded into the **Seed Pool**.
2. **Selection**: Seeds are drawn according to fitness performance and exploitation metrics via standard evolutionary selection techniques.
3. **AI Mutation**: Selected prompts are passed to a high-throughput inference engine (e.g., Groq, OpenRouter) running specialized mutation operators. These operators transform the structure using specific strategic contexts, including:
* **Roleplay**: Forcing the model into a fictional persona.
* **Authority**: Simulating administrative or elevated execution privileges.
* **Persona**: Shifting social or behavioral contexts to bypass internal guardrails.


4. **Execution (Target Inference)**: Mutated variants are dispatched concurrently to the **Target LLM** (e.g., local deployments via Ollama or remote model nodes).
5. **Oracle Evaluation**: The target's response is processed by the **Oracle Engine** to quantify jailbreak status, semantic evasion, or policy violations.
6. **Fitness & Behavior Tracking**: A composite scoring module evaluates the prompt's success, tracking unique behavioral profiles to prevent genetic drift and reward diverse paths.
7. **Generation Step & Pool Update**: High-scoring mutations populate the pool as child seeds, preserving their historical lineage (**Parent-Child Relationships**), while lower-tier prompts face generational culling.

---

## 2. Theoretical and Mathematical Foundations

AutoFuzzLLM abstracts prompt vulnerabilities as an optimization problem over a discrete semantic space. The primary objective is to maximize an objective function that reflects alignment failure under safety evaluation constraints.

### Core Fitness Formulation

The fitness function evaluates each individual mutated prompt $x$ within a given generation. Let the prompt's performance be characterized by a multi-component heuristic:

$$F(x) = w_1 \cdot O_{score}(x) + w_2 \cdot B_{novelty}(x) + w_3 \cdot C_{efficiency}(x)$$

Where:

* $O_{score}(x) \in [0, 1]$ represents the target semantic score assigned by the Oracle Engine, indicating how effectively the prompt breached the model's safety policy.
* $B_{novelty}(x) \in [0, 1]$ represents the semantic distance or structural diversity of the response compared to previously tracked generation behaviors.
* $C_{efficiency}(x)$ tracks efficiency constraints, penalizing overly long token arrays to keep the adversarial prompt concise.
* $w_1, w_2, w_3$ represent normalization and scaling weights where $\sum w_i = 1.0$.

### Selection and Reward Strategy

To maintain a balance between **exploring new prompt variations** and **reusing successful prompts**, AutoFuzzLLM assigns each seed a fitness score. Prompts with higher fitness have a greater chance of being selected for the next generation.

The selection probability of a seed is calculated as:

$$
P(x)=\frac{F(x)}{\sum_{j=1}^{N}F(j)}
$$

where:

- **\(P(x)\)** = Probability of selecting seed \(x\)
- **\(F(x)\)** = Fitness score of seed \(x\)
- **\(N\)** = Total number of seeds in the current seed pool

This means that prompts with higher fitness are **more likely** to be selected, but lower-fitness prompts still have a chance, helping maintain diversity in the search.

As the campaign progresses, successful prompts generate new child prompts. If a particular mutation operator (such as **Roleplay**, **Authority**, or **Persona**) consistently produces high-quality mutations, it is selected more frequently in future generations. This allows the framework to gradually focus on mutation strategies that are more effective at discovering vulnerabilities while still exploring new attack paths.


## 3. Directory Structure & Component Significance

The repository is structured to separate interface layers, test orchestrators, and core evolutionary compute logic:

```
├── app.py                       # Streamlit web interface and analytics dashboard
├── main.py                      # CLI entry point for batch campaigns
├── core/
│   ├── __init__.py
│   ├── fuzzer.py                # Live conversation and campaign state machine
│   ├── evolution.py             # Genetic algorithm loop, parent-child managers
│   ├── mutators.py              # Groq/OpenRouter prompt transformation drivers
│   ├── targets.py               # Target LLM connectors (Ollama, API wrappers)
│   ├── oracles.py               # LLM-as-a-Judge and rule-based safety evaluators
│   └── tracker.py               # Behavioral tracking and semantic hashing
└── utils/
    ├── __init__.py
    └── dashboard_helpers.py     # Aggregation modules for fuzzing statistics

```

### Module Specifications

* **`app.py`**: Launches an interactive dashboard using Streamlit. It displays live mutation streams, mutation tree lineages, vulnerability detection metrics, and generational fitness plots.
* **`main.py`**: The headless execution engine for non-interactive, automated fuzzing runs. It reads configurations, sets initial constraints, and saves structured campaign logs.
* **`core/fuzzer.py`**: Manages runtime interactions for multi-turn sessions and batch evaluations, maintaining conversation history while simulating continuous fuzzing conditions.
* **`core/evolution.py`**: Houses the population lifecycle logic. It handles seed selection, generational culling, and parent-child tracking to preserve successful adversarial traits.
* **`core/mutators.py`**: Coordinates API requests to high-speed inference backends (Groq/OpenRouter), prompting helper models to rewrite seeds using specific security personas (e.g., rule negation, obfuscation).
* **`core/targets.py`**: Standardizes the target runtime interface. It decouples target configurations, allowing users to swap local engines (Ollama) with external endpoints seamlessly.
* **`core/oracles.py`**: The framework's automated assessment engine. It combines classification checks, rule matching, and secondary judge calls to evaluate target responses objectively.
* **`core/tracker.py`**: Maps and deduplicates model outputs. It uses state tracking to detect duplicate defense states (e.g., standard refusal phrases) and prioritizes novel outputs.

---

## 4. Framework Capabilities

### Core Feature Set

* **Hybrid Execution Framework**: Provides both a responsive web interface for exploration and a programmatic command-line tool for high-volume automated processing.
* **Intelligent Mutation Infrastructure**: Moves beyond simple random character replacements by using language models to implement complex structural, stylistic, and situational mutations.
* **Lineage Tracking**: Maintains clear records of prompt transformations, helping developers map and study how adversarial prompts evolve across generations.
* **Granular Observability**: Logs detailed execution histories, performance metrics, and behavioral changes to support deeper analysis and downstream security validation.

---

# 5. Internal Data Model

Each prompt within AutoFuzzLLM is represented as a **Seed** object. A seed encapsulates both the prompt itself and the metadata accumulated throughout the evolutionary search process.

```python
Seed(
    prompt: str,
    operator: str,
    generation: int,
    fitness: float,
    visits: int,
    reward: float,
    average_reward: float,
    parent: Seed | None
)
```

## Seed Attributes

| Attribute | Description |
|-----------|-------------|
| Prompt | Current adversarial prompt |
| Operator | Mutation strategy used to generate the prompt |
| Generation | Evolution generation in which the prompt was created |
| Fitness | Composite score assigned after Oracle evaluation |
| Visits | Number of times selected for mutation |
| Reward | Cumulative reward accumulated across selections |
| Average Reward | Reward ÷ Visits |
| Parent | Reference to the parent seed for lineage tracking |

---

# 6. Evolutionary Lifecycle

Each fuzzing campaign follows a complete evolutionary cycle.

```
Generation n

        │

        ▼

Seed Selection

        │

        ▼

AI Mutation

        │

        ▼

Target LLM Evaluation

        │

        ▼

Oracle Analysis

        │

        ▼

Fitness Computation

        │

        ▼

Behaviour Tracking

        │

        ▼

Reward Update

        │

        ▼

Seed Pool Update

        │

        ▼

Generation n + 1
```

This process repeats until the configured generation budget has been exhausted.

---

# 7. Oracle Engine

The Oracle acts as the automated decision mechanism responsible for determining whether a generated prompt successfully induced unsafe or policy-violating behavior.

Current evaluation considers:

- Sensitive keyword detection
- Refusal phrase detection
- Response classification
- Confidence estimation
- Attack success determination

Example evaluation output:

```
Attack Success : True
Score          : 2
Confidence     : 0.70
Category       : Prompt Injection
Reason         : Potential attack indicators detected.
```

The Oracle serves as the primary feedback signal used by the evolutionary algorithm.

---

# 8. Behaviour Tracking

Traditional fuzzers detect unique crashes.

AutoFuzzLLM instead detects unique **LLM behaviours**.

Rather than storing duplicate refusal responses repeatedly, the framework maintains behavioural diversity.

Examples include:

- Standard refusal
- Partial compliance
- Information leakage
- Role confusion
- System prompt disclosure
- Policy bypass
- Hallucinated authority
- Context manipulation

Novel behaviours are rewarded more heavily to encourage exploration of previously unseen attack paths.

---

# 9. Fitness Function

The fitness function estimates the usefulness of every generated mutation.

Conceptually,

\[
Fitness =
OracleScore
+
BehaviourNovelty
+
ResponseQuality
+
Efficiency
\]

where

- OracleScore measures attack success.
- BehaviourNovelty rewards previously unseen behaviours.
- ResponseQuality evaluates usefulness of the generated output.
- Efficiency rewards concise and effective prompts.

Higher fitness values increase the probability that a prompt survives into future generations.

---

# 10. Reward Mechanism

Each seed accumulates reward throughout the campaign.

For every evaluation,

```
Reward += Fitness
Visits += 1
AverageReward = Reward / Visits
```

Average reward estimates the long-term usefulness of a mutation lineage rather than relying solely on a single successful mutation.

---

# 11. Parent–Child Lineage

Every generated mutation preserves a reference to its parent seed.

Example:

```
Original Prompt

        │

        ▼

Roleplay Mutation

        │

        ▼

Persona Mutation

        │

        ▼

Authority Mutation
```

This enables complete reconstruction of mutation trees and provides explainability regarding how successful jailbreaks evolved.

---

# 12. Campaign Statistics

After every campaign AutoFuzzLLM reports:

- Total Tests
- Successful Attacks
- Failed Attacks
- Refused Responses
- Average Oracle Score
- Average Confidence
- Pool Size
- Best Fitness
- Average Fitness
- Behaviour Diversity
- Top Mutations
- Parent–Child Relationships
- Best Mutation Details

These statistics allow quantitative comparison between different target models and mutation strategies.

---

# 13. Current Limitations

Current implementation intentionally prioritizes simplicity and modularity.

Known limitations include:

- Rule-based Oracle can generate false positives.
- Weighted seed selection instead of Monte Carlo Tree Search.
- Behaviour tracking relies primarily on heuristic comparison.
- No semantic embedding-based novelty search.
- Limited benchmark integration.
- Single-objective fitness optimization.

---

# 14. Future Research Roadmap

The framework is actively evolving toward a research-grade LLM security evaluation platform.

Planned improvements include:

- Monte Carlo Tree Search (MCTS)
- UCB1-based node selection
- True reward backpropagation
- Semantic embedding-based novelty search
- Multi-objective fitness optimization
- LLM-as-a-Judge Oracle
- Policy-aware evaluation
- Multi-model benchmarking

---

# 15. Research Motivation

Large Language Models are increasingly deployed in high-impact environments, making systematic security evaluation essential.

AutoFuzzLLM aims to bridge the gap between traditional software fuzzing and modern LLM security by combining evolutionary optimization, AI-guided mutation, and automated behavioural evaluation into a unified, extensible framework capable of discovering adversarial vulnerabilities with minimal human intervention.

The long-term vision is to provide an open, reproducible platform for benchmarking, improving, and stress-testing language models against emerging prompt injection and jailbreak techniques.