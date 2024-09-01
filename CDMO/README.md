# Multiple-Couriers-Problem
This project solves the Multiple Couriers Problem using various methods. Below are the instructions for building the Docker image, running the Docker container, and executing experiments.

## Building the Docker Image

To build the Docker image for this project, use the following command:
```
docker build -t cdmo_project .
```
## Running the Docker Container
```
docker run -v ${PWD}/res:/CDMO/res cdmo_project instance_number --method CP 
```
## Running Experiments

You can run experiments by passing various arguments to the script. Here are the available arguments and their usage:
- --instance_number (required): The number of the instance to solve. Use 0 to solve all instances.
- --timelimit (optional): Time limit for the solver in seconds. Default is 300.
- --save_directory (optional): Directory to save the results. Default is res.
- --method (optional): Method to use for solving the problem. Choices are MIP, CP, SAT. Default is CP.
- --verbosity (optional): Output verbosity level. Choices are s (silent) and v (verbose). Default is s.
- --solver (optional): Solver to use for MIP. Choices are CBC, GLPK, ALL. Default is CBC.
- --variation (optional): MTZ variation to use for MIP. Choices are 0, 1. Default is 0.

 Run All Instances with CP Method:
  ```
  docker run -v ${PWD}/res:/CDMO/res cdmo_project 0 --method CP
  ```
 Run All Instances with SAT  Method:
  ```
  docker run -v ${PWD}/res:/CDMO/res cdmo_project 0 --method SAT
  ```
 Run All Instances with MIP  Method:
  ```
  docker run -v ${PWD}/res:/CDMO/res cdmo_project 0 --method MIP --solver ALL
  ```
To run all experiments, you can concatenate these three commands. Note that instances that are not solved are excluded from this method to streamline the process.
