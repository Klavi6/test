from pulp import *
import time
from utils import distance
from math import *


def route_generate(df_user_info, data, bs_in_range, BASE_STATIONS):
    SLICES_INFO = data['slices']
    
    # e
    # 基地局
    e = []
    i = 1
    for b in BASE_STATIONS:
        e.append(bs_in_range[i][1:])
        i += 1
    
    # S
    # slice infomation
    slice_info = []
    for name in SLICES_INFO.items():
        slice_info.append(name)
    
    # Wa, Wb, wa, wb
    # 基地局ごとの帯域、スライスに割り当てられている帯域
    Wa = []
    Wb = []
    wa = []
    wb = []
    bw = []
    
    for bs in BASE_STATIONS:
        Wa.append(bs.Wa)
        Wb.append(bs.Wb)
        
        for sl in bs.access_slices:
            bw.append(sl.capacity.capacity)
        wa.append(bw)
        bw = []
        
        for sl in bs.backhaul_slices:
            bw.append(sl.capacity.capacity)
        wb.append(bw)
        bw = []
    
    # V
    # base station coordinates and coverage
    bs_info = []
    for b in BASE_STATIONS:
        bs_info.append([b.x, b.y, b.coverage.radius])
    
    # U
    ps = df_user_info.values.tolist()
    
    
    prob = LpProblem('routing_generation', sense = LpMinimize)
    
    # 決定変数
    l = [[[LpVariable("l%s,%s_%s"%(u,i,j), cat="Binary") if i != j and int(e[i][j]) == 1 else 0 for j in range(len(e))] for i in range(len(e))] for u in range(len(ps))]
    c = [[LpVariable("c%s,%s"%(u,i), cat="Binary") if distance(ps[u][2], ps[u][3], bs_info[i][0], bs_info[i][1]) <= bs_info[i][2] else 0 for i in range(len(e))] for u in range(len(ps))]
    ya = [[LpVariable("ya%s,%s"%(i,s), lowBound=0) for s in range(len(slice_info))] for i in range(len(e))]
    yb = [[LpVariable("yb%s,%s"%(i,s), lowBound=0) for s in range(len(slice_info))] for i in range(len(e))]
    z = LpVariable('z', lowBound=0)
    
    # 目的関数
    
    # ホップ数を小さくする
    prob += z
    
    # 制約条件
    prob += lpSum(l[u][i][j] for u in range(len(ps)) for i in range(len(e)) for j in range(len(e))) <= z
    
    # Each user access one base station
    for u in range(len(ps)):
        prob += lpSum(c[u][i] for i in range(len(e))) == 1
    
    # Each user's route ends at the donor
    for u in range(len(ps)):
        prob += lpSum(l[u][i][0] for i in range(len(e))) == 1
    
    # If the u uses the link between vi and vj, a subsequent backhaul link must exist (applied big-M, M=1)
    for u in range(len(ps)):
        #for j in range(len(e)-1):
        for j in range(1,len(e)):
            #for i in range(len(e)-1):
            for i in range(1,len(e)):
                if i != j and int(e[i][j]) == 1:
                    prob += l[u][i][j] <= lpSum(l[u][j][k] if k != i and k != j else 0 for k in range(len(e)))
                    prob += lpSum(l[u][j][k] if k != i and k != j else 0 for k in range(len(e))) <= 2 - l[u][i][j]
    
    # If the u access to vi, a subsequent backhaul link must exist (applied big-M, M=1)
    for u in range(len(ps)):
        #for i in range(len(e)-1):
        for i in range(1,len(e)):
            if c[u][i] == 1:
                prob += c[u][i] <= lpSum(l[u][i][j] for j in range(len(e)))
                prob += lpSum(l[u][i][j] for j in range(len(e))) <= 2 - c[u][i]
    
    # prohibit exceeding maximum bandwidth allocated to access link of slices at each base stations
    for i in range(len(e)):
        for sl in range(len(slice_info)):
            prob += lpSum(ps[u][1] * c[u][i] if ps[u][0] == sl else 0\
                            for u in range(len(ps))) \
                            <= wa[i][sl] + ya[i][sl]
    
    # prohibit exceeding maximum bandwidth allocated to backhaul link of slices at each base station
    for j in range(len(e)):
        for sl in range(len(slice_info)):
            prob += lpSum(ps[u][1] * l[u][i][j] if i != j and ps[u][0] == sl else 0\
                            for i in range(len(e)) for u in range(len(ps))) \
                    + lpSum(ps[u][1] * c[u][j] if ps[u][0] == sl else 0\
                            for u in range(len(ps))) \
                            <= wb[j][sl] + yb[j][sl]
    
    # prohibit exceeding shared bandwidth for access link at each base station
    for i in range(len(e)):
        prob += lpSum(ya[i][sl] for sl in range(len(slice_info))) <= Wa[i] - lpSum(wa[i][sl] for sl in range(len(slice_info)))
    
    # prohibit exceeding shared bandwidth for backhaul link at each base station
    for i in range(len(e)):
        prob += lpSum(yb[i][sl] for sl in range(len(slice_info))) <= Wb[i] - lpSum(wb[i][sl] for sl in range(len(slice_info)))
    
    
    """
    # delay toleranceの範囲内
    for k in range(len(ps)):
        if ps[k][0] != len(e)-1: # ユーザーがドナーに接続していない場合のみ
            prob += lpSum(l[i][j][k] if i != j else 0 for i in range(len(e)) for j in range(len(e))) * 0.05 <= slice_info[ps[k][1]][1]["delay_tolerance"]
    """
    #with open("output_text.txt","a+") as f:
    #    f.write("\n"f'{prob}')
    time_start = time.perf_counter()
    status = prob.solve(CPLEX(msg=0))
    #status = prob.solve(SCIP(msg=0))
    time_stop = time.perf_counter()
    print("Status", LpStatus[status])
    
    
    if LpStatus[status] == "Optimal":
        route, ps_route = [], []
        link_pre = None
        for u in range(len(ps)):
            
            """
            with open("output_text.txt","a+") as f:
                f.write("\n")
            for i in range(len(e)):
                if round(value(c[u][i])) == 1:
                    with open("output_text.txt","a+") as f:
                        f.write(f'{c[u][i]} ')
                for j in range(len(e)):
                    if round(value(l[u][i][j])) == 1:
                        with open("output_text.txt","a+") as f:
                            f.write(f'{l[u][i][j]} ')  
            """
            
            # donorへのリンクがあるかどうかを確認
            df_user_info.iat[u, 4] = False
            
            for i in range(len(e)):
                if round(value(l[u][i][0])) == 1:
                    df_user_info.iat[u, 4] = True
                if round(value(c[u][0])) == 1:
                    df_user_info.iat[u, 4] = True
            
            if df_user_info.iat[u, 4] == True:
                
                for i in range(len(e)):
                    if round(value(c[u][i])) == 1:
                        route.append(i)
                        link_pre = i
                if link_pre is not None:
                    while link_pre != 0:
                        for i in range(len(e)):
                            for j in range(len(e)):
                                if round(value(l[u][i][j])) == 1 and i == link_pre:
                                    route.append(j)
                                    link_pre = j
                else:
                    pass
            
            ps_route.append(route)
            route = []
        
        for (p, r) in zip(range(len(ps)), ps_route):
            if r != []:
                df_user_info.iat[p, 5] = r
            else:
                df_user_info.iat[p, 5] = []
                df_user_info.iat[p, 4] = False
        
        #print(f"objective value {value(prob.objective)}")
        print(f"calculation time {time_stop - time_start:.3f} s")
        
        return df_user_info