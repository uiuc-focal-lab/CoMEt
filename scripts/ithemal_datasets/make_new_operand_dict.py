import sys
# sys.path.append('utils/')
sys.path.append('instrData/')
from HSW_data import *
import json

instData = instrData  # this is the haswell dictionary

inst_strings = []

for v in instData.values():
    for my_item in v:  # v is a list containing the instruction details
        inst_strings.append(my_item['string'])

operands_dict_new = {}

with open('data/Ithemal_dataset/intel_supported_opcodes.txt', 'r') as f:
    opcodes_str = f.read()
    intel_supported_opcodes = opcodes_str.splitlines()
    intel_supported_opcodes = [x.strip() for x in intel_supported_opcodes if x.strip() != '']

with open('utils/invalid_opcodes', 'r') as f:
    invalids = f.read()
    invalid_opcodes = invalids.splitlines()
    invalid_opcodes = [x.strip() for x in invalid_opcodes if x.strip() != '']

supported_opcodes = [x for x in intel_supported_opcodes if x not in invalid_opcodes]
all_added_opcodes = []

for s in inst_strings:
    parts = s.split(' (')
    opcode = parts[0].strip()
    if '_' in opcode:
        opcode = opcode.split('_', 1)[0]
    if len(parts) == 1:  # no operand
        operands = ''
    else:
        operands = parts[1][:-1].strip()  # removed the closing parenthesis ')'
    if operands in operands_dict_new.keys():
        if opcode not in operands_dict_new[operands] and opcode in supported_opcodes:
            operands_dict_new[operands].append(opcode)
            all_added_opcodes.append(opcode)
    else:  # this operand is seen for first time
        if opcode in supported_opcodes:
            operands_dict_new[operands] = [opcode]
            all_added_opcodes.append(opcode)

for opc in supported_opcodes:
    if opc not in all_added_opcodes:
        print(opc)

with open('utils/operand_dict.py', 'w') as f:
    json.dump(operands_dict_new, f)
