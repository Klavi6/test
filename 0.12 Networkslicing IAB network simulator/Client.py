import random

import numpy as np

from utils import format_bps

class Client:
    def __init__(self, pk, x, y, mobility_pattern, usage_freq, usage_fix, subscribed_slice_index, stat_collector,
                slice_weights, base_stations, x_vals, y_vals, mv_route, mv_route_fix, df_user_info, access_slices, backhaul_slices, move_inside_area, requested_usage):
        self.pk = pk
        self.x = x
        self.y = y
        self.mobility_pattern = mobility_pattern
        self.usage_freq = usage_freq
        self.usage_fix = usage_fix
        self.base_station = None
        self.stat_collector = stat_collector
        self.subscribed_slice_index = subscribed_slice_index
        self.requested_usage = requested_usage
        self.connected = False
        self.base_stations = base_stations
        self.move_inside_area = move_inside_area
        self.x_vals = x_vals
        self.y_vals = y_vals
        self.mv_route = mv_route
        self.mv_route_fix = mv_route_fix
        self.df_user_info = df_user_info
        self.green_to_donor = False
        self.access_slices = access_slices
        self.backhaul_slices = backhaul_slices
        self.route_to_donor = []
        self.pre_bs = None
        self.pre_route = []
        self.last_usage = 0
        
        if self.usage_fix:
            self.requested_usage = self.usage_freq
        
        # Stats
        self.total_connected_time = 0
        self.total_unconnected_time = 0
        self.total_request_count = 0
        self.total_consume_time = 0
        self.total_usage = 0
        
        self.slice_weights = slice_weights
    
    def connected_stats_counter(c):
        c.total_consume_time += 1
        c.total_usage += c.last_usage
    
    def generate_usage(c, i):
        c.requested_usage = c.access_slices[c.subscribed_slice_index].usage_pattern.generate()
        with open("output_text.txt","a+") as f:
            f.write("\n"f'[{i}] Client_{c.pk} [{c.x}, {c.y}] ^ requests {format_bps(c.requested_usage)} usage.')
    
    def connect(c, i):
        c.connected = True
        
        if c.pre_bs != None:
            c.disconnect(i)
            with open("output_text.txt","a+") as f:
                f.write("\n"f'[{i}] Client_{c.pk} [{c.x}, {c.y}] <--> handed over to {c.base_station}')
            c.stat_collector.incr_handover_count(c)
        
        # AL
        c.base_stations[c.route_to_donor[0]].access_slices[c.subscribed_slice_index].connected_users += 1
        # BL
        #for a in c.route_to_donor[1:]:
        for a in c.route_to_donor:
            c.base_stations[a].backhaul_slices[c.subscribed_slice_index].connected_users += 1
        
        with open("output_text.txt","a+") as f:
            f.write("\n"f'[{i}] Client_{c.pk} [{c.x}, {c.y}] -> connected to slice={c.get_slice()}, route to donor is: {c.route_to_donor}')
        
        with open("output_text.txt","a+") as f:
            f.write(f'gets {format_bps(c.requested_usage)} usage')
        
    def start_consume(c, i):
        # AL
        c.base_stations[c.route_to_donor[0]].access_slices[c.subscribed_slice_index].capacity.get(c.requested_usage)
        c.base_stations[c.route_to_donor[0]].AL_capacity.get(c.requested_usage)
        # BL
        c.base_stations[0].backhaul_slices[c.subscribed_slice_index].capacity.get(c.requested_usage)
        c.base_stations[0].BL_capacity.get(c.requested_usage)
        for a in c.route_to_donor[1:-1]:
            c.base_stations[a].backhaul_slices[c.subscribed_slice_index].capacity.get(2*c.requested_usage)
            c.base_stations[a].BL_capacity.get(2*c.requested_usage)
        c.base_stations[-1].backhaul_slices[c.subscribed_slice_index].capacity.get(c.requested_usage)
        c.base_stations[-1].BL_capacity.get(c.requested_usage)
        
        c.last_usage = c.requested_usage
        c.total_consume_time += 1
        c.total_usage += c.last_usage
    
    def release_consume(c, i):
        if c.last_usage > 0: # note: s.capacity.put cannot take 0
            # AL
            c.pre_bs.access_slices[c.subscribed_slice_index].capacity.put(c.last_usage)
            # BL
            #for a in c.pre_route[1:]:
            for a in c.pre_route:
                c.base_stations[a].backhaul_slices[c.subscribed_slice_index].capacity.put(c.last_usage)
            
            with open("output_text.txt","a+") as f:
                f.write("\n"f'[{i}] Client_{c.pk} [{c.x}, {c.y}] <- puts back {format_bps(c.last_usage)} usage.')
            c.last_usage = 0
    
    def disconnect(c, i):
        # AL
        c.pre_bs.access_slices[c.subscribed_slice_index].connected_users -= 1
        # BL
        #for a in c.pre_route[1:]:
        for a in c.pre_route:
            c.base_stations[a].backhaul_slices[c.subscribed_slice_index].connected_users -= 1
        
        c.connected = False
        with open("output_text.txt","a+") as f:
            f.write("\n"f'[{i}] Client_{c.pk} [{c.x}, {c.y}] <- disconnected from slice: {c.get_slice()} @ {c.pre_bs}')
    
    def move_phase(c, i):
        if c.mv_route_fix: # fix clients movement route
            if i in c.mv_route:
                c.x = c.mv_route[i][0]
                c.y = c.mv_route[i][1]
        else:
            """
            x, y = c.mobility_pattern.generate_movement()
            
            if c.move_inside_area:
                while c.x + x > c.x_vals['max'] or c.x + x < c.x_vals['min']:
                    x = c.mobility_pattern.generate_movement()[0]
            
            if c.move_inside_area:
                while c.y + y > c.y_vals['max'] or c.y + y < c.y_vals['min']:
                    y = c.mobility_pattern.generate_movement()[1]
            """
            
            vec = 2*np.pi*np.random.uniform(0, 1)
            amount = np.random.uniform(0, 5)
            x = amount*np.cos(vec)
            y = amount*np.sin(vec)
            
            if c.move_inside_area:
                while c.x + x > c.x_vals['max'] or c.x + x < c.x_vals['min'] or c.y + y > c.y_vals['max'] or c.y + y < c.y_vals['min']:
                    vec = 2*np.pi*np.random.uniform(0, 1)
                    amount = np.random.uniform(0, 5)
                    x = amount*np.cos(vec)
                    y = amount*np.sin(vec)
            c.x += x
            c.y += y
            c.x = round(c.x, 2)
            c.y = round(c.y, 2)
            #with open("output_text.txt","a+") as f:
            #    f.write("\n"f'[{i}] Client_{c.pk} alt vec[{round(vec, 2)}], alt amount[{round(amount, 2)}]')
    
    def release_randomizer(self):
        r = random.random()
        w = [0.0000, 1.0000] # [change, change + maintain connection]
        if w[0] > r: # change or maintain connection
            return True
        return False
    
    def slice_randomizer(self):
        i1 = 0
        r1 = random.random()
        r2 = random.random()
        w = [0.01, 1.0] # [change, change + maintain slice]
        if w[0] > r1: # change or maintain slice
            while self.slice_weights[i1] < r2: # which slice to choose
                i1 += 1
            slice_before = self.subscribed_slice_index
            self.subscribed_slice_index = i1
            with open("output_text.txt","a+") as f:
                f.write("\n"f'Client_{self.pk} [{self.x}, {self.y}] changed slice from {slice_before} to {self.subscribed_slice_index}')
    
    def get_slice(self):
        if self.base_station is None:
            return None
        return self.base_station.access_slices[self.subscribed_slice_index]
    

# following def will be outputted finally
    def __str__(self):
        return f'Client_{self.pk} [{self.x:<5}, {self.y:>5}] connected to: slice={self.get_slice()} @ {self.base_station}\t with mobility pattern of {self.mobility_pattern}'
