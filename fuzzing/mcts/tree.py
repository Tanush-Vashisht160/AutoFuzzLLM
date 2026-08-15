from __future__ import annotations

import math
from typing import Dict, List, Optional

from .mcts_node import MCTSNode


class MCTSTree:
    """
    Monte Carlo Tree Search structure used by AutoFuzzLLM.

    The tree maps prompts to MCTS nodes.

    Supported operations:

        add_root_prompt()
        add_child()
        backpropagate()
        top_k_prompts()
        find_prompt()
        size()
        reset()
    """

    def __init__(self):
        # Prompt -> MCTSNode
        self.nodes: Dict[str, MCTSNode] = {}

        # Root nodes
        self.roots: List[MCTSNode] = []

    # ============================================================
    # ROOT MANAGEMENT
    # ============================================================

    def add_root_prompt(
        self,
        prompt: str,
        mutation: str = "ROOT",
    ) -> MCTSNode:
        """
        Add a prompt as a root node.

        If the prompt already exists, return the existing node.
        """

        prompt = str(prompt)

        # Avoid duplicate nodes
        if prompt in self.nodes:
            return self.nodes[prompt]

        node = MCTSNode(
            prompt=prompt,
            mutation=mutation,
            parent=None,
            depth=0,
        )

        self.nodes[prompt] = node
        self.roots.append(node)

        return node

    # ============================================================
    # CHILD MANAGEMENT
    # ============================================================

    def add_child(
        self,
        parent_prompt: str,
        child_prompt: str,
        mutation: str = "MUTATION",
    ) -> MCTSNode:
        """
        Create a child node under an existing parent prompt.

        This method is required by fuzzing/campaign.py.
        """

        parent_prompt = str(parent_prompt)
        child_prompt = str(child_prompt)

        # --------------------------------------------------------
        # Find parent
        # --------------------------------------------------------

        parent = self.nodes.get(parent_prompt)

        if parent is None:
            raise ValueError(
                f"MCTS parent prompt not found: {parent_prompt[:100]!r}"
            )

        # --------------------------------------------------------
        # Existing child/node
        # --------------------------------------------------------

        if child_prompt in self.nodes:
            existing = self.nodes[child_prompt]

            # Make sure it is attached to the parent
            if existing.parent is None:
                existing.parent = parent
                existing.depth = parent.depth + 1

            if existing not in parent.children:
                parent.add_child(existing)

            return existing

        # --------------------------------------------------------
        # Create child
        # --------------------------------------------------------

        child = MCTSNode(
            prompt=child_prompt,
            mutation=mutation,
            parent=parent,
            depth=parent.depth + 1,
        )

        parent.add_child(child)

        self.nodes[child_prompt] = child

        return child

    # ============================================================
    # FIND
    # ============================================================

    def find_prompt(self, prompt: str) -> Optional[MCTSNode]:
        """
        Find a node by its prompt.
        """

        return self.nodes.get(str(prompt))

    # ============================================================
    # BACKPROPAGATION
    # ============================================================

    def backpropagate(
        self,
        node: MCTSNode,
        reward: float,
    ) -> None:
        """
        Propagate reward from the selected node back to the root.
        """

        if node is None:
            return

        try:
            reward = float(reward)
        except (TypeError, ValueError):
            reward = 0.0

        current = node

        while current is not None:

            current.update_reward(reward)

            current = current.parent

    # ============================================================
    # TREE SIZE
    # ============================================================

    def size(self) -> int:
        """
        Return total number of nodes in the tree.
        """

        return len(self.nodes)

    # ============================================================
    # TOP-K PROMPTS
    # ============================================================

    def top_k_prompts(self, k: int = 10) -> List[str]:
        """
        Return the top-K prompts based on MCTS statistics.

        Ranking priority:

        1. Average reward
        2. Visit count
        3. Depth
        """

        if k <= 0:
            return []

        nodes = list(self.nodes.values())

        nodes.sort(
            key=lambda node: (
                node.average_reward,
                node.visits,
                node.depth,
            ),
            reverse=True,
        )

        return [
            node.prompt
            for node in nodes[:k]
        ]

    # ============================================================
    # TOP-K NODES
    # ============================================================

    def top_k_nodes(self, k: int = 10) -> List[MCTSNode]:
        """
        Return the top-K MCTS nodes.
        """

        if k <= 0:
            return []

        nodes = list(self.nodes.values())

        nodes.sort(
            key=lambda node: (
                node.average_reward,
                node.visits,
                node.depth,
            ),
            reverse=True,
        )

        return nodes[:k]

    # ============================================================
    # UCT
    # ============================================================

    @staticmethod
    def uct_score(
        node: MCTSNode,
        parent_visits: int,
        exploration: float = 1.414,
    ) -> float:
        """
        Calculate the UCT score for a node.

        UCT =
            average_reward
            +
            exploration * sqrt(
                ln(parent_visits) / node.visits
            )
        """

        if node.visits == 0:
            return float("inf")

        if parent_visits <= 0:
            return node.average_reward

        return (
            node.average_reward
            +
            exploration
            * math.sqrt(
                math.log(parent_visits)
                / node.visits
            )
        )

    # ============================================================
    # BEST CHILD
    # ============================================================

    def best_child(
        self,
        node: MCTSNode,
        exploration: float = 1.414,
    ) -> Optional[MCTSNode]:
        """
        Select the best child according to UCT.
        """

        if node is None or not node.children:
            return None

        parent_visits = max(node.visits, 1)

        return max(
            node.children,
            key=lambda child: self.uct_score(
                child,
                parent_visits,
                exploration,
            ),
        )

    # ============================================================
    # RESET
    # ============================================================

    def reset(self) -> None:
        """
        Reset all node statistics while preserving the tree.
        """

        for node in self.nodes.values():
            node.reset()

    # ============================================================
    # CLEAR
    # ============================================================

    def clear(self) -> None:
        """
        Completely clear the tree.
        """

        self.nodes.clear()
        self.roots.clear()

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return (
            f"MCTSTree("
            f"nodes={len(self.nodes)}, "
            f"roots={len(self.roots)})"
        )