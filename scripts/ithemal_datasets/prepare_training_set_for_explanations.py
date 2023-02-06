import numpy as np
import pandas as pd
import multiprocessing as mp
import subprocess
import sys
sys.path.append('./models/Ithemal_gpu')
sys.path.append('./models')
from testing_models import testing_uica
from get_hex_gpu import get_hex_of_code_att

df_hsw = pd.read_csv('data/Ithemal_dataset/train_w_categories.csv').drop_duplicates()
df_cat = pd.read_csv('data/Ithemal_dataset/bhive_categories.csv', header=None, names=['hex', 'categories'])
#
# print(df_hsw.head())
print(df_hsw.shape)
# print(df_cat.head())
# print(df_hsw.columns)
# print(df_hsw.iloc[0]['hex'][2:-1])
# exit(0)
# compute the hex of the code of all the blocks and add a column of that
# def get_hex(i, aive):
#     if i%1000 == 0:
#         print(i)
#     hex = get_hex_of_code_att(df_hsw.iloc[i]['code'])
#     return hex, i
#
# pool = mp.Pool(mp.cpu_count()-1)
# results = pool.starmap_async(get_hex, [(i, 0) for i in range(df_hsw.shape[0])]).get()
# pool.close()
# pool.join()
# results.sort(key=lambda a: a[1])
# hex = []
# for i in range(df_hsw.shape[0]):
#     hex.append(results[i][0])
# df_hsw['hex'] = hex
# df_hsw.to_csv('data/Ithemal_dataset/train_w_categories.csv', index=None)
# do a disas of the hex and add intel code of all the blocks as another column
# def run_disasm(row, i):
#     output = subprocess.check_output(['python3', 'utils/disasm.py', row['hex'][2:-1], '--output-intel-syntax'], universal_newlines = True)
#     if i%1000 == 0:
#         print(i)
#     return i, output
#
#
# pool = mp.Pool(mp.cpu_count())
#
# results = pool.starmap_async(run_disasm, [(row, index) for index, row in df_hsw.iterrows()]).get()
#
# pool.close()
# pool.join()
#
# results.sort(key = lambda x: x[0])
# intels = [x[1] for x in results]
# print(len(intels))
# print(intels[0])
#
# df_hsw['intel_code'] = intels
# df_hsw.to_csv('data/Ithemal_dataset/train_w_categories.csv', index=None)

# correct hex of df
# df_hsw['hex'] = [df_hsw.iloc[i]['hex'][2:-1] for i in range(df_hsw.shape[0])]
# df_hsw.to_csv('data/Ithemal_dataset/train_w_categories.csv', index=None)
# exit(0)
# concatenate the categories column
# df_joined = df_hsw.join(df_cat.set_index('hex'), on='hex')
# print(df_joined.head())
# print(df_joined.shape)
# print(df_joined['categories'].value_counts())
# print(df_joined.isna().any(axis=1).sum())
# df_joined = df_joined[df_joined['categories'].notna()]
# print(df_joined.shape)
# # exit(0)
# df_joined.to_csv('data/Ithemal_dataset/train_w_categories.csv', index=None)

# add a bottlenecks column obtained from uiCA
# inputs = [df_hsw.iloc[i]['intel_code'] for i in range(df_hsw.shape[0])]
# # inputs_insts = [code.strip().splitlines() for code in inputs]
# inputs = ['.intel_syntax noprefix; ' + code for code in inputs]
# # inputs = [code.replace('\t', ' ') for code in inputs]
# bottlenecks = testing_uica(inputs, output_type='bottleneck')
# df_hsw['bottlenecks'] = bottlenecks
# df_hsw.to_csv('data/Ithemal_dataset/train_w_categories.csv', index=None)
#
#
# print(df_hsw['bottlenecks'].value_counts())

# ports_df = df_hsw[df_hsw['bottlenecks'] == "['Ports']"]
# # num_insts = [ports_df.iloc[i]['intel_code'].strip().splitlines()-1 for i in range(ports_df.shape[0])]
# ports_df_num_insts = ports_df.loc[ports_df.apply(lambda x: len(x['intel_code'].strip().splitlines())-1 in np.arange(4, 11), axis=1)]
# print(ports_df_num_insts['categories'].value_counts())
# print(ports_df_num_insts.iloc[0]['intel_code'])
# # will need to remove the Ld/St type blocks as they have less than 4 instructions
#
# ports_df_num_insts.to_csv('data/Ithemal_dataset/explanation_dataset.csv', index=None)

frontend_df = df_hsw[(df_hsw['bottlenecks'] == "['Predecoder']") | (df_hsw['bottlenecks'] == "['Decoder']")]  # front-end dataset
# num_insts = [ports_df.iloc[i]['intel_code'].strip().splitlines()-1 for i in range(ports_df.shape[0])]
print(frontend_df.shape)
frontend_df_num_insts = frontend_df.loc[frontend_df.apply(lambda x: len(x['intel_code'].strip().splitlines())-1 in np.arange(4, 11), axis=1)]
print(frontend_df_num_insts['categories'].value_counts())
print(frontend_df_num_insts.iloc[0]['intel_code'])
# will need to remove the Ld/St type blocks as they have less than 4 instructions

frontend_df_num_insts.to_csv('data/Ithemal_dataset/frontend_explanation_dataset.csv', index=None)

