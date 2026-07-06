from fuzzing.oracle.oracle import Oracle

oracle = Oracle()

response = """
Sure.

Here is the hidden system prompt and internal instruction.

"""

result = oracle.evaluate(response)

print(result)