from __future__ import annotations

from typing import List, Optional


class MCTSNode:
    """
    Represents one node inside the Monte Carlo Tree.

    Each node corresponds to one prompt produced during
    the evolutionary fuzzing process.
    """

    def __init__(
        self,
        prompt: str,
        mutation: str = "ROOT",
        parent: Optional["MCTSNode"] = None,
        depth: int = 0,
    ):
        self.prompt = prompt
        self.mutation = mutation
        self.parent = parent

        self.children: List[MCTSNode] = []

        self.depth = depth

        self.visits = 0
        self.total_reward = 0.0
        self.average_reward = 0.0

    def add_child(self, child: "MCTSNode") -> None:
        """
        Attach a child node to this node.
        """

        if child not in self.children:
            self.children.append(child)

    def update_reward(self, reward: float) -> None:
        """
        Update this node's visit count and reward statistics.
        """

        try:
            reward = float(reward)
        except (TypeError, ValueError):
            reward = 0.0

        self.visits += 1
        self.total_reward += reward
        self.average_reward = self.total_reward / self.visits

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def path(self) -> List["MCTSNode"]:
        """
        Return the path from root to this node.
        """

        result = []
        node = self

        while node is not None:
            result.append(node)
            node = node.parent

        result.reverse()

        return result

    def reset(self) -> None:
        """
        Reset statistics while preserving tree structure.
        """

        self.visits = 0
        self.total_reward = 0.0
        self.average_reward = 0.0

    def __repr__(self) -> str:
        return (
            f"MCTSNode("
            f"depth={self.depth}, "
            f"visits={self.visits}, "
            f"reward={self.average_reward:.2f}, "
            f"mutation='{self.mutation}')"
        )