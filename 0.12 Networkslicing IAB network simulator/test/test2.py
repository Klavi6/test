from pulp import LpVariable, LpProblem, value, CPLEX_PY, LpMaximize

x = LpVariable('x')
y = LpVariable('y', lowBound=-3)  # y ≥ -3

prob = LpProblem("Problem", LpMaximize)
prob += -x + 4*y + 4*y # 目的関数
prob += -3*x + y <= 6
prob += -x - 2*y >= -4

solver = CPLEX_PY(msg=1)
prob.solve(solver)
print(value(prob.objective), value(x), value(y))


# 線形/整数線形最適化問題を解くためにPuLPをインポート
import pulp
# 計算時間を計るのにtimeをインポート
import time

# 作業員の集合（便宜上、リストを用いる）
I = ["Aさん", "Bさん", "Cさん"]

print(f"作業員の集合 I = {I}")


# タスクの集合（便宜上、リストを用いる）
J = ["仕事イ", "仕事ロ", "仕事ハ"]

print(f"タスクの集合 J = {J}")


# 作業員 i を タスク j に割り当てたときのコストの集合（一時的なリスト）
cc = [
      [ 1,  2,  3],
      [ 4,  6,  8],
      [10, 13, 16],
     ]

# cc はリストであり、添え字が数値なので、
# 辞書 c を定義し、例えばcc[0][0] は c["Aさん","仕事イ"] でアクセスできるようにする
c = {} # 空の辞書
for i in I:
    for j in J:
        c[i,j] = cc[I.index(i)][J.index(j)]

print("コスト c[i,j]: ")
for i in I:
    for j in J:
        print(f"c[{i},{j}] = {c[i,j]:2d},  ", end = "")
    print("")
print("")



# 数理最適化問題（最小化）を宣言
problem = pulp.LpProblem("Problem-2", pulp.LpMinimize)
# pulp.LpMinimize : 最小化 
# pulp.LpMaximize : 最大化


# 変数集合を表す辞書
x = {} # 空の辞書
       # x[i,j] または x[(i,j)] で、(i,j) というタプルをキーにしてバリューを読み書き

# 0-1変数を宣言
for i in I:
    for j in J:
        x[i,j] = pulp.LpVariable(f"x({i},{j})", 0, 1, pulp.LpInteger)
        # 変数ラベルに '[' や ']' や '-' を入れても、なぜか '_' に変わる…？
# lowBound, upBound を指定しないと、それぞれ -無限大, +無限大 になる

# 内包表記も使える
# x_suffixes = [(i,j) for i in I for j in J]
# x = pulp.LpVariable.dicts("x", x_suffixes, cat = pulp.LpBinary) 

# pulp.LpContinuous : 連続変数
# pulp.LpInteger    : 整数変数
# pulp.LpBinary     : 0-1変数


# 目的関数を宣言
problem += pulp.lpSum(c[i,j] * x[i,j] for i in I for j in J), "TotalCost"
# problem += sum(c[i,j] * x[i,j] for i in I for j in J)
# としてもOK


# 制約条件を宣言
# 各作業員 i について、割り当ててよいタスク数は1つ以下
for i in I:
    problem += sum(x[i,j] for j in J) <= 1, f"Constraint_leq_{i}"
    # 制約条件ラベルに '[' や ']' や '-' を入れても、なぜか '_' に変わる…？

# 各タスク j について、割り当てられる作業員数はちょうど1人
for j in J:
    problem += sum(x[i,j] for i in I) == 1, f"Constraint_eq_{j}"


# 問題の式全部を表示
print("問題の式")
print(f"-" * 8)
print(problem)
print(f"-" * 8)
print("")

# 計算
# ソルバー指定
solver = CPLEX_PY(msg=1)

# 時間計測開始
time_start = time.perf_counter()

result_status = problem.solve(solver)

# 時間計測終了
time_stop = time.perf_counter()

# （解が得られていれば）目的関数値や解を表示
print("計算結果")
print(f"*" * 8)
print(f"最適性 = {pulp.LpStatus[result_status]}, ", end="")
print(f"目的関数値 = {pulp.value(problem.objective)}, ", end="")
print(f"計算時間 = {time_stop - time_start:.3f} (秒)")
print("解 x[i,j]: ")
for i in I:
    for j in J:
        print(f"{x[i,j].name} = {x[i,j].value()},  ", end="")
    print("")
print(f"*" * 8)
