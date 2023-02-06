#!/bin/bash

echo $predicate_type
for iter in 0 7 #28 45 58 66 69 75 81 91
do
  echo "starting with block $((iter))"
#  echo file name data/anchors_outputs/$((iter)).txt
#  cd ../
#  echo bb_explain.py $(iter) $(predicate_type) > data/anchors_$(predicate_type)_outputs/$(iter).txt
  for predicate_type in opcode dependency register token instruction
  do
    echo "starting with predicate type $predicate_type"
    python3 bb_explain.py ${iter} $predicate_type > data/Ithemal_exp/anchors_${predicate_type}_outputs/${iter}.txt || exit 1
    echo "done with predicate type $predicate_type"
  done
  echo "done with block $((iter))"
done
# run from code_predicates/ folder

# results completed
# token: 0 7
# instruction:
