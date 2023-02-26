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
    parser = argparse.ArgumentParser(description='Explain the throughput prediction made by given cost model for one basic block')
    parser.add_argument("code", type=str, help='code for input x86 assembly basic block')
    parser.add_argument("cost_model", type=str, help='cost model whose throughput predictions are to be explained')
    parser.add_argument("-threshold", type=float, help='precision threshold for the Anchors algorithm (default=0.82)', default=0.82)
    parser.add_argument("-probability", type=float, help='probability parameter in perturbation model (default=0.5)', default=0.5)
    parser.add_argument('-token', action='store_true', help='give explanations with token-level predicates')
    parser.add_argument('-verbose', action='store_true', help='get verbose output if -verbose is included')
    args = parser.parse_args()

    predicate_type = 'instruction'
    if args.token:
        predicate_type = 'token'
    settings.init()
    code_text = args.code
    print()
    print("The basic block being explained is:\n{}".format(code_text.replace('; ', '\n')))
    print()
    # preprocess code to send to explain
    code = preprocess_my_code(code_text)

    if args.cost_model == 'ithemal':
        my_model = testing_ithemal_gpu
        print("Testing cost model Ithemal")
    elif args.cost_model == 'uica':
        my_model = testing_uica
        print("Testing cost model uiCA")
    else:
        raise("model type not recognized!")

    explainer = anchor_code.AnchorCode()
    performance_prediction = my_model(code)[0]
    print()
    print('Throughput Prediction for input basic block made by model {}: {}'.format(args.cost_model, performance_prediction))

    exp = explainer.explain_instance(code, my_model, predicate_type, threshold=args.threshold, perturbation_probability=args.probability)
    print()
    print('='*100)
    print("Predicate type: ", predicate_type)
    print("CoMEt's explanation consists of predicates corresponding to: %s" % (' AND '.join(exp.names())))
    print('Precision: %.2f' % exp.precision())
    print('Coverage: %.2f' % exp.coverage())
    print('='*100)
    if args.verbose:
        print('Examples where anchor applies and model predicts close to the original throughput prediction:')
        print()
        print('\n\n'.join([x[0] for x in exp.examples(only_same_prediction=True)]))
        print('='*100)
        print()
        print('Examples where anchor applies and model predicts far from the original throughput prediction:')
        print()
        print('\n\n'.join([x[0] for x in exp.examples(partial_index=None, only_different_prediction=True)]))
        print('='*100)


if __name__ == '__main__':
    main()
