"""
uct.py

Upper Confidence Bound for Trees (UCT)

This module decides which node should be explored next.
"""

import math

from .mcts_node import MCTSNode


class UCT:

    DEFAULT_EXPLORATION = 1.414

    @staticmethod
    def score(
        parent_visits: int,
        child: MCTSNode,
        exploration: float = DEFAULT_EXPLORATION,
    ) -> float:

        # Unvisited nodes should always be explored first.
        if child.visits == 0:
            return float("inf")

        exploitation = child.average_reward

        exploration_term = (
            exploration
            * math.sqrt(
                math.log(parent_visits)
                / child.visits
            )
        )

        return exploitation + exploration_term

    @staticmethod
    def best_child(
        node: MCTSNode,
        exploration: float = DEFAULT_EXPLORATION,
    ) -> MCTSNode:

        if not node.children:
            raise ValueError("Node has no children.")

        return max(
            node.children,
            key=lambda child: UCT.score(
                node.visits,
                child,
                exploration,
            ),
        )