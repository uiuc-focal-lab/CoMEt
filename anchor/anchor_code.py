import anchor_base
import anchor_explanation
from sample_func import *


class AnchorCode(object):
    def __init__(self):
        pass

    def explain_instance(self, code, classifier_fn, predicate_type, threshold=0.82, perturbation_probability=0.5,
                          delta_beta=0.1, epsilon=0.15, batch_size=100, onepass=False,
                          use_proba=False, beam_size=4, **kwargs):
        all_types = ['token', 'instruction']
        if predicate_type not in all_types:
            raise Exception("Unrecognized predicate type!")
        words, positions, true_label, sample_fn = get_sample_fn(
            code, classifier_fn, predicate_type, perturbation_probability, onepass=onepass, use_proba=use_proba)  # predicate type sends the type of predicate for sampling function
        print("All predicates to explain with are characterized by: ", words)  # TODO: make these words actual elements of the basic block
        t1 = time.time()
        exp = anchor_base.AnchorBaseBeam.anchor_beam(sample_fn, delta=delta_beta, epsilon=epsilon, batch_size=batch_size, desired_confidence=threshold,
                                                     stop_on_first=False, coverage_samples=10000, min_samples_start=batch_size, **kwargs)  # changed number of coverage samples from 1 to 2000
        exp['names'] = [words[x] for x in exp['feature']]
        exp['positions'] = [positions[x] for x in exp['feature']]
        exp['instance'] = code
        exp['prediction'] = true_label
        explanation = anchor_explanation.AnchorExplanation('text', exp)
        print()
        print(f"Total time taken for creating explanations with {predicate_type} predicate:", time.time()-t1)
        return explanation
