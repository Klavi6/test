from pulp import *

usage17 = [3, 3, 2, 1]
percentage17 = [0.3, 0.3, 0.5, 1.0]
allocation17 = [10, 10, 4, 1] # sum 27

a = LpVariable('a', lowBound = 0)
b = LpVariable('b', lowBound = 0)
c = LpVariable('c', lowBound = 0)
d = LpVariable('d', lowBound = 0)
x = LpVariable('x', lowBound = 0)
y = LpVariable('y', lowBound = 0)
prob_list = [a*0.33, b*0.33, c*0.5, d*1.0]

prob = LpProblem("Problem", LpMinimize)
prob += y - x

prob += a+b+c+d == 27
for i in range(4):
    prob += prob_list[i] <= y
    prob += prob_list[i] >= x


solver = CPLEX_PY(msg=1)
prob.solve(solver)
print(value(prob.objective))
print(value(a), value(b), value(c), value(d))
print(value(x), value(y))
