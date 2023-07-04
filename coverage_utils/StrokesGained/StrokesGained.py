import os
import pandas as pd

# For the purposes of data entry from the UDisc scorecards we format hole entries like this
hole_entry = {"name": 'Kyle Herbertson', "hole": 1, "driving": 'C1X/C2/Parked/Fairway/OffFairway/OB', "C1X": 1, "C2": 0, "scramble": True/False, "penalty": 0, "made_distance": 2}


# E(X) from Tee = hole scoring average
# E(X) from Parked = 1
# E(X) from Basket = 0

# E(X) from C1X
# E(X) from C2
# E(X) from Recovery Positions (has been in C2 or better already)

enums = {'R': 0, 'C2': 1, 'C1X': 2, 'P': 3, 'B':4}

# Solve the Equations