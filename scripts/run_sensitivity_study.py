import pandas as pd
import os
import subprocess
import sys
sys.path.append('models/')
from testing_models import testing_ithemal_gpu

BASE_PATH='data/sensitivity_analysis'

def process_code(code):
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
    code = '; '.join(insts)
    code = code.replace('\t', ' ')
    return code

# combine the explanation and the frontend explanation dataset
# df_backend = pd.read_csv('data/Ithemal_dataset/explanation_dataset.csv')
# # filter out those blocks which are in the ports_explanations/ folder
# ports_path = 'data/ports_explanations/Ithemal'
# backend_filter_list = []
# for dir in os.listdir(ports_path):  # all the directories
#     dir_path = os.path.join(ports_path, dir)
#     for file in os.listdir(dir_path):
#         backend_filter_list.append(int(file.split('.')[0]))
# # print('backend list:', backend_filter_list)
# df_backend_filtered = df_backend.iloc[backend_filter_list]
# df_frontend = pd.read_csv('data/Ithemal_dataset/frontend_explanation_dataset.csv')
# frontend_path = 'data/frontend_explanations/Ithemal'
# frontend_filter_list = []
# for dir in os.listdir(frontend_path):  # all the directories
#     dir_path = os.path.join(frontend_path, dir)
#     for file in os.listdir(dir_path):
#         frontend_filter_list.append(int(file.split('.')[0]))
# df_frontend_filtered = df_frontend.iloc[frontend_filter_list]
# df_combined = pd.concat([df_backend_filtered, df_frontend_filtered])
# print(df_combined.head())

# pick out 100 random samples from that dataset, which have error = 0
def ape(true, pred):  # absolute percentage error: true value = a, prediction = b
    true = round(true*2, 0)/2
    pred = round(pred*2, 0)/2
    return abs(true-pred)  #/max(true, 1e-6)
# get ithemal_preds

# my_inputs = []
# for i in range(df_combined.shape[0]):
#     my_code = df_combined.iloc[i]['intel_code']
#     my_inputs.append(process_code(my_code))
#
# print('processed code')
# print(df_combined.shape)
#
# ithemal_preds = testing_ithemal_gpu(my_inputs)
# print('ithemal done')
# # get uica_preds
# uica_preds = df_combined['uiCA'].to_list()
# uica_preds = [x/100 for x in uica_preds]
# # get error between them
# error_u_i = []
# for idx in range(len(ithemal_preds)):
#     error_u_i.append(ape(uica_preds[idx], ithemal_preds[idx]))
# print('error done')
# # print('error:', error_u_i)
# # make df with only 0 error
# df_combined['error_u_i'] = error_u_i
# df_combined['ithemal_preds'] = ithemal_preds
# df_error_0 = df_combined.loc[df_combined['error_u_i'] == 0.0]
# # pick a random sample of 100 points from that df
# df_sensitivity = df_error_0.sample(n=101, random_state=0)
# print(df_sensitivity.head())
# print(df_error_0.shape)
# df_sensitivity.to_csv('data/Ithemal_dataset/sensitivity_dataset.csv', index=False)

# take the code from the dataframe and put it as a list statically
df_sensitivity = pd.read_csv('data/Ithemal_dataset/sensitivity_dataset.csv')
print(df_sensitivity.head())
code_list = []

for i in range(df_sensitivity.shape[0]):
    code_list.append(process_code(df_sensitivity.iloc[i]['intel_code']))

# fix the perturbation model probability to 0.5 and vary the precision thresholds in your range and run for the 100 samples
threshold_vals = [0.82]  #[0.85, 0.90, 0.95]  # [0.75, 0.80, 0.82]
perturbation_probability = [0.3, 0.7]

# make the directories for the threshold_vals values
for thresh in threshold_vals:
    for prob in perturbation_probability:
        print('trying threshold:', thresh, 'with probability:', prob)
        path_ithemal = os.path.join(BASE_PATH, 'Ithemal', str(thresh)+'_'+str(prob))
        if not os.path.exists(path_ithemal):
            # make this directory
            os.makedirs(path_ithemal)
        path_uica = os.path.join(BASE_PATH, 'uica', str(thresh)+'_'+str(prob))
        if not os.path.exists(path_uica):
            os.makedirs(path_uica)

        # run the whole sensitivity dataframe with the params
        for i in range(len(code_list)):
            code = code_list[i]
            try:
                print("Trying block", i)
                print("code:", code)

                my_output_ithemal = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'instruction', 'ithemal', str(thresh), str(prob)], universal_newlines=True)
                print('Ithemal done')
                # my_output_uica = subprocess.check_output(['python3', 'bb_explain.py', '.intel_syntax noprefix; '+code+'\n', 'instruction', 'uica', str(thresh), str(prob)], universal_newlines=True)
                # print('uica done')
                with open(f'{path_ithemal}/{i}.txt', 'w') as f:
                    f.write(my_output_ithemal)
                # with open(f'{path_uica}/{i}.txt', 'w') as f:
                #     f.write(my_output_uica)
            except Exception as err:
                print(f"exception for block number {i}")
                print(err)
                continue

# for the best precision threshold, run the expt with varying perturbation probability parameters for the 100 samples

