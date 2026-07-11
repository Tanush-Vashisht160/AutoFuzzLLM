import math

class UCB1:

    def score(
        self,
        reward,
        visits,
        total_visits
    ):

        if visits == 0:
            return float("inf")

        return reward + math.sqrt(
            2 * math.log(total_visits) / visits
        )