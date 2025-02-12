# coding : utf-8

################# A SageMath implementation for the Algorithm "ClassicalToQuantum" ####################
# Three instances: 
# 1) The AND-depth-4 and AND-count-34 classical circuit for the AES S-box (Boyar and Peralta's S-box)
# 2) The AND-depth-3 and AND-count-42 classical circuit for the AES S-box introduced in Section 5.2
# 3) The AND-depth-3 and AND-count-78 classical circuit for the AES S-box introduced in ASIACRYPT 2022

# need Sagemath environment
from sage.all import *

"""
class of quantum circuit information
n                        : number of inputs(X) 
m                        : number of outputs(Y)  
s                        : T-depth
width                    : number of qubits
CNOT_layers_qubits       : CNOT sub-circuit qubits(inputs and outputs, s+1 layers)
Toffoli_layers_qubits    : Toffoli layer qubits(outputs, s layers)
state_transform_matrices : invertible matrices(CNOT sub-circuits)
"""
class quantum_circuit_info():
    def __init__(self, n: int, m: int, s: int, width: int
                , CNOT_layers_qubits: list
                , Toffoli_layers_qubits: list
                , state_transform_matrices: list):
        self.n                        = n 
        self.m                        = m  
        self.s                        = s
        self.width                    = width
        self.CNOT_layers_qubits       = CNOT_layers_qubits
        self.Toffoli_layers_qubits    = Toffoli_layers_qubits
        self.state_transform_matrices = state_transform_matrices
    
    def print_Info(self, save_file_name="info.txt"):
        print_rows = ["# quantum circuit information"]
        print_rows.append(f"# n: {self.n}")
        print_rows.append(f"# m: {self.n}")
        print_rows.append(f"# T-depth: {self.s}")
        print_rows.append(f"# width: {self.width}")
        print_rows.append(f"#########################")
        # print_rows.append(f"# ")
        for i in range(self.s):
            print_rows.append(f"# CNOT sub-circuit-{i+1}")
            print_rows.append(f"# CNOT inputs qubits({len(self.CNOT_layers_qubits[i])}):")
            print_rows.append(f"{self.CNOT_layers_qubits[i]}")
            print_rows.append(f"# state transform matrix:")
            print_rows.append(f"{self.state_transform_matrices[i]}")
            ni = len(self.Toffoli_layers_qubits[i])
            print_rows.append(f"# Toffoli inputs qubits({2*ni}):")
            print_rows.append(f"{self.CNOT_layers_qubits[i][:2*ni]}")
            print_rows.append(f"# Toffoli outputs qubits({ni}):")
            print_rows.append(f"{self.Toffoli_layers_qubits[i]}")
            print_rows.append(f"#########################")
        print_rows.append(f"# CNOT sub-circuit-Y")
        print_rows.append(f"# CNOT inputs qubits:")
        print_rows.append(f"{self.CNOT_layers_qubits[-1]}")
        print_rows.append(f"# state transform matrix:")
        print_rows.append(f"{self.state_transform_matrices[-1]}")
        print_rows.append(f"# outputs qubits:")
        print_rows.append(f"{self.CNOT_layers_qubits[-1][:self.m]}")

        # print("\n".join(print_rows))
        with open(save_file_name, "w") as f:
            f.write("\n".join(print_rows))
            
######################### auxiliary functions #########################
# matrix over GF(2)
def matGF2(mat_list: list):
    return matrix(GF(2), mat_list)

