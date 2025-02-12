from projectq import MainEngine
from projectq.backends import ResourceCounter, _resource, ClassicalSimulator, CommandPrinter
from projectq.meta import Uncompute, Compute, Dagger
from projectq.ops import H, Tdag, CNOT, T, X, S, Sdag, Toffoli, Measure, All, Allocate
import random


RCon   = [0x01000000, 0x02000000, 0x04000000, 0x08000000, 0x10000000, 0x20000000, 0x40000000, 0x80000000, 0x1B000000, 0x36000000]

Round_Key = [0x12345678123456781234567812345678, 
             0x0b85eab119b1bcc90b85eab119b1bcc9, 
             0xc1e03765d8518bacd3d4611dca65ddd4, 
             0x88217f115070f4bd83a495a049c14874, 
             0xf873ed2aa80319972ba78c376266c443, 
             0xdb6ff780736cee1758cb62203aada663, 
             0x6e4b0c001d27e21745ec80377f412654, 
             0xadbc2cd2b09bcec5f5774ef28a3668a6, 
             0x28f908ac9862c6696d15889be723e03d, 
             0x15182f388d7ae951e06f61ca074c81f7, 
             0x0a1447fd876eaeac6701cf66604d4e91]


"""---------------------Basic Quantum Gates---------------------"""

def QAND_gate(eng, control1, control2, target, resource_check):
    if (resource_check):
        ancilla = eng.allocate_qureg(1)

        H | target
        CNOT | (control2, ancilla[0])
        CNOT | (target, control1)
        CNOT | (target, control2)
        CNOT | (control1, ancilla[0])

        Tdag | control1
        Tdag | control2
        T | target
        T | ancilla[0]

        CNOT | (control1, ancilla[0])
        CNOT | (target, control2)
        CNOT | (target, control1)
        CNOT | (control2, ancilla[0])
        H | target
        S | target
        
        eng.deallocate_qubit(ancilla[0])
    else:
        Toffoli | (control1, control2, target)


def QAND_Adj(eng, control1, control2, target, resource_check):
    if (resource_check):
        H | control2
        H | target
        # Here we replace "Measure | target" by "Toffoli | (control1, control2, target)" for a correct full depth in resouce estimation
        Toffoli | (control1, control2, target)
        # Measure | target 
        CNOT | (control1, control2)
        X | target 
        H | control2

    else:
        Toffoli | (control1, control2, target)

"""------------------------Basic Tools------------------------"""

def Rotate_Left_Bit(eng, vector, shift):
    ancilla = eng.allocate_qureg(len(vector))
    for i in range(len(vector)):
        CNOT | (vector[i], ancilla[i])
    for i in range(len(vector)):
        CNOT | (ancilla[i], vector[i])
    for i in range(len(vector)-shift):
        CNOT | (ancilla[i+shift], vector[i])
    for i in range(shift):
        CNOT | (ancilla[i], vector[len(vector)-shift+i])
    for i in range(len(vector)-shift):
        CNOT | (vector[i], ancilla[i+shift])
    for i in range(shift):
        CNOT | (vector[len(vector)-shift+i], ancilla[i])


def Rotate_Left_Byte(eng, S1, S2, S3, S4, shift):
    ancilla = eng.allocate_qureg(8*4)
    XOR_State(S1, ancilla[0:8])
    XOR_State(S2, ancilla[8:16])
    XOR_State(S3, ancilla[16:24])
    XOR_State(S4, ancilla[24:32])
        
    XOR_State(ancilla[0:8], S1)
    XOR_State(ancilla[8:16], S2)
    XOR_State(ancilla[16:24], S3)
    XOR_State(ancilla[24:32], S4)

    if shift  == 1:
        XOR_State(ancilla[0:8], S4)
        XOR_State(ancilla[8:16], S1)
        XOR_State(ancilla[16:24], S2)
        XOR_State(ancilla[24:32], S3)
        
        XOR_State(S1, ancilla[8:16])
        XOR_State(S2, ancilla[16:24])
        XOR_State(S3, ancilla[24:32])
        XOR_State(S4, ancilla[0:8])
    if shift  == 2:
        XOR_State(ancilla[0:8], S3)
        XOR_State(ancilla[8:16], S4)
        XOR_State(ancilla[16:24], S1)
        XOR_State(ancilla[24:32], S2)
        
        XOR_State(S1, ancilla[16:24])
        XOR_State(S2, ancilla[24:32])
        XOR_State(S3, ancilla[0:8])
        XOR_State(S4, ancilla[8:16])
    if shift  == 3:
        XOR_State(ancilla[0:8], S2)
        XOR_State(ancilla[8:16], S3)
        XOR_State(ancilla[16:24], S4)
        XOR_State(ancilla[24:32], S1)
        
        XOR_State(S1, ancilla[24:32])
        XOR_State(S2, ancilla[0:8])
        XOR_State(S3, ancilla[8:16])
        XOR_State(S4, ancilla[16:24])
    

def Affine_Equivalence(eng, U):
    CNOT | (U[7], U[6])
    CNOT | (U[5], U[4])
    CNOT | (U[3], U[2])
    CNOT | (U[1], U[0])
    CNOT | (U[3], U[1])
    CNOT | (U[7], U[5])
    CNOT | (U[3], U[5])
    CNOT | (U[7], U[1])
    CNOT | (U[1], U[3])
    CNOT | (U[5], U[7])
    CNOT | (U[5], U[3])
    CNOT | (U[1], U[7])
    CNOT | (U[5], U[2])
    CNOT | (U[7], U[4])
    CNOT | (U[1], U[6])
    CNOT | (U[3], U[0])
    CNOT | (U[0], U[3])
    CNOT | (U[2], U[5])
    CNOT | (U[4], U[7])
    CNOT | (U[6], U[1])
    CNOT | (U[6], U[3])
    CNOT | (U[0], U[5])
    CNOT | (U[2], U[7])
    CNOT | (U[4], U[1])
    Rotate_Left_Bit(eng, U, 6)
    

def Format_Input(binary_num, Input):
    binary_str = bin(binary_num)[2:].zfill(len(Input))
    for index, bit in enumerate(binary_str):
        if int(bit) == 1:
            X | Input[index]


