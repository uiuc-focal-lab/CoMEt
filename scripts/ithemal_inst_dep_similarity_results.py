import pandas as pd
import os
import subprocess
import numpy as np
import sys
sys.path.append('models')
sys.path.append('.')
from testing_models import *
import basic_block


def cosine_similarity(a, b):
    return np.dot(a, b) / max((np.linalg.norm(a) * np.linalg.norm(b)), 1e-6)

def containership_similarity(a, b):  # a contained within b
    if set(a).issubset(set(b)):
        return 1
    elif set(b).issubset(set(a)):
        return -1
    return 0

def ape(true, pred):  # absolute percentage error: true value = a, prediction = b
    return abs(true-pred)/max(true, 1e-6)

# print(os.listdir('data/ithemal_inst_anchors'))
original_asm = []
block_category = []
block_id = []
num_insts = []
all_predicates = []
anchors = []
precision = []
coverage = []
my_time = []
anchors_uica = []
precision_uica = []
coverage_uica = []
similarity_uica_ithemal = []
# ground_truth_exp = []
# similarity_gt_uica = []
similarity_uica_ithemal_containership = []
num_perturbations = []
actual_tp = []
ithemal_error = []
# ithemal_preds
# uica_preds
ITHEMAL_DIR = 'data/results_inst_dep_combined/Ithemal'
UICA_DIR = 'data/results_inst_dep_combined/uica'

directories = os.listdir(ITHEMAL_DIR)
directories = [d for d in directories if os.path.isdir(os.path.join(ITHEMAL_DIR, d))]  # just pull out the subdirectories
if '__pycache__' in directories:
    directories.remove('__pycache__')
print(directories)

df_hsw = pd.read_csv('data/Ithemal_dataset/hsw_w_categories.csv')

