from statistics import mean

from matplotlib import gridspec
#import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, FuncFormatter
import randomcolor
#import threading

#import pygame
#matplotlib.use('module://pygame_matplotlib.backend_pygame')
from utils import format_bps

class Graph:
    def __init__(self, base_stations, clients, slice_variation, xlim, map_limits):
        self.base_stations = base_stations
        self.clients = clients
        self.xlim = xlim
        self.map_limits = map_limits
        self.fig = plt.figure(figsize=(16,9))
        self.slice_variation = slice_variation
        
        a = 0
        for bs in self.base_stations:
            a += 1
        a = a//4 + 1
        
        #self.gs1 = gridspec.GridSpec(4, 3, width_ratios=[6, 3, 3])
        self.gs1 = gridspec.GridSpec(1, 2)
        self.gs2 = gridspec.GridSpec(4, a)
        self.gs3 = gridspec.GridSpec(4, a)
        self.gs4 = gridspec.GridSpec(4, a)
        self.gs5 = gridspec.GridSpec(4, a)
        rand_color = randomcolor.RandomColor()
        colors = rand_color.generate(luminosity='bright', count=len(self.base_stations))
        #colors = [np.random.randint(256*0.2, 256*0.7+1, size=(3,))/256 for __ in range(len(self.base_stations))]
        for c, bs in zip(colors, self.base_stations):
            bs.color = c
    
    def draw_all(self, **stats):
        plt.clf()
        self.draw_map()
        self.draw_stats(**stats)

    def draw_map(self):
        markers = ['o', 's', 'p', 'P', '*', 'H', 'X', 'D', 'v', '^', '<', '>', '1', '2', '3', '4']
        self.ax = plt.subplot(self.gs1[0, 0])
        xlims, ylims = self.map_limits
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.set_aspect('equal')
        
        # base stations
        for bs in self.base_stations:
            circle = plt.Circle(bs.coverage.center, bs.coverage.radius,
                                fill=False, linewidth=1, alpha=0.9, color=bs.color)
            
            #self.ax.scatter(bs.x, bs.y, color=bs.color, s=20)
            self.ax.add_artist(circle)
        
        # clients
        legend_indexed = []
        for c in self.clients:
            label = None
            if c.subscribed_slice_index not in legend_indexed and c.base_station is not None:
                label = c.get_slice().name
                legend_indexed.append(c.subscribed_slice_index)
            self.ax.scatter(c.x, c.y,
                            color=c.base_station.color if c.base_station is not None else '0.8',
                            label=label, s=20,
                            marker=markers[c.subscribed_slice_index % len(markers)])
        
        box = self.ax.get_position()
        self.ax.set_position([box.x0 - box.width * 0.05, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        
        if legend_indexed != []:
            leg = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                                shadow=True, ncol=5)
            
            for i in range(len(legend_indexed)):
                leg.legendHandles[i].set_color('k')
        
        
        markers = ['o', 's', 'p', 'P', '*', 'H', 'X', 'D', 'v', '^', '<', '>', '1', '2', '3', '4']
        self.ax = plt.subplot(self.gs1[0, 1])
        xlims, ylims = self.map_limits
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.set_aspect('equal')
        
        # base stations
        for bs in self.base_stations:
            circle = plt.Circle(bs.coverage.center, bs.coverage.radius,
                                fill=False, linewidth=1, alpha=0.9, color=bs.color)
            
            #self.ax.scatter(bs.x, bs.y, color=bs.color, s=20)
            self.ax.add_artist(circle)
        
        # clients
        legend_indexed = []
        for c in self.clients:
            label = None
            if c.subscribed_slice_index not in legend_indexed and c.base_station is not None:
                label = c.get_slice().name
                legend_indexed.append(c.subscribed_slice_index)
            self.ax.scatter(c.x, c.y,
                            color = "b" if c.subscribed_slice_index == 0 else "g",
                            label=label, s=20,
                            marker=markers[c.subscribed_slice_index % len(markers)])
        
        box = self.ax.get_position()
        self.ax.set_position([box.x0 - box.width * 0.05, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        
        if legend_indexed != []:
            leg = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                                shadow=True, ncol=5)

            for i in range(len(legend_indexed)):
                leg.legendHandles[i].set_color('k')
        
        plt.tight_layout()
        plt.savefig("graph/overall.png", dpi=1000)
        

    def draw_stats(self, **stats):
        
        # overall
        """
        self.ax = plt.subplot(self.gs1[0, 1])
        plt.xlabel("time")
        plt.ylabel("ratio")
        self.ax.plot(stats["total_connected_users_ratio"])
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        self.ax.set_title(f'Connected Clients Ratio')
        
        self.ax = plt.subplot(self.gs1[3, 2])
        row_labels = [
            'Average connected clients',
            'Average bandwidth usage',
            'Average load factor of slices',
            'Average covorage ratio',
            'Average block ratio',
            'Average handover ratio',
        ]
        l, r = self.xlim
        cell_text = [
            [f'{mean(stats["total_connected_users_ratio"][l:r]):.2f}' if stats["total_connected_users_ratio"][l:r] else '0.00'],
            [f'{format_bps(mean(stats["total_used_bw"][l:r]), return_float=True)}' if stats["total_used_bw"][l:r] else '0.00'],
            [f'{mean(stats["avg_slice_load_ratio"][l:r]):.2f}' if stats["avg_slice_load_ratio"][l:r] else '0.00'],
            [f'{mean(stats["coverage_ratio"][l:r]):.2f}' if stats["coverage_ratio"][l:r] else '0.00'],
            [f'{mean(stats["block_count"][l:r]):.4f}' if stats["block_count"][l:r] else '0.0000'],
            [f'{mean(stats["handover_count"][l:r]):.4f}' if stats["handover_count"][l:r] else '0.0000'],
        ]
        
        self.ax.axis('off')
        self.ax.axis('tight')
        self.ax.tick_params(axis='x', which='major', pad=15)
        self.ax.table(cellText=cell_text, rowLabels=row_labels, colWidths=[0.35, 0.2], loc='center right')
        
        plt.tight_layout()
        plt.savefig("graph/overall.png", dpi=1000)
        """
        
        # capacity usage
        
        def capacity_usage_graph(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(self.gs2[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("usage")
            for i in self.slice_variation:
                self.ax.plot(stats[f'AL_usage_bs{bs_num}_{i}'], label=f'A_{i}')
                self.ax.plot(stats[f'BL_usage_bs{bs_num}_{i}'], label=f'B_{i}')
            #self.ax.plot(stats[f'AL_usage_bs{bs_num}'], label="AL_bs")
            #self.ax.plot(stats[f'BL_usage_bs{bs_num}'], label="BL_bs")
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.legend(loc="lower right")
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('Bandwidth usage at donor')
            else:
                self.ax.set_title(f'Bandwidth usage at node{bs_num}')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            capacity_usage_graph(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig("graph/capacity_usage.png", dpi=1000)
        
        
        
        # load ratio
        
        def load_ratio_graph(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(self.gs3[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("ratio")
            for i in self.slice_variation:
                self.ax.plot(stats[f'AL_load_ratio_bs{bs_num}_{i}'], label=f'A_{i}')
                self.ax.plot(stats[f'BL_load_ratio_bs{bs_num}_{i}'], label=f'B_{i}')
            #self.ax.plot(stats[f'AL_load_ratio_bs{bs_num}'], label=f'AL_bs')
            #self.ax.plot(stats[f'BL_load_ratio_bs{bs_num}'], label=f'BL_bs')
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.legend(loc="lower right")
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('Bandwidth usage ratio at donor')
            else:
                self.ax.set_title(f'Bandwidth usage ratio at node{bs_num}')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            load_ratio_graph(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig("graph/load_ratio.png", dpi=1000)
        
        # UE count
        
        def UE_count(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(self.gs4[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("UE count")
            for i in self.slice_variation:
                self.ax.plot(stats[f'AL_c_count_bs{bs_num}_{i}'], label=f'A_{i}')
                self.ax.plot(stats[f'BL_c_count_bs{bs_num}_{i}'], label=f'B_{i}')
            #self.ax.plot(stats[f'AL_c_count_bs{bs_num}'], label=f'AL_bs')
            #self.ax.plot(stats[f'BL_c_count_bs{bs_num}'], label=f'BL_bs')
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.legend(loc="lower right")
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('The number of connected UEs at donor')
            else:
                self.ax.set_title(f'The number of connected UEs at node{bs_num}')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            UE_count(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig("graph/user_amount.png", dpi=1000)
        
        # bandwidth allocation
        
        def bandwidth_allocation(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(self.gs5[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("bps")
            for i in self.slice_variation:
                self.ax.plot(stats[f'AL_bandwidth_allocation_bs{bs_num}_{i}'], label=f'A_{i}')
                self.ax.plot(stats[f'BL_bandwidth_allocation_bs{bs_num}_{i}'], label=f'B_{i}')
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.legend(loc="lower right")
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('Allocated bandwidth to slices at donor')
            else:
                self.ax.set_title(f'Allocated bandwidth to slices at node{bs_num}')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            bandwidth_allocation(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig("graph/bandwidth_allocation.png", dpi=1000)

    def show_plot(self):
        plt.show()

    def get_map_limits(self):
        # deprecated
        x_min = min([bs.coverage.center[0]-bs.coverage.radius for bs in self.base_stations])
        x_max = max([bs.coverage.center[0]+bs.coverage.radius for bs in self.base_stations])
        y_min = min([bs.coverage.center[1]-bs.coverage.radius for bs in self.base_stations])
        y_max = max([bs.coverage.center[1]+bs.coverage.radius for bs in self.base_stations])

        return (x_min, x_max), (y_min, y_max)
    
    """
    def draw_init(self):
        self.fig.canvas.draw()
        self.screen = pygame.display.set_mode((800, 600))

    def init_plot(self):
        self.ax = plt.subplot(self.gs1[0, 1])
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        return []
    
    def update_plot(self, frame, stats):
        self.ax.clear()
        for i in self.slice_variation:
            self.ax.plot(stats['AL_load_ratio_bs1_{i}'][:frame+1], label='{i}')
        self.ax.legend(loc="lower right")
        self.ax.set_title('Bandwidth Usage Ratio in Slices at node1')
        plt.xlabel("time")
        plt.ylabel("ratio")
        return []
    
    def draw_live(self, **stats):
        ani = animation.FuncAnimation(self.fig, self.update_plot, fargs=(stats,), init_func=self.init_plot, blit=False, cache_frame_data=False)
        plt.show()
        
        #self.screen.blit(self.draw_all(),**stats)
        #pygame.display.update()
    """