def Format_Output(Output):
    binary_str = ''.join(map(str, Output)) 
    binary_num = int(binary_str, 2)
    return hex(binary_num)


def XOR_State(state1, state2):
    for i in range(len(state1)):
        CNOT | (state1[i], state2[i])


def Swap_Bit(a, b):
    CNOT | (a, b)
    CNOT | (b, a)
    CNOT | (a, b)


def Swap_State(a, b):
    XOR_State(a, b)
    XOR_State(b, a)
    XOR_State(a, b)
    
"""-----------------------AES Components----------------------"""

# Inv_S_Box: ifInv = 1
# S_Box    : ifInv = 0
def T_Depth_3_CStar_S_Box_and_Inv(eng, U, T, S, ifInv, resource_check):
    if ifInv == 1 and resource_check == 0: 
        Affine_Equivalence(eng, U)
        X | U[5]
        X | U[7]
        with Dagger(eng):
            Affine_Equivalence(eng, S)
    
    """--------------T-depth-0-----------------"""
    CNOT | (U[2], U[1])
    CNOT | (U[6], U[0])
    CNOT | (U[5], U[4])
    CNOT | (U[7], T[0])
    CNOT | (U[7], U[1])
    CNOT | (U[0], U[5])
    CNOT | (U[6], U[2])
    CNOT | (T[0], T[2])
    CNOT | (U[5], U[3])
    CNOT | (U[4], U[2])
    CNOT | (U[1], U[6])
    CNOT | (U[0], T[6])
    CNOT | (U[1], U[5])
    CNOT | (U[3], U[4])
    CNOT | (U[2], T[1])
    CNOT | (U[0], T[8])
    CNOT | (U[6], T[9])
    CNOT | (U[4], U[7])
    CNOT | (U[1], T[1])
    CNOT | (U[2], T[3])
    CNOT | (U[3], T[5])
    CNOT | (U[6], T[6])
    CNOT | (T[1], T[2])
    CNOT | (U[4], T[3])
    CNOT | (U[1], T[4])
    CNOT | (U[5], T[5])
    CNOT | (T[6], T[7])
    CNOT | (U[3], T[8])
    CNOT | (U[7], T[4])
    CNOT | (T[5], T[7])
    CNOT | (U[5], T[9])
    """--------------T-depth-1-----------------"""
    QAND_gate(eng, U[4], U[3], T[10], resource_check)
    QAND_gate(eng, U[5], U[7], T[11], resource_check)
    QAND_gate(eng, T[0], T[5], T[12], resource_check)
    QAND_gate(eng, U[0], U[2], T[13], resource_check)
    QAND_gate(eng, U[6], U[1], T[14], resource_check)
    QAND_gate(eng, T[1], T[6], T[15], resource_check)
    QAND_gate(eng, T[2], T[7], T[16], resource_check)
    QAND_gate(eng, T[3], T[8], T[17], resource_check)
    QAND_gate(eng, T[4], T[9], T[18], resource_check)
    CNOT | (T[2], T[7])
    CNOT | (T[10], T[12])
    CNOT | (T[13], T[14])
    CNOT | (T[1], T[15])
    CNOT | (T[16], T[18])
    CNOT | (T[10], T[11])
    CNOT | (T[4], T[12])
    CNOT | (U[2], T[14])
    CNOT | (T[18], T[15])
    CNOT | (T[16], T[17])
    CNOT | (T[7], T[11])
    CNOT | (T[18], T[12])
    CNOT | (T[17], T[14])
    CNOT | (T[6], T[15])
    CNOT | (S[7], S[5])
    CNOT | (T[2], T[7])
    CNOT | (T[17], T[11])
    CNOT | (T[9], T[12])
    CNOT | (U[0], T[14])
    CNOT | (T[13], T[15])
    CNOT | (T[16], T[18])
    CNOT | (S[1], S[2])
    CNOT | (S[4], S[6])
    CNOT | (S[3], S[7])
    CNOT | (T[1], T[2])
    CNOT | (T[6], T[7])
    CNOT | (T[16], T[17])
    CNOT | (T[11], T[25])
    CNOT | (T[12], T[34])
    CNOT | (T[14], T[41])
    CNOT | (T[15], T[48])
    CNOT | (S[3], S[1])
    CNOT | (S[6], S[2])
    CNOT | (U[1], T[1])
    CNOT | (T[0], T[2])
    CNOT | (U[0], T[6])
    CNOT | (T[5], T[7])
    CNOT | (T[3], T[19])
    CNOT | (U[3], T[20])
    CNOT | (U[5], T[21])
    CNOT | (U[0], T[22])
    CNOT | (U[6], T[23])
    CNOT | (T[8], T[24])
    CNOT | (T[25], T[26])
    CNOT | (T[11], T[27])
    CNOT | (T[12], T[35])
    CNOT | (T[34], T[36])
    CNOT | (T[14], T[42])
    CNOT | (T[41], T[43])
    CNOT | (T[15], T[49])
    CNOT | (T[48], T[50])
    CNOT | (S[0], S[3])
    CNOT | (S[7], S[6])
    CNOT | (U[2], T[1])
    CNOT | (U[7], T[2])
    CNOT | (U[6], T[6])
    CNOT | (U[1], T[7])
    CNOT | (T[11], T[28])
    CNOT | (T[25], T[29])
    CNOT | (T[26], T[30])
    CNOT | (T[27], T[31])
    CNOT | (T[12], T[37])
    CNOT | (T[34], T[38])
    CNOT | (T[35], T[39])
    CNOT | (T[36], T[40])
    CNOT | (T[14], T[44])
    CNOT | (T[41], T[45])
    CNOT | (T[42], T[46])
    CNOT | (T[43], T[47])
    CNOT | (T[49], T[51])
    CNOT | (T[50], T[52])
    CNOT | (S[4], S[7])
    CNOT | (S[1], S[0])
    CNOT | (U[4], T[1])
    CNOT | (U[2], T[6])
    CNOT | (T[30], T[32])
    CNOT | (T[31], T[33])
    CNOT | (T[41], T[81])
    CNOT | (T[48], T[82])
    CNOT | (S[0], S[4])
    CNOT | (S[6], S[5])
    """--------------T-depth-2-----------------"""
    QAND_gate(eng, T[11], T[14], T[53], resource_check)
    QAND_gate(eng, T[12], T[41], T[54], resource_check)
    QAND_gate(eng, T[34], T[15], T[55], resource_check)
    QAND_gate(eng, T[25], T[48], T[56], resource_check)
    QAND_gate(eng, T[81], T[82], T[83], resource_check)
    QAND_gate(eng, T[26], U[2], T[57], resource_check)
    QAND_gate(eng, T[27], U[1], T[58], resource_check)
    QAND_gate(eng, T[28], U[0], T[59], resource_check)
    QAND_gate(eng, T[29], U[6], T[60], resource_check)
    QAND_gate(eng, T[30], T[3], T[61], resource_check)
    QAND_gate(eng, T[31], T[8], T[62], resource_check)
    QAND_gate(eng, T[32], T[0], T[63], resource_check)
    QAND_gate(eng, T[33], T[5], T[64], resource_check)
    QAND_gate(eng, T[35], T[7], T[65], resource_check)
    QAND_gate(eng, T[36], T[23], T[66], resource_check)
    QAND_gate(eng, T[37], T[6], T[67], resource_check)
    QAND_gate(eng, T[38], T[22], T[68], resource_check)
    QAND_gate(eng, T[39], T[4], T[69], resource_check)
    QAND_gate(eng, T[40], T[9], T[70], resource_check)
    QAND_gate(eng, T[42], U[4], T[71], resource_check)
    QAND_gate(eng, T[43], U[3], T[72], resource_check)
    QAND_gate(eng, T[44], U[7], T[73], resource_check)
    QAND_gate(eng, T[45], U[5], T[74], resource_check)
    QAND_gate(eng, T[46], T[19], T[75], resource_check)
    QAND_gate(eng, T[47], T[24], T[76], resource_check)
    QAND_gate(eng, T[49], T[2], T[77], resource_check)
    QAND_gate(eng, T[50], T[21], T[78], resource_check)
    QAND_gate(eng, T[51], T[1], T[79], resource_check)
    QAND_gate(eng, T[52], T[20], T[80], resource_check)
    CNOT | (U[4], T[1])
    CNOT | (U[2], T[6])
    CNOT | (T[30], T[32])
    CNOT | (T[31], T[33])
    CNOT | (T[73], T[77])
    CNOT | (T[74], T[78])
    CNOT | (T[58], T[65])
    CNOT | (T[60], T[66])
    CNOT | (T[71], S[3])
    CNOT | (T[57], S[1])
    CNOT | (T[72], S[0])
    CNOT | (T[59], S[7])
    CNOT | (U[2], T[1])
    CNOT | (U[7], T[2])
    CNOT | (U[6], T[6])
    CNOT | (U[1], T[7])
    CNOT | (T[11], T[28])
    CNOT | (T[25], T[29])
    CNOT | (T[26], T[30])
    CNOT | (T[27], T[31])
    CNOT | (T[12], T[37])
    CNOT | (T[34], T[38])
    CNOT | (T[35], T[39])
    CNOT | (T[36], T[40])
    CNOT | (T[14], T[44])
    CNOT | (T[41], T[45])
    CNOT | (T[42], T[46])
    CNOT | (T[43], T[47])
    CNOT | (T[49], T[51])
    CNOT | (T[50], T[52])
    CNOT | (T[58], T[57])
    CNOT | (T[60], T[59])
    CNOT | (T[77], S[3])
    CNOT | (T[78], S[0])
    CNOT | (T[65], S[4])
    CNOT | (T[66], S[5])
    CNOT | (U[1], T[1])
    CNOT | (T[0], T[2])
    CNOT | (U[0], T[6])
    CNOT | (T[5], T[7])
    CNOT | (T[3], T[19])
    CNOT | (U[3], T[20])
    CNOT | (U[5], T[21])
    CNOT | (U[0], T[22])
    CNOT | (U[6], T[23])
    CNOT | (T[8], T[24])
    CNOT | (T[25], T[26])
    CNOT | (T[11], T[27])
    CNOT | (T[53], T[29])
    CNOT | (T[12], T[35])
    CNOT | (T[34], T[36])
    CNOT | (T[14], T[42])
    CNOT | (T[41], T[43])
    CNOT | (T[15], T[49])
    CNOT | (T[48], T[50])
    CNOT | (T[57], T[51])
    CNOT | (T[59], T[52])
    CNOT | (T[65], S[1])
    CNOT | (T[66], S[2])
    CNOT | (T[77], S[4])
    CNOT | (T[78], S[5])
    CNOT | (T[1], T[2])
    CNOT | (T[6], T[7])
    CNOT | (T[54], T[26])
    CNOT | (T[83], T[27])
    CNOT | (T[15], T[29])
    CNOT | (T[55], T[31])
    CNOT | (T[63], T[51])
    CNOT | (T[64], T[52])
    CNOT | (T[14], T[81])
    CNOT | (T[48], T[82])
    CNOT | (T[65], S[6])
    CNOT | (T[66], S[7])
    CNOT | (T[73], T[77])
    CNOT | (T[74], T[78])
    CNOT | (T[58], T[65])
    CNOT | (T[60], T[66])
    CNOT | (T[56], T[26])
    CNOT | (T[54], T[27])
    CNOT | (T[31], T[29])
    """--------------Uncompute----------------"""
    QAND_Adj(eng, T[48], U[7], T[77], resource_check)
    QAND_Adj(eng, T[15], U[5], T[78], resource_check)
    QAND_Adj(eng, T[34], U[1], T[65], resource_check)
    QAND_Adj(eng, T[12], U[6], T[66], resource_check)
    QAND_Adj(eng, T[41], U[4], T[71], resource_check)
    QAND_Adj(eng, T[14], U[3], T[72], resource_check)
    CNOT | (T[54], T[29])
    CNOT | (T[56], T[31])
    CNOT | (U[6], U[0])
    CNOT | (U[7], U[1])
    CNOT | (U[4], U[2])
    CNOT | (U[5], U[3])
    CNOT | (T[11], T[25])
    CNOT | (T[31], T[28])
    CNOT | (T[29], T[30])
    CNOT | (T[12], T[34])
    CNOT | (T[14], T[41])
    CNOT | (T[15], T[48])
    CNOT | (T[6], U[0])
    CNOT | (T[4], U[1])
    CNOT | (T[3], U[2])
    CNOT | (T[5], U[3])
    CNOT | (U[7], U[4])
    CNOT | (U[6], U[5])
    CNOT | (T[12], T[11])
    CNOT | (T[15], T[14])
    X | T[31]
    CNOT | (T[55], T[43])
    CNOT | (T[0], U[4])
    CNOT | (T[9], U[5])
    CNOT | (T[2], T[3])
    CNOT | (T[7], T[8])
    CNOT | (T[55], T[11])
    CNOT | (T[53], T[12])
    CNOT | (T[56], T[15])
    CNOT | (T[54], T[43])
    CNOT | (T[4], T[3])
    CNOT | (T[9], T[8])
    CNOT | (T[55], T[14])
    CNOT | (T[53], T[15])
    CNOT | (T[11], T[26])
    CNOT | (T[12], T[28])
    CNOT | (T[83], T[56])
    CNOT | (T[54], T[42])
    X | T[43]
    CNOT | (T[42], T[12])
    CNOT | (T[14], T[26])
    CNOT | (T[28], T[30])
    CNOT | (T[54], T[55])
    X | T[55]
    CNOT | (T[11], T[32])
    CNOT | (T[12], T[33])
    CNOT | (T[14], T[34])
    CNOT | (T[15], T[35])
    CNOT | (T[26], T[36])
    CNOT | (T[27], T[37])
    CNOT | (T[28], T[38])
    CNOT | (T[29], T[39])
    CNOT | (T[30], T[40])
    CNOT | (T[31], T[41])
    CNOT | (T[56], T[44])
    CNOT | (T[83], T[45])
    """--------------T-depth-3-----------------"""
    QAND_gate(eng, T[12], T[79], U[0], resource_check)
    QAND_gate(eng, T[11], T[73], U[1], resource_check)
    QAND_gate(eng, T[15], T[67], U[2], resource_check)
    QAND_gate(eng, T[14], T[58], U[3], resource_check)
    QAND_gate(eng, T[33], T[80], U[4], resource_check)
    QAND_gate(eng, T[32], T[74], U[5], resource_check)
    QAND_gate(eng, T[35], T[68], T[3], resource_check)
    QAND_gate(eng, T[34], T[60], T[8], resource_check)
    QAND_gate(eng, T[29], T[0], T[19], resource_check)
    QAND_gate(eng, T[45], T[63], T[20], resource_check)
    QAND_gate(eng, T[28], T[1], T[21], resource_check)
    QAND_gate(eng, T[54], T[57], T[22], resource_check)
    QAND_gate(eng, T[30], T[2], T[23], resource_check)
    QAND_gate(eng, T[27], T[51], T[24], resource_check)
    QAND_gate(eng, T[43], T[61], T[25], resource_check)
    QAND_gate(eng, T[31], T[75], T[46], resource_check)
    QAND_gate(eng, T[26], T[4], T[47], resource_check)
    QAND_gate(eng, T[44], T[69], T[48], resource_check)
    QAND_gate(eng, T[39], T[5], T[49], resource_check)
    QAND_gate(eng, T[83], T[64], T[50], resource_check)
    QAND_gate(eng, T[38], T[6], T[65], resource_check)
    QAND_gate(eng, T[42], T[59], T[66], resource_check)
    QAND_gate(eng, T[40], T[7], T[71], resource_check)
    QAND_gate(eng, T[37], T[52], T[72], resource_check)
    QAND_gate(eng, T[55], T[62], T[77], resource_check)
    QAND_gate(eng, T[41], T[76], T[78], resource_check)
    QAND_gate(eng, T[36], T[9], T[81], resource_check)
    QAND_gate(eng, T[56], T[70], T[82], resource_check)
    CNOT | (T[19], T[20])
    CNOT | (T[21], T[22])
    CNOT | (T[23], T[24])
    CNOT | (T[25], T[46])
    CNOT | (T[47], T[48])
    CNOT | (T[49], T[50])
    CNOT | (T[65], T[66])
    CNOT | (T[71], T[72])
    CNOT | (T[77], T[78])
    CNOT | (T[81], T[82])
    CNOT | (U[0], S[3])
    CNOT | (U[2], S[1])
    CNOT | (T[8], S[2])
    CNOT | (U[4], S[0])
    CNOT | (U[1], S[4])
    CNOT | (U[5], S[5])
    CNOT | (U[3], S[6])
    CNOT | (T[3], S[7])
    CNOT | (U[1], S[3])
    CNOT | (T[46], S[1])
    CNOT | (T[78], S[2])
    CNOT | (U[5], S[0])
    CNOT | (U[3], S[4])
    CNOT | (T[8], S[5])
    CNOT | (T[22], S[6])
    CNOT | (T[72], S[7])
    CNOT | (T[24], S[3])
    CNOT | (U[3], S[1])
    CNOT | (T[66], S[2])
    CNOT | (T[72], S[0])
    CNOT | (T[20], S[4])
    CNOT | (T[50], S[5])
    CNOT | (T[46], S[6])
    CNOT | (T[78], S[7])
    CNOT | (T[46], S[3])
    CNOT | (T[24], S[1])
    CNOT | (T[82], S[2])
    CNOT | (T[78], S[0])
    CNOT | (T[22], S[4])
    CNOT | (T[66], S[5])
    CNOT | (T[48], S[6])
    CNOT | (T[8], S[7])
    CNOT | (T[19], T[20])
    CNOT | (T[21], T[22])
    CNOT | (T[23], T[24])
    CNOT | (T[25], T[46])
    CNOT | (T[47], T[48])
    CNOT | (T[49], T[50])
    CNOT | (T[65], T[66])
    CNOT | (T[71], T[72])
    CNOT | (T[77], T[78])
    CNOT | (T[81], T[82])
    CNOT | (S[0], S[4])
    CNOT | (S[6], S[5])
    """--------------UNCOMPUTE-----------------"""
    QAND_Adj(eng, T[12], T[79], U[0], resource_check)
    QAND_Adj(eng, T[11], T[73], U[1], resource_check)
    QAND_Adj(eng, T[15], T[67], U[2], resource_check)
    QAND_Adj(eng, T[14], T[58], U[3], resource_check)
    QAND_Adj(eng, T[33], T[80], U[4], resource_check)
    QAND_Adj(eng, T[32], T[74], U[5], resource_check)
    QAND_Adj(eng, T[35], T[68], T[3], resource_check)
    QAND_Adj(eng, T[34], T[60], T[8], resource_check)
    QAND_Adj(eng, T[29], T[0], T[19], resource_check)
    QAND_Adj(eng, T[45], T[63], T[20], resource_check)
    QAND_Adj(eng, T[28], T[1], T[21], resource_check)
    QAND_Adj(eng, T[54], T[57], T[22], resource_check)
    QAND_Adj(eng, T[30], T[2], T[23], resource_check)
    QAND_Adj(eng, T[27], T[51], T[24], resource_check)
    QAND_Adj(eng, T[43], T[61], T[25], resource_check)
    QAND_Adj(eng, T[31], T[75], T[46], resource_check)
    QAND_Adj(eng, T[26], T[4], T[47], resource_check)
    QAND_Adj(eng, T[44], T[69], T[48], resource_check)
    QAND_Adj(eng, T[39], T[5], T[49], resource_check)
    QAND_Adj(eng, T[83], T[64], T[50], resource_check)
    QAND_Adj(eng, T[38], T[6], T[65], resource_check)
    QAND_Adj(eng, T[42], T[59], T[66], resource_check)
    QAND_Adj(eng, T[40], T[7], T[71], resource_check)
    QAND_Adj(eng, T[37], T[52], T[72], resource_check)
    QAND_Adj(eng, T[55], T[62], T[77], resource_check)
    QAND_Adj(eng, T[41], T[76], T[78], resource_check)
    QAND_Adj(eng, T[36], T[9], T[81], resource_check)
    QAND_Adj(eng, T[56], T[70], T[82], resource_check)
    CNOT | (S[4], S[7])
    CNOT | (S[1], S[0])
    CNOT | (T[11], T[32])
    CNOT | (T[12], T[33])
    CNOT | (T[14], T[34])
    CNOT | (T[15], T[35])
    CNOT | (T[26], T[36])
    CNOT | (T[27], T[37])
    CNOT | (T[28], T[38])
    CNOT | (T[29], T[39])
    CNOT | (T[30], T[40])
    CNOT | (T[31], T[41])
    CNOT | (T[56], T[44])
    CNOT | (T[83], T[45])
    X | T[55]
    CNOT | (S[0], S[3])
    CNOT | (S[7], S[6])
    CNOT | (T[42], T[12])
    CNOT | (T[14], T[26])
    CNOT | (T[28], T[30])
    CNOT | (T[54], T[55])
    CNOT | (S[3], S[1])
    CNOT | (S[6], S[2])
    CNOT | (T[4], T[3])
    CNOT | (T[9], T[8])
    CNOT | (T[55], T[14])
    CNOT | (T[53], T[15])
    CNOT | (T[11], T[26])
    CNOT | (T[12], T[28])
    CNOT | (T[83], T[56])
    CNOT | (T[54], T[42])
    X | T[43]
    CNOT | (S[1], S[2])
    CNOT | (S[4], S[6])
    CNOT | (S[3], S[7])
    CNOT | (T[0], U[4])
    CNOT | (T[9], U[5])
    CNOT | (T[2], T[3])
    CNOT | (T[7], T[8])
    CNOT | (T[55], T[11])
    CNOT | (T[53], T[12])
    CNOT | (T[56], T[15])
    CNOT | (T[54], T[43])
    CNOT | (S[7], S[5])
    CNOT | (T[6], U[0])
    CNOT | (T[4], U[1])
    CNOT | (T[3], U[2])
    CNOT | (T[5], U[3])
    CNOT | (U[7], U[4])
    CNOT | (U[6], U[5])
    CNOT | (T[12], T[11])
    CNOT | (T[15], T[14])
    X | T[31]
    CNOT | (T[55], T[43])
    X | S[1]
    X | S[2]
    X | S[6]
    X | S[7]
    CNOT | (U[6], U[0])
    CNOT | (U[7], U[1])
    CNOT | (U[4], U[2])
    CNOT | (U[5], U[3])
    CNOT | (T[11], T[25])
    CNOT | (T[31], T[28])
    CNOT | (T[29], T[30])
    CNOT | (T[12], T[34])
    CNOT | (T[14], T[41])
    CNOT | (T[15], T[48])
    CNOT | (T[1], T[2])
    CNOT | (T[6], T[7])
    CNOT | (T[83], T[27])
    CNOT | (T[54], T[29])
    CNOT | (T[56], T[31])
    CNOT | (T[63], T[51])
    CNOT | (T[64], T[52])
    CNOT | (T[14], T[81])
    CNOT | (T[48], T[82])
    CNOT | (U[1], T[1])
    CNOT | (T[0], T[2])
    CNOT | (U[0], T[6])
    CNOT | (T[5], T[7])
    CNOT | (T[3], T[19])
    CNOT | (U[3], T[20])
    CNOT | (U[5], T[21])
    CNOT | (U[0], T[22])
    CNOT | (U[6], T[23])
    CNOT | (T[8], T[24])
    CNOT | (T[56], T[26])
    CNOT | (T[54], T[27])
    CNOT | (T[31], T[29])
    CNOT | (U[2], T[1])
    CNOT | (U[7], T[2])
    CNOT | (U[6], T[6])
    CNOT | (U[1], T[7])
    CNOT | (T[54], T[26])
    CNOT | (T[15], T[29])
    CNOT | (T[55], T[31])
    CNOT | (T[12], T[35])
    CNOT | (T[34], T[36])
    CNOT | (T[14], T[42])
    CNOT | (T[41], T[43])
    CNOT | (T[15], T[49])
    CNOT | (T[48], T[50])
    CNOT | (T[57], T[51])
    CNOT | (T[59], T[52])
    CNOT | (T[25], T[26])
    CNOT | (T[11], T[27])
    CNOT | (T[53], T[29])
    CNOT | (T[11], T[28])
    CNOT | (T[25], T[29])
    CNOT | (T[26], T[30])
    CNOT | (T[27], T[31])
    CNOT | (T[12], T[37])
    CNOT | (T[34], T[38])
    CNOT | (T[35], T[39])
    CNOT | (T[36], T[40])
    CNOT | (T[14], T[44])
    CNOT | (T[41], T[45])
    CNOT | (T[42], T[46])
    CNOT | (T[43], T[47])
    CNOT | (T[49], T[51])
    CNOT | (T[50], T[52])
    CNOT | (T[58], T[57])
    CNOT | (T[60], T[59])
    CNOT | (U[4], T[1])
    CNOT | (U[2], T[6])
    CNOT | (T[30], T[32])
    CNOT | (T[31], T[33])
    QAND_Adj(eng, T[11], T[14], T[53], resource_check)
    QAND_Adj(eng, T[12], T[41], T[54], resource_check)
    QAND_Adj(eng, T[34], T[15], T[55], resource_check)
    QAND_Adj(eng, T[25], T[48], T[56], resource_check)
    QAND_Adj(eng, T[81], T[82], T[83], resource_check)
    QAND_Adj(eng, T[26], U[2], T[57], resource_check)
    QAND_Adj(eng, T[27], U[1], T[58], resource_check)
    QAND_Adj(eng, T[28], U[0], T[59], resource_check)
    QAND_Adj(eng, T[29], U[6], T[60], resource_check)
    QAND_Adj(eng, T[30], T[3], T[61], resource_check)
    QAND_Adj(eng, T[31], T[8], T[62], resource_check)
    QAND_Adj(eng, T[32], T[0], T[63], resource_check)
    QAND_Adj(eng, T[33], T[5], T[64], resource_check)
    QAND_Adj(eng, T[37], T[6], T[67], resource_check)
    QAND_Adj(eng, T[38], T[22], T[68], resource_check)
    QAND_Adj(eng, T[39], T[4], T[69], resource_check)
    QAND_Adj(eng, T[40], T[9], T[70], resource_check)
    QAND_Adj(eng, T[44], U[7], T[73], resource_check)
    QAND_Adj(eng, T[45], U[5], T[74], resource_check)
    QAND_Adj(eng, T[46], T[19], T[75], resource_check)
    QAND_Adj(eng, T[47], T[24], T[76], resource_check)
    QAND_Adj(eng, T[51], T[1], T[79], resource_check)
    QAND_Adj(eng, T[52], T[20], T[80], resource_check)
    CNOT | (U[4], T[1])
    CNOT | (U[2], T[6])
    CNOT | (T[30], T[32])
    CNOT | (T[31], T[33])
    CNOT | (T[41], T[81])
    CNOT | (T[48], T[82])
    CNOT | (U[2], T[1])
    CNOT | (U[7], T[2])
    CNOT | (U[6], T[6])
    CNOT | (U[1], T[7])
    CNOT | (T[11], T[28])
    CNOT | (T[25], T[29])
    CNOT | (T[26], T[30])
    CNOT | (T[27], T[31])
    CNOT | (T[12], T[37])
    CNOT | (T[34], T[38])
    CNOT | (T[35], T[39])
    CNOT | (T[36], T[40])
    CNOT | (T[14], T[44])
    CNOT | (T[41], T[45])
    CNOT | (T[42], T[46])
    CNOT | (T[43], T[47])
    CNOT | (T[49], T[51])
    CNOT | (T[50], T[52])
    CNOT | (U[1], T[1])
    CNOT | (T[0], T[2])
    CNOT | (U[0], T[6])
    CNOT | (T[5], T[7])
    CNOT | (T[3], T[19])
    CNOT | (U[3], T[20])
    CNOT | (U[5], T[21])
    CNOT | (U[0], T[22])
    CNOT | (U[6], T[23])
    CNOT | (T[8], T[24])
    CNOT | (T[25], T[26])
    CNOT | (T[11], T[27])
    CNOT | (T[12], T[35])
    CNOT | (T[34], T[36])
    CNOT | (T[14], T[42])
    CNOT | (T[41], T[43])
    CNOT | (T[15], T[49])
    CNOT | (T[48], T[50])
    CNOT | (T[1], T[2])
    CNOT | (T[6], T[7])
    CNOT | (T[16], T[17])
    CNOT | (T[11], T[25])
    CNOT | (T[12], T[34])
    CNOT | (T[14], T[41])
    CNOT | (T[15], T[48])
    CNOT | (T[2], T[7])
    CNOT | (T[17], T[11])
    CNOT | (T[9], T[12])
    CNOT | (U[0], T[14])
    CNOT | (T[13], T[15])
    CNOT | (T[16], T[18])
    CNOT | (T[7], T[11])
    CNOT | (T[18], T[12])
    CNOT | (T[17], T[14])
    CNOT | (T[6], T[15])
    CNOT | (T[10], T[11])
    CNOT | (T[4], T[12])
    CNOT | (U[2], T[14])
    CNOT | (T[18], T[15])
    CNOT | (T[16], T[17])
    CNOT | (T[2], T[7])
    CNOT | (T[10], T[12])
    CNOT | (T[13], T[14])
    CNOT | (T[1], T[15])
    CNOT | (T[16], T[18])
    QAND_Adj(eng, U[4], U[3], T[10], resource_check)
    QAND_Adj(eng, U[5], U[7], T[11], resource_check)
    QAND_Adj(eng, T[0], T[5], T[12], resource_check)
    QAND_Adj(eng, U[0], U[2], T[13], resource_check)
    QAND_Adj(eng, U[6], U[1], T[14], resource_check)
    QAND_Adj(eng, T[1], T[6], T[15], resource_check)
    QAND_Adj(eng, T[2], T[7], T[16], resource_check)
    QAND_Adj(eng, T[3], T[8], T[17], resource_check)
    QAND_Adj(eng, T[4], T[9], T[18], resource_check)
    CNOT | (U[7], T[4])
    CNOT | (T[5], T[7])
    CNOT | (U[5], T[9])
    CNOT | (T[1], T[2])
    CNOT | (U[4], T[3])
    CNOT | (U[1], T[4])
    CNOT | (U[5], T[5])
    CNOT | (T[6], T[7])
    CNOT | (U[3], T[8])
    CNOT | (U[4], U[7])
    CNOT | (U[1], T[1])
    CNOT | (U[2], T[3])
    CNOT | (U[3], T[5])
    CNOT | (U[6], T[6])
    CNOT | (U[1], U[5])
    CNOT | (U[3], U[4])
    CNOT | (U[2], T[1])
    CNOT | (U[0], T[8])
    CNOT | (U[6], T[9])
    CNOT | (U[5], U[3])
    CNOT | (U[4], U[2])
    CNOT | (U[1], U[6])
    CNOT | (U[0], T[6])
    CNOT | (U[7], U[1])
    CNOT | (U[0], U[5])
    CNOT | (U[6], U[2])
    CNOT | (T[0], T[2])
    CNOT | (U[2], U[1])
    CNOT | (U[6], U[0])
    CNOT | (U[5], U[4])
    CNOT | (U[7], T[0])

    if ifInv == 1 and resource_check == 0: 
        X | U[5]
        X | U[7]
        with Dagger(eng):  
            Affine_Equivalence(eng, U)
        Affine_Equivalence(eng, S)
        X | S[5]
        X | S[7]


