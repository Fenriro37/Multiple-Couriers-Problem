% %%%%%%%%%% VARIABLES %%%%%%%%%%
% int: m; 
% int: n;
% array[1..m] of int: l; 
% array[1..n] of int: s; 
% array[1..n+1, 1..n+1] of int: D; 
% array[1..m, 1..n] of var 0..1: x; % x[i][j] = 1 if courier i delivers item j
% array[1..m, 0..n+1] of var 0..n+1: tour; % tour[i][k] is the k-th location courier i visits
% array[1..m] of var int: total_distance;



% %%%%%%%%%% CONSTRAINTS %%%%%%%%%%
% % Calculate load constraints
% constraint forall(i in 1..m)(
%     sum(j in 1..n)(x[i,j] * s[j]) <= l[i]
% );
% % Ensure that each item is assigned to exactly one courier
% constraint forall(j in 1..n)(
%     sum(i in 1..m)(x[i,j]) = 1
% );
% % Start and end at the origin point (point n+1)
% constraint forall(i in 1..m)(
%     tour[i, 0] = n+1 /\ tour[i, n+1] = n+1
% );
% % Ensure all items assigned to a courier are included in the tour
% constraint forall(i in 1..m)(
%     forall(j in 1..n)(
%         (x[i,j] = 1) -> exists(k in 1..n)(tour[i,k] = j)
%     )
% );


% % Ensure that no location is visited more than once in the tour (except for the origin)no loop
% constraint forall(i in 1..m)(
%     forall(j in 1..n)(
%         sum(k in 1..n+1)(tour[i,k] = j) <= 1
%     )
% );

% % symmetry breaking
% constraint forall(i in 1..m-1) (
%     l[i] >= l[i+1] -> sum(j in 1..n)(x[i,j] * s[j]) >= sum(j in 1..n)(x[i+1,j] * s[j])
% );
% constraint forall(i in 1..m-1) (
%     (l[i] = l[i+1]) -> lex_lesseq([tour[i,k] | k in 1..n], [tour[i+1,k] | k in 1..n])
% );

% % Calculate the total distance traveled by each courier
% constraint forall(i in 1..m)(
%     total_distance[i] = sum(k in 0..n)(
%         D[tour[i,k], tour[i,k+1]]
%     )
% );
% % % biggest item for most capable courier
% % constraint x[arg_max(l), arg_max(s)] = 1;



% %%%%%%%%%% OBJECTIVE %%%%%%%%%%
% var int: max_distance = max(total_distance);
% %%%%%%%%%% SEARCH STRATEGY %%%%%%%%%%
% solve :: restart_luby(100) :: int_search([tour[i, k] | i in 1..m, k in 0..n+1], first_fail, indomain_min) minimize max_distance;


% %%%%%%%%%% OUTPUT %%%%%%%%%%
% output [
%     "Max Distance: ", show(max_distance), "\n",
%     "Total Distances: ", show(total_distance), "\n",
%     "Tour:\n",
%     show([tour[i, k] | i in 1..m, k in 0..n+1]) ++ "\n"
% ];




include "alldifferent.mzn";
include "globals.mzn";


% Input variables
int: courier;
int: items;
int: up_bound;
int :low_bound;
int :d_low_bound;

% useful sets
set of int: COURIERS = 1..courier;
set of int: ITEMS = 1..items;
set of int: NODES = 1..items + 1;

array[COURIERS] of int: courier_size;
array[ITEMS] of int: item_size;
array[NODES, NODES] of int: distances; 

% Model variables
array[COURIERS] of var d_low_bound..up_bound: obj_dist;
array[COURIERS, NODES] of var NODES: asg;

% objective function


var low_bound..up_bound: maximum; 

int :max_load = max(courier_size) + 1;

array[ITEMS] of var 0..courier: loads;

array[COURIERS] of var 0..max_load: couriers_loads;


% ensure that each courier starts and ends in origin point
constraint forall(k in COURIERS) (
      if asg[k, items+1] != items+1 then count([asg[k, i] | i in ITEMS], items+1, 1) 
      else forall(i in NODES) (asg[k, i] == i)  endif
);

% each item must be assigned only to one courier
constraint forall(i in ITEMS)(
      count([asg[k, i]| k in COURIERS], i, courier-1)
);


% setting the loads to verify the load_size for each courier
constraint forall(k in COURIERS) (
          forall(i in ITEMS)(
          if asg[k, i] != i then
          loads[i] = k endif
           )
);

% ensure that each courier does not exceed the max capacity
constraint bin_packing_capa(
                           courier_size,
                           loads,
                           item_size);

% Circuit
constraint forall(k in COURIERS) (
      subcircuit([asg[k, i] |i in NODES]) 
);

% distance computation
constraint forall(k in COURIERS) (
      obj_dist[k] = sum([distances[i, asg[k, i]]| i in NODES where asg[k, i] != i])
);


% Symmetry breaking constraint
constraint forall(k in COURIERS)(
    couriers_loads[k] = sum(
            [item_size[i] | i in ITEMS where loads[i]=k]
    )
);

% sub tour elimination, if the last courier can carry all the packages
% then all courier must start
constraint forall(k in COURIERS) (
                  if courier_size[courier] >= max(item_size) then 
                  asg[k, items+1] != items+1   
                  endif
            );


constraint maximum = max(obj_dist);
 


solve :: seq_search([
                int_search(asg, first_fail, indomain_min),
                int_search(loads, first_fail, indomain_min)])
     minimize(maximum);

%%%%%%%%%% OUTPUT %%%%%%%%%%
output [
    "Max Distance: ", show(maximum), "\n"
];




