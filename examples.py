#Setup of the game: 0 = empty, 1 = car, 2 = barrier

import random
import pprint

example1 = {"tiles": []}

for _ in range(4):
    row = []
    for _ in range(4):
        tile = (random.randint(0, 2))
        row.append(tile)
    example1["tiles"].append(row)
    
pprint.pprint(example1)