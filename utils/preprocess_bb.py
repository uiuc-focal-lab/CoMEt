import tempfile
import subprocess
import binascii

def preprocess_my_code(code):
    # bring to intel syntax by compiling and then disassembling
    _, my_code_file = tempfile.mkstemp()
    _, my_bin_file = tempfile.mkstemp()
    with open(my_code_file, 'w') as fp:
        fp.write(code)
    # this will create binary of the code in any format
    subprocess.run(['as', my_code_file, '-o', my_bin_file])
    # now the code in binary needs to be converted to its hex for the disassembler
    with open(my_bin_file, 'r') as fp:
        block_binary = fp.read()
    block_hex = binascii.b2a_hex(block_binary)

    # disassemble the block_hex using disasm.py
    asm_code = subprocess.check_output(['python3', 'disasm.py', block_hex, '--output-intel-syntax'], universal_newlines=True)

    # remove tabs
    asm_code = asm_code.replace('\t', ' ')

    # remove any comments in the intel code
    insts = asm_code.splitlines()
    if '.text' in insts[0]:  # remove the .text directive from the code
        insts = insts[1:]
    for ins in range(len(insts)):
        hash_pos = insts[ins].find('#')
        if hash_pos == -1:  # not here!
            continue
        insts[ins] = insts[ins][:hash_pos]

    insts = [x for x in insts if x != '']
    asm_code = '; '.join(insts)

    # add the .intel_syntax noprefix directive to the new code
    asm_code = '.intel_syntax noprefix; ' + asm_code

    # return the code in the transformed state
    return asm_code
