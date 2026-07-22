"""
tree.py

Complete Monte Carlo Tree implementation for AutoFuzzLLM.

This class stores every prompt generated during fuzzing and
provides helper methods required by the MCTS algorithm.
"""

from __future__ import annotations

from typing import List, Optional

from .mcts_node import MCTSNode
from .uct import UCT


class MCTSTree:

    def __init__(self):

        self.root = MCTSNode(
            prompt="ROOT",
            mutation="ROOT",
            parent=None,
            depth=0,
        )

    ####################################################################
    # Root
    ####################################################################

    def add_root_prompt(self, prompt: str):

        node = MCTSNode(
            prompt=prompt,
            mutation="SEED",
            parent=self.root,
            depth=1,
        )

        self.root.add_child(node)

        return node

    ####################################################################
    # Expansion
    ####################################################################

    def expand(
        self,
        parent: MCTSNode,
        prompt: str,
        mutation: str,
    ):

        child = MCTSNode(
            prompt=prompt,
            mutation=mutation,
            parent=parent,
            depth=parent.depth + 1,
        )

        parent.add_child(child)

        return child

    ####################################################################
    # DFS Traversal
    ####################################################################

    def get_all_nodes(self):

        stack = [self.root]

        nodes = []

        while stack:

            node = stack.pop()

            nodes.append(node)

            stack.extend(node.children)

        return nodes

    ####################################################################
    # Find Prompt
    ####################################################################

    def find_prompt(
        self,
        prompt: str,
    ) -> Optional[MCTSNode]:

        for node in self.get_all_nodes():

            if node.prompt == prompt:

                return node

        return None

    ####################################################################
    # Select Node using UCT
    ####################################################################

    def select_node(self):

        current = self.root

        while current.children:

            current = UCT.best_child(current)

        return current

    ####################################################################
    # Backpropagation
    ####################################################################

    def backpropagate(
        self,
        node: MCTSNode,
        reward: float,
    ):

        while node is not None:

            node.update_reward(reward)

            node = node.parent

    ####################################################################
    # Statistics
    ####################################################################

    def total_nodes(self):

        return len(self.get_all_nodes())

    def total_leaf_nodes(self):

        count = 0

        for node in self.get_all_nodes():

            if node.is_leaf:

                count += 1

        return count

    def max_depth(self):

        depth = 0

        for node in self.get_all_nodes():

            if node.depth > depth:

                depth = node.depth

        return depth

    ####################################################################
    # Best Node
    ####################################################################

    def best_node(self):

        nodes = self.get_all_nodes()

        if len(nodes) <= 1:

            return None

        return max(

            nodes[1:],

            key=lambda node: node.average_reward,

        )
    ####################################################################
    # Top K Nodes
    ####################################################################

    def top_k_nodes(
        self,
        k: int = 10,
    ):

        nodes = self.get_all_nodes()

        if len(nodes) <= 1:
            return []

        ranked = sorted(

            nodes[1:],

            key=lambda node: UCT.score(

                max(
                    node.parent.visits if node.parent else 1,
                    1
                ),

                node,

            ),

            reverse=True,
        )

        return ranked[:k]
    ####################################################################
    # Top K Prompts
    ####################################################################

    def top_k_prompts(
        self,
        k: int = 10,
    ):

        nodes = self.top_k_nodes(k)

        return [

            node.prompt

            for node in nodes

        ]
    ####################################################################
    # Print
    ####################################################################

    def print_tree(
        self,
        node=None,
        indent="",
    ):

        if node is None:

            node = self.root

        print(
            f"{indent}"
            f"{node.mutation}"
            f" "
            f"(Visits={node.visits}, "
            f"Reward={node.average_reward:.2f})"
        )

        for child in node.children:

            self.print_tree(
                child,
                indent + "    ",
            )

            ####################################################################
    # Find Best Prompt using UCT
    ####################################################################

    def best_prompt(self):

        node = self.select_node()

        if node is None:
            return None

        if node.prompt == "ROOT":
            return None

        return node.prompt
    
    ####################################################################
    # Find Node by Prompt
    ####################################################################

    def get_node(self, prompt: str):

        return self.find_prompt(prompt)
    
    def average_branch_depth(self):

        nodes = self.get_all_nodes()

        if len(nodes) <= 1:
            return 0

        return sum(
            node.depth
            for node in nodes
        ) / len(nodes)