def MixColumns(X):
    CNOT | (X[7], X[23])
    CNOT | (X[6], X[22])
    CNOT | (X[5], X[21])
    CNOT | (X[4], X[20])
    CNOT | (X[3], X[19])
    CNOT | (X[2], X[18])
    CNOT | (X[1], X[17])
    CNOT | (X[0], X[16])
    CNOT | (X[15], X[31])
    CNOT | (X[14], X[30])
    CNOT | (X[13], X[29])
    CNOT | (X[12], X[28])
    CNOT | (X[11], X[27])
    CNOT | (X[10], X[26])
    CNOT | (X[9], X[25])
    CNOT | (X[8], X[24])
    CNOT | (X[7], X[15])
    CNOT | (X[6], X[14])
    CNOT | (X[5], X[13])
    CNOT | (X[4], X[12])
    CNOT | (X[3], X[11])
    CNOT | (X[2], X[10])
    CNOT | (X[1], X[9])
    CNOT | (X[0], X[8])
    CNOT | (X[23], X[31])
    CNOT | (X[22], X[30])
    CNOT | (X[21], X[29])
    CNOT | (X[20], X[28])
    CNOT | (X[19], X[27])
    CNOT | (X[18], X[26])
    CNOT | (X[17], X[25])
    CNOT | (X[16], X[24])
    CNOT | (X[8], X[3])
    CNOT | (X[8], X[4])
    CNOT | (X[8], X[6])
    CNOT | (X[15], X[6])
    CNOT | (X[14], X[5])
    CNOT | (X[13], X[4])
    CNOT | (X[12], X[3])
    CNOT | (X[11], X[2])
    CNOT | (X[10], X[1])
    CNOT | (X[9], X[0])
    CNOT | (X[8], X[7])
    CNOT | (X[23], X[14])
    CNOT | (X[22], X[13])
    CNOT | (X[21], X[12])
    CNOT | (X[20], X[11])
    CNOT | (X[19], X[10])
    CNOT | (X[18], X[9])
    CNOT | (X[17], X[8])
    CNOT | (X[16], X[15])
    CNOT | (X[31], X[7])
    CNOT | (X[30], X[6])
    CNOT | (X[29], X[5])
    CNOT | (X[28], X[4])
    CNOT | (X[27], X[3])
    CNOT | (X[26], X[2])
    CNOT | (X[25], X[1])
    CNOT | (X[24], X[0])
    CNOT | (X[24], X[22])
    CNOT | (X[16], X[14])
    CNOT | (X[24], X[20])
    CNOT | (X[16], X[12])
    CNOT | (X[24], X[19])
    CNOT | (X[16], X[11])
    CNOT | (X[31], X[22])
    CNOT | (X[30], X[21])
    CNOT | (X[29], X[20])
    CNOT | (X[28], X[19])
    CNOT | (X[27], X[18])
    CNOT | (X[26], X[17])
    CNOT | (X[25], X[16])
    CNOT | (X[24], X[23])
    CNOT | (X[7], X[23])
    CNOT | (X[6], X[22])
    CNOT | (X[5], X[21])
    CNOT | (X[4], X[20])
    CNOT | (X[3], X[19])
    CNOT | (X[2], X[18])
    CNOT | (X[1], X[17])
    CNOT | (X[0], X[16])
    CNOT | (X[15], X[31])
    CNOT | (X[14], X[30])
    CNOT | (X[13], X[29])
    CNOT | (X[12], X[28])
    CNOT | (X[11], X[27])
    CNOT | (X[10], X[26])
    CNOT | (X[9], X[25])
    CNOT | (X[8], X[24])
    CNOT | (X[7], X[15])
    CNOT | (X[6], X[14])
    CNOT | (X[5], X[13])
    CNOT | (X[4], X[12])
    CNOT | (X[3], X[11])
    CNOT | (X[2], X[10])
    CNOT | (X[1], X[9])
    CNOT | (X[0], X[8])
    CNOT | (X[23], X[31])
    CNOT | (X[22], X[30])
    CNOT | (X[21], X[29])
    CNOT | (X[20], X[28])
    CNOT | (X[19], X[27])
    CNOT | (X[18], X[26])
    CNOT | (X[17], X[25])
    CNOT | (X[16], X[24])


