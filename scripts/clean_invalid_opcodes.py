with open('utils/invalid_opcodes', 'r') as f:
    invalid_str = f.read()
    invalid_list = invalid_str.splitlines()

invalid_list = [inv.strip() for inv in invalid_list if inv.strip() != '']

invalid_list = list(set(invalid_list))

with open('utils/invalid_opcodes1', 'w') as f:
    for inv in invalid_list:
        f.write(inv + '\n')
