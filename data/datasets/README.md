This folder contains datasets containing frontend and backend bound basic blocks derived from the [BHive dataset](https://github.com/ithemal/bhive). These basic blocks are ones which have number of instructions between 4 and 10. 
Frontend bound basic blocks are the ones which have a major throughput bottleneck at the predecoder or decoder of the processor. 
Backend bound basic blocks are the ones which have a major throughput bottleneck at the backend of the processor (at its execution ports).
The above descriptions of frontend and backend bound blocks are not comprehensive, they are just the notions of frontend and backend bottlenecks that we have used currently for our experiments. 
Kindly note that CoMEt is in no way restricted to work with only this set of basic blocks. It is a very general framework and our selection of these basic blocks is only for demonstrating CoMEt's working on commonly encountered types of basic blocks. 

The explanation dataset used in our experiments shown in our paper is a subset of these datasets. 

The BHive dataset categorizes its basic blocks into 6 categories.
- Load
- Store
- Load/Store
- Scalar
- Vector
- Scalar/Vector

These categories are based on the main functionality of the basic block. We have tried to maintain the representation of all categories of basic blocks in the dataset for which explanations were created. 
