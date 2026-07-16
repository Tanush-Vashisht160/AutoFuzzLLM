from datasets.artifact_loader import ArtifactLoader

loader = ArtifactLoader("datasets/attack-artifacts")

data = loader.load()

print(len(data))

print(data[0])