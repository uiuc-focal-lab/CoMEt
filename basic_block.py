import xed
import subprocess
import sys
import tempfile
sys.path.append('predicates')
sys.path.append('utils')
from microArchConfigs import MicroArchConfigs
import pred_tokens
import pred_instructions
import instruction


class BasicBlock(pred_tokens.Tokens, pred_instructions.Instructions):
    def __init__(self, code, predicate_type, classifier_func, **kwargs):
        _, asm_file = tempfile.mkstemp()
        _, bin_file = tempfile.mkstemp()
        with open(asm_file, 'w') as f:
            f.write(code)
        subprocess.run(['as', asm_file, '-o', bin_file])
        self.disas = xed.disasFile(bin_file, chip=MicroArchConfigs['HSW'].XEDName)

        for i in range(len(self.disas)):  # considering the disas object as it will have all the directives removed
            if self.disas[i]['iclass'].split('_')[0].upper() == 'NOP':
                self.disas[i]['asm'] = self.disas[i]['asm'].split(', ', 1)[0]
            # lone 'ptr' keywords (which are not preceded by 'word' indicating the length of operand) are dangerous as they put the displacement to be 0
            # so we want to remove all the lone 'ptr's
            # for this, we first remove all 'ptr's
            self.disas[i]['asm'] = self.disas[i]['asm'].replace(' ptr ', ' ')
            # then when we find an occurrence of a 'word', we add a 'ptr' after it to maintain the syntax
            self.disas[i]['asm'] = self.disas[i]['asm'].replace('word ', 'word ptr ')
            self.disas[i]['asm'] = self.disas[i]['asm'].replace('byte ', 'byte ptr ')

        self.instructions = [instruction.Instruction(x, i) for i, x in enumerate(self.disas)]
        self.original_asm = '; '.join(x['asm'] for x in self.disas)
        # print("Original: ", self.original_asm)
        self.all_token_dict = {}
        for i, x in enumerate(self.instructions):
            self.all_token_dict[i] = x.get_tokens()
        self.predicate_type = predicate_type
        self.classifier_fn = classifier_func
        if 'uica_output_type' in kwargs.keys():
            self.center = self.classifier_fn([self.original_asm], output_type=kwargs['uica_output_type'])[0]
        else:
            self.center = self.classifier_fn([self.original_asm])[0]
        self.token_list = []
        self.positions = []
        if self.predicate_type == 'token':
            self.make_predicates, self.perturb = self.make_predicates_tokens, self.perturb_tokens
        elif self.predicate_type == 'instruction':
            self.make_predicates, self.perturb = self.make_predicates_inst, self.perturb_inst
        self.make_predicates()

    def get_original_pred(self):
        return self.center
    
    def get_tokens(self):
        return self.token_list, self.positions

    def get_num_perturbations(self):
        # each instruction will have some number of possibilities for it
        # for all perturbations, each instruction will be perturbed independently
        # total num_perturbations = product of num perturbations for all instructions
        num_perturbations = 1  # includes the original code
        for inst in self.instructions:
            num_perturbations *= inst.get_num_perturbations()  # guaranteed to be > 0
        return num_perturbations
