# run from code_predicates/

import argparse
import json

# get the invalid opcodes list file as input and read it

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('invalid_opcodes_file', type=str)
    parser.add_argument('operand_dict_dest_file', type=str)
    args = parser.parse_args()

    with open(args.invalid_opcodes_file, 'r') as f:
        invalid_str = f.read()

    invalid_opcodes = [x.strip() for x in invalid_str.splitlines()]

    # print(invalid_opcodes)
    # exit(0)
    with open('utils/operand_dict.py', 'r') as f:
        operand_dict = json.load(f)

    for k in operand_dict.keys():
        my_opnds = operand_dict[k]
        my_opnds = [op for op in my_opnds if op not in invalid_opcodes]
        operand_dict[k] = my_opnds

    with open(args.operand_dict_dest_file, 'w') as f:
        json.dump(operand_dict, f)

if __name__ == '__main__':
    main()
