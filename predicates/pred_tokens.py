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
        # each data dependency must not be perturbed with some probability
        # this has to be done here, as this can't be done at the instruction level
        # for (i, j) in self.data_dependency_graph.edges():
        #     if np.random.uniform(0, 1) > 0.5:
        #         # this dependency has to be preserved
        #         # the dependency will be preserved by keeping one pool of operands intact
        #         opnd_structured_list = self.operands_for_data_dependencies[(i, j)]
        #         pool_num = np.random.choice(np.arange(len(opnd_structured_list)))  # randomly selecting an index of the opnd_structured_list
        #         # only the elements of the opnd_list need to be preserved. Rest can be changed randomly
        #         opnd_list = [x for x in opnd_structured_list[pool_num]]
        #         if i not in present_inst_tokens.keys():
        #             present_inst_tokens[i] = []
        #         if j not in present_inst_tokens.keys():
        #             present_inst_tokens[j] = []
        #         present_inst_tokens[i].extend([x for x in opnd_list if x.startswith(f'opnd_{i}')])  # operands of instruction i in the data dependency
        #         present_inst_tokens[j].extend([x for x in opnd_list if x.startswith(f'opnd_{j}')])  # operands of instruction j in the data dependency
        #         present_inst_tokens[i].append(f'opc_{i}')  # opcodes of a fixed data dependency must also not change
        #         present_inst_tokens[j].append(f'opc_{j}')
        for i, inst in enumerate(self.instructions):
            present_tokens = present_inst_tokens[i] if i in present_inst_tokens.keys() else []
            if i not in self.inst_not_to_be_perturbed:
                perturbed_inst, changes = inst.perturb(present_tokens, p, n=(my_seed*(i+1))%10001)
            else:
                perturbed_inst = inst.get_original_asm()
                changes = np.ones((len(inst.get_tokens())))
            perturbed_asm_insts.append(perturbed_inst)
            data.extend(list(changes))
        perturbed_asm_insts = [ins for ins in perturbed_asm_insts if ins != '']
        perturbed_asm = '; '.join(perturbed_asm_insts)
        if perturbed_asm_insts == []:  # all instructions got blank
            perturbed_asm = 'nop'

        # print("Perturbed asm: ", perturbed_asm, 'data:', data)
        return data, perturbed_asm, n
