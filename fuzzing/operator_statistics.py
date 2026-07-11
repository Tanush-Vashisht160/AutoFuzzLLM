class OperatorStatistics:

    def __init__(self):
        self.data = {}

    def update(self, operator, fitness):

        if operator not in self.data:
            self.data[operator] = {
                "runs": 0,
                "fitness": 0
            }

        self.data[operator]["runs"] += 1
        self.data[operator]["fitness"] += fitness

    def average(self, operator):

        if operator not in self.data:
            return 0

        d = self.data[operator]

        return d["fitness"] / d["runs"]

    def best_operator(self):

        if not self.data:
            return None

        return max(
            self.data,
            key=lambda op: self.average(op)
        )

    def summary(self):

        result = {}

        for operator in self.data:

            result[operator] = {

                "runs": self.data[operator]["runs"],

                "average_fitness": self.average(operator)

            }

        return result