for dir in directories:
    for file in os.listdir(os.path.join(ITHEMAL_DIR, dir)):
        fullfile = os.path.join(ITHEMAL_DIR, dir, file)

        with open(fullfile, 'r') as f:
            my_output_str = f.read()

        original_idx = my_output_str.find('Code:\n') + 6  # where the original asm starts
        original_idx_end = my_output_str.find('\n', original_idx)  # where the original asm ends
        my_code = my_output_str[original_idx:original_idx_end]
        original_asm.append(my_code.replace('; ', '\n'))
        block_category.append(dir)  # dir name is category name
        block_id.append(int(file[:file.find('.txt')]))
        num_insts.append(len(my_output_str[original_idx:original_idx_end].strip().split('; ')))

        actual_tp.append(df_hsw.iloc[block_id[-1]]['throughput'])

        # all the predicates used to explain
        predicates_start = my_output_str.find('All predicates to explain with:  [')
        predicates_start = my_output_str.find('[', predicates_start) + 1
        predicates_end = my_output_str.find(']', predicates_start)
        predicates = my_output_str[predicates_start:predicates_end]
        predicates_list = predicates.split(', ')
        predicates_list = [predic[1:-1] for predic in predicates_list]  # to remove the quotation marks
        # print(predicates_list)
        # exit(0)
        all_predicates.append(predicates_list)

        anchor_idx = my_output_str.find('Anchor: ', original_idx_end) + 8  # where the anchor starts
        anchor_idx_end = my_output_str.find('\n', anchor_idx)  # where the anchor ends
        anchors_out = my_output_str[anchor_idx:anchor_idx_end].split(' AND ')
        anchors_out = [anc for anc in anchors_out if anc != '']
        # anchors_out.sort()
        idxs = np.zeros((len(predicates_list)))  # bit map of the anchors
        # print(idxs, anchor)
        for anc in anchors_out:
            # print(anc.strip().split('_', 1)[1][:-1])
            # print(anc)
            # try:
            idxs[predicates_list.index(anc)] = 1
            # except:
            #     print("anc", anc, 'anchor out', anchors_out)
            #     exit(1)
        anchors.append(idxs)

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

        fullfile_uica = os.path.join(UICA_DIR, dir, file)

        with open(fullfile_uica, 'r') as f:
            my_output_str_uica = f.read()

        anchor_idx = my_output_str_uica.find('Anchor: ', original_idx_end) + 8  # where the anchor starts
        anchor_idx_end = my_output_str_uica.find('\n', anchor_idx)  # where the anchor ends
        anchors_out_uica = my_output_str_uica[anchor_idx:anchor_idx_end].split(' AND ')
        anchors_out_uica = [anc for anc in anchors_out_uica if anc != '']
        # anchors_out.sort()
        uica_idxs = np.zeros((len(predicates_list)))  # bit map of the anchors
        # print(idxs, anchor)
        for anc in anchors_out_uica:
            # print(anc.strip().split('_', 1)[1][:-1])
            uica_idxs[predicates_list.index(anc)] = 1
        anchors_uica.append(uica_idxs)
        # anchors_uica.append(anchors_out)

        precision_idx = my_output_str_uica.find('Precision: ', anchor_idx_end) + 11  # where the precision starts
        precision_idx_end = my_output_str_uica.find('\n', precision_idx)  # where the precision ends
        precision_uica.append(float(my_output_str_uica[precision_idx:precision_idx_end].strip()))

        coverage_idx = my_output_str_uica.find('Coverage: ', precision_idx_end) + 10  # where the coverage starts
        coverage_idx_end = my_output_str_uica.find('\n', coverage_idx)  # where the coverage ends
        coverage_uica.append(float(my_output_str_uica[coverage_idx:coverage_idx_end].strip()))

        # print(anchors_uica[-1], anchors[-1])
        similarity_uica_ithemal.append(cosine_similarity(anchors_uica[-1], anchors[-1]))  # between uica and ithemal anchors
        # print('now gt')
        # compute ground truth explanation
        # with open('data/scratch/test.asm', 'w') as f:
        #     f.write('.intel_syntax noprefix; ' + my_code + '\n')
        # subprocess.run(['as', 'data/scratch/test.asm', '-o', 'data/scratch/test.o'])
        # output = subprocess.check_output(['./uiCA_exp.py', '../data/scratch/test.o', '-arch', 'HSW', '-TPonly'],
        #                                  universal_newlines=True, stderr=subprocess.DEVNULL,
        #                                  cwd='/home/isha/Documents/cost_model_exp/code_predicates/models')
        #
        # exp_start_idx = output.find('Explanation: ')
        # exp_end_idx = output.find(']', exp_start_idx)
        # gt_exps = output[exp_start_idx: exp_end_idx].split(': [', 1)[1].split()
        # gt_exp_list = [round(float(e.strip()), 2) for e in gt_exps]
        # # print(exp_list)
        # ground_truth_exp.append(gt_exp_list)
        # print('done gt')

        # ground truth similarity
        # similarity_gt_uica.append(cosine_similarity(anchors_uica[-1], ground_truth_exp[-1]))  # between uica anchors and ground truth explanations

        # containership similarity between anchors_out and anchors_out_uica
        similarity_uica_ithemal_containership.append(containership_similarity(anchors_out, anchors_out_uica))
        # print('computing num_perturbations')

        bb = basic_block.BasicBlock('.intel_syntax noprefix; '+my_code+'\n', 'instruction', testing_uica)
        num_perturbations.append(bb.get_num_perturbations())

ithemal_preds = testing_ithemal_gpu(original_asm)
uica_preds = testing_uica(original_asm)

ithemal_error = [ape(uica_preds[i], ithemal_preds[i]/100) for i in range(len(actual_tp))]

df = pd.DataFrame(list(zip(original_asm, block_category, block_id, num_insts, all_predicates, anchors, precision, coverage, my_time, anchors_uica, precision_uica, coverage_uica, similarity_uica_ithemal, similarity_uica_ithemal_containership, num_perturbations, actual_tp, ithemal_preds, ithemal_error, uica_preds)), columns=['Code', 'Category', 'MCA block id', 'Number of instructions', 'All predicates', 'Anchors', 'Precision', 'Coverage', 'Time taken (Ithemal)', 'Anchors uiCA', 'Precision uiCA', 'Coverage uiCA', 'Similarity bw uica, ithemal anchors', 'containership similarity bw ithemal, uica anchors', 'Number of perturbations', 'Actual TP', 'Ithemal prediction', 'Ithemal error', 'uiCA prediction'])
df.sort_values('MCA block id', inplace=True)
df.to_csv('data/results/ithemal_instr_dep_predicate_anchor_similarity_new.csv', index = False)
