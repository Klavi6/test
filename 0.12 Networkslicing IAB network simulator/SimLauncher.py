import main, yaml, os, csv, sys, datetime


SIM_TIME = 500
NUM_CLIENTS = 100

#import_file = "plane" # random
#import_file = "simple" # 3 nodes 1 donor square
#import_file = "grid" # 3*3
#import_file = "single" # only a donor
import_file = "line" # 2 nodes 1 donor in line

if import_file == "plane":
    setting_file = "setting.yml"
    in_range_file = "basestation_in_range.csv"
elif import_file == "simple":
    setting_file = "setting_simple.yml"
    in_range_file = "basestation_in_range_simple.csv"
elif import_file == "grid":
    setting_file = "setting_grid.yml"
    in_range_file = "basestation_in_range_grid.csv"
elif import_file == "single":
    setting_file = "setting_single.yml"
    in_range_file = "basestation_in_range_single.csv"
elif import_file == "line":
    setting_file = "setting_line.yml"
    in_range_file = "basestation_in_range_line.csv"

with open(os.path.join(os.path.dirname(__file__), setting_file), 'r') as stream:
    data = yaml.load(stream, Loader=yaml.FullLoader)

with open(os.path.join(os.path.dirname(__file__), in_range_file), mode='r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    bs_in_range = [row for row in reader]

while True:
    with open("output_text.txt","wt") as f:
        f.write("======logging proccess initiated======")
    print(f"num client is {NUM_CLIENTS}")
    with open("output_text.txt","a+") as f:
        f.write("\n"f'NUM_CLIENT is {NUM_CLIENTS}')
    
    if main.main(SIM_TIME, NUM_CLIENTS, data, bs_in_range) is False:
        NUM_CLIENTS -= round(NUM_CLIENTS/10)
    else:
        with open("output_text.txt","a+") as f:
            f.write("\n"f'{datetime.datetime.now()}')
            f.write("\n"f'======logging proccess terminated======')
        
        sys.exit(0)