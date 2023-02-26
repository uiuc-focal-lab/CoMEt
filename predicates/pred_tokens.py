import numpy as np
import settings

class Tokens:
    def make_predicates_tokens(self):
        for i, x in enumerate(self.instructions):
            tokens = x.get_tokens()
            self.token_list += tokens
            self.positions += [i]*len(tokens)

    def perturb_tokens(self, present_inst_tokens, p, n):
        perturbed_asm = self.original_asm
        my_seed = n
        my_seed += 10000
        np.random.seed((settings.seed*(n+1)*100) % 1000000001)
        perturbed_asm_insts = []
        data = []
        for i, inst in enumerate(self.instructions):
            present_tokens = present_inst_tokens[i] if i in present_inst_tokens.keys() else []
            perturbed_inst, changes = inst.perturb(present_tokens, p, n=(my_seed*(i+1))%10001)
            perturbed_asm_insts.append(perturbed_inst)
            data.extend(list(changes))
        perturbed_asm_insts = [ins for ins in perturbed_asm_insts if ins != '']
        perturbed_asm = '; '.join(perturbed_asm_insts)
        if perturbed_asm_insts == []:  # all instructions got blank
            perturbed_asm = 'nop'

        # print("Perturbed asm: ", perturbed_asm, 'data:', data)
        return data, perturbed_asm, n
