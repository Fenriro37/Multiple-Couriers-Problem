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


%%%%%%%%%%%%%%%%%% Symmetry Breaking %%%%%%%%%%%%%%%%%%%
constraint forall(k in couriers)(
    couriers_loads[k] = sum(
            [s[i] | i in items where loads[i]=k]
    )
);

constraint forall(k in couriers) (
                  if l[k] >= max(s) then 
                  route[k, n+1] != n+1   
                  endif
            );

constraint forall(k in 1..m-1) (
    if l[k] == l[k+1] then
        obj_dist[k] <= obj_dist[k+1]
    endif
);



%%%%%%%%%%%%%%%%%%% Objective function %%%%%%%%%%%%%%%%%%%
constraint maximum = max(obj_dist);
 

% %%%%%%%%%%%%%%%%%%% Search Strategy %%%%%%%%%%%%%%%%%%%
solve :: restart_luby(100) :: seq_search([
                int_search(route, first_fail, indomain_min),
                int_search(loads, first_fail, indomain_min)])
     minimize(maximum);




%%%%%%%%%% OUTPUT %%%%%%%%%%
output [
    "Max Distance: ", show(maximum), "\n"
];