def AddRoundKey(key, state):
    for i in range(128):
        if (key >> i) & 1 == 1:
            X | state[127-i]


def RotWord(eng, state):
    Rotate_Left_Bit(eng, state, 8)


def AddRCon(state, rcon):
    for i in range(32):
        if (rcon >> i) & 1 == 1:
            X | state[31-i]


def ShiftRows(eng, state):
    Rotate_Left_Byte(eng, state[8*1:8+8*1], state[8*5:8+8*5], state[8*9:8+8*9], state[8*13:8+8*13], 1)
    Rotate_Left_Byte(eng, state[8*2:8+8*2], state[8*6:8+8*6], state[8*10:8+8*10], state[8*14:8+8*14], 2)
    Rotate_Left_Byte(eng, state[8*3:8+8*3], state[8*7:8+8*7], state[8*11:8+8*11], state[8*15:8+8*15], 3)


"""-------------------AES Round Functions------------------"""

def Round_1(eng, State_Registers, Ancilla_State, T_State, resource_check):
    Inv = 1
    Forward = 0
    
    AddRoundKey(Round_Key[0], State_Registers)

    for i in range(16):
        T_Depth_3_CStar_S_Box_and_Inv(eng, State_Registers[8*i:8+8*i], T_State[84*i:84+84*i], Ancilla_State[8*i:8+8*i], Forward, resource_check)
    XOR_State(Ancilla_State[0:128], Ancilla_State[128:256])
    if resource_check == 0:
        ShiftRows(eng, Ancilla_State[0:128])
    for i in range(4):
        MixColumns(Ancilla_State[32*i:32+32*i])
    
    if resource_check == 0:
        Swap_State(State_Registers, Ancilla_State[0:128])
        Swap_State(Ancilla_State[128:256], Ancilla_State[256:384])
        Swap_State(State_Registers, Ancilla_State[256:384])


