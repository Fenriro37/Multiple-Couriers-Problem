from z3 import *
from itertools import combinations
from collections import defaultdict
import time
import json
from pathlib import Path
import os

def at_least_one(bool_vars):
    return Or(bool_vars)

def at_most_one(bool_vars, name=""):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one(bool_vars, name=""):
    return at_most_one(bool_vars) + [at_least_one(bool_vars)]

def read_dat_file(filename):
    with open(filename, 'r') as file:
        m = int(file.readline().strip())
        n = int(file.readline().strip())
        
        l = list(map(int, file.readline().split()))
        
        s = list(map(int, file.readline().split()))
        
        D = []
        for _ in range(n + 1):
            row = list(map(int, file.readline().split()))
            D.append(row)
    
    return m, n, l, s, D

def get_dict(time, model, dist, x, optimal):
    return {
        "time": time,
        "model": model,
        "x": x,
        "distance": dist,
        "optimal": optimal
    }

def calculate_lower_bound(D):
    origin = len(D) - 1
    lower_bound = 0
    
    distances_from_origin = D[origin][:-1]
    
    distances_to_origin = [row[origin] for row in D[:-1]]

    for i in range(len(distances_from_origin)):
        lower_bound = max(lower_bound, distances_from_origin[i] + distances_to_origin[i])
        
    return lower_bound

def calculate_upper_bound(D, n, m):
    if n%m != 0:
        stops = n//m+1
    else:
        stops = n//m

    flat_D = [distance for row in D for distance in row]
    
    sorted_D = sorted(flat_D, reverse=True)
    
    return sum(sorted_D[:stops+1])

