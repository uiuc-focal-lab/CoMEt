import subprocess
import pandas as pd

blocks = pd.read_csv('data/Ithemal_dataset/hsw_w_categories.csv')
print(blocks.head())


for i in range(blocks.shape[0]):

    if blocks.iloc[i]['categories'] != 'Vec':  # only vector blocks!!
        continue

    code = blocks.iloc[i]['asm']

    insts = code.splitlines()
    if '.text' in insts[0]:  # remove the .text directive from the code
        insts = insts[1:]

    # remove comments from the code
    for i in range(len(insts)):
        hash_pos = insts[i].find('#')
        if hash_pos == -1:  # not here!
            continue
        insts[i] = insts[i][:hash_pos]

    insts = [x for x in insts if x is not '']

    code = '; '.join(insts)
    code = code.replace('\t', ' ')

    print("code:", code)

    try:
        print("Trying block", i)
        my_output = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; ' + code, 'instruction', 'ithemal'], universal_newlines=True)
        with open(f'data/Ithemal_inst_anchors_vector/{i}.txt', 'w') as f:
            f.write(my_output)
    except:
        continue


