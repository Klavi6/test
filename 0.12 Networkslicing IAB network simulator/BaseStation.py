#from utils import format_bps


class BaseStation:
    def __init__(self, pk, x, y, coverage, b_id, b_type, Wa, Wb, access_slices, backhaul_slices):
        self.pk = pk
        self.x = x
        self.y = y
        self.coverage = coverage
        self.b_id = b_id
        self.b_type = b_type
        self.Wa = Wa
        self.Wb = Wb
        self.access_slices = access_slices
        self.backhaul_slices = backhaul_slices
        with open("output_text.txt","a+") as f:
            f.write("\n"f"{self}")

    def __str__(self):
        #return f'BS_{self.pk:<2}(id={self.b_id},type={self.b_type})\t cov:{self.coverage}\t with cap {format_bps(self.capacity_bandwidth)}'
        return f'BS_{self.pk:<2}(id={self.b_id},type={self.b_type})'
