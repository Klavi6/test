class Stats:
    def __init__(self, base_stations, slice_variation, clients, area):
        self.base_stations = base_stations
        self.clients = clients
        self.area = area
        self.slice_variation = slice_variation
        
        # Stats
        self.total_connected_users_ratio = []
        self.total_used_bw = []
        self.avg_slice_load_ratio = []
        self.avg_slice_client_count = []
        self.coverage_ratio = []
        self.connect_attempt = []
        self.block_count = []
        self.handover_count = []
        self.number_of_slices = 0
        
        for bs in self.base_stations:
            exec(f'self.AL_usage_bs{bs.pk} = []')
            exec(f'self.BL_usage_bs{bs.pk} = []')
            exec(f'self.AL_load_ratio_bs{bs.pk} = []')
            exec(f'self.BL_load_ratio_bs{bs.pk} = []')
            exec(f'self.AL_c_count_bs{bs.pk} = []')
            exec(f'self.BL_c_count_bs{bs.pk} = []')
            
            for i in self.slice_variation:
                exec(f'self.AL_usage_bs{bs.pk}_{i} = []')
                exec(f'self.AL_load_ratio_bs{bs.pk}_{i} = []')
                exec(f'self.AL_c_count_bs{bs.pk}_{i} = []')
                exec(f'self.AL_bandwidth_allocation_bs{bs.pk}_{i} = []')
                exec(f'self.AL_c_block_count_bs{bs.pk}_{i} = []')
            
                exec(f'self.BL_usage_bs{bs.pk}_{i} = []')
                exec(f'self.BL_load_ratio_bs{bs.pk}_{i} = []')
                exec(f'self.BL_c_count_bs{bs.pk}_{i} = []')
                exec(f'self.BL_bandwidth_allocation_bs{bs.pk}_{i} = []')
                exec(f'self.BL_c_block_count_bs{bs.pk}_{i} = []')
                
                exec(f'self.connect_per_attempt_bs{bs.pk}_{i} = []')
        
        self.connect_attempt.append(0)
        self.block_count.append(0)
        self.handover_count.append(0)
        for bs in self.base_stations:
            for sl in bs.access_slices:
                exec(f'self.AL_c_block_count_bs{bs.pk}_{sl.name}.append(0)')
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                exec(f'self.BL_c_block_count_bs{bs.pk}_{sl.name}.append(0)')
    
    def get_stats(self):
        stats_to_return = {"total_connected_users_ratio":self.total_connected_users_ratio, "total_used_bw":self.total_used_bw, "avg_slice_load_ratio":self.avg_slice_load_ratio, "avg_slice_client_count":self.avg_slice_client_count, "coverage_ratio":self.coverage_ratio, "block_count":self.block_count, "handover_count":self.handover_count}
        for bs in self.base_stations:
            exec(f'stats_to_return.update(AL_usage_bs{bs.pk} = self.AL_usage_bs{bs.pk}, BL_usage_bs{bs.pk} = self.BL_usage_bs{bs.pk}, AL_load_ratio_bs{bs.pk} = self.AL_load_ratio_bs{bs.pk}, BL_load_ratio_bs{bs.pk} = self.BL_load_ratio_bs{bs.pk}, AL_c_count_bs{bs.pk} = self.AL_c_count_bs{bs.pk}, BL_c_count_bs{bs.pk} = self.BL_c_count_bs{bs.pk})')
            for i in self.slice_variation:
                exec(f'stats_to_return.update(AL_usage_bs{bs.pk}_{i} = self.AL_usage_bs{bs.pk}_{i}, AL_load_ratio_bs{bs.pk}_{i} = self.AL_load_ratio_bs{bs.pk}_{i}, AL_c_count_bs{bs.pk}_{i} = self.AL_c_count_bs{bs.pk}_{i}, AL_bandwidth_allocation_bs{bs.pk}_{i} = self.AL_bandwidth_allocation_bs{bs.pk}_{i}, connect_per_attempt_bs{bs.pk}_{i} = self.connect_per_attempt_bs{bs.pk}_{i}, AL_c_block_count_bs{bs.pk}_{i} = self.AL_c_block_count_bs{bs.pk}_{i})')
                exec(f'stats_to_return.update(BL_usage_bs{bs.pk}_{i} = self.BL_usage_bs{bs.pk}_{i}, BL_load_ratio_bs{bs.pk}_{i} = self.BL_load_ratio_bs{bs.pk}_{i}, BL_c_count_bs{bs.pk}_{i} = self.BL_c_count_bs{bs.pk}_{i}, BL_bandwidth_allocation_bs{bs.pk}_{i} = self.BL_bandwidth_allocation_bs{bs.pk}_{i})')
        return stats_to_return
    
    def save_stats(self):
        with open("stats_text.txt","wt") as f:
            f.write(f'base_stations:{self.base_stations}\nclients:{self.clients}\narea:{self.area}\ntotal_connected_users_ratio:{self.total_connected_users_ratio}\ntotal_used_bw{self.total_used_bw}\navg_slice_load_ratio{self.avg_slice_load_ratio}\navg_slice_client_count{self.avg_slice_client_count}\ncoverage_ratio{self.coverage_ratio}\nblock_count{self.block_count}\nhandover_count{self.handover_count}')
        return

    def collect(self):
        self.total_connected_users_ratio.append(self.get_total_connected_users_ratio())
        self.total_used_bw.append(self.get_total_used_bw())
        self.avg_slice_load_ratio.append(self.get_avg_slice_load_ratio())
        self.avg_slice_client_count.append(self.get_avg_slice_client_count())
        self.coverage_ratio.append(self.get_coverage_ratio())
        
        self.connect_attempt.append(0)
        self.block_count.append(0)
        self.handover_count.append(0)
        for bs in self.base_stations:
            for sl in bs.access_slices:
                exec(f'self.AL_c_block_count_bs{bs.pk}_{sl.name}.append(0)')
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                exec(f'self.BL_c_block_count_bs{bs.pk}_{sl.name}.append(0)')

    def get_total_connected_users_ratio(self):
        t, cc = 0, 0
        for c in self.clients:
            if self.is_client_in_coverage(c):
                #t += c.connected
                t += c.green_to_donor
                cc += 1
        # for bs in self.base_stations:
        #     for sl in bs.slices:
        #         t += sl.connected_users
        return t/cc if cc != 0 else 0

    def get_total_used_bw(self):
        t = 0
        for bs in self.base_stations:
            for sl in bs.access_slices:
                t += sl.capacity.level
                exec(f'self.AL_usage_bs{bs.pk}_{sl.name}.append(sl.capacity.level)')
                exec(f'self.AL_bandwidth_allocation_bs{bs.pk}_{sl.name}.append(sl.capacity.capacity)')
            exec(f'self.AL_usage_bs{bs.pk}.append(bs.AL_capacity.level)')
            t = 0
        
        t = 0
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                t += sl.capacity.level
                exec(f'self.BL_usage_bs{bs.pk}_{sl.name}.append(sl.capacity.level)')
                exec(f'self.BL_bandwidth_allocation_bs{bs.pk}_{sl.name}.append(sl.capacity.capacity)')
            exec(f'self.BL_usage_bs{bs.pk}.append(bs.BL_capacity.level)')
            t = 0
        return t

    def get_avg_slice_load_ratio(self):
        t, c = 0, 0
        for bs in self.base_stations:
            for sl in bs.access_slices: 
                c += sl.capacity.capacity
                t += sl.capacity.level
                exec(f'self.AL_load_ratio_bs{bs.pk}_{sl.name}.append(sl.capacity.level/sl.capacity.capacity if sl.capacity.capacity != 0 else 0)')
            exec(f'self.AL_load_ratio_bs{bs.pk}.append(bs.AL_capacity.level/bs.Wa if bs.Wa != 0 else 0)')
            t = 0
        
        t, c = 0, 0
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                c += sl.capacity.capacity
                t += sl.capacity.level
                exec(f'self.BL_load_ratio_bs{bs.pk}_{sl.name}.append(sl.capacity.level/sl.capacity.capacity if sl.capacity.capacity != 0 else 0)')
            exec(f'self.BL_load_ratio_bs{bs.pk}.append(bs.BL_capacity.level/bs.Wb if bs.Wb != 0 else 0)')
            t = 0
        
        return t/c if c !=0 else 0

    def get_avg_slice_client_count(self):
        t, c = 0, 0
        for bs in self.base_stations:
            for sl in bs.access_slices:
                c += 1
                t += sl.connected_users
                exec(f'self.AL_c_count_bs{bs.pk}_{sl.name}.append(sl.connected_users)')
                #exec(f'self.connect_per_attempt_bs{bs.pk}_{sl.name}.append((sl.connected_users/(sl.connected_users + self.block_count[-1])) if (sl.connected_users + self.block_count[-1]) != 0 else 0)')
            exec(f'self.AL_c_count_bs{bs.pk}.append(t)')
            t = 0
        
        t, c = 0, 0
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                c += 1
                t += sl.connected_users
                exec(f'self.BL_c_count_bs{bs.pk}_{sl.name}.append(sl.connected_users)')
            exec(f'self.BL_c_count_bs{bs.pk}.append(t)')
            t = 0
        
        return t/c if c !=0 else 0
    
    def get_coverage_ratio(self):
        t, cc = 0, 0
        for c in self.clients:
            if self.is_client_in_coverage(c):
                cc += 1
                if c.base_station is not None and c.base_station.coverage.is_in_coverage(c.x, c.y):
                    t += 1
        return t/cc if cc !=0 else 0

    def incr_connect_attempt(self, client):
        if self.is_client_in_coverage(client):
            self.connect_attempt[-1] += 1

    def incr_block_count(self, client):
        if self.is_client_in_coverage(client):
            self.block_count[-1] += 1

    def incr_c_block_count(self, bs, sl):
        exec(f'self.c_block_count_bs{bs}_{sl}[-1] += 1')
    
    def BL_incr_c_block_count(self, bs):
        exec(f'self.c_block_count_bs{bs}_backhaul_link[-1] += 1')
    
    def incr_handover_count(self, client):
        if self.is_client_in_coverage(client):
            self.handover_count[-1] += 1

    def is_client_in_coverage(self, client):
        xs, ys = self.area
        return True if xs[0] <= client.x <= xs[1] and ys[0] <= client.y <= ys[1] else False
    
    def return_usage(self, ALorBL, bs, sl):
        stats = {}
        exec(f'stats.update(data = self.{ALorBL}_usage_bs{bs.pk}_{sl.name})')
        return stats
    
    def return_load_ratio(self, ALorBL, bs):
        stats = {}
        exec(f'stats.update(data = self.{ALorBL}_load_ratio_bs{bs.pk})')
        return stats