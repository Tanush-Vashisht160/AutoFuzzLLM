class Seed:
    """
    Represents one prompt in the mutation tree.

    Every successful mutation becomes a new Seed.
    """

    def __init__(
        self,
        prompt,
        parent=None,
        score=0,
        generation=0,
        operator="Original"
    ):

        self.prompt = prompt

        # Parent seed
        self.parent = parent

        # Children produced from this seed
        self.children = []

        # Oracle score
        self.score = score

        # Tree depth
        self.generation = generation

        # Mutation operator
        self.operator = operator

        # ---------- For future MCTS ----------
        self.visits = 0
        self.reward = 0

        # Automatically register with parent
        if parent is not None:
            parent.children.append(self)

    def add_child(self, child):

        self.children.append(child)

    def update_reward(self, reward):

        self.reward += reward

    def visit(self):

        self.visits += 1

    def average_reward(self):

        if self.visits == 0:
            return 0

        return self.reward / self.visits

    def __repr__(self):

        return (
            f"<Seed "
            f"gen={self.generation} "
            f"score={self.score} "
            f"children={len(self.children)} "
            f"visits={self.visits}>"
        )