def Round_2_10(eng, r, State_Registers, Ancilla_State, T_State, resource_check):
    Inv = 1       # Inv_S_Box
    Forward = 0   # S_Box
    
    AddRoundKey(Round_Key[r-1], Ancilla_State[256:384])

    for i in range(16):
        # Inv_SubBytes
        T_Depth_3_CStar_S_Box_and_Inv(eng, State_Registers[8*i:8+8*i], T_State[84*i:84+84*i], Ancilla_State[8*i:8+8*i], Inv, resource_check)
        # SubBytes
        T_Depth_3_CStar_S_Box_and_Inv(eng, Ancilla_State[256+8*i:264+8*i], T_State[1344+84*i:1428+84*i], Ancilla_State[128+8*i:136+8*i], Forward, resource_check)
    XOR_State(Ancilla_State[128:256], Ancilla_State[0:128])
    if resource_check == 0:
        ShiftRows(eng, State_Registers)
        ShiftRows(eng, Ancilla_State[128:256])
    for i in range(4):
        MixColumns(State_Registers[32*i:32+32*i])
        if r != 10:
            MixColumns(Ancilla_State[128+32*i:160+32*i])
    XOR_State(Ancilla_State[256:384], State_Registers)

    AddRoundKey(Round_Key[r-1], State_Registers)
    
    
    if resource_check == 0:
        if r != 10:
            Swap_State(State_Registers, Ancilla_State[0:128])
            Swap_State(Ancilla_State[128:256], Ancilla_State[256:384])
            Swap_State(Ancilla_State[0:128], Ancilla_State[128:256])
        else:
            Swap_State(State_Registers, Ancilla_State[0:128])
            Swap_State(State_Registers, Ancilla_State[128:256])
    

