import pandas as pd
import os
import sys
sys.path.append('models')
from testing_models import *

# print(os.listdir('data/ithemal_inst_anchors'))
original_asm = []
block_id = []
num_insts = []
anchors = []
not_anchors = []
precision = []
coverage = []
my_time = []
anchors_uica = []
not_anchors_uica = []
precision_uica = []
coverage_uica = []
for file in os.listdir('data/uica_inst_anchors2'):
    fullfile = os.path.join('data/Ithemal_inst_anchors2', file)

    with open(fullfile, 'r') as f:
        my_output_str = f.read()

    original_idx = my_output_str.find('Original: ') + 10  # where the original asm starts
    original_idx_end = my_output_str.find('\n', original_idx)  # where the original asm ends
    original_asm.append(my_output_str[original_idx:original_idx_end].replace('; ', '\n'))
    block_id.append(int(file[:file.find('.txt')]))
    num_insts.append(len(my_output_str[original_idx:original_idx_end].strip().split('; ')))

    anchor_idx = my_output_str.find('Anchor: ', original_idx_end) + 8  # where the anchor starts
    anchor_idx_end = my_output_str.find('\n', anchor_idx)  # where the anchor ends
    anchors_out = my_output_str[anchor_idx:anchor_idx_end].split(' AND ')
    anchors_out.sort()
    anchors.append(anchors_out)
    all_possible = [f'inst_{x}' for x in range(num_insts[-1])]
    not_my_anchors = [x for x in all_possible if x not in anchors_out]
    not_anchors.append(not_my_anchors)

    precision_idx = my_output_str.find('Precision: ', anchor_idx_end) + 11  # where the precision starts
    precision_idx_end = my_output_str.find('\n', precision_idx)  # where the precision ends
    precision.append(float(my_output_str[precision_idx:precision_idx_end].strip()))

    coverage_idx = my_output_str.find('Coverage: ', precision_idx_end) + 10  # where the coverage starts
    coverage_idx_end = my_output_str.find('\n', coverage_idx)  # where the coverage ends
    coverage.append(float(my_output_str[coverage_idx:coverage_idx_end].strip()))

    my_time_idx = my_output_str.find('Total time taken ')
    my_time_idx = my_output_str.find(': ', my_time_idx) + 2  # where the my_time starts
    my_time_idx_end = my_output_str.find('\n', my_time_idx)  # where the my_time ends
    my_time.append(float(my_output_str[my_time_idx:my_time_idx_end].strip()))

    fullfile_uica = os.path.join('data/uica_inst_anchors2', file)

    with open(fullfile_uica, 'r') as f:
        my_output_str_uica = f.read()

    anchor_idx = my_output_str_uica.find('Anchor: ', original_idx_end) + 8  # where the anchor starts
    anchor_idx_end = my_output_str_uica.find('\n', anchor_idx)  # where the anchor ends
    anchors_out = my_output_str_uica[anchor_idx:anchor_idx_end].split(' AND ')
    anchors_out.sort()
    anchors_uica.append(anchors_out)
    all_possible = [f'inst_{x}' for x in range(num_insts[-1])]
    not_my_anchors = [x for x in all_possible if x not in anchors_out]
    not_anchors_uica.append(not_my_anchors)

    precision_idx = my_output_str_uica.find('Precision: ', anchor_idx_end) + 11  # where the precision starts
    precision_idx_end = my_output_str_uica.find('\n', precision_idx)  # where the precision ends
    precision_uica.append(float(my_output_str_uica[precision_idx:precision_idx_end].strip()))

    coverage_idx = my_output_str_uica.find('Coverage: ', precision_idx_end) + 10  # where the coverage starts
    coverage_idx_end = my_output_str_uica.find('\n', coverage_idx)  # where the coverage ends
    coverage_uica.append(float(my_output_str_uica[coverage_idx:coverage_idx_end].strip()))

ithemal_preds = testing_ithemal(original_asm)
uica_preds = testing_uica(original_asm)

df = pd.DataFrame(list(zip(original_asm, block_id, num_insts, anchors, not_anchors, precision, coverage, my_time, anchors_uica, not_anchors_uica, precision_uica, coverage_uica, ithemal_preds, uica_preds)), columns=['Code', 'MCA block id', 'Number of instructions', 'Anchors', 'Not anchors', 'Precision', 'Coverage', 'Time taken (Ithemal)', 'Anchors uiCA', 'Not anchors uiCA', 'Precision uiCA', 'Coverage uiCA', 'Ithemal prediction', 'uiCA prediction'])
df.sort_values('MCA block id', inplace=True)
df.to_csv('data/results/ithemal_instr_predicate_anchors2.csv', index = False)
