import os
import json
import minizinc
from datetime import timedelta
import numpy as np

class CP_solver:
    def __init__(self, instance_number, timelimit, save_directory):
        self.instance_number = instance_number
        self.timelimit = timelimit
        self.save_directory = save_directory
        self.instances_dir = 'instances/'
        self.results_dir = os.path.join(save_directory, 'CP/')
        os.makedirs(self.results_dir, exist_ok=True)

    def preprocess_dat_file(self, file_path):
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

        max_last_row = max(D[-1, :-1])
        max_last_col = max(D[:-1, -1])
        low_bound = max(max_last_row, max_last_col)
        
        return m, n, l, s, D, up_bound, low_bound

    def solve_instance(self, instance, solver_name, m, n):
        result = instance.solve(timeout=timedelta(seconds=self.timelimit))
        
        time_taken = int(result.statistics.get('time', timedelta(seconds=self.timelimit)).total_seconds())

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
        else:
            return None

    def solve(self):
        model_with_symmetry = minizinc.Model('CP_model(with SB).mzn')
        model_without_symmetry = minizinc.Model('CP_model(without SB).mzn')

        gecode = minizinc.Solver.lookup("gecode")
        chuffed = minizinc.Solver.lookup("chuffed")

        instance_file = f'inst{self.instance_number:02d}.dat'
        instance_path = os.path.join(self.instances_dir, instance_file)

        m, n, l, s, D, up_bound, low_bound = self.preprocess_dat_file(instance_path)

        output = {}
        
        for model_name, model in [("with_symmetry", model_with_symmetry), ("without_symmetry", model_without_symmetry)]:
            instance_gecode = minizinc.Instance(gecode, model)
            instance_chuffed = minizinc.Instance(chuffed, model)

            for instance_name, instance in [("gecode", instance_gecode), ("chuffed", instance_chuffed)]:
                instance["m"] = m
                instance["n"] = n
                instance["l"] = l
                instance["s"] = s
                instance["D"] = D
                instance["up_bound"] = up_bound
                instance["low_bound"] = low_bound

                result = self.solve_instance(instance, instance_name, m, n)
                if result and result["obj"] is not None:
                    output[f"{instance_name}_{model_name}"] = result

        if output:
            json_filename = f'{self.instance_number:02d}.json'
            json_path = os.path.join(self.results_dir, json_filename)
            with open(json_path, 'w') as f:
                json.dump(output, f, indent=4)
            
            print(f"Results for {instance_file} saved to {json_filename}.")
        else:
            print(f"No valid results for {instance_file}, no JSON file created.")
