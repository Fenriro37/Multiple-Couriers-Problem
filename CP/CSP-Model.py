import minizinc
import numpy as np
from datetime import timedelta


# def preprocess_dat_file(file_path):
#     with open(file_path, 'r') as f:
#         lines = [line.strip() for line in f.readlines()]

#     m = int(lines[0])
#     n = int(lines[1])
#     l = list(map(int, lines[2].split()))
#     s = list(map(int, lines[3].split()))
#     D = [list(map(int, line.split())) for line in lines[4:4 + (n + 1)]]
#     D = np.array(D)

#     return m, n, l, s, D

def preprocess_dat_file(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    courier = int(lines[0])
    items = int(lines[1])
    courier_size = list(map(int, lines[2].split()))
    item_size = list(map(int, lines[3].split()))
    distances = [list(map(int, line.split())) for line in lines[4:4 + (items + 1)]]
    distances = np.array(distances)

    dp_upper = max([sum(sorted(row)[-2:]) for row in distances])
    up_bound = dp_upper

    # Lower bound (lb)
    max_last_row = max(distances[-1, :-1])
    max_last_col = max(distances[:-1, -1])
    low_bound = max(max_last_row, max_last_col)

    # Lower bound on distance
    d_low_bound = 0 
    
    return courier, items, courier_size, item_size, distances, up_bound, low_bound, d_low_bound
    


courier, items, courier_size, item_size, distances, up_bound, low_bound, d_low_bound = preprocess_dat_file('C:/Users/sandr/Desktop/CSP_model/instances/inst11.dat')
model = minizinc.Model('C:/Users/sandr/Desktop/CSP_model/CSP-Model.mzn')

gecode = minizinc.Solver.lookup("gecode")
chuffed = minizinc.Solver.lookup("chuffed")
org_chuffed = minizinc.Solver.lookup("org.chuffed.chuffed")

instance = minizinc.Instance(chuffed, model)

# instance["m"] = m
# instance["n"] = n
# instance["l"] = l
# instance["s"] = s
# instance["D"] = D

instance["courier"] = courier
instance["items"] = items
instance["courier_size"] = courier_size
instance["item_size"] = item_size
instance["distances"] = distances
instance["up_bound"] = up_bound
instance["low_bound"] = low_bound
instance["d_low_bound"] = d_low_bound


result = instance.solve(timeout=timedelta(milliseconds=300 * 1000))

if result.status.has_solution():
    print("Solution found:")
    print(result.solution)
else:
    print("No solution found within the time limit.")



