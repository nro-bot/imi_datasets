import random
import shutil
from pathlib import Path

files =list( Path('./nogit_data/text').glob('*.txt'))
random.shuffle(files)
sample = files[:20]
print(sample)

sample_output_dir = Path('./nogit_data/text_sample')
Path.mkdir(sample_output_dir, parents=True, exist_ok=True) # create or don't create are both fine
for file in sample:
    shutil.copy2(file, sample_output_dir)