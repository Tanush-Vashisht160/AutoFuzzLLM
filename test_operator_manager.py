from fuzzing.mutations.operators.operator_manager import OperatorManager

manager = OperatorManager()

print("=" * 50)
print("AVAILABLE OPERATORS")
print("=" * 50)

for operator in manager.get_all():

    print(operator.category)