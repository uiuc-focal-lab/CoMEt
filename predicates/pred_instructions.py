class Instructions:
    def make_predicates_inst(self):
        for i in range(len(self.instructions)):
            self.token_list.append(f'inst_{i}')
            self.positions.append(i)

    def perturb_inst(self, present_inst_tokens, p, n, use_stoke=False):
        perturbed_asm = self.original_asm
        my_seed = n
        my_seed += 10000
        perturbed_asm_insts = []
        data = []
        for i, inst in enumerate(self.instructions):
            present = present_inst_tokens[i] if i in present_inst_tokens.keys() else []
            perturbed_inst = inst.get_original_asm()
            changes_list = []
            if len(present) == 0:  # this instruction can be perturbed as its token is not present in present (which is why that is empty)
                perturbed_inst, changes_list = inst.perturb(present, p, n=(my_seed*(i+1))%10001, use_stoke=use_stoke)
            # print(perturbed_inst)
            perturbed_asm_insts.append(perturbed_inst)
            changes = 1
            if 0 in changes_list:  # some change happened
                changes = 0
            data.append(changes)
        perturbed_asm_insts = [ins for ins in perturbed_asm_insts if ins != '']
        if perturbed_asm_insts == []:  # all instructions got blank
            perturbed_asm = 'nop'
        else:
            perturbed_asm = '; '.join(perturbed_asm_insts)
        # print("Perturbed asm: ", perturbed_asm)
        return data, perturbed_asm, n

