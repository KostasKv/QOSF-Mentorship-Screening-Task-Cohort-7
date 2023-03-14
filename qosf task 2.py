import pennylane as qml
from pennylane import numpy as np


def swap_test_pairs(pair1, pair2, drawer=None):
    ''' Uses quantum circuit SWAP test to determine if the integers in pair1 are the same as the integers in pair2.
        The input integer pairs (w, x) and (y, z) are encoded into two states (|wx> + |xw>), and (|yz> + |zy>). A SWAP test
        is performed to see if these two states are the same. If they are the same, that implies the set {w, x} equals
        the set {y, z}.

        Input: tuples pair1 and pair2, each of the form (u, v), where u and v are some binary strings encoding an integer.

        Output: Result of the SWAP test. Specifically, the probability of measuring 0 on the 0th qubit (which is 1 if {w, x} == {y, z}, 0.5 otherwise).
    '''
    num_qubits_per_state = 2 * len(pair1[0])
    NUM_WIRES = (2 * num_qubits_per_state) + 1
    
    dev = qml.device("default.qubit", wires=NUM_WIRES)

    def create_equal_superposition_statevector(basis_states):
        # Convert binary strings to decimal integers, which correspond to the statevector indices of those basis states.
        basis_state_indices = [int(x, 2) for x in basis_states]

        # Count number of unique basis states. Calculate equal amplitude based off of this.
        num_unique = len(set(x for x in basis_states))
        amplitude = 1 / np.sqrt(num_unique)

        # Create the statevector
        statevector = np.zeros(shape=(2**NUM_WIRES))
        for index in basis_state_indices:
            statevector[index] = amplitude

        return statevector

    def state_preparation(pair_1, pair_2):
        ''' For input pairs of binary strings (w, x) and (y, z), prepare the 
            circuit in the state |0> (|wx> + |xw>) (|yz> + |zy>)
        '''
        combo1_1 = pair_1[0] + pair_1[1]
        combo1_2 = pair_1[1] + pair_1[0]
        combo2_1 = pair_2[0] + pair_2[1]
        combo2_2 = pair_2[1] + pair_2[0]

        # Basis states to be superposed, written as binary strings
        state1 = '0' + combo1_1 + combo2_1
        state2 = '0' + combo1_1 + combo2_2
        state3 = '0' + combo1_2 + combo2_1
        state4 = '0' + combo1_2 + combo2_2

        # Create normalised statevector of the state we wish to prepare 
        # |0wxyz> + |0wxzy> + |0xwyz> + |0xwzy>
        state = create_equal_superposition_statevector([state1, state2, state3, state4])
        
        # Prepare circuit in the state
        qml.QubitStateVector(state, wires=range(NUM_WIRES))


    @qml.qnode(dev)
    def swap_test_circuit(pair_1, pair_2):
        # encode lengths into states of qubits
        state_preparation(pair_1, pair_2)

        # SWAP test to see if the states match (implying lengths are the same)
        qml.Hadamard(0)
        
        for i in range(1, num_qubits_per_state + 1):
            qml.CSWAP(wires=[0, i, i + num_qubits_per_state])

        qml.Hadamard(0)

        return qml.probs(wires=[0])

    # Draw circuit if requested
    if drawer is not None:
        if drawer == "mpl":
            fig, _ = qml.draw_mpl(swap_test_circuit)(pair1, pair2)
            fig.show()
        else:
            text_drawer = qml.draw(swap_test_circuit)(pair1, pair2)
            print(text_drawer)

    qubit_0_probs = swap_test_circuit(pair1, pair2)
    return float(qubit_0_probs[0])

def int_to_fixed_length_binary_string(integer, length):
    return format(integer, f'0{length}b')

def convert_inputs_to_equal_width_binary_strings(inputs):
    # Get number of bits required to represent the largest integer input
    max_num = max(inputs)
    length = len(format(max_num, f'0b')) 

    # Convert inputs to binary strings, all with the same length (padded with 0's from the left side where needed)
    return [int_to_fixed_length_binary_string(num, length) for num in inputs]
     

def is_rectangle(A, B, C, D, draw_circuit, mpl_drawer=True):
    ''' Determines whether it is possible to construct a rectangle with input (positive) integer side lengths A, B, C, D (in any order).

        Returns "1" if it is a rectangle, otherwise "0".

        These lengths are paired, and then encoded into quantum basis states. A SWAP test is used to determine if these length-pairs are
        the same. If they are, then we know a rectangle is possible, otherwise if no such matches are found then a rectangle cannot be
        constructed.
    '''

    inputs = [A, B, C, D]
    assert all((num > 0 and int(num) == num) for num in inputs), "Input side lengths must be integers greater than 0"

    A, B, C, D = convert_inputs_to_equal_width_binary_strings(inputs)
   
    pair_combos = [
        [[A, B], [C, D]],
        [[A, C], [B, D]],
        [[A, C], [B, D]]
    ]
    
    # Draw circuit if requested
    if draw_circuit:
        drawer = "mpl" if mpl_drawer else "default"
        swap_test_pairs(*pair_combos[0], drawer=drawer)
        
    # Perform SWAP test on each combination of pairs to see if the pairs contain the same integers.
    # If pair1 and pair2 contain the same integers, then a rectangle can be constructed with those side lengths
    for (pair1, pair2) in pair_combos:
        # Probability is 1 if the integers in pair1 are the same as the integers in pair2, otherwise it's 0.5
        prob_of_measuring_0_in_qubit_0 = swap_test_pairs(pair1, pair2)

        if np.isclose(float(prob_of_measuring_0_in_qubit_0), 1):
            return "1"  # Rectangle can be constructed

    # No rectangle found
    return "0"


if __name__ == "__main__":
    input = [2, 4, 4, 2]

    # If using mpl_drawer=True, try setting a breakpoint to be able to see the circuit figure
    output = is_rectangle(*input, draw_circuit=True, mpl_drawer=False)

    print(output)
