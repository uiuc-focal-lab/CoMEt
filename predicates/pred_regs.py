import copy
import sys
sys.path.append('utils')
import perturbation_utils
import numpy as np
import settings
import time

class Registers:
    def make_predicates_reg(self):
        # predicates are all the unique registers used in the basic block
        my_regs = []
        for inst in self.instructions:
            inst.make_all_regs()
            inst_regs = inst.get_all_regs()
            my_regs.extend(inst_regs)
        my_regs = list(set(my_regs))
        my_regs.sort()
        for i, r in enumerate(my_regs):
            self.positions.append(i)  # contains register names
            self.token_list.append(r)  # contains corresponding register operands


    def perturb_reg(self, present_inst_tokens, n):
        # present_inst_tokens is a dict from an index to register names in basic block.
        # present_inst_tokens contains the registers' indices which must be present in the basic block
        # all locations of a register need to be perturbed similarly so as to maintain the data dependencies
        # create pool of all registers available in basic block
        np.random.seed((settings.seed*(n+1)*100)%1000000001)
        all_avail_regs = copy.deepcopy(self.token_list)  # names of all the available registers in basic block

        label = -1
        perturbed_asm = self.original_asm
        perturber = perturbation_utils.AsmPerturber()
        my_seed = n
        while label == -1:  # repeat if the label = -1
            # perturb each register to some other (except for the registers which are in present_inst_tokens)
            my_seed += 10000
            perturbed_regs = {}
            data = [1]*len(self.positions)
            for my_idx, reg in enumerate(all_avail_regs):
                if my_idx in present_inst_tokens.keys():  # this register must be preserved
                    perturbed_regs[reg] = reg
                    continue
                new_reg = reg
                if np.random.uniform(0, 1) > 0.5:  # perturb with 0.5 probability
                    new_reg = perturber.perturb_register(reg, n=(my_idx+1)*my_seed)
                    data[my_idx] = 0  # there is a change here in this predicate
                perturbed_regs[reg] = new_reg  # this will store the new reg values for the register reg
                # set the data diff object with the registers that were perturbed

            # reflect the changes in the basic block by short-circuiting the perturb function

            perturbed_asm_insts = []
            for i, inst in enumerate(self.instructions):
                perturbed_inst = inst.change_all_regs(perturbed_regs, n=(my_seed*(i+1))%1000001)
                perturbed_asm_insts.append(perturbed_inst)
            perturbed_asm = '; '.join(perturbed_asm_insts)
            label = self.classifier_fn([perturbed_asm], self.center, n)[0]

        print("Perturbed asm: ", perturbed_asm)
        print("Label: ", label)
        return data, perturbed_asm, label
