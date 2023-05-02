import subprocess
import yaml
import altair as alt
from pathlib import Path


def set_altair_theme():
    COLOR = '#F9F3DC'
    # chart = chart.configure(background='#F9F3DC').configure_view(fill='white')
    print(f'{alt.__version__=}')
    SCALE=1.5
    def theme_1(*args, **kwargs):
        my_theme = {'width': 400, 'height': 300,
                'config': {#'style': {'bar': {'size': 20}},
                        #'legend': {'symbolSize': 20, 'titleFontSize': 20, 'labelFontSize': 20}, 
                        'title':{'fontSize': 20*SCALE, 'subtitleFontSize': 12*SCALE, 'subtitleColor':'dimgray'},
                        'axis': {'titleFontSize': 15*SCALE, 'labelFontSize': 12*SCALE},
                        "axisX": { 
                            #https://towardsdatascience.com/consistently-beautiful-visualizations-with-altair-themes-c7f9f889602
                            "tickSize": 10, # default, including it just to show you can change it
                            "tickWidth":2,
                        },
                        'background': COLOR,
                        'view': {'fill':'white'}
                },
        }
        return my_theme
                #'encoding': {'x': {'axis': {'title': 'options'}, 'scale': {'paddingOuter': 0.5, 'paddingInner': 0.5}},
                #             'y': {'axis': {'title': 'percentage of students'}}}}
    alt.themes.register('theme_1', theme_1)
    alt.themes.enable('theme_1')

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


def my_snippets():
    '''
    from funcy import print_durations
    with print_durations('importing models'):
        do_something()
    '''
    '''
    from pandarallel import pandarallel
    pandarallel.initialize(progress_bar=True)
    df.parallel_apply()

    from tqdm import tqdm 
    tqdm.pandas()
    df.progress_apply()
    '''
    '''
    '''
    pass