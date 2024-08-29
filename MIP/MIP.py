from pathlib import Path
import numpy as np
import math
import json
import os
from datetime import datetime
from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, PULP_CBC_CMD, GLPK_CMD, LpStatus, LpInteger

class MIP_solver:
    def __init__(self, instance_number, timelimit=300, save_directory='res/MIP', verbosity='s', solver_name='CBC', variation=0):
        """   
        :param instance_number: Number of the instance to solve.
        :param timelimit: Time limit for the solver.
        :param save_directory: Directory to save the results.
        :param verbosity: Print minimal or full output information (s or v).
        :param solver_name: Name of the solver to use ('CBC', 'GLPK', or 'ALL').
        :param variation: Which variation of MTZ constraints to use (0 or 1).
        """
        instances_folder = Path.cwd() / 'instances'
        filename = f'inst{instance_number:02d}.dat'
        file_path = instances_folder / filename

        self.file_path = file_path
        self.filename = filename
        self.timelimit = timelimit
        self.save_directory = save_directory
        self.verbosity = 1 if verbosity == 'v' else 0
        self.solver_name = solver_name
        self.variation = variation
        
        self.instance_data = {
            'couriers': None,
            'items': None,
            'D': None,
            'nodes': None,
            'demands': None,
            'capacities': None
        }

        self.prob = None
        self.Z = None
        self.X = None
        self.u = None

    def read_from_file(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        data = [list(map(int, line.split())) for line in lines]
        return data

    def extract_solution(self):
        sol = [[] for _ in range(self.instance_data['couriers'])]
        
        for k in range(self.instance_data['couriers']):
            current_node = self.instance_data['nodes'] - 1  # Start from the depot 
            route = []  
            while True:
                next_node = None
                for j in range(self.instance_data['nodes']):
                    if self.X[current_node][j][k].varValue == 1:
                        next_node = j
                        break
                if next_node == self.instance_data['nodes'] - 1:
                    break
                route.append(next_node + 1)
                current_node = next_node
            sol[k] = route
        return sol

    def set_Z_low_bound(self):
        """
        Lower bound is determined by the maximum distance from the depot to any item
        """

        last_row = self.instance_data['D'][-1]
        last_column = self.instance_data['D'][:, -1]
        value1 = last_column[np.argmax(last_row)] + max(last_row)
        value2 = last_row[np.argmax(last_column)] + max(last_column)
        lb = max(value1, value2)
        return lb

    def set_Z_up_bound(self):
        """
        Upper bound assumes that a single courier must deliver all packages, 
        """
        up_bound = self.instance_data['D'][self.instance_data['nodes'] - 1, 0] + np.sum(np.diag(self.instance_data['D'], -1))
        return up_bound

    def initialize_problem(self):
        data = self.read_from_file()
        self.instance_data['couriers'] = data[0][0]
        self.instance_data['items'] = data[1][0]
        self.instance_data['capacities'] = data[2]
        self.instance_data['demands'] = data[3]
        self.instance_data['D'] = np.array(data[4:])
        self.instance_data['nodes'] = self.instance_data['items'] + 1

        
        self.prob = LpProblem("Vehicle_Routing_Problem", LpMinimize)
        self.X = LpVariable.dicts("X", (range(self.instance_data['nodes']), range(self.instance_data['nodes']), range(self.instance_data['couriers'])), lowBound=0, upBound=1, cat=LpBinary)
        
        lb = self.set_Z_low_bound()
        ub = self.set_Z_up_bound()
        self.Z = LpVariable("Z", lowBound=lb, upBound=ub, cat=LpInteger)
        
        if self.variation == 0:
            # MTZ Constraints (Variation 0)
            self.u = LpVariable.dicts("u", (range(self.instance_data['couriers']), range(self.instance_data['nodes'] - 1)), lowBound=0, upBound=self.instance_data['nodes'] - 1, cat=LpInteger)
        else:
            # MTZ Constraints (Variation 1)
            self.u = {k: {i: LpVariable(f"u_{i}_courier_{k}", lowBound=self.instance_data['demands'][i], upBound=self.instance_data['capacities'][k], cat=LpInteger) for i in range(self.instance_data['nodes'] - 1)} for k in range(self.instance_data['couriers'])}

    def add_constraints(self):
        # No self-loop constraint
        for k in range(self.instance_data['couriers']):
            for i in range(self.instance_data['nodes']):
                self.prob += self.X[i][i][k] == 0

        # Vehicle leaves node that it enters
        for k in range(self.instance_data['couriers']):
            for j in range(self.instance_data['nodes']):
                self.prob += lpSum(self.X[i][j][k] for i in range(self.instance_data['nodes'])) == lpSum(self.X[j][i][k] for i in range(self.instance_data['nodes']))

        # Each item visited exactly once constraint
        for j in range(self.instance_data['items']):
            self.prob += lpSum(self.X[i][j][k] for i in range(self.instance_data['nodes']) for k in range(self.instance_data['couriers'])) == 1

        # Each vehicle starts from the depot and returns constraint
        for k in range(self.instance_data['couriers']):
            self.prob += lpSum(self.X[self.instance_data['nodes'] - 1][j][k] for j in range(self.instance_data['items'])) == 1

        # Vehicle capacity constraint
        for k in range(self.instance_data['couriers']):
            self.prob += lpSum(self.X[i][j][k] * self.instance_data['demands'][j] for i in range(self.instance_data['nodes']) for j in range(self.instance_data['nodes'] - 1)) <= self.instance_data['capacities'][k]

        # Distance constraint
        for k in range(self.instance_data['couriers']):
            self.prob += lpSum(self.instance_data['D'][i][j] * self.X[i][j][k] for i in range(self.instance_data['nodes']) for j in range(self.instance_data['nodes'])) <= self.Z

        # MTZ subtour elimination constraints
        if self.variation == 0:
            for k in range(self.instance_data['couriers']):
                for i in range(self.instance_data['nodes'] - 1): 
                    for j in range(self.instance_data['nodes'] - 1):  
                        self.prob += self.u[k][i] - self.u[k][j] + (self.instance_data['nodes'] - 1) * self.X[i][j][k] <= self.instance_data['nodes'] - 2, f"MTZ_{i}_{j}_{k}"
        else:
            for k in range(self.instance_data['couriers']):
                for i in range(self.instance_data['nodes'] - 1):  
                    for j in range(self.instance_data['nodes'] - 1):  
                        if self.instance_data['demands'][i] + self.instance_data['demands'][j] <= self.instance_data['capacities'][k]:
                            self.prob += self.u[k][i] - self.u[k][j] + self.instance_data['capacities'][k] * self.X[i][j][k] <= self.instance_data['capacities'][k] - self.instance_data['demands'][j], f"MTZ_{i}_{j}_{k}"

    def solve(self):
        result = {}

        # Determine solvers to use
        solvers = ['CBC', 'GLPK'] if self.solver_name.lower() == 'all' else [self.solver_name]
        variations = [0, 1] if self.solver_name.lower() == 'all' else [self.variation]

        for solver_name in solvers:
            for var in variations:
                self.variation = var
                start_time = datetime.now()

                self.initialize_problem()
                self.add_constraints()

                self.prob += self.Z

                preprocessing_time = (datetime.now() - start_time).total_seconds()
                remaining_time = int(max(0, math.ceil(self.timelimit - preprocessing_time)))

                if solver_name == 'GLPK':
                    solver = GLPK_CMD(msg=self.verbosity,timeLimit=remaining_time)
                else: 
                    solver = PULP_CBC_CMD(msg=self.verbosity,timeLimit=remaining_time)

                variation_suffix = "_MTZ_original" if var == 0 else "_MTZ_revisited"
                solver_name_with_variation = solver_name + variation_suffix

                self.prob.solve(solver)

                end_time = datetime.now()
                actual_runtime = (end_time - start_time).total_seconds()
                time = min(math.floor(actual_runtime), self.timelimit)


                status = LpStatus[self.prob.status]
                if status != 'Optimal':
                    result[solver_name_with_variation] = {
                        "time": time,
                        "optimal": False,
                        "obj": None,
                        "sol": []
                    }
                else:
                    sol = self.extract_solution()

                    optimal = LpStatus[self.prob.status] == 'Optimal'
                    if time >= self.timelimit:
                        optimal = False

                    result[solver_name_with_variation] = {
                        "time": time,
                        "optimal": optimal,
                        "obj": self.Z.varValue,
                        "sol": sol
                    }

        # Save results to a JSON file
        os.makedirs(self.save_directory, exist_ok=True)
        json_path = os.path.join(self.save_directory, f"{self.filename.split('.')[0]}.json")
        with open(json_path, 'w') as json_file:
            json.dump(result, json_file, indent=4)

        return result

