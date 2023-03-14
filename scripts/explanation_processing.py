import pandas as pd
import os
import numpy as np


def cosine_similarity(a, b):
    return np.dot(a, b) / max((np.linalg.norm(a) * np.linalg.norm(b)), 1e-6)


def error_func(true, pred):  # absolute error
    true = round(true*2, 0)/2
    pred = round(pred*2, 0)/2
    return abs(true-pred)


def process_explanations(ITHEMAL_DIR, UICA_DIR):
    original_asm = []
    block_id = []
    num_insts = []
    anchors_ithemal = []
    precision_ithemal = []
    coverage_ithemal = []
    time_ithemal = []
    anchors_uica = []
    precision_uica = []
    coverage_uica = []
    similarity_uica_ithemal = []
    ithemal_error = []

    for file in os.listdir(ITHEMAL_DIR):
        fullfile = os.path.join(ITHEMAL_DIR, file)
        with open(fullfile, 'r') as f:
            my_output_str = f.read()
        original_idx = my_output_str.find('The basic block being explained is:\n') + 36  # where the original asm starts
        original_idx_end = my_output_str.find('\n', original_idx)  # where the original asm ends
        my_code = my_output_str[original_idx:original_idx_end]
        original_asm.append(my_code.replace('; ', '\n'))
        block_id.append(int(file[:file.find('.txt')]))
        print('block id: ', block_id[-1])
        num_insts.append(len(my_output_str[original_idx:original_idx_end].strip().split('; '))-1)  # removing the intel syntax directive's line

        anchor_idx = my_output_str.find('Anchor: ', original_idx_end) + 8  # where the anchor starts
        anchor_idx_end = my_output_str.find('\n', anchor_idx)  # where the anchor ends
        anchors_out = my_output_str[anchor_idx:anchor_idx_end].split(' AND ')
        idxs = np.zeros((num_insts[-1]))  # bit map of the anchors
        for anc in anchors_out:
            if anc != '':
                idxs[int(anc.strip().split('_', 1)[1])] = 1
        anchors_ithemal.append(idxs)

        precision_idx = my_output_str.find('Precision: ', anchor_idx_end) + 11  # where the precision starts
        precision_idx_end = my_output_str.find('\n', precision_idx)  # where the precision ends
        precision_ithemal.append(float(my_output_str[precision_idx:precision_idx_end].strip()))

        coverage_idx = my_output_str.find('Coverage: ', precision_idx_end) + 10  # where the coverage starts
        coverage_idx_end = my_output_str.find('\n', coverage_idx)  # where the coverage ends
        coverage_ithemal.append(float(my_output_str[coverage_idx:coverage_idx_end].strip()))

        my_time_idx = my_output_str.find('Total time taken ')
        my_time_idx = my_output_str.find(': ', my_time_idx) + 2  # where the my_time starts
        my_time_idx_end = my_output_str.find('\n', my_time_idx)  # where the my_time ends
        time_ithemal.append(float(my_output_str[my_time_idx:my_time_idx_end].strip()))

        fullfile_uica = os.path.join(UICA_DIR, file)

        with open(fullfile_uica, 'r') as f:
            my_output_str_uica = f.read()

        anchor_idx = my_output_str_uica.find('Anchor: ', original_idx_end) + 8  # where the anchor starts
        anchor_idx_end = my_output_str_uica.find('\n', anchor_idx)  # where the anchor ends
        anchors_out_uica = my_output_str_uica[anchor_idx:anchor_idx_end].split(' AND ')
        uica_idxs = np.zeros((num_insts[-1]))  # bit map of the anchors
        for anc in anchors_out_uica:
            if anc != '':
                uica_idxs[int(anc.strip().split('_', 1)[1])] = 1
        anchors_uica.append(uica_idxs)

        precision_idx = my_output_str_uica.find('Precision: ', anchor_idx_end) + 11  # where the precision starts
        precision_idx_end = my_output_str_uica.find('\n', precision_idx)  # where the precision ends
        precision_uica.append(float(my_output_str_uica[precision_idx:precision_idx_end].strip()))

        coverage_idx = my_output_str_uica.find('Coverage: ', precision_idx_end) + 10  # where the coverage starts
        coverage_idx_end = my_output_str_uica.find('\n', coverage_idx)  # where the coverage ends
        coverage_uica.append(float(my_output_str_uica[coverage_idx:coverage_idx_end].strip()))

        similarity_uica_ithemal.append(cosine_similarity(anchors_uica[-1], anchors_ithemal[-1]))  # between uica and ithemal anchors

    ithemal_preds = testing_ithemal_gpu(original_asm)
    uica_preds = testing_uica(original_asm)

    ithemal_error = [error_func(uica_preds[i], ithemal_preds[i]) for i in range(len(actual_tp))]

    df = pd.DataFrame(list(zip(original_asm, block_id, num_insts, anchors_ithemal, precision_ithemal, coverage_ithemal, time_ithemal, anchors_uica, precision_uica, coverage_uica, similarity_uica_ithemal, ithemal_preds, ithemal_error, uica_preds)), columns=['Code', 'MCA block id', 'Number of instructions', 'Anchors', 'Precision', 'Coverage', 'Time taken (Ithemal)', 'Anchors uiCA', 'Precision uiCA', 'Coverage uiCA', 'Similarity bw uica, ithemal anchors', 'Ithemal prediction', 'Ithemal error', 'uiCA prediction'])
    df.sort_values('MCA block id', inplace=True)
    df.to_csv('data/results/paper_results/ablation/instr_predicate_anchor_port_bound_only_deletion.csv', index = False)
