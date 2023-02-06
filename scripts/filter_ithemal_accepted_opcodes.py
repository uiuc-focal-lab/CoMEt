# run this from within code_predicates/
import copy
import sys
sys.path.append('utils/')
sys.path.append('.')
import xed
from microArchConfigs import MicroArchConfigs
import instrData.HSW_data as archData
import json
import pandas as pd
import subprocess
import argparse
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('block_num', type=int)
    args = parser.parse_args()
    blocks = pd.read_csv('data/Ithemal_dataset/hsw_w_categories.csv')

    with open('utils/operand_dict.py', 'r') as f:
        operands_dict = json.load(f)

    print("block id:", args.block_num)
    code = blocks.iloc[args.block_num]['asm']
    code = code.replace('\t', ' ')
    insts = code.splitlines()
    if '.text' in insts[0]:  # remove the .text directive from the code
        insts = insts[1:]

    # remove comments from the code
    for i in range(len(insts)):
        hash_pos = insts[i].find('#')
        if hash_pos == -1:  # not here!
            continue
        insts[i] = insts[i][:hash_pos]

    insts = [x for x in insts if x != '']

    code = '; '.join(insts)

    print("code:", code)
    with open('data/test.asm', 'w') as f:
        f.write('.intel_syntax noprefix; ' + code)
    subprocess.run(['as', 'data/test.asm', '-o', 'data/test.o'])
    disas = xed.disasFile('data/test.o', chip=MicroArchConfigs['HSW'].XEDName)

    for i in range(len(disas)):  # considering the disas object as it will have all the directives removed
        if disas[i]['iclass'] == 'NOP':
            disas[i]['asm'] = disas[i]['asm'].split(', ', 1)[0]
    invalid_tokens = []
    for inst_num, instrD in enumerate(disas):
        # print(inst_num)
        for instrData in archData.instrData.get(instrD['iform'], []):
             if xed.matchXMLAttributes(instrD, archData.attrData[instrData['attr']]):
                 if ' (' in instrData['string']:
                    operands = instrData['string'][instrData['string'].find(' (')+2:instrData['string'].find(')')]
                 else:
                    operands = ''
                 # print("instruction assembly:", instrD['asm'])
                 # print("iform", instrD['iform'])
                 # print("operands: ", operands)
                 substitutes = []
                 if operands in operands_dict.keys():
                    substitutes = copy.deepcopy(operands_dict[operands])
                 if instrD['iclass'] in substitutes:
                    substitutes.remove(instrD['iclass'])
                 if instrD['iclass'] == 'LEA': # lea is very special
                     substitutes = ['LEA']
                 if instrD['iclass'] == 'NOP':  # NOP is also very special as it may become widenop and start having two operands
                     instrD['asm'] = instrD['asm'].split(', ', 1)[0]
                 for s in substitutes:
                     perturbed_inst = ' '.join([s.split('_', 1)[0], instrD['asm'].split(' ', 1)[-1]])
                     perturbed_code = ''
                     for inst_num_h, instrD_h in enumerate(disas):
                         if inst_num_h == inst_num:
                             perturbed_code = '; '.join([perturbed_code, perturbed_inst])
                         else:
                             perturbed_code = '; '.join([perturbed_code, instrD_h['asm']])
                     try:
                        output = float(subprocess.check_output(['docker', 'exec', '--env-file', '../ithemal/Ithemal/.env', 'ithemal', 'python', 'ithemal/learning/pytorch/ithemal/predict.py', '--model', 'ithemal/Ithemal-models/bhive/hsw.dump', '--model-data', 'ithemal/Ithemal-models/bhive/hsw.mdl', '--inputs', '.intel_syntax noprefix; '+perturbed_code], universal_newlines=True, stderr=subprocess.DEVNULL))
                     except:
                         print('except', perturbed_code)
                         invalid_tokens.append(s)
                         operands_dict[operands].remove(s)
                 break

    with open('utils/invalid_opcodes', 'a') as f:
        for opcs in invalid_tokens:
            f.write(opcs + '\n')

    # print(operands_dict)

if __name__ == '__main__':
    main()
