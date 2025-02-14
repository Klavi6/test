from utils import format_bps


class Slice:
    def __init__(self, name, connected_users, user_share, delay_tolerance, qos_class,
                 bandwidth_guaranteed, bandwidth_max, capacity, usage_pattern):
        self.name = name
        self.connected_users = connected_users
        self.user_share = user_share
        self.delay_tolerance = delay_tolerance
        self.qos_class = qos_class
        self.bandwidth_guaranteed = bandwidth_guaranteed
        self.bandwidth_max = bandwidth_max
        self.capacity = capacity
        self.usage_pattern = usage_pattern
        self.level = 0

    def __str__(self):
        #return f'{self.name:<10} init_cap={format_bps(self.init_capacity)} consumable_cap={format_bps(self.capacity.level)} diff={format_bps(self.init_capacity - self.capacity.level)}'
        return f'{self.name:<10}'