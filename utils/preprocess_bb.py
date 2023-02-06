import tempfile
import subprocess

def preprocess_my_code(code):
    # bring to intel syntax by compiling and then disassembling
    _, my_code_file = tempfile.mkstemp()
    _, my_bin_file = tempfile.mkstemp()
    with open(my_code_file, 'w') as fp:
        fp.write(code)

    subprocess.run(['as', my_code_file, '-o', my_bin_file])

