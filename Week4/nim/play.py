import json

from nim import train, play

ai = train(10000)
play(ai)

# Stringify the keys for the JSON dump
knowledge = {str(key): value for key, value in ai.q.items()}

with open('knowledge.json', 'w') as f:
    json.dump(knowledge, f)