# L        : linear expressions
# n        : number of "X"(initial inputs)
# cols     : number of columns(variables)
# return ML: the matrix of linear expressions L(over GF(2))
# variables are "X"(initial inputs) and "M"(outputs of AND gates)
def linears_to_matrix(L: list, n: int, cols: int):
    rows = len(L)

    vars_to_idx = {}
    for i in range(n):
        vars_to_idx[f"X{i}"] = i 
    for i in range(cols-n):
        vars_to_idx[f"M{i}"] = n+i 
    
    ML = [[0 for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        rights = L[i].split("+")
        for j in rights:
            if j not in vars_to_idx.keys():
                continue
     
            ML[i][vars_to_idx[j]] = 1 

    return matGF2(ML)

def get_AES_Sbox_ANF(X):
    X0 = X[0]
    X1 = X[1]
    X2 = X[2]
    X3 = X[3]
    X4 = X[4]
    X5 = X[5]
    X6 = X[6]
    X7 = X[7]
    # 1005 XOR
    return[ X0*X1*X2*X3*X4*X5*X7 + X0*X1*X2*X3*X4*X6*X7 + X0*X1*X2*X3*X4*X6 + X0*X1*X2*X3*X4 + X0*X1*X2*X3*X5*X7 + X0*X1*X2*X3*X6 + X0*X1*X2*X3 + X0*X1*X2*X4*X5*X7 + X0*X1*X2*X4*X6*X7 + X0*X1*X2*X4*X6 + X0*X1*X2*X4*X7 + X0*X1*X2*X5*X6 + X0*X1*X2*X5 + X0*X1*X2*X6*X7 + X0*X1*X2*X6 + X0*X1*X3*X4*X5*X7 + X0*X1*X3*X4*X6*X7 + X0*X1*X3*X4*X7 + X0*X1*X3*X5*X6 + X0*X1*X3*X5 + X0*X1*X3*X6 + X0*X1*X3*X7 + X0*X1*X3 + X0*X1*X4*X5*X6*X7 + X0*X1*X4*X6 + X0*X1*X4*X7 + X0*X1*X5*X6*X7 + X0*X1*X5 + X0*X1*X7 + X0*X2*X3*X4*X5*X7 + X0*X2*X3*X4*X6*X7 + X0*X2*X3*X5*X6*X7 + X0*X2*X3*X6*X7 + X0*X2*X3*X6 + X0*X2*X3 + X0*X2*X4*X7 + X0*X2*X4 + X0*X2*X5*X6*X7 + X0*X2 + X0*X3*X4*X5*X7 + X0*X3*X4*X5 + X0*X3*X4*X6*X7 + X0*X3*X4*X6 + X0*X3*X4*X7 + X0*X3*X5*X7 + X0*X3*X6*X7 + X0*X3*X6 + X0*X4*X5*X6 + X0*X4*X5*X7 + X0*X4*X7 + X0*X5*X6*X7 + X0*X5*X7 + X0*X6 + X0*X7 + X0 + X1*X2*X3*X4*X5*X7 + X1*X2*X3*X4*X5 + X1*X2*X3*X4*X7 + X1*X2*X3*X4 + X1*X2*X3*X5*X6 + X1*X2*X3*X6*X7 + X1*X2*X3 + X1*X2*X4*X5*X6 + X1*X2*X4*X7 + X1*X2*X5 + X1*X2*X7 + X1*X3*X4*X5*X7 + X1*X3*X4*X7 + X1*X3*X5*X6*X7 + X1*X3*X5*X6 + X1*X3*X5*X7 + X1*X3*X5 + X1*X3 + X1*X4*X5*X6*X7 + X1*X4*X5*X7 + X1*X4*X6*X7 + X1*X4*X6 + X1*X4*X7 + X1*X5*X6 + X1*X5 + X1*X6*X7 + X1*X7 + X2*X3*X4*X5*X7 + X2*X3*X4*X6*X7 + X2*X3*X4 + X2*X3*X5*X6 + X2*X3*X7 + X2*X4*X5*X6 + X2*X4*X5*X7 + X2*X4*X5 + X2*X4*X6 + X2*X4*X7 + X2*X4 + X2*X5*X6*X7 + X2*X5*X7 + X2*X6*X7 + X2 + X3*X4*X5*X6*X7 + X3*X4*X5*X6 + X3*X4*X6*X7 + X3*X5*X6*X7 + X3*X5 + X3*X6*X7 + X3 + X4*X5*X6*X7 + X4*X5*X6 + X4*X5*X7 + X5*X6 + X5*X7 + X5
    ,X0*X1*X2*X3*X4*X6*X7 + X0*X1*X2*X3*X4*X6 + X0*X1*X2*X3*X4 + X0*X1*X2*X3*X5*X6*X7 + X0*X1*X2*X3*X6 + X0*X1*X2*X3*X7 + X0*X1*X2*X3 + X0*X1*X2*X4*X5 + X0*X1*X2*X4*X6*X7 + X0*X1*X2*X5*X6*X7 + X0*X1*X2*X5*X6 + X0*X1*X2*X5*X7 + X0*X1*X2 + X0*X1*X3*X4*X5 + X0*X1*X3*X4*X6*X7 + X0*X1*X3*X4*X7 + X0*X1*X3*X5*X6*X7 + X0*X1*X3*X5*X7 + X0*X1*X3*X6 + X0*X1*X3*X7 + X0*X1*X4*X6*X7 + X0*X1*X4 + X0*X1*X6*X7 + X0*X1*X6 + X0*X2*X3*X4*X6*X7 + X0*X2*X3*X4*X6 + X0*X2*X3*X5*X6*X7 + X0*X2*X3*X5*X7 + X0*X2*X3*X6*X7 + X0*X2*X3*X6 + X0*X2*X4*X5*X6 + X0*X2*X4*X5 + X0*X2*X4*X6 + X0*X2*X4 + X0*X2*X5*X7 + X0*X2*X7 + X0*X2 + X0*X3*X4*X5*X6*X7 + X0*X3*X4*X5*X6 + X0*X3*X4*X6 + X0*X3*X4*X7 + X0*X3*X5*X6 + X0*X3*X5 + X0*X3*X6 + X0*X3*X7 + X0*X4*X5*X6*X7 + X0*X4*X5*X7 + X0*X4*X5 + X0*X4*X6*X7 + X0*X4 + X0*X5*X6 + X0*X6 + X0*X7 + X1*X2*X3*X4*X6*X7 + X1*X2*X3*X4*X6 + X1*X2*X3*X5*X6*X7 + X1*X2*X3*X5*X6 + X1*X2*X3 + X1*X2*X4*X5*X6*X7 + X1*X2*X4*X5*X7 + X1*X2*X4*X5 + X1*X2*X6 + X1*X2*X7 + X1*X3*X4*X5 + X1*X3*X4*X6 + X1*X3*X4*X7 + X1*X3*X4 + X1*X3*X5*X7 + X1*X3*X5 + X1*X3*X6 + X1*X3*X7 + X1*X3 + X1*X4*X5*X6*X7 + X1*X4*X5*X6 + X1*X4*X5*X7 + X1*X4*X6*X7 + X1*X4*X6 + X1*X4*X7 + X1*X5*X6 + X1*X5*X7 + X1 + X2*X3*X4*X5*X6 + X2*X3*X4*X5*X7 + X2*X3*X4*X5 + X2*X3*X4*X6*X7 + X2*X3*X5*X6 + X2*X3*X5*X7 + X2*X3*X7 + X2*X4*X5*X6*X7 + X2*X4*X5*X6 + X2*X4*X5*X7 + X2*X4*X7 + X2*X4 + X2*X5*X6*X7 + X2*X5*X6 + X2*X5*X7 + X2*X6*X7 + X2*X7 + X2 + X3*X4*X5*X6 + X3*X4*X5 + X3*X4*X6*X7 + X3*X4*X6 + X3*X5*X6*X7 + X3*X5*X7 + X3*X6*X7 + X3*X7 + X4*X5 + X4*X6*X7 + X4*X6 + X4 + 1
    ,X0*X1*X2*X3*X5*X6*X7 + X0*X1*X2*X3*X5*X6 + X0*X1*X2*X3*X5*X7 + X0*X1*X2*X3*X5 + X0*X1*X2*X3*X7 + X0*X1*X2*X4*X5*X6*X7 + X0*X1*X2*X4*X5*X6 + X0*X1*X2*X4*X5 + X0*X1*X2*X6*X7 + X0*X1*X2*X7 + X0*X1*X2 + X0*X1*X3*X4*X5*X6 + X0*X1*X3*X4*X5*X7 + X0*X1*X3*X4*X6 + X0*X1*X3*X4 + X0*X1*X3*X6*X7 + X0*X1*X3*X7 + X0*X1*X4*X5*X7 + X0*X1*X5*X6*X7 + X0*X1*X5 + X0*X1*X6 + X0*X2*X3*X4*X7 + X0*X2*X3*X4 + X0*X2*X3*X5*X6*X7 + X0*X2*X3*X5*X7 + X0*X2*X3*X5 + X0*X2*X3*X6*X7 + X0*X2*X3*X6 + X0*X2*X3 + X0*X2*X4*X5*X6*X7 + X0*X2*X4*X5*X7 + X0*X2*X4*X6*X7 + X0*X2*X4*X6 + X0*X2*X4 + X0*X2*X5 + X0*X2*X6*X7 + X0*X2*X6 + X0*X2 + X0*X3*X4*X5*X6 + X0*X3*X4*X5*X7 + X0*X3*X4*X5 + X0*X3*X4*X6 + X0*X3*X4*X7 + X0*X3*X5*X6 + X0*X3*X5 + X0*X3*X6*X7 + X0*X3*X6 + X0*X3*X7 + X0*X4*X5*X6*X7 + X0*X4*X5 + X0*X4*X6*X7 + X0*X4*X6 + X0*X6*X7 + X0 + X1*X2*X3*X4*X5 + X1*X2*X3*X4*X6 + X1*X2*X3*X4*X7 + X1*X2*X3*X4 + X1*X2*X3*X5*X6*X7 + X1*X2*X3*X5*X6 + X1*X2*X3*X6*X7 + X1*X2*X4*X5*X6*X7 + X1*X2*X4*X5 + X1*X2*X4*X6 + X1*X2*X6*X7 + X1*X2*X6 + X1*X2*X7 + X1*X3*X4*X5*X6 + X1*X3*X4*X5 + X1*X3*X4*X6 + X1*X3*X5*X6*X7 + X1*X3*X6*X7 + X1*X3*X6 + X1*X3 + X1*X4*X5*X6*X7 + X1*X4*X5*X6 + X1*X4*X5 + X1*X4*X6 + X1*X5*X6 + X1*X5*X7 + X1*X6*X7 + X1*X6 + X1 + X2*X3*X4*X5*X6*X7 + X2*X3*X4*X5 + X2*X3*X4 + X2*X3*X5*X6*X7 + X2*X3*X5*X6 + X2*X3*X5*X7 + X2*X3*X5 + X2*X3*X6*X7 + X2*X4*X5*X6*X7 + X2*X4*X5*X6 + X2*X4*X5*X7 + X2*X4*X6 + X2*X4*X7 + X2*X5*X6*X7 + X2*X5*X6 + X2*X6*X7 + X2*X6 + X3*X4*X5*X6*X7 + X3*X4*X5*X7 + X3*X4*X6*X7 + X3*X4 + X3*X5*X6 + X3*X5*X7 + X3*X5 + X3*X6*X7 + X3 + X4*X5*X6*X7 + X4*X6*X7 + X4*X7 + X5*X6*X7 + 1
    ,X0*X1*X2*X3*X4*X5*X7 + X0*X1*X2*X3*X4*X7 + X0*X1*X2*X3*X4 + X0*X1*X2*X3*X5 + X0*X1*X2*X3*X6 + X0*X1*X2*X3*X7 + X0*X1*X2*X4*X5*X6 + X0*X1*X2*X4*X6 + X0*X1*X2*X4*X7 + X0*X1*X2*X4 + X0*X1*X2*X5*X6 + X0*X1*X2*X6*X7 + X0*X1*X2 + X0*X1*X3*X4*X5*X6*X7 + X0*X1*X3*X4*X5*X6 + X0*X1*X3*X4*X5 + X0*X1*X3*X4*X7 + X0*X1*X3*X4 + X0*X1*X3*X5*X7 + X0*X1*X3*X7 + X0*X1*X3 + X0*X1*X4*X6*X7 + X0*X1*X4*X7 + X0*X1*X4 + X0*X1*X5*X6*X7 + X0*X1*X5*X6 + X0*X1*X5 + X0*X1*X6*X7 + X0*X1*X6 + X0*X1*X7 + X0*X1 + X0*X2*X3*X4*X5*X6*X7 + X0*X2*X3*X4*X5*X6 + X0*X2*X3*X4*X5*X7 + X0*X2*X3*X4*X5 + X0*X2*X3*X4*X6 + X0*X2*X3*X4 + X0*X2*X3*X5*X6 + X0*X2*X3 + X0*X2*X4*X5*X6 + X0*X2*X4*X5*X7 + X0*X2*X4*X5 + X0*X2*X4*X6*X7 + X0*X2*X4*X7 + X0*X2*X4 + X0*X2*X5*X6*X7 + X0*X2*X5*X6 + X0*X2*X5*X7 + X0*X2*X6*X7 + X0*X2*X6 + X0*X2 + X0*X3*X4*X5*X6*X7 + X0*X3*X4*X5 + X0*X3*X4*X6 + X0*X3*X4*X7 + X0*X3*X4 + X0*X3*X5 + X0*X3*X7 + X0*X4*X5*X6*X7 + X0*X4*X6*X7 + X0*X4 + X0*X7 + X1*X2*X3*X4*X5*X6 + X1*X2*X3*X4*X5 + X1*X2*X3*X4*X6*X7 + X1*X2*X3*X4*X6 + X1*X2*X3*X5*X6*X7 + X1*X2*X3*X5*X6 + X1*X2*X3*X6*X7 + X1*X2*X3*X7 + X1*X2*X4*X5*X6*X7 + X1*X2*X4*X5*X6 + X1*X2*X4*X5*X7 + X1*X2*X4*X5 + X1*X2*X4*X7 + X1*X2*X4 + X1*X2*X5 + X1*X2*X6*X7 + X1*X3*X4*X5*X6 + X1*X3*X4*X5*X7 + X1*X3*X4*X6*X7 + X1*X3*X4*X7 + X1*X3*X4 + X1*X3*X5*X6 + X1*X3*X6*X7 + X1*X3*X7 + X1*X3 + X1*X4*X5*X6*X7 + X1*X4*X5 + X1*X4*X6*X7 + X1*X5*X6*X7 + X1*X5*X7 + X1*X6 + X1*X7 + X2*X3*X4*X5*X6*X7 + X2*X3*X4*X5*X7 + X2*X3*X4*X6 + X2*X3*X4*X7 + X2*X3*X4 + X2*X3*X5*X6*X7 + X2*X3*X5 + X2*X3*X6*X7 + X2*X3*X6 + X2*X3*X7 + X2*X3 + X2*X4*X5*X6 + X2*X4*X5 + X2*X4*X6*X7 + X2*X4*X6 + X2*X4*X7 + X2*X4 + X2*X5 + X2*X6 + X2*X7 + X2 + X3*X4*X5*X6*X7 + X3*X4*X5*X6 + X3*X4*X5*X7 + X3*X4*X5 + X3*X4*X7 + X3*X4 + X3*X5*X6 + X3*X6 + X3*X7 + X4*X5*X7 + X4*X5 + X4 + X5 + X6*X7 + X6 + X7
    ,X0*X1*X2*X3*X4*X5*X7 + X0*X1*X2*X3*X4*X5 + X0*X1*X2*X3*X4*X6*X7 + X0*X1*X2*X3*X4 + X0*X1*X2*X3*X5*X6 + X0*X1*X2*X3*X5 + X0*X1*X2*X3*X7 + X0*X1*X2*X3 + X0*X1*X2*X4*X5*X6*X7 + X0*X1*X2*X4*X5*X6 + X0*X1*X2*X4*X5*X7 + X0*X1*X2*X4*X6 + X0*X1*X2*X4*X7 + X0*X1*X2*X4 + X0*X1*X2*X5*X6 + X0*X1*X2*X5*X7 + X0*X1*X2*X6*X7 + X0*X1*X2*X6 + X0*X1*X2*X7 + X0*X1*X2 + X0*X1*X3*X4*X5*X6 + X0*X1*X3*X4*X5*X7 + X0*X1*X3*X4*X6 + X0*X1*X3*X4*X7 + X0*X1*X3*X4 + X0*X1*X3*X5*X6*X7 + X0*X1*X3*X5 + X0*X1*X3*X6 + X0*X1*X4*X5*X6*X7 + X0*X1*X4*X5*X7 + X0*X1*X4*X7 + X0*X1*X5*X6 + X0*X1*X5*X7 + X0*X1*X6*X7 + X0*X1 + X0*X2*X3*X4*X5*X6 + X0*X2*X3*X4*X5 + X0*X2*X3*X4*X6*X7 + X0*X2*X3*X4*X7 + X0*X2*X3*X5*X6*X7 + X0*X2*X3*X5*X7 + X0*X2*X3*X5 + X0*X2*X3*X6*X7 + X0*X2*X3*X6 + X0*X2*X4*X5*X6*X7 + X0*X2*X4*X5*X7 + X0*X2*X4 + X0*X2*X5*X6*X7 + X0*X2*X5*X6 + X0*X2*X5 + X0*X2 + X0*X3*X4*X5*X6*X7 + X0*X3*X4*X6*X7 + X0*X3*X4*X6 + X0*X3*X4 + X0*X3*X5*X6*X7 + X0*X3*X5*X6 + X0*X3*X5*X7 + X0*X4*X5*X6*X7 + X0*X4*X5*X6 + X0*X4*X5*X7 + X0*X4*X5 + X0*X4*X7 + X0*X4 + X0*X5*X6 + X0*X5*X7 + X0*X6*X7 + X0*X6 + X0*X7 + X0 + X1*X2*X3*X4*X5*X6*X7 + X1*X2*X3*X4*X5*X6 + X1*X2*X3*X4*X5 + X1*X2*X3*X4*X7 + X1*X2*X3*X4 + X1*X2*X3*X5*X6 + X1*X2*X3*X5*X7 + X1*X2*X3*X5 + X1*X2*X3*X6 + X1*X2*X3*X7 + X1*X2*X4*X5*X6*X7 + X1*X2*X4*X5*X6 + X1*X2*X4*X5*X7 + X1*X2*X4*X6*X7 + X1*X2*X4*X6 + X1*X2*X4 + X1*X2*X5*X6*X7 + X1*X2*X5*X7 + X1*X2*X6*X7 + X1*X2*X6 + X1*X2 + X1*X3*X4*X5*X6*X7 + X1*X3*X4*X6*X7 + X1*X3*X4*X6 + X1*X3*X4*X7 + X1*X3*X5*X7 + X1*X3*X6*X7 + X1*X3*X7 + X1*X4*X5*X6 + X1*X4*X6*X7 + X1*X4*X7 + X1*X4 + X1*X5*X6 + X1*X5*X7 + X1*X6*X7 + X1 + X2*X3*X4*X5*X7 + X2*X3*X4*X5 + X2*X3*X4*X6*X7 + X2*X3*X4*X6 + X2*X3*X5*X6 + X2*X3*X5 + X2*X3*X7 + X2*X3 + X2*X4*X5*X6*X7 + X2*X4*X5*X6 + X2*X4*X5 + X2*X5*X6*X7 + X2*X5*X6 + X2*X6*X7 + X3*X4*X5*X6*X7 + X3*X4*X5 + X3*X4*X6 + X3*X4*X7 + X3*X5*X6*X7 + X3*X5*X7 + X3*X6*X7 + X3 + X4*X5*X6*X7 + X4*X5*X6 + X4*X5*X7 + X4*X5 + X4*X6*X7 + X4*X7 + X5*X6 + X7
    ,X0*X1*X2*X3*X4*X5*X6 + X0*X1*X2*X3*X4*X5*X7 + X0*X1*X2*X3*X4*X5 + X0*X1*X2*X3*X4*X6*X7 + X0*X1*X2*X3*X4 + X0*X1*X2*X3*X5*X7 + X0*X1*X2*X3*X6*X7 + X0*X1*X2*X3*X6 + X0*X1*X2*X3*X7 + X0*X1*X2*X3 + X0*X1*X2*X4*X5*X6*X7 + X0*X1*X2*X4*X5*X7 + X0*X1*X2*X4*X5 + X0*X1*X2*X4*X6*X7 + X0*X1*X2*X4*X6 + X0*X1*X2*X4*X7 + X0*X1*X2*X4 + X0*X1*X2*X5*X7 + X0*X1*X2*X5 + X0*X1*X2*X6 + X0*X1*X3*X4*X5*X6*X7 + X0*X1*X3*X4*X5*X6 + X0*X1*X3*X4*X5*X7 + X0*X1*X3*X4*X5 + X0*X1*X3*X4*X6*X7 + X0*X1*X3*X4*X6 + X0*X1*X3*X5*X6 + X0*X1*X3*X5 + X0*X1*X3*X6*X7 + X0*X1*X3 + X0*X1*X4*X5*X6 + X0*X1*X4*X6*X7 + X0*X1*X4*X6 + X0*X1*X5*X6*X7 + X0*X1*X5*X6 + X0*X1*X5 + X0*X1*X7 + X0*X1 + X0*X2*X3*X4*X5*X6 + X0*X2*X3*X4*X6*X7 + X0*X2*X3*X4*X7 + X0*X2*X3*X5*X6*X7 + X0*X2*X3*X5*X6 + X0*X2*X3*X5 + X0*X2*X3*X6 + X0*X2*X4*X5*X7 + X0*X2*X4*X6*X7 + X0*X2*X4*X6 + X0*X2*X4*X7 + X0*X2*X5*X6*X7 + X0*X2*X5*X6 + X0*X2*X6 + X0*X2*X7 + X0*X3*X4*X5*X6*X7 + X0*X3*X4*X5*X7 + X0*X3*X4*X5 + X0*X3*X4*X6*X7 + X0*X3*X4*X7 + X0*X3*X5*X6*X7 + X0*X3*X5*X6 + X0*X3*X5*X7 + X0*X3*X6 + X0*X3*X7 + X0*X3 + X0*X4*X5*X6*X7 + X0*X4*X5*X7 + X0*X4*X5 + X0*X4*X6 + X0*X4*X7 + X0*X5*X6*X7 + X0*X5*X6 + X0*X5*X7 + X0*X6*X7 + X0*X7 + X0 + X1*X2*X3*X4*X5*X7 + X1*X2*X3*X4*X6 + X1*X2*X3*X4 + X1*X2*X3*X5*X6*X7 + X1*X2*X3*X5*X6 + X1*X2*X3*X5*X7 + X1*X2*X3*X5 + X1*X2*X4*X5*X6*X7 + X1*X2*X4*X5 + X1*X2*X4*X7 + X1*X2*X4 + X1*X2*X6*X7 + X1*X2*X6 + X1*X2 + X1*X3*X4*X5*X6*X7 + X1*X3*X4*X5*X6 + X1*X3*X4*X5 + X1*X3*X4*X6*X7 + X1*X3*X4*X7 + X1*X3*X4 + X1*X3*X5*X7 + X1*X3*X6*X7 + X1*X3*X7 + X1*X4*X5*X6*X7 + X1*X4*X5*X6 + X1*X4*X5 + X1*X4*X6*X7 + X1*X4*X7 + X1*X5*X6 + X1*X6*X7 + X1*X7 + X2*X3*X4*X5*X6*X7 + X2*X3*X4*X5*X6 + X2*X3*X4 + X2*X3*X5*X6*X7 + X2*X3*X5 + X2*X3*X6 + X2*X3*X7 + X2*X4*X5*X6*X7 + X2*X4*X5*X6 + X2*X4*X5*X7 + X2*X4*X6*X7 + X2*X4*X6 + X2*X4*X7 + X2*X5*X6*X7 + X2*X5*X6 + X2*X5*X7 + X2*X6*X7 + X2*X7 + X2 + X3*X4*X5*X6*X7 + X3*X4*X5*X6 + X3*X4*X5*X7 + X3*X4*X5 + X3*X4*X6*X7 + X3*X4*X6 + X3*X4*X7 + X3*X4 + X3*X5*X6 + X3*X5*X7 + X3*X6*X7 + X3*X6 + X3*X7 + X4*X5*X7 + X4*X5 + X4*X6*X7 + X4*X7 + X5*X7 + X6 + X7
    ,X0*X1*X2*X3*X4*X6*X7 + X0*X1*X2*X3*X4*X6 + X0*X1*X2*X3*X5*X6*X7 + X0*X1*X2*X3*X5 + X0*X1*X2*X3*X7 + X0*X1*X2*X4*X5*X6*X7 + X0*X1*X2*X4*X5*X6 + X0*X1*X2*X4*X5*X7 + X0*X1*X2*X4*X7 + X0*X1*X2*X5*X6*X7 + X0*X1*X2*X5*X7 + X0*X1*X2*X6*X7 + X0*X1*X2 + X0*X1*X3*X4*X5*X6*X7 + X0*X1*X3*X4*X5*X6 + X0*X1*X3*X4*X5*X7 + X0*X1*X3*X4*X5 + X0*X1*X3*X4*X6*X7 + X0*X1*X3*X4 + X0*X1*X3*X5*X6*X7 + X0*X1*X3*X5 + X0*X1*X3*X6 + X0*X1*X3*X7 + X0*X1*X4*X5*X7 + X0*X1*X4*X6*X7 + X0*X1*X4 + X0*X1*X5*X6*X7 + X0*X1*X5*X6 + X0*X1*X5 + X0*X1*X7 + X0*X2*X3*X4*X5*X7 + X0*X2*X3*X4*X5 + X0*X2*X3*X4*X6 + X0*X2*X3*X4*X7 + X0*X2*X3*X4 + X0*X2*X3*X5*X6*X7 + X0*X2*X3*X5 + X0*X2*X3*X6 + X0*X2*X3*X7 + X0*X2*X4*X5*X7 + X0*X2*X4*X5 + X0*X2*X4*X6*X7 + X0*X2*X4*X6 + X0*X2*X4 + X0*X2*X5*X6 + X0*X2*X5 + X0*X2*X7 + X0*X3*X4*X5*X6*X7 + X0*X3*X4*X5*X7 + X0*X3*X4*X5 + X0*X3*X4*X6*X7 + X0*X3*X4*X6 + X0*X3*X4 + X0*X3*X5*X6*X7 + X0*X3*X5*X6 + X0*X3*X6*X7 + X0*X3*X6 + X0*X3*X7 + X0*X4*X5*X6*X7 + X0*X4*X6 + X0*X4 + X0*X5*X7 + X0*X5 + X0*X6 + X0*X7 + X0 + X1*X2*X3*X4*X5*X6 + X1*X2*X3*X4*X5*X7 + X1*X2*X3*X4*X6*X7 + X1*X2*X3*X4*X6 + X1*X2*X3*X4 + X1*X2*X3*X5*X6 + X1*X2*X3*X5*X7 + X1*X2*X3*X6*X7 + X1*X2*X3*X7 + X1*X2*X4*X5*X6*X7 + X1*X2*X4*X5*X6 + X1*X2*X4*X6*X7 + X1*X2*X4*X6 + X1*X2*X4 + X1*X2*X5*X6 + X1*X2*X5*X7 + X1*X2*X6*X7 + X1*X2*X6 + X1*X3*X4*X5*X6*X7 + X1*X3*X4*X5*X6 + X1*X3*X4*X6*X7 + X1*X3*X4*X7 + X1*X3*X4 + X1*X3*X5*X6*X7 + X1*X3*X7 + X1*X3 + X1*X4*X5*X6*X7 + X1*X4*X5*X7 + X1*X4*X5 + X1*X4*X6*X7 + X1*X4*X6 + X1*X5*X6*X7 + X1*X5 + X1*X6*X7 + X1 + X2*X3*X4*X5*X7 + X2*X3*X4*X5 + X2*X3*X4*X6 + X2*X3*X4*X7 + X2*X3*X5*X6*X7 + X2*X3*X5*X7 + X2*X3*X6*X7 + X2*X3*X7 + X2*X3 + X2*X4*X5*X6 + X2*X4*X5 + X2*X4*X6 + X3*X4*X5*X6*X7 + X3*X4*X5 + X3*X4*X6*X7 + X3*X4*X6 + X3*X4*X7 + X3*X5*X6 + X3*X6*X7 + X3*X6 + X3*X7 + X4*X5*X6 + X4*X5*X7 + X4*X5 + X4*X6*X7 + X4*X6 + X4*X7 + X4 + X5*X7 + X6*X7 + X7 + 1
    ,X0*X1*X2*X3*X4*X5*X7 + X0*X1*X2*X3*X4*X5 + X0*X1*X2*X3*X4*X6 + X0*X1*X2*X3*X5*X6*X7 + X0*X1*X2*X3*X5*X6 + X0*X1*X2*X3*X5 + X0*X1*X2*X3*X6*X7 + X0*X1*X2*X4*X5*X7 + X0*X1*X2*X4*X7 + X0*X1*X2*X4 + X0*X1*X2*X5*X6*X7 + X0*X1*X2*X5*X6 + X0*X1*X2*X6*X7 + X0*X1*X2*X6 + X0*X1*X2 + X0*X1*X3*X4*X5*X6*X7 + X0*X1*X3*X4*X5*X6 + X0*X1*X3*X4*X6*X7 + X0*X1*X3*X4*X7 + X0*X1*X3*X5*X6 + X0*X1*X3*X5*X7 + X0*X1*X3*X7 + X0*X1*X4*X5*X6*X7 + X0*X1*X4*X5 + X0*X1*X4*X6*X7 + X0*X1*X4*X6 + X0*X1*X4 + X0*X1*X5*X6*X7 + X0*X1*X5*X6 + X0*X1*X5 + X0*X1 + X0*X2*X3*X4*X5*X7 + X0*X2*X3*X4*X5 + X0*X2*X3*X4*X6 + X0*X2*X3*X4*X7 + X0*X2*X3*X5*X6*X7 + X0*X2*X3*X5*X7 + X0*X2*X3*X5 + X0*X2*X3*X6 + X0*X2*X3*X7 + X0*X2*X4*X5*X6*X7 + X0*X2*X4*X5*X6 + X0*X2*X4*X5 + X0*X2*X4*X6*X7 + X0*X2*X4 + X0*X2*X5*X6*X7 + X0*X2*X5*X7 + X0*X2*X5 + X0*X2 + X0*X3*X4*X5*X6*X7 + X0*X3*X4 + X0*X3*X5*X6*X7 + X0*X3*X5*X6 + X0*X3*X5*X7 + X0*X3*X5 + X0*X3*X6*X7 + X0*X3*X7 + X0*X4*X5*X6*X7 + X0*X4*X5*X6 + X0*X4*X5*X7 + X0*X4*X5 + X0*X4*X6 + X0*X5*X6*X7 + X0*X5*X7 + X0*X5 + X0*X6*X7 + X1*X2*X3*X4*X5*X7 + X1*X2*X3*X4*X5 + X1*X2*X3*X4*X7 + X1*X2*X3*X5*X6 + X1*X2*X3*X5 + X1*X2*X3*X6*X7 + X1*X2*X3*X6 + X1*X2*X3*X7 + X1*X2*X3 + X1*X2*X4*X5*X6 + X1*X2*X4*X6*X7 + X1*X2*X4*X7 + X1*X2*X5*X7 + X1*X2*X5 + X1*X2*X6 + X1*X2 + X1*X3*X4*X5*X6*X7 + X1*X3*X4*X5*X7 + X1*X3*X4*X6*X7 + X1*X3*X4*X6 + X1*X3*X4*X7 + X1*X3*X5*X6 + X1*X3*X6 + X1*X3*X7 + X1*X3 + X1*X4*X5*X6*X7 + X1*X4*X5*X6 + X1*X4*X7 + X1*X5*X6*X7 + X1*X5*X6 + X1*X5*X7 + X1*X5 + X1*X6*X7 + X1*X6 + X1*X7 + X2*X3*X4*X5*X7 + X2*X3*X5*X6*X7 + X2*X3*X5*X7 + X2*X3*X6*X7 + X2*X4*X5*X6 + X2*X4*X5*X7 + X2*X4*X5 + X2*X4*X7 + X2*X5*X6*X7 + X2*X5*X7 + X2*X7 + X3*X4*X5*X6*X7 + X3*X4*X6 + X3*X4*X7 + X3*X5*X6 + X3*X5*X7 + X3*X5 + X3*X6*X7 + X3*X6 + X3*X7 + X3 + X4*X5*X6*X7 + X4*X5*X6 + X4*X5 + X4*X6 + X4 + X5*X6 + X5 + X6*X7 + X7 + 1]

######################### main functions #########################
# C: classical circuit (uses {NOT, XOR, AND})
# inputs must be "X", outputs must be "Y"
# C has 3 kinds of operations
# (1) NOT: "X=X+1"
# (2) XOR: "X0=X1+X2"
# (3) AND: "X0=X1*X2"
# return the affine expressions (the inputs of AND gates and outputs Y)
# affine(X, M), M is AND variable
# k AND gates have 2k inputs 
def extract_linear(n: int, m: int, C: list):
    AND_vars = []
    AND_vars_inputs = {}
    # AND-depth
    vars_AND_depth = {"1" : 0}
    for i in range(n):
        vars_AND_depth[f"X{i}"] = 0 
 
    AND_depth = 0
    # AND_vars depth layer
    AND_depth_layer = [[]]
    # extract all AND-variable in classical circuit
    for oper in C:
        oper = oper.replace(" ", "")
        x1 = oper.split("=")[0]
        # "x1=x2+x3"
        if "+" in oper:
            x2 = oper.split("=")[1].split("+")[0]
            x3 = oper.split("=")[1].split("+")[1]
            vars_AND_depth[x1] = max(vars_AND_depth[x2], vars_AND_depth[x3])
        # "x1=x2*x3" 
        if "*" in oper:
            x2 = oper.split("=")[1].split("*")[0]
            x3 = oper.split("=")[1].split("*")[1]
            AND_vars.append(x1)
            AND_vars_inputs[x1] = [x2, x3]
            # AND depth +1
            vars_AND_depth[x1] = 1+max(vars_AND_depth[x2], vars_AND_depth[x3])
            
            if vars_AND_depth[x1] > AND_depth:
                AND_depth = vars_AND_depth[x1]
                AND_depth_layer.append([])
            
            AND_depth_layer[vars_AND_depth[x1]].append(x1)
     
    AND_vars_n = len(AND_vars)

    # Set inputs(X) and AND-variable(M) as a basis
    # Others can be expressed as affine(X, M)
    # variable over Boolean Polynomial Ring
    BV_vars_str = ["1"] + [f"X{i}" for i in range(n)] + [f"M{i}" for i in range(AND_vars_n)]
    BV = BooleanPolynomialRing(names=BV_vars_str[1:])

    # map all strings to Boolean variables
    vars_to_BV_maps = {"1" : 1}
    for i in range(n):
        vars_to_BV_maps[f"X{i}"] =  BV(f"X{i}")
    # need to reorder the seq of AND-vars
    # eg: the AND_vars[i] maybe not the M[i]  
    # get the AND vars real seq [[AND-1], [AND-2], [AND-s]]
    idx = 0
    for d in range(1, AND_depth+1):
        AND_vars_d = AND_depth_layer[d]
        for v in AND_vars_d:
            vars_to_BV_maps[v] = BV(f"M{idx}")
            idx += 1

    # convert to Boolean operation(XOR)
    for oper in C:
        oper = oper.replace(" ", "")
        if "*" in oper:
            continue 
        # "x1=x2+x3"
        x1 = oper.split("=")[0]
        x2 = oper.split("=")[1].split("+")[0]
        x3 = oper.split("=")[1].split("+")[1]

        x2_v = vars_to_BV_maps[x2]
        x3_v = vars_to_BV_maps[x3]
        vars_to_BV_maps[x1] = x2_v + x3_v
  
    # 1+s+1 layer(initial inputs + s-layer + outputs Y)
    # L = [[X(x)], [AND-1-L], [AND-2-L],..., [AND-s-L], [Y]]
    L = [[] for i in range(AND_depth+2)]
    L[0] = [f"X{i}" for i in range(n)]
    for d in range(1, AND_depth+1):
        AND_vars_d = AND_depth_layer[d]
        for v in AND_vars_d:
            x1 = AND_vars_inputs[v][0]
            x2 = AND_vars_inputs[v][1]
            L[d].append(f"{vars_to_BV_maps[x1]}".replace(" ", ""))
            L[d].append(f"{vars_to_BV_maps[x2]}".replace(" ", ""))
 
    for i in range(m):
        L[-1].append(f"{vars_to_BV_maps[f'Y{i}']}".replace(" ", ""))

    return L

# zero states    : can be restored to "0" only use CNOT gates
# nonzero states : cannot be restored to "0" only use CNOT gates
#                  including initial inputs and outputs of Toffoli gates
# eg: ["X0", "X1", "X0"], the first (or the second) "X0" is a zero state
# we have a rule to select zero states
# for a linear B with rank(B)=dim, there are size(B)-dim zero states
# select k=dim nonzero states from front(0) to back(size-1) such that rank is dim
# the remainder size(B)-dim states are zero states(eg: the second "X0")
def check_two_states_qubits(states: list, n: int, dim: int):
    states_n = len(states)

    # r states, rank is r
    nonzero_states = []
    nonzero_qubits = []

    for i in range(states_n): 
        rank1 = linears_to_matrix(L=nonzero_states, n=n, cols=dim).rank()
        # rank = r
        if rank1 == dim:
            break 
        
        state = states[i]
        nonzero_states.append(state)
        rank2 = linears_to_matrix(L=nonzero_states, n=n, cols=dim).rank()

        # rank does not increase. Do not select this state
        if rank2 == rank1:
            nonzero_states.pop()
        else:
            nonzero_qubits.append(i)
 
    zero_qubits = list(set([i for i in range(states_n)]) - set(nonzero_qubits))

    return nonzero_qubits, zero_qubits

# select some S[i-1] to S[i]
# initial_states   : necessary states
# candidate_states : selectable states
# n                : number of initial variables
# dim              : number of variables
# target_n         : number of target state
# select some states from candidate_states and add them to initial_states
# such that rank(selected_states) = dim, full column rank
def select_step(initial_states: list, candidate_states: list, n:int, dim: int, target_n: int):
    states_n = len(candidate_states)
    selected_states = initial_states[:]
    # print(f"initial size: {len(selected_states)}")
    # idx of nonzeros states(can add rank)
    nonzero_states_idxs = []
    # 1. select nonzeros states such that rank = dim
    for i in range(states_n):
        rank1 = linears_to_matrix(L=selected_states, n=n, cols=dim).rank()
        # rank = dim
        if rank1 == dim:
            break 

        state = candidate_states[i]
        selected_states.append(state)
        rank2 = linears_to_matrix(L=selected_states, n=n, cols=dim).rank()

        # rank does not increas. Do not select this state
        if rank2 == rank1:
            selected_states.pop()
        else:
            nonzero_states_idxs.append(i)

    # 2. select (target_n-dim) zero states
    zero_states_idxs = list(set([i for i in range(states_n)]) - set(nonzero_states_idxs))
  
    # fill size to target_n
    zero_states = [candidate_states[i] for i in zero_states_idxs[:target_n-len(selected_states)]]
    selected_states = selected_states + zero_states

    return selected_states

# transform S_pre to S
# (1) size(S_pre) = size(S)
# (2) rank(S_pre) = rank(S) = dim(number of columns)
def get_state_transform_matrix(S_pre, S, n, dim):
    rows = len(S_pre)

    # Si_pre -> A, Si -> B, find an invertible matrix MT
    # such that MT * A = B
    A = linears_to_matrix(L=S_pre, n=n, cols=dim)
    B = linears_to_matrix(L=S, n=n, cols=dim)
    IMA = A.extended_echelon_form(transformation=True)
    IMB = B.extended_echelon_form(transformation=True)

    # the nxn matrices in right
    MA = [[0 for j in range(rows)] for i in range(rows)]
    MB = [[0 for j in range(rows)] for i in range(rows)]

    for i in range(rows):
        for j in range(rows):
            MA[i][j] = IMA[i][dim+j]
            MB[i][j] = IMB[i][dim+j]

    MT = matGF2(MB).inverse() * matGF2(MA)

    return MT

# the last AND(Toffoli) layer to outputs layer
# CNOT-s -> Toffoli-s -> CNOT-outputs
# n          : number of inputs  x
# m          : number of outputs y
# cur_dim    : current number of variables
# cur_states : current states
# Bs         : CNOT-s linear(affine) expressions
# By         : outputs Y linear(affine) expressions
def output_part(n: int, m: int, cur_dim: int, cur_states: list, Bs: list, By: list):
    dim = cur_dim
    states = cur_states[:]
    width = len(states)
    qubits = [i for i in range(width)]
    # need to store
    CNOT_layers_qubits = []
    Toffoli_layers_qubits = []
    state_transform_matrices = []

    # AND-layer-s
    ns = len(Bs) // 2
    a = 2*ns - linears_to_matrix(Bs, n=n, cols=dim).rank()

    nonzero_qubits, zero_qubits = check_two_states_qubits(states=states, n=n, dim=dim)
    zero_states    = [states[i] for i in zero_qubits]
    nonzero_states = [states[i] for i in nonzero_qubits]
    zero_states_n = len(zero_states)

    # additionally consider outputs qubits(at least m newly allocated)
    allocate_qubits_n = m
    clean_for_Toffoli_outputs = 0 
    # (1) last outputs of Toffoli layer less than m
    if ns <= m:
        # use zero states for inputs of Toffoli gates(zero_states_n - a < 0)
        # allocate (a - zero_states_n) > 0, or no need to allocate
        allocate_qubits_n += max(a - zero_states_n, 0)
    # (2) ns > m, some outputs of Toffoli can store in old qubits
    else:     
        # CNOT sub-circuit needs to allocate qubits(obviously Toffoli layer also needs)
        if a - zero_states_n > 0:
            allocate_qubits_n += (a - zero_states_n) + (ns - m)
        # CNOT sub-circuit does not need to allocate qubits
        else:
            clean_for_Toffoli_outputs = min(zero_states_n - a, ns - m)
            # Toffoli layer needs to allocate qubits
            allocate_qubits_n += (ns - m) - clean_for_Toffoli_outputs

    # allocate qubits (last m qubits storing the outputs Y)
    print(f"##### allocate qubits: {allocate_qubits_n} #####")

    zero_states += ["" for i in range(allocate_qubits_n)]
    zero_qubits += [width+i for i in range(allocate_qubits_n)]
    states      += ["" for i in range(allocate_qubits_n)]
    qubits      += [width+i for i in range(allocate_qubits_n)]
    width       += allocate_qubits_n
    
    # CNOT (1) nonzero (2) zero(inputs) (3) zero(outputs)
    CNOT_n = dim + a + clean_for_Toffoli_outputs
    # qubits of CNOT and Toffoli layer
    CNOT_qubits = nonzero_qubits[:] + zero_qubits[:a+clean_for_Toffoli_outputs]
    if ns >= m:
        Toffoli_qubits = zero_qubits[a:a+(ns-m)] + zero_qubits[-m:]
    else:
        Toffoli_qubits = zero_qubits[-m:-m+ns]
    
    # the inputs and outputs of the CNOT sub-circuit
    Ss_pre_states = nonzero_states[:] + zero_states[:a+clean_for_Toffoli_outputs]      
    Ss_states = select_step(initial_states=Bs, candidate_states=Ss_pre_states
                , n=n, dim=dim, target_n=CNOT_n-clean_for_Toffoli_outputs)
    # clean up Toffoli outputs
    Ss_states += ["" for i in range(clean_for_Toffoli_outputs)]
    
    # find a CNOT circuit(invertible matrix MT) that maps S'[s-1] to S'[s]
    MT = get_state_transform_matrix(S_pre=Ss_pre_states, S=Ss_states, n=n, dim=dim)
  
    # update states of CNOT and Toffoli layer
    for j in range(CNOT_n):
        cj = CNOT_qubits[j]
        states[cj] = Ss_states[j]
    
    # ni Toffoli variables(use "M") 
    for j in range(ns):
        tj = Toffoli_qubits[j]
        states[tj] = f"M{cur_dim-n+j}"
    dim += ns
    
    # need to store three parts
    CNOT_layers_qubits.append(CNOT_qubits)
    Toffoli_layers_qubits.append(Toffoli_qubits)
    state_transform_matrices.append(MT)

    outputs_qubits = qubits[-m:]
    ay = len(By) - linears_to_matrix(By, n=n, cols=dim).rank()

    nonzero_qubits, zero_qubits = check_two_states_qubits(states=states, n=n, dim=dim)
    zero_states    = [states[i] for i in zero_qubits]
    nonzero_states = [states[i] for i in nonzero_qubits]

    # m > ns, outputs Y store in the last allocated qubits
    CNOT_n = dim + ay + max(0, m - ns)

    # before m qubits are outputs qubits
    CNOT_qubits = outputs_qubits[:]
    for q in nonzero_qubits:
        if q not in CNOT_qubits:
            CNOT_qubits.append(q)
    
    CNOT_qubits += zero_qubits[:ay]

    Y_pre_states = [states[i] for i in CNOT_qubits]
    Y_states = select_step(initial_states=By
            , candidate_states=Y_pre_states[m:] if m >= ns else Y_pre_states
            , n=n, dim=dim, target_n=CNOT_n)
    
    MT_Y = get_state_transform_matrix(S_pre=Y_pre_states, S=Y_states, n=n, dim=dim)
    CNOT_layers_qubits.append(CNOT_qubits)
    state_transform_matrices.append(MT_Y)

    output_part_returns = [dim, width, CNOT_layers_qubits, Toffoli_layers_qubits, state_transform_matrices]
    return output_part_returns

# Algorithm  : classical to quantum
# n          : number of inputs  x
# m          : number of outputs y
# s          : AND-depth
# C          : classical circuit (uses gates[NOT, XOR, AND])
def classical_to_quantum(n: int, m: int, s: int, C: list):
    print(f"##### classical to quantum #####")
    print(f"##### AND-depth: {s} #####")
    # 1+s+1 linear expressions
    B = C[:]
    if "=" in C[0]:  
        B = extract_linear(n=n, m=m, C=C)
    # width: all qubits
    width = n 
    print(f"##### allocate qubits: {n} #####")
    # linear(affine) states use string, eg: "X0+M1"
    states = [f"X{i}" for i in range(n)]
    # index
    qubits = [i for i in range(n)]

    # number of variable(columns of matrix, n+n1+n2+...ns)
    dim = n 

    # need to store
    state_transform_matrices = []
    CNOT_layers_qubits = []
    Toffoli_layers_qubits = []
    # 2. each AND layer to Toffoli(QAND) layer
    # note that the index starts from 1(not 0) is the inputs of AND-layer-1
    # idx 0 is the initial n inputs X
    for i in range(1, s):
        # print(f"##### AND-Layer-{i} #####")
        # ni: number of AND gates in this layer(2ni inputs)
        ni = len(B[i]) // 2

        # ai: number of ancilla qubits in the CNOT sub-circuit
        ai = 2*ni - linears_to_matrix(B[i], n=n, cols=dim).rank()

        nonzero_qubits, zero_qubits = check_two_states_qubits(states=states, n=n, dim=dim)
        zero_states    = [states[j] for j in zero_qubits]
        nonzero_states = [states[j] for j in nonzero_qubits]
        zero_states_n = len(zero_states)
  
        # firstly use zero states for inputs of Toffoli gates 
        # if still zero states left, can be cleaned to "0" for outputs of Toffoli gates
        clean_for_Toffoli_outputs = min(zero_states_n - ai, ni)
        # no zero states can be cleaned to 0
        if clean_for_Toffoli_outputs < 0:
            clean_for_Toffoli_outputs = 0
        
        allocate_qubits_n = ni + ai - zero_states_n
   
        # allocate qubits, then size(zero_states) >= ni+ai 
        if allocate_qubits_n > 0:
            print(f"##### allocate qubits: {allocate_qubits_n} #####")
            zero_states += ["" for j in range(allocate_qubits_n)]
            zero_qubits += [width+j for j in range(allocate_qubits_n)]
            states      += ["" for j in range(allocate_qubits_n)]
            qubits      += [width+j for j in range(allocate_qubits_n)]
            width       += allocate_qubits_n
        
        # CNOT (1)nonzero (2) zero(inputs) (3) zero(outputs)
        CNOT_n = dim + ai + clean_for_Toffoli_outputs
        # qubits for CNOT and Toffoli layer
        CNOT_qubits = nonzero_qubits[:] + zero_qubits[:ai+clean_for_Toffoli_outputs]
        Toffoli_qubits = zero_qubits[ai:ai+ni]
        
        # the inputs and outputs of CNOT sub-circuit
        Si_pre_states = nonzero_states[:] + zero_states[:ai+clean_for_Toffoli_outputs]      
        Si_states = select_step(initial_states=B[i], candidate_states=Si_pre_states
                                , n=n, dim=dim, target_n=CNOT_n-clean_for_Toffoli_outputs)
        
        # clean up Toffoli outputs
        Si_states += ["" for j in range(clean_for_Toffoli_outputs)]
        
        # find a CNOT circuit (invertible matrix MT) that maps S'[i-1] to S'[i]
        MT = get_state_transform_matrix(S_pre=Si_pre_states, S=Si_states, n=n, dim=dim)
        
        # update states of the CNOT and Toffoli layer
        for j in range(CNOT_n):
            cj = CNOT_qubits[j]
            states[cj] = Si_states[j]
        
        # ni Toffoli variables(use "M") 
        for j in range(ni):
            tj = Toffoli_qubits[j]
            states[tj] = f"M{dim-n+j}"
        dim += ni
        
        # need to store three parts
        CNOT_layers_qubits.append(CNOT_qubits)
        Toffoli_layers_qubits.append(Toffoli_qubits)
        state_transform_matrices.append(MT)

    # output_part() return results
    output_part_returns = output_part(n=n, m=m, cur_dim=dim, cur_states=states, Bs=B[s], By=B[s+1])
    dim                       = output_part_returns[0]
    width                     = output_part_returns[1]
    CNOT_layers_qubits       += output_part_returns[2]
    Toffoli_layers_qubits    += output_part_returns[3]
    state_transform_matrices += output_part_returns[4]

    print(f"##### width: {width} #####")
    qc_info = quantum_circuit_info(n, m, s, width, CNOT_layers_qubits
                                   , Toffoli_layers_qubits, state_transform_matrices)

    return qc_info

# verify quantum circuit by CNOT sub-circuit, Toffoli layer
def verify_quantum_circuit(qc_info: quantum_circuit_info, outputs_ANF: list):
    n                        = qc_info.n 
    m                        = qc_info.m
    s                        = qc_info.s
    width                    = qc_info.width
    CNOT_layers_qubits       = qc_info.CNOT_layers_qubits
    Toffoli_layers_qubits    = qc_info.Toffoli_layers_qubits
    state_transform_matrices = qc_info.state_transform_matrices
    # variable X over Boolean Polynomial Ring
    BV = BooleanPolynomialRing(names=[f"X{i}" for i in range(n)])
    # states
    N = [BV(f"X{i}") for i in range(n)] + [0 for i in range(width-n)]

    # CNOT sub-circuit -> Toffoli layer->...
    for i in range(s):
        CNOT_qubits = CNOT_layers_qubits[i]
        Toffoli_qubits = Toffoli_layers_qubits[i]
        MT = state_transform_matrices[i]

        CNOT_inputs = [N[j] for j in CNOT_qubits]
        CNOT_outputs = MT * vector(CNOT_inputs)
        
        # CNOT sub-circuit
        for j in range(len(CNOT_qubits)):
            cj = CNOT_qubits[j]
            N[cj] = CNOT_outputs[j]

        # Toffoli layer
        for j in range(len(Toffoli_qubits)):
            tj = Toffoli_qubits[j]
            N[tj] += CNOT_outputs[2*j] * CNOT_outputs[2*j+1]
    
    # outputs(CNOT) layer
    CNOT_qubits = CNOT_layers_qubits[-1]   
    MT_Y = state_transform_matrices[-1]
    CNOT_inputs = [N[j] for j in CNOT_qubits]
    CNOT_outputs = MT_Y * vector(CNOT_inputs)
    for j in range(len(CNOT_qubits)):
        cj = CNOT_qubits[j]
        N[cj] = CNOT_outputs[j]

    print(f"##### verify T-depth-{s} quantum circuit #####")
    print(f"##### width: {width} #####")
    print(f"##### Y store in qubits: {CNOT_qubits[:m]} #####")
    Y = CNOT_outputs[:m]
    # verify ANF(without NOT gate(+1))
    print([Y[i] + outputs_ANF[i] in [0, 1] for i in range(m)])
    print("\n#############################################")

"""
CNOT matrix to CNOT gates
X: CNOT inputs
M: CNOT matrix
Y = M * X => Y = PLU * X
"""
def get_CNOT_circuit_PLU(X, M):
    n = len(X)
    # PLU decomposition
    P, L, U = M.LU()
    CNOT_opers = []
    # U: add row-j to row-i(j > i)
    for i in range(n):
        for j in range(i + 1, n):
            if U[i][j] == 1:
                CNOT_opers.append([X[j], X[i]])
                
    # L: add row-j to row-i(j < i)
    for i in range(n - 1, 0, -1):
        for j in range(i):
            if L[i][j] == 1:
                CNOT_opers.append([X[j], X[i]])

    CNOT_outputs = list(P * vector(X))
    return CNOT_opers, CNOT_outputs

"""
generate QASM format quantum circuit
"""
def generate_quantum_circuit(qc_info: quantum_circuit_info, outputs_ANF: list, filename="test.qasm"):
    n                        = qc_info.n 
    m                        = qc_info.m
    s                        = qc_info.s
    width                    = qc_info.width
    CNOT_layers_qubits       = qc_info.CNOT_layers_qubits
    Toffoli_layers_qubits    = qc_info.Toffoli_layers_qubits
    state_transform_matrices = qc_info.state_transform_matrices
    BV = BooleanPolynomialRing(names=[f"X{i}" for i in range(n)])
    # qubits
    Q = [i for i in range(width)]

    # quantum gate sequence
    seq = []
 
    for i in range(s):
        CNOT_qubits, MT = CNOT_layers_qubits[i], state_transform_matrices[i]
        CNOT_inputs = [Q[j] for j in CNOT_qubits]
        # basic CNOT sub-circuit(CNOT-count can be further reduced by using other methods)
        CNOT_opers, CNOT_outputs = get_CNOT_circuit_PLU(CNOT_inputs, MT)
        # CNOT Layer
        seq += CNOT_opers[:]

        # wires permutation
        for j in range(len(CNOT_qubits)):
            Q[CNOT_qubits[j]] = CNOT_outputs[j]

        Toffoli_qubits = Toffoli_layers_qubits[i]
        # Toffoli Layer
        for j in range(len(Toffoli_qubits)):
            tj = Toffoli_qubits[j]
            seq.append([CNOT_outputs[2*j], CNOT_outputs[2*j+1], Q[tj]])
   
    # output CNOT Layer
    CNOT_qubits, MT_Y = CNOT_layers_qubits[-1], state_transform_matrices[-1]
    CNOT_inputs = [Q[j] for j in CNOT_qubits]
    CNOT_opers, CNOT_outputs = get_CNOT_circuit_PLU(CNOT_inputs, MT_Y)
    seq += CNOT_opers[:]

    for j in range(len(CNOT_qubits)):
        Q[CNOT_qubits[j]] = CNOT_outputs[j]
    
    # quantum circuit outputs
    output_qubits = CNOT_outputs[:m]
    # add the NOT gate(+1)
    for i in range(m):
        if outputs_ANF[i].constant_coefficient() == 1:
            seq.append([output_qubits[i]])

    # generate QASM format quantum circuit and verify
    Q = [BV(f"X{i}") for i in range(n)] + [0 for i in range(width - n)]
    # rows with QASM format
    rows = ['OPENQASM 2.0;', 'include "qelib1.inc";', f'qreg q[{width}];', '']
    # NOT, CNOT, Toffoli
    gates = ["", "x", "cx", "ccx"]
    for oper in seq:
        qubits = [f"q[{j}]" for j in oper]
        rows.append(f"{gates[len(oper)]} {','.join(qubits)};")
        if len(oper) == 1:
            i = oper[0]
            Q[i] += 1
        elif len(oper) == 2:
            i, j = oper 
            Q[j] += Q[i]
        else:
            i, j, k = oper 
            Q[k] += Q[i] * Q[j]

    rows.append(f"///// Y store in qubits: {output_qubits} /////")
    with open(filename, "w") as f:
        f.write("\n".join(rows))
    print(f'##### quantum circuit store in file: "{filename}" #####')
    print("##### verify quantum circuit #####")
    
    print([outputs_ANF[i] == Q[output_qubits[i]] for i in range(m)])
    return seq, output_qubits

# Three instances: 
# 1) The AND-depth-4 and AND-count-34 classical circuit for the AES S-box (Boyar and Peralta's S-box)
# 2) The AND-depth-3 and AND-count-42 classical circuit for the AES S-box introduced in Section 5.2
# 3) The AND-depth-3 and AND-count-78 classical circuit for the AES S-box introduced in ASIACRYPT 2022
def AES_Sbox_quantum():
    n = 8
    # variable X over Boolean Polynomial Ring
    BV = BooleanPolynomialRing(names=[f"X{i}" for i in range(n)])
    AES_Sbox_ANF = get_AES_Sbox_ANF(X=[BV(f"X{i}") for i in range(n)])
    ######################################################################################
    # classical circuit("X" -> inputs, "Y" -> "outputs")
    AES_Sbox_ANDDepth4_34AND = ["T1=X0+X3", "T2=X0+X5", "T3=X0+X6", "T4=X3+X5", "T5=X4+X6", "T6=T1+T5", "T7=X1+X2", "T8=X7+T6", "T9=X7+T7", "T10=T6+T7", "T11=X1+X5", "T12=X2+X5", "T13=T3+T4", "T14=T6+T11", "T15=T5+T11", "T16=T5+T12", "T17=T9+T16", "T18=X3+X7", "T19=T7+T18", "T20=T1+T19", "T21=X6+X7", "T22=T7+T21", "T23=T2+T22", "T24=T2+T10", "T25=T20+T17", "T26=T3+T16", "T27=T1+T12", "M1=T13*T6", "M2=T23*T8", "M3=T14+M1", "M4=T19*X7", "M5=M4+M1", "M6=T3*T16", "M7=T22*T9", "M8=T26+M6", "M9=T20*T17", "M10=M9+M6", "M11=T1*T15", "M12=T4*T27", "M13=M12+M11", "M14=T2*T10", "M15=M14+M11", "M16=M3+M2", "M17=M5+T24", "M18=M8+M7", "M19=M10+M15", "M20=M16+M13", "M21=M17+M15", "M22=M18+M13", "M23=M19+T25", "M24=M22+M23", "M25=M22*M20", "M26=M21+M25", "M27=M20+M21", "M28=M23+M25", "M29=M28*M27", "M30=M26*M24", "M31=M20*M23", "M32=M27*M31", "M33=M27+M25", "M34=M21*M22", "M35=M24*M34", "M36=M24+M25", "M37=M21+M29", "M38=M32+M33", "M39=M23+M30", "M40=M35+M36", "M41=M38+M40", "M42=M37+M39", "M43=M37+M38", "M44=M39+M40", "M45=M42+M41", "M46=M44*T6", "M47=M40*T8", "M48=M39*X7", "M49=M43*T16", "M50=M38*T9", "M51=M37*T17", "M52=M42*T15", "M53=M45*T27", "M54=M41*T10", "M55=M44*T13", "M56=M40*T23", "M57=M39*T19", "M58=M43*T3", "M59=M38*T22", "M60=M37*T20", "M61=M42*T1", "M62=M45*T4", "M63=M41*T2", "L0=M61+M62", "L1=M50+M56", "L2=M46+M48", "L3=M47+M55", "L4=M54+M58", "L5=M49+M61", "L6=M62+L5", "L7=M46+L3", "L8=M51+M59", "L9=M52+M53", "L10=M53+L4", "L11=M60+L2", "L12=M48+M51", "L13=M50+L0", "L14=M52+M61", "L15=M55+L1", "L16=M56+L0", "L17=M57+L1", "L18=M58+L8", "L19=M63+L4", "L20=L0+L1", "L21=L1+L7", "L22=L3+L12", "L23=L18+L2", "L24=L15+L9", "L25=L6+L10", "L26=L7+L9", "L27=L8+L10", "L28=L11+L14", "L29=L11+L17", "Y0=L6+L24", "Y1=L16+L26", "Y1=Y1+1", "Y2=L19+L28", "Y2=Y2+1", "Y3=L6+L21", "Y4=L20+L22", "Y5=L25+L29", "Y6=L13+L27", "Y6=Y6+1", "Y7=L6+L23", "Y7=Y7+1"]
    AES_Sbox_ANDDepth3_42AND = ["L0=X0+X3", "L1=X0+X6", "L2=X0+X5", "L3=L0+L2", "L4=L1+L3", "L5=X4+L4", "L6=X5+L5", "L7=X7+L6", "L8=X1+X2", "L9=X7+L8", "L10=X3+L9", "L11=L4+L10", "L12=L2+L11", "L13=L1+L12", "L14=L7+L9", "L15=X1+L0", "L16=L5+L15", "L17=X7+L16", "L18=L9+L17", "L19=L14+L16", "M0=L7*L11", "M1=X7*L10", "M2=L9*L12", "M3=L13*L17", "M4=L4*L6", "M5=L0*L16", "M6=L1*L18", "M7=L2*L14", "M8=L3*L19", "L20=X2+M0", "L21=L1+M2", "L22=L15+M4", "L23=L22+M6", "L24=L20+L21", "L25=L23+L24", "L26=M1+M3", "L27=L23+L26", "L28=L25+L27", "L29=L18+M5", "L30=X0+M7", "L31=L21+M8", "L32=L29+M6", "L33=L31+L32", "L34=L25+L33", "L35=L30+M3", "L36=L32+L35", "L37=L27+L36", "L38=L34+L37", "L39=L33+L36", "M9=L33*L34", "M10=L36*L37", "M11=L38*L39", "M12=L11*L33", "M13=L10*L36", "M14=L12*L34", "M15=L13*L37", "M16=L4*L39", "M17=L0*L27", "M18=L1*L38", "M19=L2*L25", "M20=L3*L28", "M21=L7*L33", "M22=X7*L36", "M23=L9*L34", "M24=L17*L37", "M25=L6*L39", "M26=L16*L27", "M27=L18*L38", "M28=L14*L25", "M29=L19*L28", "L40=M10+M11", "L41=L28+L40", "L42=L27+M9", "L43=L42+M10", "L44=L41+L43", "L45=M19+M20", "L46=M17+M20", "L47=L46+M18", "L48=L47+M14", "L49=L45+M15", "L50=L47+L49", "L51=L48+L50", "L52=L46+M16", "L53=L52+M12", "L54=L45+M13", "L55=L52+L54", "L56=L53+L55", "L57=M28+M29", "L58=M26+M29", "L59=L58+M27", "L60=L59+M23", "L61=L57+M24", "L62=L59+L61", "L63=L60+L62", "L64=L58+M25", "L65=L64+M21", "L66=L57+M22", "L67=L64+L66", "L68=L65+L67", "M30=L41*L53", "M31=L44*L55", "M32=L43*L56", "M33=L41*L48", "M34=L44*L50", "M35=L43*L51", "M36=L41*L65", "M37=L44*L67", "M38=L43*L68", "M39=L41*L60", "M40=L44*L62", "M41=L43*L63", "L69=M30+M32", "L70=L69+M39", "L71=M37+M38", "L72=L71+M35", "L73=M36+M38", "L74=M40+M41", "L75=L72+L74", "Y0=L70+M41", "Y1=L69+L73", "Y2=L72+M34", "Y3=L73+Y0", "Y7=L75+M33", "L76=L71+Y3", "L77=L76+Y7", "L78=M32+Y2", "L79=L78+Y0", "Y4=L74+L76", "Y5=L79+M31", "Y6=L77+Y1", "Y1=Y1+1", "Y2=Y2+1", "Y6=Y6+1", "Y7=Y7+1"]
    AES_Sbox_ANDDepth3_78AND = ["T1=X0+X3", "T2=X0+X5", "T3=X0+X6", "T4=X3+X5", "T5=X4+X6", "T6=T1+T5", "T7=X1+X2", "T8=X7+T6", "T9=X7+T7", "T10=T6+T7", "T11=X1+X5", "T12=X2+X5", "T13=T3+T4", "T14=T6+T11", "T15=T5+T11", "T16=T5+T12", "T17=T9+T16", "T18=X3+X7", "T19=T7+T18", "T20=T1+T19", "T21=X6+X7", "T22=T7+T21", "T23=T2+T22", "T24=T2+T10", "T25=T20+T17", "T26=T3+T16", "T27=T1+T12", "M1=T13*T6", "M2=T23*T8", "M3=T14+M1", "M4=T19*X7", "M5=M4+M1", "M6=T3*T16", "M7=T22*T9", "M8=T26+M6", "M9=T20*T17", "M10=M9+M6", "M11=T1*T15", "M12=T4*T27", "M13=M12+M11", "M14=T2*T10", "M15=M14+M11", "M16=M3+M2", "M17=M5+T24", "M18=M8+M7", "M19=M10+M15", "M20=M16+M13", "M21=M17+M15", "M22=M18+M13", "M23=M19+T25", "M24=M22+M23", "M25=M22*M20", "M26=M21+M25", "M27=M20+M21", "M28=M23+M25", "M29=M20*M23", "M30=M27+M25", "M31=M21*M22", "M32=M24+M25", "N1=M24*T6", "N2=M23+M32", "N3=M26+M31", "W1=N3*N1", "W2=N2*T6", "M33=W1+W2", "N4=M24*T8", "N5=M32*T8", "W3=N4*M31", "M34=W3+N5", "N6=M24*X7", "N7=M23*X7", "W4=N6*M26", "M35=W4+N7", "N8=M21+M30", "N9=M28+M29", "N10=M27*T16", "W5=N8*T16", "W6=N9*N10", "M36=W5+W6", "N11=M27*T9", "N12=M30*T9", "W7=M29*N11", "M37=W7+N12", "N13=M21*T17", "N14=M27*T17", "W8=M28*N14", "M38=W8+N13", "N15=M21+M23", "N16=M27*T15", "N17=M24*T15", "W9=N15*T15", "W10=N16*M28", "W11=N17*M26", "M139=W9+W10", "M39=M139+W11", "N18=M30+M32", "N19=N15+N18", "N20=M28+M29", "N21=M26+M31", "N22=M27*T27", "N23=M24*T27", "W12=N19*T27", "W13=N20*N22", "W14=N21*N23", "M140=W12+W13", "M40=M140+W14", "N24=M27*T10", "N25=M24*T10", "W15=M29*N24", "W16=N18*T10", "W17=M31*N25", "M141=W15+W16", "M41=M141+W17", "N26=M24*T13", "W18=N3*N26", "W19=N2*T13", "M42=W18+W19", "N27=M24*T23", "N28=M32*T23", "W20=N27*M31", "M43=W20+N28", "N29=M24*T19", "N30=M23*T19", "W21=N29*M26", "M44=W21+N30", "N31=M27*T3", "W22=N8*T3", "W23=N9*N31", "M45=W22+W23", "N32=M27*T22", "N33=M30*T22", "W24=M29*N32", "M46=W24+N33", "N34=M21*T20", "N35=M27*T20", "W25=M28*N35", "M47=W25+N34", "N36=M27*T1", "N37=M24*T1", "W26=N15*T1", "W27=N36*M28", "W28=N37*M26", "M148=W26+W27", "M48=M148+W28", "N38=M27*T4", "N39=M24*T4", "W29=N19*T4", "W30=N20*N38", "W31=N21*N39", "M149=W29+W30", "M49=M149+W31", "N40=M27*T2", "N41=M24*T2", "W32=M29*N40", "W33=N18*T2", "W34=M31*N41", "M150=W32+W33", "M50=M150+W34", "L0=M48+M49", "L1=M37+M43", "L2=M33+M35", "L3=M34+M42", "L4=M41+M45", "L5=M36+M48", "L6=M49+L5", "L7=M33+L3", "L8=M38+M46", "L9=M39+M40", "L10=M40+L4", "L11=M47+L2", "L12=M35+M38", "L13=M37+L0", "L14=M39+M48", "L15=M42+L1", "L16=M43+L0", "L17=M44+L1", "L18=M45+L8", "L19=M50+L4", "L20=L0+L1", "L21=L1+L7", "L22=L3+L12", "L23=L18+L2", "L24=L15+L9", "L25=L6+L10", "L26=L7+L9", "L27=L8+L10", "L28=L11+L14", "L29=L11+L17", "Y0=L6+L24", "Y1=L16+L26", "Y1=Y1+1", "Y2=L19+L28", "Y2=Y2+1", "Y3=L6+L21", "Y4=L20+L22", "Y5=L25+L29", "Y6=L13+L27", "Y6=Y6+1", "Y7=L6+L23", "Y7=Y7+1"]
    # AND_numbers=[9,3,4,18]
    qc_info1 = classical_to_quantum(n=8, m=8, s=4, C=AES_Sbox_ANDDepth4_34AND)
    # AND_numbers=[9,21,12]
    qc_info2 = classical_to_quantum(n=8, m=8, s=3, C=AES_Sbox_ANDDepth3_42AND)
    # # AND_numbers=[9,33,36]
    qc_info3 = classical_to_quantum(n=8, m=8, s=3, C=AES_Sbox_ANDDepth3_78AND)

    # print and save quantum circuit information
    qc_info1.print_Info(save_file_name="AES_Sbox_T4_34Toffoli_info.txt")
    qc_info2.print_Info(save_file_name="AES_Sbox_T3_42Toffoli_info.txt")
    qc_info3.print_Info(save_file_name="AES_Sbox_T3_78Toffoli_info.txt")

    verify_quantum_circuit(qc_info=qc_info1, outputs_ANF=AES_Sbox_ANF)
    verify_quantum_circuit(qc_info=qc_info2, outputs_ANF=AES_Sbox_ANF)
    verify_quantum_circuit(qc_info=qc_info3, outputs_ANF=AES_Sbox_ANF)

# AES_Sbox_quantum()