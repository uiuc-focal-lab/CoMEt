import subprocess
import pandas as pd
import sys
import argparse
sys.path.append('data/test_data/backend_explanation_files/')  # adding path for backend explanation folder
sys.path.append('data/test_data/frontend_explanation_files/')  # adding path for frontend explanation folder


def run_expts(BASE_FOLDER, explanation_blocks_path):
    blocks = pd.read_csv(explanation_blocks_path)
    type_count = {'Scalar': 0, 'Vec': 0, 'Scalar/Vec': 0, 'Ld': 0, 'St': 0, 'Ld/St': 0}
    for i in range(0, blocks.shape[0]):
        code = blocks.iloc[i]['intel_code']
        category = blocks.iloc[i]['categories']
        if type_count[category] >= 45:  # executed more than 45 basic blocks of same type
            continue
        try:
            print("Trying block", i)
            print("code:", code)
            print("category:", category)
            my_output_ithemal = subprocess.check_output(['python3', 'explainOneBasicBlock.py', code, 'instruction', 'ithemal'], universal_newlines=True)
            print('Ithemal done')
            my_output_uica = subprocess.check_output(['python3', 'explainOneBasicBlock.py', code, 'instruction', 'uica'], universal_newlines=True)
            print('uica done')
            category_folder = category.replace('/', '')
            with open(f'{BASE_FOLDER}/Ithemal/{category_folder}/{i}.txt', 'w') as f:
                f.write(my_output_ithemal)
            with open(f'{BASE_FOLDER}/uica/{category_folder}/{i}.txt', 'w') as f:
                f.write(my_output_uica)
            type_count[category] += 1
            print(type_count)
        except Exception as err:
            print("exception for block", i)
            print(err)
            print('Current status of computation')
            print(type_count)
            continue

        if all(ele >= 45 for ele in type_count.values()):
            break

def main():
    parser = argparse.ArgumentParser(description='Generate the files for the experiments in the paper')
    parser.add_argument('bottleneck_type', choices=['backend', 'frontend', 'all'])
    args = parser.parse_args()

    backend = False
    frontend = False

    if args.bottleneck_type == 'backend':
        backend = True
    elif args.bottleneck_type == 'frontend':
        frontend = True
    else:
        backend = True
        frontend = True

    if backend:
        print('Computing explanations for backend bound blocks')
        run_expts('data/test_data/backend_explanation_files/', 'data/datasets/backend_bound_blocks_dataset.csv')
    if frontend:
        print('Computing explanations for frontend bound blocks')
        run_expts('data/test_data/frontend_explanation_files/', 'data/datasets/frontend_bound_blocks_dataset.csv')


if __name__ == '__main__':
    main()
