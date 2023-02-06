import json

with open('utils/operand_dict.py', 'r') as f:
    operand_dict = json.load(f)

with open('data/Ithemal_dataset/intel_supported_opcodes.txt', 'r') as f:
    intel_opcodes_str = f.read()
    intel_opcodes = intel_opcodes_str.splitlines()

for opnd in operand_dict.keys():
    opc_list = operand_dict[opnd]
    for op in opc_list:
        if op not in intel_opcodes:
            print(op)
