import anchor_base
import anchor_explanation
from sample_func import *


class AnchorCode(object):
    def __init__(self):
        pass

    def explain_instance(self, text, classifier_fn, predicate_type, threshold=0.9, perturbation_probability=0.5,
                          delta=0.1, tau=0.15, batch_size=100, onepass=False,
                          use_proba=False, beam_size=4, use_stoke=False,
                          **kwargs):
        if type(text) == bytes:
            text = text.decode()

        all_types = ['token', 'instruction']
        predicates = []
        if predicate_type in all_types:
            predicates = [predicate_type]
        else:
            if predicate_type == 'levels':
                predicates = ['opcode', 'dependency', 'register']
            elif predicate_type == 'levels_till_dep':
                predicates = ['opcode', 'dependency']
            else:
                raise Exception("Unrecognized predicate type!")
        explanations = {}

        for predicate in predicates:
            words, positions, true_label, sample_fn = get_sample_fn(
                text, classifier_fn, predicate, perturbation_probability, onepass=onepass, use_proba=use_proba, use_stoke=use_stoke)  # predicate type sends the type of predicate for sampling function
            # TODO: add a check if words is non-empty (specifically for level 2 of predicates)
            # TODO: add iterative exp objects for a hierarchy of predicates
            if words == []:  # empty list of words
                print('Anchor: <no predicates>')  # printing the fact that there are no predicates, so it is easy to parse its results file
                continue
            print("All predicates to explain with: ", words)
            t1 = time.time()
            exp = anchor_base.AnchorBaseBeam.anchor_beam(
                sample_fn, delta=delta, epsilon=tau, batch_size=batch_size,
                desired_confidence=threshold, stop_on_first=False, #beam_size=2,
                coverage_samples=10000, verbose=True, min_samples_start=batch_size, **kwargs)  # changed number of coverage samples from 1 to 2000
            exp['names'] = [words[x] for x in exp['feature']]
            exp['positions'] = [positions[x] for x in exp['feature']]
            exp['instance'] = text
            exp['prediction'] = true_label
            explanation = anchor_explanation.AnchorExplanation('text', exp,
                                                               self.as_html)
            explanations[predicate] = explanation
            print(f"Total time taken for predicate type {predicate}:", time.time()-t1)
        return explanations
