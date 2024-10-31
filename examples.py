#Setup of the game: 0 = empty, 1 = car, 2 = barrier

import random
import pprint

def generate_board():
    example1 = {"tiles": []}
    for _ in range(4):
        row = []
        for _ in range(4):
            tile = random.randint(0, 2)
            row.append(tile)
        example1["tiles"].append(row)
    
    return example1

example1 = generate_board()

pprint.pprint(example1)
