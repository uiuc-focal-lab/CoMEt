import pandas as pd
from sklearn import metrics
import sys
import multiprocessing as mp
sys.path.append('models/')
sys.path.append('.')
from basic_block import *
from statistics import mean

# from testing_models import *

df_hsw = pd.read_csv('data/Ithemal_dataset/hsw_w_categories.csv')
print(df_hsw.head())


# mape_ithemal = [metrics.mean_absolute_percentage_error([df_hsw.iloc[i]['throughput']], [df_hsw.iloc[i]['ithemal_result']]) if df_hsw.iloc[i]['ithemal_result'] != -1 else -1 for i in range(df_hsw.shape[0])]
filtered_mape = [df_hsw.iloc[i]['ithemal_mape'] for i in range(df_hsw.shape[0]) if df_hsw.iloc[i]['ithemal_result'] != -1]
print(mean(filtered_mape))
#
# df_hsw.to_csv('data/Ithemal_dataset/hsw_w_categories.csv', index=False)

# high_error_idx = df_hsw[df_hsw['ithemal_mape'] <= 0.05]
#
# print(high_error_idx.shape[0])

# print(high_error_idx.idxmax())

# asm = df_hsw.iloc[77745]['asm']
# asm = asm.replace('\n', '; ')
# asm = asm.replace('\t', ' ')
# print(asm)
#
# print(df_hsw.iloc[5082]['asm'])
#
#
# print(df_hsw.iloc[77745]['hex'])

# add number of memory reads and memory writes for entire dataset
# num_insts = []
# num_mem_writes = []
# num_mem_reads = []
#
#
# def bb_process(i, awe):
#     if i % 1000 == 0:
#         print(f'reached {i}')
#     code = df_hsw.iloc[i]['asm']
#     my_insts = code.splitlines()
#     # if '.text' in my_insts[0]:
#     #     my_insts = my_insts[1:]
#     my_insts = [ins.strip() for ins in my_insts if ins.strip() != '']
#     code = '; '.join(my_insts)
#     code = code.replace('\t', ' ')
#     # print(code)
#     bb = BasicBlock('.intel_syntax noprefix; ' + code + '\n', 'instruction',
#                     None)  # predicate type and classifier function are just placeholders
#     my_mem_reads = 0
#     my_mem_writes = 0
#     for inst in bb.instructions:
#         # make the rw pools
#         # print('instruction:', inst.get_original_asm())
#         inst.make_rw_pools()
#         read_pool = inst.get_read_pool()
#         write_pool = inst.get_write_pool()
#         for opnd in read_pool.keys():
#             if '[' in opnd:  # memory opnd
#                 my_mem_reads += 1
#         for opnd in write_pool.keys():
#             if '[' in opnd:  # memory opnd
#                 my_mem_writes += 1
#     my_num_insts = len(bb.instructions)
#     return my_num_insts, my_mem_reads, my_mem_writes, i
#
#
# pool = mp.Pool(mp.cpu_count()-1)
# results = pool.starmap_async(bb_process, [(k, 0) for k in range(df_hsw.shape[0])]).get()
# pool.close()
# pool.join()
# results.sort(key=lambda a: a[3])
# for res in results:
#     num_insts.append(res[0])
#     num_mem_reads.append(res[1])
#     num_mem_writes.append(res[2])
#     # print('code:', code)
#     # print('insts:', num_insts[-1])
#     # print('mem reads:', num_mem_reads[-1])
#     # print('mem writes:', num_mem_writes[-1])
# df_hsw['num_insts'] = num_insts
# df_hsw['num_mem_reads'] = num_mem_reads
# df_hsw['num_mem_writes'] = num_mem_writes
# df_hsw.to_csv('data/Ithemal_dataset/hsw_w_categories.csv', index=False)
#
# baseline_tp = [max(num_insts[i]/4, num_mem_reads[i]/2, num_mem_writes[i]) for i in range(len(num_insts))]
# # print('baseline tp:', baseline_tp)
# df_hsw['baseline_tp'] = baseline_tp
#
# df_hsw.to_csv('data/Ithemal_dataset/hsw_w_categories.csv', index=False)

# baseline_mape = [metrics.mean_absolute_percentage_error([df_hsw.iloc[i]['throughput']/100], [df_hsw.iloc[i]['baseline_tp']]) for i in range(df_hsw.shape[0])]
#
# df_hsw['baseline_mape'] = baseline_mape
#
# df_hsw.to_csv('data/Ithemal_dataset/hsw_w_categories.csv', index=False)
# print(mean(baseline_mape))
