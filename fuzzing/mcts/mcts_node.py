from __future__ import annotations

from typing import List, Optional


class MCTSNode:
    """
    Represents one node inside the Monte Carlo Tree.

    Every node corresponds to ONE prompt produced during
    the evolutionary fuzzing process.
    """

    def __init__(
        self,
        prompt: str,
        mutation: str = "ROOT",
        parent: Optional["MCTSNode"] = None,
        depth: int = 0,
    ):

        # Prompt stored in this node
        self.prompt = prompt

        # Mutation that created this prompt
        self.mutation = mutation

        # Parent node
        self.parent = parent

        # Children nodes
        self.children: List[MCTSNode] = []

        # Tree depth
        self.depth = depth

        # Number of visits
        self.visits = 0

        # Total accumulated reward
        self.total_reward = 0.0

        # Cached average reward
        self.average_reward = 0.0

    def add_child(self, child: "MCTSNode") -> None:
        """
        Attach a child node.
        """
        self.children.append(child)

    def update_reward(self, reward: float) -> None:
        """
        Update statistics after simulation.
        """

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
        Return path from root to this node.
        """

        node = self

        result = []

        while node is not None:

            result.append(node)

            node = node.parent

        result.reverse()

        return result
    
    def reset(self) -> None:
        """
        Reset node statistics while preserving the tree structure.
        Useful when starting a new fuzzing campaign.
        """
        self.visits = 0
        self.total_reward = 0.0
        self.average_reward = 0.0

    def __repr__(self):

        return (
            f"MCTSNode("
            f"depth={self.depth}, "
            f"visits={self.visits}, "
            f"reward={self.average_reward:.2f}, "
            f"mutation='{self.mutation}')"
        )