# Round 10* (Excluding the AddRoundKeys)
def Round_11(eng, State_Registers, Ancilla_State, T_State, resource_check):
    Inv = 1       # Inv_S_Box
    Forward = 0   # S_Box
    """--------------------Status Update-------------------"""
    for i in range(16):
        # Inv_SubBytes
        T_Depth_3_CStar_S_Box_and_Inv(eng, Ancilla_State[128+8*i:136+8*i], T_State[84*i:84+84*i], Ancilla_State[256+8*i:264+8*i], Inv, resource_check)
        
    if resource_check == 0:
        ShiftRows(eng, Ancilla_State[128:256])
    XOR_State(State_Registers, Ancilla_State[128:256])


"""------------------------AES-128-----------------------"""

def AES_128_Encrypt(eng, State_Registers, resource_check):
    Ancilla_State = eng.allocate_qureg(128*3)
    T_State = eng.allocate_qureg(84*16+84*16)

    Round_1(eng, State_Registers, Ancilla_State, T_State, resource_check)
    # print(f"round-{1} finished!")
    for r in range(2, 11):
        
        Round_2_10(eng, r, State_Registers, Ancilla_State, T_State, resource_check)
        # print(f"round-{r} finished!")

    AddRoundKey(Round_Key[10], State_Registers)
    Round_11(eng, State_Registers, Ancilla_State, T_State, resource_check)
    AddRoundKey(Round_Key[10], Ancilla_State[128:256])


    # Measuring the registers and output the state
    if resource_check == 0:
        AllQubits = [State_Registers, Ancilla_State, T_State]
        for qubit in AllQubits:
            All(Measure) | qubit

        ciphertext = [int(qubit) for qubit in State_Registers]
        print("Ciphertext:", Format_Output(ciphertext))

        # Checking if the Ancilla Registers are uncomputed to 0
        ancilla_qubits = [int(qubit) for qubit in (Ancilla_State + T_State)]
        if ancilla_qubits != [0] * (len(Ancilla_State) + len(T_State)):
            print("UNCOMPUTE ERROR")
        else:
            print("The ancilla registers have all been uncomputed to 0")




