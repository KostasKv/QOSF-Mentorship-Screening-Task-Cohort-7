# QOSF-Mentorship-Screening-Task-Cohort-7
A solution to the screening task (titled "Is Rectangle?") for the QOSF Mentorship's 7th cohort.
Implemented using PennyLane.

## Solution idea
Lengths were encoded into quantum states, and a SWAP test was used to compare these.

A rectangle exists if you can split the 4 integer inputs into two pairs of integers (w, x) and (y, z), where the pair (w, x) contains the same integers as the pair (y, z). For example, for inputs [5, 6, 6, 5], the pairs (5, 6) and (6, 5) contain the same integers as eachother and so a rectangle can be made with these side lengths. For inputs [A, B, C, D], it is enough to compare the following combinations of pairs:
- (A, B) and (C, D)
- (A, C) and (B, D)
- (A, D) and (B, C)

For each of these combinations of pairs, we encode each pair into a quantum state, and then use a SWAP test to see if these are the same. E.g., for lengths (w, x) and (y, z), we prepare the two states (|wx> + |xw>) and (|yz> + |zy>). If the set {w, x} is the same as the set {y, z}, then these two states are identical, otherwise they are orthorogonal. Thus, according to the general results of a SWAP test, the probability of measuring qubit 0 to be in the state |0...0> is 1 if  the states are identical (the pairs are the same), otherwise 0.5 if the states are orthogonal (the pairs are different)
