import json
import glob
import os

# Read latest FP result file
def read_fp_results(server_folder):
    list_of_files = glob.glob('servers/'+server_folder+'/results/*FP*')
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, encoding='utf-16-le') as json_file:
        data = json.load(json_file)
        return data

# Read latest Q result file
def read_q_results(server_folder):
    list_of_files = glob.glob('servers/'+server_folder+'/results/*Q*')
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, encoding='utf-16-le') as json_file:
        data = json.load(json_file)
        return data

# Read latest R result file
def read_r_results(server_folder):
    list_of_files = glob.glob('servers/'+server_folder+'/results/*R*')
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, encoding='utf-16-le') as json_file:
        data = json.load(json_file)
        return data

def convert_result_to_seconds(milliseconds):
    seconds, milliseconds = divmod(milliseconds,1000)
    seconds = seconds+milliseconds/1000
    return f"{seconds:.3f}"

def convert_result_to_minutes(milliseconds):
    seconds, milliseconds = divmod(milliseconds,1000)
    minutes, seconds = divmod(seconds, 60)
    seconds = f"{seconds+milliseconds/1000:.3f}"
    result = str(minutes) + ':' + str(seconds)
    return result
    