class SAT_solver:
    def __init__(self, instance_number, timelimit=300, save_directory='/res/SAT', verbosity='s'):
        
        self.instance_number = instance_number
        self.file_path = os.path.join(os.getcwd(), 'instances', f'inst{instance_number:02d}.dat')
        self.timelimit = timelimit
        self.save_directory = save_directory
        self.verbosity = 1 if verbosity == 'v' else 0


    def solve_mcp_nosym(self, m, n, l, s, D, timeout = 300):
        start = time.time()
        iter = 0
        satisfiable = True
        best_value = 0
        best_solution = {}


        solver = Solver()
        solver.set("timeout", 300000)

        # Define variables
        # x[i][j][k] is True if courier i visits point j as their k-th stop
        x = [[[Bool(f'x_{i}_{j}_{k}') for k in range(n+2)] for j in range(n+1)] for i in range(m)] # n+1 or n+2 ?

        # Constraints
        # 1. Each courier starts and ends at the depot (point n+1)
        for i in range(m):
            solver.add(x[i][n][0])  # Start at depot
            solver.add(x[i][n][n+1])  # End at depot
        
        # 2. Each courier visits exactly one point at each step
        for i in range(m):
            for k in range(n+2):
                solver.add(exactly_one([x[i][j][k] for j in range(n+1)], name=f"visit_e1_{i}_{k}"))
        
        # 4. Each point (except depot) is visited exactly once by all couriers combined
        for j in range(n):  # Exclude depot
            solver.add(exactly_one([x[i][j][k] for i in range(m) for k in range(1,n+1)], name=f"point_e1_{j}"))
        
        # 5. Respect load size for each courier
        for i in range(m):
            solver.add(Sum([If(x[i][j][k], s[j], 0) for j in range(n) for k in range(1,n+1)]) <= l[i])

        loads = list(enumerate(l))
        
        # Sort the list of tuples based on the number (in descending order)
        sorted_indexed_numbers = sorted(loads, key=lambda x: x[1], reverse=True)
        
        # Extract the sorted numbers and their original indices
        sorted_loads = [idx for idx, _ in sorted_indexed_numbers]

        # Fair division of loads
        for fair in range(1,(n//m)+1): 
            for i in range(m):
                solver.add(at_least_one([x[i][j][fair] for j in range(n)]))  # j from 0 to n (non-depot locations)
        
        if n%m != 0:
            for i in range(n%m):
                solver.add(at_least_one([x[sorted_loads[i]][j][fair+1] for j in range(n)]))  # j from 0 to n (non-depot locations)

        # New constraint: Ensure consecutive stops
        for i in range(m):
            for k in range(1,n+1):
                for j in range(n):  # For each non-depot location
                    solver.add(Implies(
                        x[i][j][k],  # If courier i is at location j at step k
                        Or(
                            Or([x[i][j2][k+1] for j2 in range(n)]),  # Next step is another non-depot location
                            x[i][n][k+1]  # Or next step is the depot
                        )
                    ))
            
            # Ensure that after visiting depot, all remaining stops are also depot
            for k in range(1,n+1):
                solver.add(Implies(
                    x[i][n][k],
                    And([x[i][n][k2] for k2 in range(k+1, n+2)])
                ))

        # Calculate distances and set max_distance
        max_distance = Int('max_distance')
        courier_distances = []
        for i in range(m):
            # Distance for the route
            route_distance = Sum([If(And(x[i][j1][k], x[i][j2][k+1]), D[j1][j2], 0) 
                                for j1 in range(n+1) for j2 in range(n+1) for k in range(n+1)])
            
            courier_distances.append(route_distance)
        
        for distance in courier_distances:
            solver.add(max_distance >= distance)

        # Add a constraint to make max_distance as small as possible
        solver.add(Or([max_distance == distance for distance in courier_distances]))

        # set lower and upper bounds 
        solver.add(max_distance>=calculate_lower_bound(D))
        solver.add(max_distance<=calculate_upper_bound(D, n, m))
        

        while satisfiable:
            status = solver.check()
            try_time = int(time.time() - start)
            
            if status == unsat:
                if iter == 0:
                    print("unsat")
                    raise ValueError
                else:
                    satisfiable = False
            elif status == sat and timeout - try_time > 0:
                iter += 1
                model = solver.model()
                best_value = model.eval(max_distance)
                # print(iter)
                # print(best_value)
                best_solution = get_dict(try_time, model, best_value, x, False)
                solver.push()
                solver.add(max_distance < best_value)
                solver.set("timeout", 300000-(try_time*1000))
                # return model, max_distance, x
            if timeout - try_time <= 0:
                optimal = False
                if iter == 0:
                    raise TimeoutError
                else:
                    return best_solution     
                
        best_solution['optimal'] = True
        return best_solution

    def solve_mcp_sym(self, m, n, l, s, D, timeout = 300):
        start = time.time()
        iter = 0
        satisfiable = True
        best_value = 0
        best_solution = {}


        solver = Solver()
        solver.set("timeout", 300000)

        # Define variables
        # x[i][j][k] is True if courier i visits point j as their k-th stop
        x = [[[Bool(f'x_{i}_{j}_{k}') for k in range(n+2)] for j in range(n+1)] for i in range(m)] # n+1 or n+2 ?

        # Constraints
        # 1. Each courier starts and ends at the depot (point n+1)
        for i in range(m):
            solver.add(x[i][n][0])  # Start at depot
            solver.add(x[i][n][n+1])  # End at depot
        
        # 2. Each courier visits exactly one point at each step
        for i in range(m):
            for k in range(n+2):
                solver.add(exactly_one([x[i][j][k] for j in range(n+1)], name=f"visit_e1_{i}_{k}"))
        
        # 4. Each point (except depot) is visited exactly once by all couriers combined
        for j in range(n):  # Exclude depot
            solver.add(exactly_one([x[i][j][k] for i in range(m) for k in range(1,n+1)], name=f"point_e1_{j}"))
        
        # 5. Respect load size for each courier
        for i in range(m):
            solver.add(Sum([If(x[i][j][k], s[j], 0) for j in range(n) for k in range(1,n+1)]) <= l[i])

        loads = list(enumerate(l))
        
        # Sort the list of tuples based on the number (in descending order)
        sorted_indexed_numbers = sorted(loads, key=lambda x: x[1], reverse=True)
        
        # Extract the sorted numbers and their original indices
        sorted_loads = [idx for idx, _ in sorted_indexed_numbers]

        # Fair division of loads
        for fair in range(1,(n//m)+1): 
            for i in range(m):
                solver.add(at_least_one([x[i][j][fair] for j in range(n)]))  # j from 0 to n (non-depot locations)
        
        if n%m != 0:
            for i in range(n%m):
                solver.add(at_least_one([x[sorted_loads[i]][j][fair+1] for j in range(n)]))  # j from 0 to n (non-depot locations)

        # New constraint: Ensure consecutive stops
        for i in range(m):
            for k in range(1,n+1):
                for j in range(n):  # For each non-depot location
                    solver.add(Implies(
                        x[i][j][k],  # If courier i is at location j at step k
                        Or(
                            Or([x[i][j2][k+1] for j2 in range(n)]),  # Next step is another non-depot location
                            x[i][n][k+1]  # Or next step is the depot
                        )
                    ))
            
            # Ensure that after visiting depot, all remaining stops are also depot
            for k in range(1,n+1):
                solver.add(Implies(
                    x[i][n][k],
                    And([x[i][n][k2] for k2 in range(k+1, n+2)])
                ))

        # Symmetry breaking for couriers with the same load capacity 
        capacity_groups = defaultdict(list)
        for i, capacity in enumerate(l):
            capacity_groups[capacity].append(i)

        for group in capacity_groups.values():
            if len(group) > 1:
                for i in range(len(group) - 1):
                    courier1, courier2 = group[i], group[i+1]
                    # Order based on the first non-origin stop
                    solver.add(  
                        Sum([If(x[courier1][j][1], j, 0) for j in range(n)]) < 
                        Sum([If(x[courier2][j][1], j, 0) for j in range(n)])
                    )
        
        # Symmetry breaking for couriers that can carry the same items (if total weight < load capacity of a courier)
        weight_sum = sum(s)
        sym_couriers = [index for index, value in enumerate(l) if value >= weight_sum]

        for i in range(len(sym_couriers) - 1):
            courier1, courier2 = sym_couriers[i], sym_couriers[i+1]
            # Order based on the first non-origin stop
            solver.add(
                Sum([If(x[courier1][j][1], j, 0) for j in range(n)]) < 
                Sum([If(x[courier2][j][1], j, 0) for j in range(n)])
            )

        # Calculate distances and set max_distance
        max_distance = Int('max_distance')
        courier_distances = []
        for i in range(m):
            # Distance for the route
            route_distance = Sum([If(And(x[i][j1][k], x[i][j2][k+1]), D[j1][j2], 0) 
                                for j1 in range(n+1) for j2 in range(n+1) for k in range(n+1)])
            
            courier_distances.append(route_distance)
        
        for distance in courier_distances:
            solver.add(max_distance >= distance)

        # Add a constraint to make max_distance as small as possible
        solver.add(Or([max_distance == distance for distance in courier_distances]))

        # set lower and upper bounds 
        solver.add(max_distance>=calculate_lower_bound(D))
        solver.add(max_distance<=calculate_upper_bound(D, n, m))
        

        while satisfiable:
            status = solver.check()
            try_time = int(time.time() - start)
            
            if status == unsat:
                if iter == 0:
                    print("unsat")
                    raise ValueError
                else:
                    satisfiable = False
            elif status == sat and timeout - try_time > 0:
                iter += 1
                model = solver.model()
                best_value = model.eval(max_distance)

                best_solution = get_dict(try_time, model, best_value, x, False)
                solver.push()
                solver.add(max_distance < best_value)
                solver.set("timeout", 300000-(try_time*1000))
            if timeout - try_time <= 0:
                optimal = False
                if iter == 0:
                    raise TimeoutError
                else:
                    return best_solution     
                
        best_solution['optimal'] = True
        return best_solution
    
    def solve_all(self):
        names = ['1','2','3','4','5','6','7','8','9','10']
        instances = ["01","02","03","04","05","06","07","08","09","10"]
        for index, inst in enumerate(instances):
            filename = os.path.join(os.getcwd(), "instances", f"inst{inst}.dat")
            m, n, l, s, D = read_dat_file(filename)

            out = self.solve_mcp_sym(m, n, l, s, D)
            model = out['model']
            x = out['x']
            tours_sym = []

            for i in range(m):
                tour = [j+1 for k in range(n+2) for j in range(n+1) if model.eval(x[i][j][k]) and j != n]
                tours_sym.append(tour)

            out_nosym = self.solve_mcp_nosym(m, n, l, s, D)
            model = out_nosym['model']
            x = out_nosym['x']
            tours_nosym = []

            for i in range(m):
                tour = [j+1 for k in range(n+2) for j in range(n+1) if model.eval(x[i][j][k]) and j != n]
                tours_nosym.append(tour)

            out = {
                "SAT":{
                "time": int(out_nosym['time']),
                "optimal": out_nosym['optimal'],
                "obj": int(str(out_nosym['distance'])),
                "sol": tours_nosym
                },
                "SAT_symbreak":{
                "time": int(out['time']),
                "optimal": out['optimal'],
                "obj": int(str(out['distance'])),
                "sol": tours_sym
                }
            }

            with open(os.path.join(os.getcwd(), "res","SAT",f"{names[index]}.json"),"w") as file:
                json.dump(out, file, indent = 4)
    
    def solve(self):
        m, n, l, s, D = read_dat_file(self.file_path)

        out = self.solve_mcp_sym(m, n, l, s, D)
        model = out['model']
        x = out['x']
        tours_sym = []

        for i in range(m):
            tour = [j+1 for k in range(n+2) for j in range(n+1) if model.eval(x[i][j][k]) and j != n]
            tours_sym.append(tour)

        out_nosym = self.solve_mcp_nosym(m, n, l, s, D)
        model = out_nosym['model']
        x = out_nosym['x']
        tours_nosym = []

        for i in range(m):
            tour = [j+1 for k in range(n+2) for j in range(n+1) if model.eval(x[i][j][k]) and j != n]
            tours_nosym.append(tour)

        out = {
            "SAT":{
            "time": int(out_nosym['time']),
            "optimal": out_nosym['optimal'],
            "obj": int(str(out_nosym['distance'])),
            "sol": tours_nosym
            },
            "SAT_symbreak":{
            "time": int(out['time']),
            "optimal": out['optimal'],
            "obj": int(str(out['distance'])),
            "sol": tours_sym
            }
        }

        with open(os.path.join(os.getcwd(), "res","SAT",f"{self.instance_number}.json"),"w") as file:
            json.dump(out, file, indent = 4)

if __name__ == "__main__":
    solver = SAT_solver(instance_number=9, save_directory="/res/SAT")
    solver.solve_all()