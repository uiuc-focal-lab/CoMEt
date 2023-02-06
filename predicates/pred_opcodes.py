import copy


class Opcodes:
    def make_predicates_opc(self):
        for i in range(len(self.instructions)):
            self.token_list.append(f'opc_{i}')
            self.positions.append(i)

    def perturb_opc(self, present_inst_tokens, n):
        my_seed = n
        my_seed += 10000
        perturbed_asm_insts = []
        data = []
        for i, inst in enumerate(self.instructions):
            present = present_inst_tokens[i] if i in present_inst_tokens.keys() else []
            perturbed_inst = inst.get_original_asm()
            changes_list = []
            if len(present) == 0:  # this instruction's opcode can be perturbed as its token is not present in present (which is why that is empty)
                present_tokens = copy.deepcopy(inst.get_tokens())
                present_tokens.remove(f'opc_{i}')
                perturbed_inst, changes_list = inst.perturb(present_tokens, n=(my_seed*(i+1))%10001)
            perturbed_asm_insts.append(perturbed_inst)
            changes = 1
            if 0 in changes_list:  # some change happened
                changes = 0
            data.append(changes)
        perturbed_asm = '; '.join(perturbed_asm_insts)
        # print("Perturbed asm: ", perturbed_asm)
        return data, perturbed_asm, n
