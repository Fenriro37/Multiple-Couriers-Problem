# ############################# TEST ##################################
# import minizinc
# import numpy as np
# from datetime import timedelta

# # def preprocess_dat_file(file_path):
# #     with open(file_path, 'r') as f:
# #         lines = [line.strip() for line in f.readlines()]

# #     m = int(lines[0])
# #     n = int(lines[1])
# #     l = list(map(int, lines[2].split()))
# #     s = list(map(int, lines[3].split()))
# #     D = [list(map(int, line.split())) for line in lines[4:4 + (n + 1)]]
# #     D = np.array(D)

# #     dp_upper = max([sum(sorted(row)[-2:]) for row in D])
# #     up_bound = dp_upper

# #     # Lower bound (lb)
# #     max_last_row = max(D[-1, :-1])
# #     max_last_col = max(D[:-1, -1])
# #     low_bound = max(max_last_row, max_last_col)
    
# #     return m, n, l, s, D, up_bound, low_bound

# def preprocess_dat_file(file_path):
#     with open(file_path, 'r') as f:
#         lines = [line.strip() for line in f.readlines()]

#     m = int(lines[0])
#     n = int(lines[1])
#     l = list(map(int, lines[2].split()))
#     s = list(map(int, lines[3].split()))
#     D = [list(map(int, line.split())) for line in lines[4:4 + (n + 1)]]
#     D = np.array(D)

#     dp_upper = max([sum(sorted(row)[-2:]) for row in D])
#     up_bound = dp_upper

#     last_row = D[-1, :-1]
#     last_column = D[:-1, -1]

#     value1 = last_column[np.argmax(last_row)] + max(last_row)
#     value2 = last_row[np.argmax(last_column)] + max(last_column)
#     low_bound = max(value1, value2)
    
#     return m, n, l, s, D, up_bound, low_bound
    


# m, n, l, s, D, up_bound, low_bound = preprocess_dat_file('C:/Users/sandr/Desktop/CSP_model/instances/inst02.dat')
# model = minizinc.Model('C:/Users/sandr/Desktop/CP/CP_model(without SB).mzn')

# gecode = minizinc.Solver.lookup("gecode")
# chuffed = minizinc.Solver.lookup("chuffed")

# instance = minizinc.Instance(chuffed, model)

# instance["m"] = m
# instance["n"] = n
# instance["l"] = l
# instance["s"] = s
# instance["D"] = D
# instance["up_bound"] = up_bound
# instance["low_bound"] = low_bound


# result = instance.solve(timeout=timedelta(milliseconds=300 * 1000))

# if result.status.has_solution():
#     print("Solution found:")
#     print(result.solution)
# else:
#     print("No solution found within the time limit.")


######################################## Formal ######################################
import minizinc
import numpy as np
import json
from datetime import timedelta
import os

def preprocess_dat_file(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    m = int(lines[0])
    n = int(lines[1])
    l = list(map(int, lines[2].split()))
    s = list(map(int, lines[3].split()))
    D = [list(map(int, line.split())) for line in lines[4:4 + (n + 1)]]
    D = np.array(D)

    dp_upper = max([sum(sorted(row)[-2:]) for row in D])
    up_bound = dp_upper

    # Lower bound (lb)
    max_last_row = max(D[-1, :-1])
    max_last_col = max(D[:-1, -1])
    low_bound = max(max_last_row, max_last_col)
    
    return m, n, l, s, D, up_bound, low_bound

# Paths
instances_dir = 'C:/Users/sandr/Desktop/CSP_model/instances/'
results_dir = 'C:/Users/sandr/Desktop/res/CP/'

os.makedirs(results_dir, exist_ok=True)

model_with_symmetry = minizinc.Model('C:/Users/sandr/Desktop/CP/CP_model(with SB).mzn')
model_without_symmetry = minizinc.Model('C:/Users/sandr/Desktop/CP/CP_model(without SB).mzn')

gecode = minizinc.Solver.lookup("gecode")
chuffed = minizinc.Solver.lookup("chuffed")


def solve_instance(instance, solver_name):
    result = instance.solve(timeout=timedelta(seconds=300))
    
    time_taken = int(result.statistics.get('time', timedelta(seconds=300)).total_seconds())

    sol = [[] for _ in range(m)]

    if result.solution is not None:
        route = result["route"]
        for k in range(1, m + 1):  
            current_node = n + 1 
            while True:
                next_node = route[k - 1][current_node - 1]  
                if next_node == n + 1:  
                    break
                sol[k - 1].append(next_node)  
                current_node = next_node 

    return {
        "time": time_taken,  
        "optimal": result.status == minizinc.result.Status.SATISFIED,
        "obj": result["maximum"] if result.solution is not None else None,
        "sol": sol  
    }


# Process each instance from instance01 to instance21
for i in range(1, 22):
    instance_file = f'inst{i:02d}.dat'
    instance_path = os.path.join(instances_dir, instance_file)
    
    m, n, l, s, D, up_bound, low_bound = preprocess_dat_file(instance_path)
    
    output = {}
    
    for model_name, model in [("with_symmetry", model_with_symmetry), ("without_symmetry", model_without_symmetry)]:
        instance_gecode = minizinc.Instance(gecode, model)
        instance_chuffed = minizinc.Instance(chuffed, model)
    
        for instance in [instance_gecode, instance_chuffed]:
            instance["m"] = m
            instance["n"] = n
            instance["l"] = l
            instance["s"] = s
            instance["D"] = D
            instance["up_bound"] = up_bound
            instance["low_bound"] = low_bound
        
        output[f"gecode_{model_name}"] = solve_instance(instance_gecode, "gecode")
        
        output[f"chuffed_{model_name}"] = solve_instance(instance_chuffed, "chuffed")
    
    # Save the output to a JSON file
    json_filename = f'{i:02d}.json'
    json_path = os.path.join(results_dir, json_filename)
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=4)
    
    print(f"Results for {instance_file} saved to {json_filename}.")
