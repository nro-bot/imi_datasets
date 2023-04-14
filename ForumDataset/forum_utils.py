import subprocess
import yaml
from pathlib import Path

def get_project_constants(var=None):
    # TODO: should probably not just inject git_home here, should move directly to config.yml somehow 
    import yaml
    cmd_str = "git rev-parse --show-toplevel"
    p = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'], capture_output=True)
    GIT_HOME = p.stdout.decode('utf-8').strip()

    with open(Path(GIT_HOME, 'config.yml'), 'r') as file:
        config = yaml.safe_load(file)
    config['git_home'] = GIT_HOME
    if var:
        return config[var]
    return config

def about_utils():
    config = get_project_constants()
    print(f"Configuration Keys: {', '.join(config.keys())}")

def save_latex_var(key, value):
    import csv
    import os

    dict_var = {}

    config = get_project_constants()
    file_path = Path(GIT_HOME, Path(config['latex_vars_file']))

    print('Saving to: ', file_path)
    DELIMITER = ';'

    try:
        with open(file_path, newline="") as file:
            reader = csv.reader(file, delimiter=DELIMITER)
            for row in reader:
                dict_var[row[0]] = row[1]
    except FileNotFoundError:
        pass

    dict_var[key] = value

    with open(file_path, "w") as f:
        for key in dict_var.keys():
            print('Saving', key, value)
            f.write(f"{key}{DELIMITER}{dict_var[key]}\n") # DELIMITER DEFINED HERE

#config = get_project_constants()
#print(config['git_home'])
#print(config['latex_vars_file'])