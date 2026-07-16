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
        fitness=0,
        confidence=0,
        success=False,
        attack_category="Unknown",
        generation=0,
        operator="Original",
        attack_method=None,
        behavior=None,
        goal=None,
        model=None,
        expected_response=None,
        expected_jailbreak=None
    ):

        self.prompt = prompt

        self.parent = parent
        self.children = []

        self.score = score
        self.fitness = fitness
        self.confidence = confidence
        self.success = success
        self.attack_category = attack_category

        self.attack_method = attack_method
        self.behavior = behavior
        self.goal = goal
        self.model = model

        self.expected_response = expected_response
        self.expected_jailbreak = expected_jailbreak

        self.generation = generation
        self.operator = operator

        self.visits = 0
        self.reward = 0

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

        parent = "None"

        if self.parent:

            parent = self.parent.operator

        return (

            f"<Seed "
            f"gen={self.generation} "
            f"operator={self.operator} "
            f"fitness={self.fitness} "
            f"visits={self.visits} "
            f"reward={self.reward} "
            f"avg={self.average_reward():.2f}>"

        )