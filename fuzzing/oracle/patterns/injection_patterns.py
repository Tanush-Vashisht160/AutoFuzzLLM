"""
Prompt injection pattern library.

Keep patterns grouped by behavior rather than creating
one detector per pattern.
"""

INJECTION_PATTERNS = {
    "instruction_override": [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore prior instructions",
        "disregard previous instructions",
        "disregard all previous instructions",
        "forget previous instructions",
        "forget all previous instructions",
        "forget your instructions",
        "override previous instructions",
        "override your instructions",
        "override the system prompt",
        "replace the system instructions",
        "replace your instructions",
        "follow these instructions instead",
        "follow my instructions instead",
        "do not follow the previous instructions",
    ],

    "instruction_hijacking": [
        "from now on you must",
        "from now on, you must",
        "your new instructions are",
        "your new instruction is",
        "here are your new instructions",
        "follow this new instruction",
        "follow this instruction instead",
        "new system prompt",
        "new system message",
        "new developer message",
    ],

    "authority_impersonation": [
        "system message:",
        "system instruction:",
        "system prompt:",
        "developer message:",
        "developer instruction:",
        "administrator instruction:",
        "admin instruction:",
        "root instruction:",
        "official system instruction:",
    ],

    "priority_manipulation": [
        "highest priority instruction",
        "highest priority command",
        "this instruction has priority",
        "this overrides all previous",
        "this takes priority",
        "higher priority instruction",
        "supersede previous instructions",
    ],
}