import numpy as np
import pandas as pd
import subprocess

df = pd.read_csv('data/results/ithemal_instr_predicate_anchors2.csv')

# print(df.head())
code = []
ithemal_anchors = []
uica_anchors = []
uica_ground_truth = []
cosine_sim = []
cosine_sim_ithemal = []

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

for i in range(df.shape[0]):
    # we will get explanations for each of the code instances and create a new dataframe out of ground truth and anchor explanations
    my_code = df.iloc[i]['Code']
    insts = my_code.splitlines()
    my_code = '; '.join(insts)
    my_code = my_code.replace('\t', ' ').strip()
    code.append(df.iloc[i]['Code'])

    anchor = df.iloc[i]['Anchors uiCA'][1:-1].split(', ')
    idxs = np.zeros((len(insts)))  # bit map of the anchors
    # print(idxs, anchor)
    for anc in anchor:
        # print(anc.strip().split('_', 1)[1][:-1])
        idxs[int(anc.strip().split('_', 1)[1][:-1])] = 1
    uica_anchors.append(list(idxs))
    # print(idxs)

    ith_anchor = df.iloc[i]['Anchors'][1:-1].split(', ')
    ith_idxs = np.zeros((len(insts)))  # bit map of the anchors
    # print(idxs, anchor)
    for anc in ith_anchor:
        # print(anc.strip().split('_', 1)[1][:-1])
        ith_idxs[int(anc.strip().split('_', 1)[1][:-1])] = 1
    ithemal_anchors.append(list(ith_idxs))

    # computing ground truth explanations
    with open('data/scratch/test.asm', 'w') as f:
        f.write('.intel_syntax noprefix; ' + my_code + '\n')
    subprocess.run(['as', 'data/scratch/test.asm', '-o', 'data/scratch/test.o'])
    output = subprocess.check_output(['./uiCA_exp.py', '../data/scratch/test.o', '-arch', 'HSW', '-TPonly'],
                                     universal_newlines=True, stderr=subprocess.DEVNULL,
                                     cwd='/home/isha/Documents/cost_model_exp/code_predicates/models')

    exp_start_idx = output.find('Explanation: ')
    exp_end_idx = output.find(']', exp_start_idx)
    exps = output[exp_start_idx: exp_end_idx].split(': [', 1)[1].split()
    exp_list = [round(float(e.strip()), 2) for e in exps]
    # print(exp_list)
    uica_ground_truth.append(exp_list)

    cosine_sim.append(cosine_similarity(uica_anchors[-1], uica_ground_truth[-1]))

    cosine_sim_ithemal.append(cosine_similarity(uica_anchors[-1], ithemal_anchors[-1]))

df_res = pd.DataFrame(list(zip(code, ithemal_anchors, uica_anchors, uica_ground_truth, cosine_sim, cosine_sim_ithemal)), columns=['Code', 'Ithemal anchors', 'uiCA Anchors', 'Ground Truth', 'similarity bw uica anchor, gt', 'similarity bw uica anchor, ithemal'])
df_res.to_csv('data/results/uica_ground_truth.csv', index=False)




