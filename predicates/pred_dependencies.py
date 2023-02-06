import copy
import networkx as nx
import sys
import numpy as np
sys.path.append('../utils')
import mem_utils
from dependency_types_pools import *
from basic_block_for_dep import *
import settings
import matplotlib.pyplot as plt


class Dependencies:

    def make_predicates_dep(self):  # this has forward edges removed, with no differentiation between the data dependencies
        self.data_dependency_graph = nx.DiGraph()
        for i, inst in enumerate(self.instructions):
            inst.make_rw_pools()  # makes the read/write pools of instruction
            self.data_dependency_graph.add_node(i)

        # if len(self.instructions) == 1:  # this basic block has no data dependencies: but need not be treated as a special case
        #     return
        self.operands_for_data_dependencies = {}
        for i in range(len(self.instructions) - 1):
            for j in range(i+1, len(self.instructions)):
                raw_list = raw(self.instructions[i].get_write_pool(), self.instructions[j].get_read_pool())  # raw() returns list of operands involved in RAW data dependency between i, j
                war_list = war(self.instructions[i].get_read_pool(), self.instructions[j].get_write_pool())
                waw_list = waw(self.instructions[i].get_write_pool(), self.instructions[j].get_write_pool())
                orig_dep_list = copy.deepcopy(raw_list) + copy.deepcopy(war_list) + copy.deepcopy(waw_list)
                dep_list = []
                for dep in orig_dep_list:
                    if dep not in dep_list:
                        dep_list.append(dep)
                # print(dep_list)
                if len(dep_list) > 0:
                    self.data_dependency_graph.add_edge(i, j)  # let's see if this works
                    self.operands_for_data_dependencies[(i, j)] = dep_list  # this would contain the operands even for dependencies which will be eventually removed. but we won't access them so fine

        self.data_dependency_graph = nx.transitive_reduction(self.data_dependency_graph)

        # nx.draw(self.data_dependency_graph, labels= {i:(i+1) for i in range(len(self.instructions))},with_labels=True)
        # plt.savefig('figures/data_dependencies/0.png')
        # exit(0)
        for (i, j) in self.data_dependency_graph.edges():
            self.positions.append((i, j))
            self.token_list.append(f'{i}_{j}')


    def perturb_dep(self, present_tokens, n):
        '''
        this can either remove or let a dependency stay.
        it doesn't create a new type of dependency between two instructions, unless that gets created without intention
        '''
        # map the present data dependencies to the operands that must be present in the basic block
        # present_tokens: a dict indicating what type of dependency between which 2 instructions must be preserved
        present_inst_tokens = {}
        data = [0]*len(self.token_list)
        for i in range(len(self.instructions)):
            present_inst_tokens[i] = [f'opc_{i}']  # opcodes must not be changed in this type of perturbation
        for (i, j) in present_tokens.keys():
            opnd_structured_list = self.operands_for_data_dependencies[(i, j)]  # contains operands of insts i, j which are involved in this dependency
            # opnd_list = [x for one in opnd_structured_list for x in one]
            # present_inst_tokens[i].extend([x for x in opnd_list if x.startswith(f'opnd_{i}')])  # operands of instruction i in the data dependency
            # present_inst_tokens[j].extend([x for x in opnd_list if x.startswith(f'opnd_{j}')])  # operands of instruction j in the data dependency
            # data[self.token_list.index(f'{i}_{j}')] = 1
            # we will require just one of these operand pools to be preserved for preserving the data dependency
            # the operand pool to be preserved will be picked at random from the opnd_structured_list
            np.random.seed((settings.seed*(n+1)*100)%1000000001)  # set the random seed for the selection of the opnd pool to preserve for the data dependency
            pool_num = np.random.choice(np.arange(len(opnd_structured_list)))  # randomly selecting an index of the opnd_structured_list
            # only the elements of the opnd_list need to be preserved. Rest can be changed randomly
            opnd_list = [x for x in opnd_structured_list[pool_num]]
            present_inst_tokens[i].extend([x for x in opnd_list if x.startswith(f'opnd_{i}')])  # operands of instruction i in the data dependency
            present_inst_tokens[j].extend([x for x in opnd_list if x.startswith(f'opnd_{j}')])  # operands of instruction j in the data dependency
            data[self.token_list.index(f'{i}_{j}')] = 1

        # perturb the basic block, while keeping the present tokens constant
        perturbed_asm = self.original_asm
        my_seed = n
        my_seed += 10000
        perturbed_asm_insts = []
        all_changes = {}
        for i, inst in enumerate(self.instructions):
            present_tokens_my_inst = present_inst_tokens[i]
            perturbed_inst, changes = inst.perturb(present_tokens_my_inst, n=(my_seed*(i+1)) % 10001)
            perturbed_asm_insts.append(perturbed_inst)
            all_changes[i] = changes
        perturbed_asm = '; '.join(perturbed_asm_insts)
        # print("Perturbed asm: ", perturbed_asm)

        # recreate the read-write pools for the perturbed asm code
        # make a basic_block_for_dependency object out of the perturbed asm code
        perturbed_bb = BasicBlockDependencies(perturbed_asm)
        present_dependencies = perturbed_bb.get_operands_dependencies().keys()
        # use the operands_for_data_dependency dict to check if the data dependencies in this block are there or not
        # map the present tokens back to a diff data object which indicates whether a data dependency changed or not
        for (i, j) in self.data_dependency_graph.edges():
            if (i, j) in present_tokens.keys():
                continue  # this data dependency was preserved, so no need to check it (data object is already having this information)
            data_index = self.token_list.index(f'{i}_{j}')
            data[data_index] = int((i, j) in present_dependencies)  # checks if the dependency is present in the perturbed asm

        # for (i, j) in self.data_dependency_graph.edges():
        #     if (i, j) in present_tokens.keys():
        #         continue  # this data dependency was preserved, so no need to check it
        #     changes_i = all_changes[i]
        #     changes_j = all_changes[j]
        #     data_index = self.token_list.index(f'{i}_{j}')
        #     data[data_index] = 0  # assuming change happened
        #     # go over all the lists in the edge's attributes
        #     # print(self.data_dependency_graph[i][j])
        #     # if even one data dependency pool has some preservation, then data dependency is assumed to be preserved according to current design
        #     for cur_opnds in self.operands_for_data_dependencies[(i, j)]:
        #         # cur_opnds is a pool of operands associated with a particular common operand in the data dependency
        #         cur_opnds_i = [x for x in cur_opnds if x.startswith(f'opnd_{i}')]
        #         cur_opnds_j = [x for x in cur_opnds if x.startswith(f'opnd_{j}')]
        #         num_changes_i = 0
        #         num_changes_j = 0
        #         for opndi in cur_opnds_i:
        #             opnd_no = int(opndi.split('_')[2])
        #             if changes_i[1 + opnd_no] == 0:  # change happened to this operand
        #                 num_changes_i += 1
        #         for opndj in cur_opnds_j:
        #             opnd_no = int(opndj.split('_')[2])
        #             if changes_j[1 + opnd_no] == 0:
        #                 num_changes_j += 1
        #         # check: this is implementing data dependency maintenance, even when one edge exists between two instructions
        #         # if the operands in no instruction change, then the data dependency is preserved
        #         if (num_changes_i + num_changes_j) == 0:
        #             data[data_index] = 1
        #             break
        #         # if the operands of one instruction don't change, but some of those of the other instruction change, then too the dependency is preserved
        #         if (num_changes_i == 0 and num_changes_j < len(cur_opnds_j)) or (num_changes_j == 0 and num_changes_i < len(cur_opnds_i)):
        #             data[data_index] = 1
        #             break
        #         # if the operands of one instruction don't change, but all of the other instruction change, then the data dependency is gone
        #         if (num_changes_i == 0 and num_changes_j == len(cur_opnds_j)) or (num_changes_j == 0 and num_changes_i == len(cur_opnds_i)):
        #             continue
        #         # if some operands change in both instructions, then the checking for data dependency needs to be done
        #         # if one operand from both instructions matches up then
        #         else:
        #             def get_operand(opnd_list, opnd):
        #                 opnd_no = int(opnd.split('_')[2])
        #                 my_opnd = opnd_list[opnd_no]
        #                 if '_b' in opnd:  # this is requesting for the base of a memory operand
        #                     base, _, _, _ = mem_utils.decompose_mem_str(my_opnd)
        #                     return base
        #                 if '_i' in opnd:  # this is requesting for the index of a memory operand (when _b_i, then both have to be same, it is captured in the above)
        #                     _, index1, _, _ = mem_utils.decompose_mem_str(my_opnd)
        #                     return index1
        #                 return my_opnd  # return the entire operand
        #
        #             def check_equality():  # this function checks if the operands are equal
        #                 # atleast two elements should be there in cur_opnds
        #                 assert len(cur_opnds) > 1
        #                 all_opnds = {i: perturbed_asm_insts[i].split(' ', 1)[1].split(', '), j: perturbed_asm_insts[j].split(' ', 1)[1].split(', ')}  # this is fine to do, as if the instructions will not have operands then they can't be in the data dependency
        #                 # these operands correspond to one type of dependency wrt one register/memory
        #                 # so we will check if in this pool of operands (cur_opnds) there are any two operands each in different instructions which are same (even after the perturbation)
        #                 # basically, we will compute the intersection in the opnds pool of both the instructions and check if that is non-empty
        #
        #                 opnds_inst_i = []
        #                 for my_idx_i in range(len(cur_opnds_i)):
        #                     opnds_inst_i.append(get_operand(all_opnds[i], cur_opnds_i[my_idx_i]))
        #                 opnds_inst_j = []
        #                 for my_idx_j in range(len(cur_opnds_j)):
        #                     opnds_inst_j.append(get_operand(all_opnds[j], cur_opnds_j[my_idx_j]))
        #
        #                 return bool(set(opnds_inst_i) & set(opnds_inst_j))  # this returns if the intersection of the two lists is non-empty
        #                 # common = get_operand(all_opnds[int(cur_opnds[0].split('_')[1])], cur_opnds[0])
        #                 # for my_idx in range(1, len(cur_opnds)):
        #                 #     this_opnd = get_operand(all_opnds[int(cur_opnds[my_idx].split('_')[1])], cur_opnds[my_idx])
        #                 #     if this_opnd != common:
        #                 #         return False
        #                 # return True
        #
        #             if check_equality():  # this function checks if the operands are equal
        #                 data[data_index] = 1
        #                 # print('equality after perturbation')
        #                 # print(f'num_changes {i}:', num_changes_i, f'changes {i}:', changes_i)
        #                 # print(f'num_changes {j}:', num_changes_j, f'changes {j}:', changes_j)
        #                 break
        #             # print("all matched after perturbation:", perturbed_asm, cur_opnds)
        #
        #     # This is a different type of thinking where the data dependency weakening is also considered a change in the dependency
        #             # # if some operands are changed: then data dependency is weakened or removed (changed in short)
        #             # elif num_changes < len(cur_opnds):
        #             #     data[data_index] = 0
        #             #     break
        #         # if all operands are changed: check if the data dependency is preserved by checking actual values of the operands in the perturbed asm
        #
        #     # opnd_list = self.data_dependency_graph[i][j]['operands']
        #     # opnd_list_i = [x for x in opnd_list if x.startswith(f'opnd_{i}')]  # operands of i involved in the data dependency
        #     # opnd_list_j = [x for x in opnd_list if x.startswith(f'opnd_{j}')]  # operands of j involved in the data dependency
        #     # changes_i = all_changes[i]
        #     # changes_j = all_changes[j]
        #     # data_index = self.token_list.index(f'{i}_{j}')
        #     # data[data_index] = 1  # assuming no change happened
        #     # for opndi in opnd_list_i:
        #     #     opnd_no = int(opndi.split('_')[2])  # number of the operand to check
        #     #     if changes_i[1 + opnd_no] == 1:  # no change happened; even if change happened (in other parts of a memory operand), the requested parts were not changed
        #     #         continue
        #     #     else:  # some change happened
        #     #         # if self.instructions[i].get_opnd(opnd_no) == self.instructions[j].get_opnd(opnd_no):
        #     #         #     continue  # the operand changed similarly in both instructions
        #     #         data[data_index] = 0
        #     #         break  # this for loop must be ended now as data dependency has undergone a change
        #     # if data[data_index]:  # if no change has been detected yet
        #     #     for opndj in opnd_list_j:
        #     #         opnd_no = int(opndj.split('_')[2])  # number of the operand to check
        #     #         if changes_j[1 + opnd_no] == 1:  # no change happened; even if change happened (in other parts of a memory operand), the requested parts were not changed
        #     #             continue
        #     #         else:  # some change happened
        #     #             data[data_index] = 0
        #     #             break  # this for loop must be ended now as data dependency has undergone a change
        # print('perturbed asm:', perturbed_asm)
        # print('data:', data)
        return data, perturbed_asm, n


    # def make_predicates_dep_types(self):  # FIXME: don't use this function as it is, as raw(), war(), waw() are not correctly defined here
    #     if len(self.instructions) == 1:  # this basic block has no data dependencies
    #         return
    #
    #     for inst in self.instructions:
    #         inst.make_rw_pools()  # makes the read/write pools of instruction
    #     # exit(0)
    #     self.operand_for_data_dependency = {}  # this will contain all operands involved in the data dependency denoted by the key
    #     for i in range(len(self.instructions) - 1):
    #         for j in range(i+1, len(self.instructions)):
    #             # checking for RAW (Read After Write)
    #             raw_list = self.raw(i, j)  # self.raw() returns list of operands involved in RAW data dependency between i, j
    #             if len(raw_list) > 0:
    #                 self.positions.append((i, j))
    #                 self.token_list.append(f'RAW_{i}_{j}')
    #                 self.operand_for_data_dependency[(i, j, 'RAW')] = raw_list
    #             # checking for WAR (Write After Read)
    #             war_list = self.war(i, j)
    #             if len(war_list) > 0:
    #                 self.positions.append((i, j))
    #                 self.token_list.append(f'WAR_{i}_{j}')
    #                 self.operand_for_data_dependency[(i, j, 'WAR')] = war_list
    #             # checking for WAW (Write After Write)
    #             waw_list = self.waw(i, j)
    #             if len(waw_list) > 0:
    #                 self.positions.append((i, j))
    #                 self.token_list.append(f'WAW_{i}_{j}')
    #                 self.operand_for_data_dependency[(i, j, 'WAW')] = waw_list
    #     print(self.operand_for_data_dependency)
    #     # exit(0)

    # def perturb_dep_types(self, present_tokens, n):
    #     '''
    #     this can either remove or let a dependency stay.
    #     it doesn't create a new type of dependency between two instructions, unless that gets created without intention
    #     '''
    #     # map the present data dependencies to the operands that must be present in the basic block
    #     # present_tokens: a dict indicating what type of dependency between which 2 instructions must be preserved
    #     present_inst_tokens = {}
    #     data = [0]*len(self.token_list)
    #     for i in range(len(self.instructions)):
    #         present_inst_tokens[i] = [f'opc_{i}']  # opcodes must not be changed in this type of perturbation
    #     for (i, j) in present_tokens.keys():
    #         for k in present_tokens[(i, j)]:
    #             type_of_dep = k.split('_', 1)[0]  # RAW, WAR, WAW
    #             opnd_list = self.operand_for_data_dependency[(i, j, type_of_dep)]  # contains operands of insts i, j which are involved in this dependency
    #             present_inst_tokens[i].extend([x for x in opnd_list if x.startswith(f'opnd_{i}')])  # operands of instruction i in the data dependency
    #             present_inst_tokens[j].extend([x for x in opnd_list if x.startswith(f'opnd_{j}')])  # operands of instruction j in the data dependency
    #             data[self.token_list.index(f'{type_of_dep}_{i}_{j}')] = 1
    #
    #     # perturb the basic block, while keeping the present tokens constant
    #     label = -1
    #     perturbed_asm = self.original_asm
    #     my_seed = n
    #     while label == -1:
    #         my_seed += 10000
    #         perturbed_asm_insts = []
    #         all_changes = {}
    #         for i, inst in enumerate(self.instructions):
    #             present_tokens_my_inst = present_inst_tokens[i]
    #             perturbed_inst, changes = inst.perturb(present_tokens_my_inst, n=(my_seed*(i+1))%10001)
    #             perturbed_asm_insts.append(perturbed_inst)
    #             all_changes[i] = changes
    #         perturbed_asm = '; '.join(perturbed_asm_insts)
    #         label = self.classifier_fn([perturbed_asm], self.center, n)[0]
    #     print("Perturbed asm: ", perturbed_asm)
    #     print("Label: ", label)
    #
    #     # map the present tokens back to a diff data object which indicates whether a data dependency changed or not
    #     for (i, j, t) in self.operand_for_data_dependency.keys():
    #         if (i, j) in present_tokens.keys() and any(item.startswith(t) for item in present_tokens[(i, j)]):
    #             continue  # this data dependency was preserved, so no need to check it
    #         opnd_list = self.operand_for_data_dependency[(i, j, t)]
    #         opnd_list_i = [x for x in opnd_list if x.startswith(f'opnd_{i}')]  # operands of i involved in the data dependency
    #         opnd_list_j = [x for x in opnd_list if x.startswith(f'opnd_{j}')]  # operands of j involved in the data dependency
    #         changes_i = all_changes[i]
    #         changes_j = all_changes[j]
    #         data_index = self.token_list.index(f'{t}_{i}_{j}')
    #         data[data_index] = 1  # assuming no change happened
    #         for opndi in opnd_list_i:
    #             opnd_no = int(opndi.split('_')[2])  # number of the operand to check
    #             if changes_i[1 + opnd_no] == 1: # no change happened; even if change happened (in other parts of memory), the requested parts were not changed
    #                 continue
    #             else:  # some change happened
    #                 data[data_index] = 0
    #                 break  # this for loop must be ended now as data dependency has undergone a change
    #         if data[data_index]:  # if no change has been detected yet
    #             for opndj in opnd_list_j:
    #                 opnd_no = int(opndj.split('_')[2])  # number of the operand to check
    #                 if changes_i[1 + opnd_no] == 1: # no change happened; even if change happened (in other parts of memory), the requested parts were not changed
    #                     continue
    #                 else:  # some change happened
    #                     data[data_index] = 0
    #                     break  # this for loop must be ended now as data dependency has undergone a change
    #
    #     return data, perturbed_asm, label
