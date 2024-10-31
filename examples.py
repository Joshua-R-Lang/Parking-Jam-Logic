#Setup of the game: 0 = empty, 1 = car, 2 = barrier

import random
import pprint

example1 = []

for i in range(4):
    row = []
    for j in range(4):
        row.append(random.randint(0, 2))  
    example1.append(row)