import argparse
from MIP import MIP_solver  
from SAT.SATclass import SAT_solver


def main():
    parser = argparse.ArgumentParser(description="Solve the Vehicle Routing Problem using various methods.")
    
    parser.add_argument(
        'instance_number',
        type=int,
        help='The number of the instance to solve.'
    )

    parser.add_argument(
        '--timelimit',
        type=int,
        default=300,
        help='Time limit for the solver in seconds (default: 300).'
    )
    
    parser.add_argument(
        '--save_directory',
        default='res',
        help='Directory to save the results (default: res).'
    )
        
    parser.add_argument(
        '--method',
        choices=['MIP', 'CP','SAT'],
        default='CP',
        help='The method to use for solving the problem (default: CP).'
    )

    parser.add_argument(
        '--verbosity',
        choices=['s', 'v'],
        default='full',
        help='Output verbosity level (default: full).'
    )
    # Arguments specific to MIP
    parser.add_argument(
        '--solver',
        choices=['CBC', 'GLPK', 'ALL'],
        default='CBC',
        help='The solver to use for MIP (default: CBC). This is ignored if method is not MIP.'
    )
    
    parser.add_argument(
        '--variation',
        type=int,
        choices=[0, 1],
        default=0,
        help='The MTZ variation to use for MIP (default: 0). This is ignored if method is not MIP.'
    )

    args = parser.parse_args()

    print(args)
        
    if args.method == 'CP':
        # Initialize and solve using CP-SAT
        # Example: Assuming a CPSAT_solver class exists
        # solver = CPSAT_solver(
        #     instance_number=args.instance_number,
        #     timelimit=args.timelimit,
        #     save_directory=args.save_directory,
        #     variation=args.variation
        # )
        #
        # results = solver.solve()
        pass

    elif args.method == 'SAT':
        # Initialize and solve using CP-SAT
        # Example: Assuming a CPSAT_solver class exists
        solver = SAT_solver(
            instance_number=args.instance_number,
            timelimit=args.timelimit,
            save_directory=args.save_directory+'/SAT',
        )
        if args.instance_number == 0:
            solver.solve_all()
        else:
            solver.solve()

    elif args.method == 'MIP':
        solver = MIP_solver(
            instance_number=args.instance_number,
            timelimit=args.timelimit,
            save_directory=args.save_directory+'/MIP',
            verbosity=args.verbosity,
            solver_name=args.solver,
            variation=args.variation
        )
    print('Solving instance')
    solver.solve()
    print(f'Results can be found in {args.save_directory} folder')


if __name__ == "__main__":
    main()
