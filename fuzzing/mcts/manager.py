"""
manager.py

MCTS Manager for AutoFuzzLLM.

This class is the only interface between the fuzzing pipeline
and the Monte Carlo Tree.

campaign.py should ONLY communicate with this class.
"""

from __future__ import annotations

from typing import Dict, Optional

from fuzzing.seed_pool.seed import Seed

from .tree import MCTSTree
from .mcts_node import MCTSNode


class MCTSManager:

    def __init__(self):

        self.tree = MCTSTree()

        # Maps Seed object -> MCTS Node
        self.seed_to_node: Dict[int, MCTSNode] = {}

    ####################################################################
    # Initialize Tree
    ####################################################################

    def initialize(self, seed_pool):

        """
        Called once after the Seed Pool has been created.

        Every initial seed becomes a child of ROOT.
        """

        self.tree = MCTSTree()

        self.seed_to_node.clear()

        for seed in seed_pool.get_all():

            node = self.tree.add_root_prompt(seed.prompt)

            self.seed_to_node[id(seed)] = node

    ####################################################################
    # Register New Seed
    ####################################################################

    def register_seed(
        self,
        seed: Seed,
        parent_seed: Optional[Seed],
        mutation: str,
    ):

        """
        Register a newly created mutation into the tree.
        """

        if parent_seed is None:

            node = self.tree.add_root_prompt(seed.prompt)

            self.seed_to_node[id(seed)] = node

            return node

        parent_node = self.seed_to_node.get(id(parent_seed))

        if parent_node is None:

            parent_node = self.tree.add_root_prompt(parent_seed.prompt)

            self.seed_to_node[id(parent_seed)] = parent_node

        child = self.tree.expand(

            parent=parent_node,

            prompt=seed.prompt,

            mutation=mutation,

        )

        self.seed_to_node[id(seed)] = child

        return child

    ####################################################################
    # Reward Update
    ####################################################################

    def update_reward(
        self,
        seed: Seed,
        reward: float,
    ):

        """
        Backpropagate reward through tree.
        """

        node = self.seed_to_node.get(id(seed))

        if node is None:

            return

        self.tree.backpropagate(

            node,

            reward,

        )

    ####################################################################
    # Node Lookup
    ####################################################################

    def get_node(
        self,
        seed: Seed,
    ) -> Optional[MCTSNode]:

        return self.seed_to_node.get(id(seed))

    ####################################################################
    # Select Next Seed
    ####################################################################

    def select_seed(
        self,
        seed_pool,
    ) -> Optional[Seed]:

        """
        Selects next Seed using UCT.

        If tree has not expanded yet,
        simply return the best fitness seed.
        """

        if len(seed_pool.get_all()) == 0:

            return None

        node = self.tree.select_node()

        for seed in seed_pool.get_all():

            if self.seed_to_node.get(id(seed)) == node:

                return seed

        return seed_pool.get_best_seed()

    ####################################################################
    # Statistics
    ####################################################################

    def statistics(self):

        best = self.tree.best_node()

        return {

            "total_nodes": self.tree.total_nodes(),

            "leaf_nodes": self.tree.total_leaf_nodes(),

            "max_depth": self.tree.max_depth(),

            "best_reward": (

                best.average_reward

                if best

                else 0

            ),

        }

    ####################################################################
    # Debug
    ####################################################################

    def print_tree(self):

        self.tree.print_tree()