import sys
from pathlib import Path
from MIP import test_instance

def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py <instance_number> <solver_name> <result_folder>")
        sys.exit(1)

    instance_number = int(sys.argv[1])
    solver_name = sys.argv[2]
    result_folder = sys.argv[3]

    # Define the folder containing the instances
    instances_folder = Path.cwd() / 'instances'

    # Format the filename to match the pattern 'instXX.dat'
    filename = f'inst{instance_number:02d}.dat'
    file_path = instances_folder / filename
    #print(filename,file_path,instances_folder)
    # Test the instance using the test_instance function
    time, obj = test_instance(file_path, filename, result_folder=result_folder, solver_name=solver_name)
    
    # Print the results for the instance
    print(f"Instance: {filename} - Time: {time}s - Objective Value: {obj}")

if __name__ == "__main__":
    main()
