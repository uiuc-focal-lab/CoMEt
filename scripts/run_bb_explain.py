import subprocess
import pandas as pd
import sys
import os
sys.path.append('data/port_explanations_only_deletion/')
from type_counts_in_dir import *

BASE_FOLDER = 'data/port_explanations_only_deletion/'

blocks = pd.read_csv('data/Ithemal_dataset/explanation_dataset.csv')
print(blocks.head())

# max_tries = 50
# num_tries = 0
# df_view = blocks.iloc[1479:1514]
# print(df_view['categories'].unique)
# exit(0)

for i in range(0, blocks.shape[0]):

    code = blocks.iloc[i]['intel_code']
    original_code = blocks.iloc[i]['intel_code']

    category = blocks.iloc[i]['categories']
    category_folder = category.replace('/', '')
    # if os.path.exists(f'{BASE_FOLDER}/Ithemal/{category_folder}/{i}.txt'):  # this block is already done
    #     continue

    if type_count[category] >= 45:  # executed more than 45 basic blocks of same type
        # print('tc')
        continue

    insts = code.splitlines()
    if '.text' in insts[0]:  # remove the .text directive from the code
        insts = insts[1:]

    # remove comments from the code
    for ins in range(len(insts)):
        hash_pos = insts[ins].find('#')
        if hash_pos == -1:  # not here!
            continue
        insts[ins] = insts[ins][:hash_pos]

    insts = [x for x in insts if x != '']

    if len(insts) < 4 or len(insts) > 10:
        continue


    code = '; '.join(insts)
    code = code.replace('\t', ' ')

    try:
        print("Trying block", i)
        print("code:", code)
        print("category:", category)

        my_output_ithemal = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'instruction', 'ithemal', str(0.82), str(0.5)], universal_newlines=True)
        print('Ithemal done')
        my_output_uica = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'instruction', 'uica', str(0.82), str(0.5)], universal_newlines=True)
        print('uica done')
        category_folder = category.replace('/', '')
        with open(f'{BASE_FOLDER}/Ithemal/{category_folder}/{i}.txt', 'w') as f:
            f.write(my_output_ithemal)
        # with open(f'{BASE_FOLDER}/Ithemal/dependency/{category_folder}/{i}.txt', 'w') as f:
        #     f.write(my_output_dep)
        with open(f'{BASE_FOLDER}/uica/{category_folder}/{i}.txt', 'w') as f:
            f.write(my_output_uica)

        # my_output_ithemal_inst = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'instruction', 'ithemal'], universal_newlines=True)
        # print('Ithemal inst done')
        # my_output_ithemal_dep = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'dependency', 'ithemal'], universal_newlines=True)
        # print('Ithemal dep done')
        # my_output_uica_inst = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'instruction', 'uica'], universal_newlines=True)
        # print('uica inst done')
        # my_output_uica_dep = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'dependency', 'uica'], universal_newlines=True)
        # print('uica dep done')
        # category_folder = category.replace('/', '')
        # with open(f'{BASE_FOLDER}/Ithemal/{category_folder}/{i}.txt', 'w') as f:
        #     f.write(my_output_ithemal_inst + '\n' + my_output_ithemal_dep)
        # # with open(f'{BASE_FOLDER}/Ithemal/dependency/{category_folder}/{i}.txt', 'w') as f:
        # #     f.write(my_output_dep)
        # with open(f'{BASE_FOLDER}/uica/{category_folder}/{i}.txt', 'w') as f:
        #     f.write(my_output_uica_inst + '\n' + my_output_uica_dep)
        # with open(f'{BASE_FOLDER}/uica/dependency/{category_folder}/{i}.txt', 'w') as f:
        #     f.write(my_output_dep_uica)
        # num_tries += 1
        type_count[category] += 1
        print(type_count)
    except Exception as err:
        print("exception for block", i)
        print(err)
        # exit(1)
        # print("filtering opcodes")
        # _ = subprocess.check_output(['python3', 'scripts/filter_ithemal_accepted_opcodes.py', str(i)], universal_newlines=True)
        # print("filtered")
        # print("updating operand dict")
        # _ = subprocess.check_output(['python3', 'scripts/ithemal_datasets/make_new_operand_dict.py'], universal_newlines=True)
        # print("Retrying block", i)
        # try:
        #     my_output = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'instruction', 'ithemal'], universal_newlines=True)
        #     with open(f'data/Ithemal_all_results_1/{i}.txt', 'w') as f:
        #         f.write(my_output)
        #     type_count[category] += 1
        #     print(type_count)
        # except:
        #     print("failed second time")
        with open(f'{BASE_FOLDER}/type_counts_in_dir.py', 'w') as fp:
            fp.write('type_count = '+str(type_count))
        continue

    # if (num_tries > max_tries):
    #     break

    if all(ele >= 45 for ele in type_count.values()):
        break

with open(f'{BASE_FOLDER}/type_counts_in_dir.py', 'w') as fp:
    fp.write('type_count = '+str(type_count))
