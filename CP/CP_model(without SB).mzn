include "alldifferent.mzn";
include "globals.mzn";

%%%%%%%%%%%%%%%%%%% Variables %%%%%%%%%%%%%%%%%%%
int: m;
int: n;
int: up_bound;
int :low_bound;

set of int: couriers = 1..m;
set of int: items = 1..n;
set of int: points = 1..n + 1;

array[couriers] of int: l;
array[items] of int: s;
array[points, points] of int: D; 

array[couriers] of var 0..up_bound: obj_dist; % distance for each courier
array[couriers, points] of var points: route; % route if route[i][j] = j then courier i doesn't deliver item j
var low_bound..up_bound: maximum; 

int :max_load = max(l);

array[items] of var 0..m: loads; % loads[i]= j then courier i delivers item j
array[couriers] of var 0..max_load: couriers_loads;


%%%%%%%%%%%%%%%%%%% Constraints %%%%%%%%%%%%%%%%%%%
% couriers start and end in depot
constraint forall(k in couriers) (
      if route[k, n+1] != n+1 then count([route[k, i] | i in items], n+1, 1) 
      else forall(i in points) (route[k, i] == i)  endif % no assignment of items
);

% each item assigned to one courier
constraint forall(i in items)(
      count([route[k, i]| k in couriers], i, m-1)
);


% setting loads for bin_packing_capa
constraint forall(k in couriers) (
          forall(i in items)(
          if route[k, i] != i then
          loads[i] = k endif
           )
);
% ensure that each courier does not exceed the max capacity
constraint bin_packing_capa(
                           l,
                           loads,
                           s);

% Circuit ensure no sub-tours
constraint forall(k in couriers) (
      subcircuit([route[k, i] |i in points]) 
);

% calculate distance for each courier
constraint forall(k in couriers) (
      obj_dist[k] = sum([D[i, route[k, i]]| i in points where route[k, i] != i])
);



%%%%%%%%%%%%%%%%%%% Objective function %%%%%%%%%%%%%%%%%%%
constraint maximum = max(obj_dist);
 

% %%%%%%%%%%%%%%%%%%% Search Strategy %%%%%%%%%%%%%%%%%%%
solve :: restart_luby(100) :: seq_search([
                int_search(route, first_fail, indomain_min),
                int_search(loads, first_fail, indomain_min)])
     minimize(maximum);




%%%%%%%%%% OUTPUT %%%%%%%%%%
% output [
%     "Max Distance: ", show(maximum), "\n"
% ];

output [
    "Maximum Distance: ", show(maximum), "\n",
    "Distances for each courier: ", show(obj_dist), "\n",
    "Routes:\n" ++
    concat([ "Courier " ++ show(k) ++ ": " ++ show([route[k, i] | i in 1..n+1]) ++ "\n" | k in couriers ])
];



