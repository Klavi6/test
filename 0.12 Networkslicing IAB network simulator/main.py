import time, pandas

import numpy as np

import BaseStation, Client, Coverage, Distributor, Graph, Slice, Stats, Container, route_generate, utils


def main(SIM_TIME, NUM_CLIENTS, data, bs_in_range):
    start_time = time.time()
    
    SETTINGS = data['settings']
    SLICES_INFO = data['slices']
    MOBILITY_PATTERNS = data['mobility_patterns']
    BASE_STATIONS = data['base_stations']
    CLIENTS = data['clients']
    PLOT = data['settings']['plotting_params']

    collected, slice_weights, slice_quantity = 0, [], []
    for __, s in SLICES_INFO.items():
        collected += s['client_weight']
        slice_weights.append(collected)
        slice_quantity.append(s['quantity'])

    slice_variation = []
    for name, s in SLICES_INFO.items():
        for i in range(s['quantity']):
            slice_variation.append(f'{name}_{i}')

    collected, mb_weights = 0, []
    for __, mb in MOBILITY_PATTERNS.items():
        collected += mb['client_weight']
        mb_weights.append(collected)

    mobility_patterns = []
    for name, mb in MOBILITY_PATTERNS.items():
        mobility_pattern = Distributor.Distributor(name, utils.get_dist(mb['distribution']), *mb['params'])
        mobility_patterns.append(mobility_pattern)

    usage_patterns = {}
    for name, s in SLICES_INFO.items():
        usage_patterns[name] = Distributor.Distributor(name, utils.get_dist(s['usage_pattern']['distribution']), *s['usage_pattern']['params'])

    base_stations = []
    i = 0
    for b in BASE_STATIONS:
        b_id = b['id']
        b_type = b['type']
        if SETTINGS["bs_batch_change"]["change"]:
            coverage = SETTINGS["bs_batch_change"][b_type]["coverage"]
            Wa = SETTINGS["bs_batch_change"][b_type]["Wa"]
            Wb = SETTINGS["bs_batch_change"][b_type]["Wb"]
        
        else:
            coverage = b['coverage']
            Wa = b['Wa']
            Wb = b['Wb']
        access_slices = []
        backhaul_slices = []
        
        # access link
        for name, s in SLICES_INFO.items():
            for n in range(s['quantity']):
                sl = Slice.Slice(f'{name}_{n}', 0, s['client_weight'],
                        s['delay_tolerance'],
                        s['qos_class'], s['bandwidth_guaranteed'],
                        s['bandwidth_max'], 0, usage_patterns[name])
                sl.capacity = Container.Container(capacity=0)
                access_slices.append(sl)
        
        # backhaul link
        for name, s in SLICES_INFO.items():
            for n in range(s['quantity']):
                sl = Slice.Slice(f'{name}_{n}', 0, s['client_weight'],
                        s['delay_tolerance'],
                        s['qos_class'], s['bandwidth_guaranteed'],
                        s['bandwidth_max'], 0, usage_patterns[name])
                sl.capacity = Container.Container(capacity=0)
                backhaul_slices.append(sl)
        
        base_station = BaseStation.BaseStation(i, b['x'], b['y'], Coverage.Coverage((b['x'], b['y']), coverage), b_id, b_type, Wa, Wb, access_slices, backhaul_slices)
        base_station.AL_capacity = Container.Container(capacity=Wa)
        base_station.BL_capacity = Container.Container(capacity=Wb)
        base_stations.append(base_station)
        i += 1

    ufp = CLIENTS['usage_frequency']
    usage_freq_pattern = Distributor.Distributor(f'ufp', utils.get_dist(ufp['distribution']), *ufp['params'], divide_scale=ufp['divide_scale'])

    x_vals = SETTINGS['statistics_params']['x']
    y_vals = SETTINGS['statistics_params']['y']
    stats = Stats.Stats(base_stations, slice_variation, None, ((x_vals['min'], x_vals['max']), (y_vals['min'], y_vals['max'])))

    df_user_info = pandas.DataFrame(columns=["id", "slice", "bandwidth", "x", "y", "green_to_donor", "route_to_donor", "pre_bs", "pre_route", "in_range"])

    clients = []
    rng = np.random.default_rng()
    coor_list_x = rng.uniform(SETTINGS['statistics_params']['x']['min'], SETTINGS['statistics_params']['x']['max'], NUM_CLIENTS)
    coor_list_y = rng.uniform(SETTINGS['statistics_params']['y']['min'], SETTINGS['statistics_params']['y']['max'], NUM_CLIENTS)
    
    for i in range(NUM_CLIENTS):
        # coodination
        loc_x = CLIENTS['location']['x']
        loc_y = CLIENTS['location']['y']
        if CLIENTS['route_fix']:
            mv_route_fix = True
            location_x = CLIENTS[i]['init_x']
            location_y = CLIENTS[i]['init_y']
            mv_route = CLIENTS[i]['route']
        else:
            mv_route_fix = False
            #location_x = round(utils.get_dist(loc_x['distribution'])(SETTINGS['statistics_params']['x']['min'], SETTINGS['statistics_params']['x']['max']), 2)
            #location_y = round(utils.get_dist(loc_y['distribution'])(SETTINGS['statistics_params']['y']['min'], SETTINGS['statistics_params']['y']['max']), 2)
            
            location_x = round(coor_list_x[i], 2)
            location_y = round(coor_list_y[i], 2)
            mv_route = {}
        
        # slice
        if CLIENTS['slice_fix']:
            connected_slice_index = CLIENTS[i]['slice']
        else:
            connected_slice_index = utils.get_random_slice_index(slice_weights, slice_quantity)
        
        # usage
        if CLIENTS['usage_fix']:
            usage_fix = True
            usage = CLIENTS[i]['usage']
        else:
            usage_fix = False
            usage = usage_freq_pattern.generate_scaled()
        
        mobility_pattern = utils.get_random_mobility_pattern(mb_weights, mobility_patterns)
        move_inside_area = CLIENTS['move_inside_area']
        
        c = Client.Client(i, location_x, location_y,
                        mobility_pattern, usage, usage_fix, connected_slice_index, stats, slice_weights, base_stations, x_vals, y_vals, mv_route, mv_route_fix, df_user_info, access_slices, backhaul_slices, move_inside_area, 0)
        clients.append(c)
    
    utils.KDTree.limit = SETTINGS['limit_closest_base_stations']
    utils.KDTree.run(clients, base_stations, 0)
    
    stats.clients = clients
    """
    xlim_left = int(SIM_TIME * SETTINGS['statistics_params']['warmup_ratio'])
    xlim_right = int(i * (1 - SETTINGS['statistics_params']['cooldown_ratio']))
    graph = Graph.Graph(base_stations, clients, slice_variation, (xlim_left, xlim_right),
                        ((x_vals['min'], x_vals['max']), (y_vals['min'], y_vals['max'])))
    """
    # ===== simulation begin =====
    for i in range(1,SIM_TIME+1):
        
        # Reallocate bandwidth of slices
        # new capacity is max(last 10 seconds) * 1.1
        
        if i % 10 == 0 and i != 0:
            for bs in base_stations:
                
                t = 0
                for sl in bs.access_slices:
                    sl.capacity.capacity = max(stats.return_usage("AL", bs, sl)["data"][-10:-1]) * 1.1
                    t += max(stats.return_usage("AL", bs, sl)["data"][-10:]) * 1.1
                if bs.Wa < t:
                    print(f"Error: could't secure extra access link bandwidth at bs{bs.pk}")
                    return False
                
                t = 0
                for sl in bs.backhaul_slices:
                    sl.capacity.capacity = max(stats.return_usage("BL", bs, sl)["data"][-10:-1]) * 1.1
                    t += max(stats.return_usage("AL", bs, sl)["data"][-10:]) * 1.1
                if bs.Wb < t:
                    print(f"Error: could't secure extra backhaul link bandwidth at bs{bs.pk}")
                    return False
        
        #Reset slice usage
        for bs in base_stations:
            bs.AL_capacity.level = 0
            bs.BL_capacity.level = 0
            for sl in bs.access_slices:
                sl.capacity.level = 0
            for sl in bs.backhaul_slices:
                sl.capacity.level = 0
        
        # Route generate
        
        for c in clients:
            if  c.requested_usage <= 0:
                c.generate_usage(i)
            
            # UEがいずれかの基地局の範囲内にあるかどうか
            c.in_range = False
            for bs in base_stations:
                if utils.distance(c.x, c.y, bs.x, bs.y) <= bs.coverage.radius:
                    c.in_range = True
            
            # データをc.df_user_infoに代入
            try:
                df_user_info.loc[c.pk, ["id", "slice", "bandwidth", "x", "y", "green_to_donor", "route_to_donor", "pre_bs", "pre_route", "in_range"]]\
                            = [c.pk, c.subscribed_slice_index, c.requested_usage, c.x, c.y, False, [], c.pre_bs, c.pre_route, c.in_range]
            except:
                print("Error: couldn't find routes from UEs to the donor")
                return False
        
        # route_generate 起動
        df_user_info = route_generate.route_generate(df_user_info, data, bs_in_range, base_stations)

        with open("output_text.txt","a+") as f:
            pandas.set_option('display.max_rows', 100000)
            f.write("\n"f'[{i}] {df_user_info}')
        
        for c in clients:
            c.green_to_donor = c.df_user_info.iat[c.pk, 5]
            c.route_to_donor = c.df_user_info.iat[c.pk, 6]
            if c.green_to_donor == True:
                c.base_station = c.base_stations[c.df_user_info.iat[c.pk, 6][0]]
            else:
                c.base_station = None
        
        # Connect or Disconnect
        
        for c in clients:
            if c.green_to_donor:
                c.start_consume(i)
                if c.base_station != c.pre_bs or c.route_to_donor != c.pre_route:
                    c.connect(i)
                else:
                    c.connected_stats_counter()
            else:
                if c.pre_bs != None and c.base_station == None: # 前は基地局あったのに無くなった場合
                    c.disconnect(i)
        
        #if i == 1:
        #    graph.draw_map()
        
        # Move
        
        for c in clients:
            c.move_phase(i)
        
        # iteration counter
        if i % 60 == 0 and i != 0:
            print(f'==={int(i/60)} minutes===')
        
        for c in clients:
            c.pre_bs = c.base_station
            c.pre_route = c.route_to_donor
        
        stats.collect()
        
        # check load ratio: exit if load ratio is over 100%
        
        for bs in base_stations:
            if stats.return_load_ratio("AL", bs)["data"][-1] > 1:
                print(f"Error: exceeded access link bandwidth at bs{bs.pk}")
                return False
            if stats.return_load_ratio("BL", bs)["data"][-1] > 1:
                print(f"Error: exceeded backhaul link bandwidth at bs{bs.pk}")
                return False
    
    # ===== simluation end =====
    
    for client in clients:
        with open("output_text.txt","a+") as f:
            f.write("\n"f'{client}')
            f.write("\n"f'\tTotal connected time: {client.total_connected_time:>5}')
            f.write("\n"f'\tTotal unconnected time: {client.total_unconnected_time:>5}')
            f.write("\n"f'\tTotal request count: {client.total_request_count:>5}')
            f.write("\n"f'\tTotal consume time: {client.total_consume_time:>5}')
            f.write("\n"f'\tTotal usage: {utils.format_bps(client.total_usage)} ({client.total_usage:>5})')
            f.write("\n")
    
    end_time = time.time()
    running_time = end_time - start_time
    with open("output_text.txt","a+") as f:
        f.write("\n"f'run time: {round(running_time)}s')
    print(f'run time is {round(running_time)}s')
    
    start_time = time.time()
    xlim_left = int(SIM_TIME * SETTINGS['statistics_params']['warmup_ratio'])
    xlim_right = int(i * (1 - SETTINGS['statistics_params']['cooldown_ratio']))
    graph = Graph.Graph(base_stations, clients, slice_variation, (xlim_left, xlim_right),
                        ((x_vals['min'], x_vals['max']), (y_vals['min'], y_vals['max'])), PLOT)
    graph.draw_all(**stats.get_stats())
    stats.save_stats()
    end_time = time.time()
    running_time = end_time - start_time
    
    with open("output_text.txt","a+") as f:
        f.write("\n"f'plot time: {round(running_time)}s')
    print(f'plot time is {round(running_time)}s')
    print('Simulation has ran completely!')
    if SETTINGS['plotting_params']['plot_show']:
        graph.show_plot()
