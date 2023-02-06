import subprocess
import pickle
import os


with open('../data/mca-blocks', 'rb') as f:
    blocks = pickle.load(f)

block_ids = [int(file[:file.find('.txt')]) for file in os.listdir('data/Ithemal_inst_anchors2')]
block_ids.sort()
start_idx = 0


for i in block_ids[start_idx:]:

    code = blocks.iloc[i]['code']
    code = '; '.join(code.splitlines())
    code = code.replace('\t', ' ')

    print("Trying block", i)
    my_output = subprocess.check_output(['python3', 'bb_explain.py', code, 'instruction', 'uica'], universal_newlines=True)
    with open(f'data/uica_inst_anchors2/{i}.txt', 'w') as f:
        f.write(my_output)