if __name__ == "__main__":

    """------------Encryption Oracle Resource Check-----------"""
    RESOURCE_CHECK = 1
    print("-------------------------------Encryption Oracle Resource Check------------------------------")
    print("This is the quantum circuit resource estimate for AES-128 (based on T-depth-3 S-box and IU structure) when implemented as an Encryption oracle:")

    circuit_backend = _resource.ResourceCounter()
    eng = MainEngine(backend=circuit_backend)

    State_Registers = eng.allocate_qureg(128)
    AES_128_Encrypt(eng, State_Registers, RESOURCE_CHECK)
    eng.flush()

    print(circuit_backend)
    print("depth_of_dag: {}".format(circuit_backend.depth_of_dag))


    """------------Encryption Oracle Correctness Check----------"""
    RESOURCE_CHECK = 0
    print("------------------------------Encryption Oracle Correctness Check----------------------------")
    print("This is the correctness verification of the quantum circuit for AES-128 (based on T-depth-3 S-box and IU structure) when implemented as an Encryption oracle:")
    print()
    eng = MainEngine(backend=ClassicalSimulator())

    Test_MainKey = 0x12345678123456781234567812345678
    Test_Plaintext = 0x12345678123456781234567812345678
    print("MainKey   :", hex(Test_MainKey))
    print("Plaintext :", hex(Test_Plaintext))

    State_Registers = eng.allocate_qureg(128)
    Format_Input(Test_Plaintext, State_Registers)

    AES_128_Encrypt(eng, State_Registers, RESOURCE_CHECK)

    eng.flush()

    
