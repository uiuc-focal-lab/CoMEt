import sys
sys.path.append('./anchor')
import argparse
import anchor_code
sys.path.append('utils')
import settings
from preprocess_bb import *
sys.path.append('models')
from testing_models import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("code", type=str, help='code for input x86 assembly basic block')
    parser.add_argument("cost_model", type=str, help='cost model whose throughput predictions are to be explained')
    parser.add_argument("precision_threshold", type=float, help='precision threshold for the Anchors algorithm (default=0.82)')
    parser.add_argument("perturbation_probability", type=float, help='probability parameter in perturbation model (default=0.5)')
    parser.add_argument('-token', action='store_true', help='give explanations with token-level predicates')
    args = parser.parse_args()

    predicate_type = 'instruction'
    if args.token:
        predicate_type = 'token'
    settings.init()
    code_text = args.code
    print("The code to explain is:\n{}".format(code_text))

    # preprocess code to send to explain


    if args.testing_model == 'ithemal':
        my_model = testing_ithemal_gpu
        print("Testing Ithemal")
    elif args.testing_model == 'uica':
        my_model = testing_uica
        print("Testing uiCA")
    else:
        raise("model type not recognized!")

    explainer = anchor_code.AnchorCode(None, ['far', 'close'], use_unk_distribution=False)  # 0: far; 1: close (to original input)
    pred = 'close'
    pred_num = my_model(code_text)
    print("Code:\n"+code_text)
    print('Prediction: %s' % pred_num)
    alternative = 'far'

    exps = explainer.explain_instance(code_text, my_model, predicate_type, threshold=args.precision_threshold, use_stoke=args.use_stoke, perturbation_probability=args.perturbation_probability) #0.82)  # FIXME: changing just for now to see the effect
    for exp_type, exp in exps.items():
        print('='*100)
        print("Predicate type: ", exp_type)
        print('Anchor: %s' % (' AND '.join(exp.names())))
        print('Precision: %.2f' % exp.precision())
        print('Coverage: %.2f' % exp.coverage())
        print('='*100)
        print('Examples where anchor applies and model predicts %s:' % pred)
        print()
        print('\n\n'.join([x[0] for x in exp.examples(only_same_prediction=True)]))
        print('='*100)
        print()
        print('Examples where anchor applies and model predicts %s:' % alternative)
        print()
        print('\n\n'.join([x[0] for x in exp.examples(partial_index=None, only_different_prediction=True)]))
        print('='*100)


if __name__ == '__main__':
    main()
