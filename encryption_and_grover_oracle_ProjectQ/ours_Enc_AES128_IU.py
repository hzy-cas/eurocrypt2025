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
def T_Depth_3_CStar_S_Box_and_Inv_new(eng, U, T, S, ifInv, resource_check):
    if ifInv == 1 and resource_check == 0: 
        Affine_Equivalence(eng, U)
        X | U[5]
        X | U[7]
        with Dagger(eng):
            Affine_Equivalence(eng, S)
    CNOT | (S[2], S[5])
    CNOT | (S[0], S[3])
    CNOT | (S[6], S[7])
    CNOT | (S[1], S[4])
    CNOT | (S[3], S[1])
    CNOT | (S[1], S[0])
    CNOT | (S[0], S[7])
    CNOT | (S[7], S[4])
    CNOT | (S[4], S[6])
    CNOT | (S[7], S[2])
    CNOT | (S[6], S[2])
    CNOT | (S[0], S[5])
    CNOT | (S[3], S[7])
    CNOT | (U[6], U[4])
    CNOT | (U[2], U[1])
    CNOT | (U[6], T[4])
    CNOT | (U[5], T[6])
    CNOT | (U[1], T[3])
    CNOT | (U[3], T[8])
    CNOT | (U[5], T[8])
    CNOT | (U[0], U[3])
    CNOT | (U[4], U[2])
    CNOT | (U[5], U[2])
    CNOT | (U[6], U[5])
    CNOT | (U[3], U[4])
    CNOT | (U[0], T[4])
    CNOT | (U[1], T[7])
    CNOT | (U[0], T[6])
    CNOT | (U[7], U[1])
    CNOT | (U[3], T[0])
    CNOT | (U[1], U[0])
    CNOT | (U[1], U[6])
    CNOT | (U[4], T[7])
    CNOT | (U[4], T[1])
    CNOT | (U[2], T[3])
    CNOT | (U[2], T[9])
    CNOT | (U[2], T[5])
    CNOT | (U[1], U[2])
    CNOT | (U[4], T[9])
    CNOT | (U[3], T[2])
    CNOT | (U[5], T[0])
    CNOT | (U[0], U[5])
    CNOT | (U[0], U[3])
    CNOT | (U[7], U[4])
    QAND_gate(eng, U[4], U[5], T[10], resource_check)
    QAND_gate(eng, U[3], U[7], T[11], resource_check)
    QAND_gate(eng, U[1], U[6], T[12], resource_check)
    QAND_gate(eng, U[0], U[2], T[13], resource_check)
    QAND_gate(eng, T[0], T[1], T[14], resource_check)
    QAND_gate(eng, T[2], T[3], T[15], resource_check)
    QAND_gate(eng, T[4], T[5], T[16], resource_check)
    QAND_gate(eng, T[6], T[7], T[17], resource_check)
    QAND_gate(eng, T[8], T[9], T[18], resource_check)
    CNOT | (U[0], T[13])
    CNOT | (T[4], T[0])
    CNOT | (T[15], T[17])
    CNOT | (T[9], T[10])
    CNOT | (T[35], T[22])
    CNOT | (T[7], T[14])
    CNOT | (T[19], U[5])
    CNOT | (U[3], T[3])
    CNOT | (T[31], T[2])
    CNOT | (T[5], T[1])
    CNOT | (T[8], T[23])
    CNOT | (T[24], T[37])
    CNOT | (U[2], U[4])
    CNOT | (T[6], T[25])
    CNOT | (T[4], U[0])
    CNOT | (T[16], T[13])
    CNOT | (T[15], T[18])
    CNOT | (T[8], T[0])
    CNOT | (U[1], T[35])
    CNOT | (T[6], T[14])
    CNOT | (T[7], U[7])
    CNOT | (T[19], T[33])
    CNOT | (T[9], T[32])
    CNOT | (T[38], T[3])
    CNOT | (T[5], T[30])
    CNOT | (T[17], T[13])
    CNOT | (U[0], U[6])
    CNOT | (T[8], T[10])
    CNOT | (T[4], T[12])
    CNOT | (T[18], T[16])
    CNOT | (T[0], T[29])
    CNOT | (T[34], T[35])
    CNOT | (T[9], U[7])
    CNOT | (T[6], U[3])
    CNOT | (T[7], T[30])
    CNOT | (U[2], T[32])
    CNOT | (T[5], T[36])
    CNOT | (U[0], U[5])
    CNOT | (T[13], U[7])
    CNOT | (T[12], T[16])
    CNOT | (T[10], T[18])
    CNOT | (T[0], U[4])
    CNOT | (T[11], T[17])
    CNOT | (T[5], T[34])
    CNOT | (T[8], U[3])
    CNOT | (T[6], T[2])
    CNOT | (T[9], T[36])
    CNOT | (T[7], T[38])
    CNOT | (T[4], T[23])
    CNOT | (U[2], T[30])
    CNOT | (U[0], T[1])
    CNOT | (T[13], U[1])
    CNOT | (T[14], T[18])
    CNOT | (T[16], T[0])
    CNOT | (T[6], U[5])
    CNOT | (T[9], T[10])
    CNOT | (U[2], T[34])
    CNOT | (T[8], T[2])
    CNOT | (T[7], U[4])
    CNOT | (T[4], T[12])
    CNOT | (U[0], T[20])
    CNOT | (U[2], T[13])
    CNOT | (T[14], T[17])
    CNOT | (T[18], T[19])
    CNOT | (T[16], U[1])
    CNOT | (T[6], T[1])
    CNOT | (T[0], U[4])
    CNOT | (T[34], T[35])
    CNOT | (T[8], T[25])
    CNOT | (T[9], T[38])
    CNOT | (T[7], T[32])
    CNOT | (T[4], U[0])
    CNOT | (T[13], T[31])
    CNOT | (T[7], T[14])
    CNOT | (T[18], T[16])
    CNOT | (T[5], T[0])
    CNOT | (T[19], U[5])
    CNOT | (U[1], T[35])
    CNOT | (T[9], T[1])
    CNOT | (T[8], T[10])
    CNOT | (T[38], T[3])
    CNOT | (T[17], T[21])
    CNOT | (T[17], T[13])
    CNOT | (U[0], U[3])
    CNOT | (T[5], T[16])
    CNOT | (T[6], T[14])
    CNOT | (T[0], T[29])
    CNOT | (T[31], T[2])
    CNOT | (T[19], T[33])
    CNOT | (T[35], T[22])
    CNOT | (T[17], T[18])
    CNOT | (T[13], T[24])
    CNOT | (U[3], T[3])
    CNOT | (T[16], T[27])
    CNOT | (T[16], T[13])
    CNOT | (T[17], U[3])
    CNOT | (T[18], T[26])
    CNOT | (T[24], T[37])
    CNOT | (T[18], U[6])
    CNOT | (T[13], T[28])
    QAND_gate(eng, U[4], U[5], T[39], resource_check)
    QAND_gate(eng, U[3], U[7], T[40], resource_check)
    QAND_gate(eng, U[1], U[6], T[41], resource_check)
    QAND_gate(eng, T[0], T[1], T[42], resource_check)
    QAND_gate(eng, T[2], T[3], T[43], resource_check)
    QAND_gate(eng, T[19], T[20], T[44], resource_check)
    QAND_gate(eng, U[0], T[21], T[45], resource_check)
    QAND_gate(eng, T[22], T[23], T[46], resource_check)
    QAND_gate(eng, T[24], T[25], T[47], resource_check)
    QAND_gate(eng, T[4], T[26], T[48], resource_check)
    QAND_gate(eng, T[6], T[27], T[49], resource_check)
    QAND_gate(eng, T[8], T[28], T[50], resource_check)
    QAND_gate(eng, T[29], T[30], T[51], resource_check)
    QAND_gate(eng, T[31], T[32], T[52], resource_check)
    QAND_gate(eng, T[33], T[34], T[53], resource_check)
    QAND_gate(eng, U[2], T[17], T[54], resource_check)
    QAND_gate(eng, T[35], T[36], T[55], resource_check)
    QAND_gate(eng, T[37], T[38], T[56], resource_check)
    QAND_gate(eng, T[5], T[18], T[57], resource_check)
    QAND_gate(eng, T[7], T[16], T[58], resource_check)
    QAND_gate(eng, T[9], T[13], T[59], resource_check)
    CNOT | (T[13], T[16])
    CNOT | (T[18], T[26])
    CNOT | (T[56], T[57])
    CNOT | (T[21], T[33])
    CNOT | (T[41], T[27])
    CNOT | (T[40], T[25])
    CNOT | (T[58], T[54])
    CNOT | (T[47], T[48])
    CNOT | (T[59], T[53])
    CNOT | (T[49], T[45])
    CNOT | (T[50], T[24])
    CNOT | (T[9], T[38])
    CNOT | (T[22], T[29])
    CNOT | (U[2], T[5])
    CNOT | (T[39], T[31])
    CNOT | (T[8], T[6])
    CNOT | (T[55], T[30])
    CNOT | (T[41], T[13])
    CNOT | (T[57], T[34])
    CNOT | (T[40], T[21])
    CNOT | (T[48], T[26])
    CNOT | (T[59], T[30])
    CNOT | (T[16], T[24])
    CNOT | (T[9], T[36])
    CNOT | (T[43], T[49])
    CNOT | (T[52], T[58])
    CNOT | (T[7], T[38])
    CNOT | (T[39], T[27])
    CNOT | (T[4], T[8])
    CNOT | (T[17], T[29])
    CNOT | (T[6], T[25])
    CNOT | (T[41], T[18])
    CNOT | (T[13], T[31])
    CNOT | (T[53], T[34])
    CNOT | (T[54], T[57])
    CNOT | (T[39], T[40])
    CNOT | (T[50], T[26])
    CNOT | (T[45], T[48])
    CNOT | (T[56], T[30])
    CNOT | (T[7], T[9])
    CNOT | (T[17], T[21])
    CNOT | (T[42], T[24])
    CNOT | (T[5], T[36])
    CNOT | (T[16], T[22])
    CNOT | (T[8], T[23])
    CNOT | (T[41], T[28])
    CNOT | (T[13], T[25])
    CNOT | (T[53], T[54])
    CNOT | (T[18], T[22])
    CNOT | (T[40], T[29])
    CNOT | (T[50], T[45])
    CNOT | (U[2], T[9])
    CNOT | (T[51], T[30])
    CNOT | (T[44], T[26])
    CNOT | (T[5], T[7])
    CNOT | (T[47], T[24])
    CNOT | (T[16], T[37])
    CNOT | (T[17], T[31])
    CNOT | (T[18], T[41])
    CNOT | (T[13], T[21])
    CNOT | (T[59], T[53])
    CNOT | (T[16], T[40])
    CNOT | (T[49], T[50])
    CNOT | (T[39], T[22])
    CNOT | (T[9], T[32])
    CNOT | (T[44], T[45])
    CNOT | (T[5], T[34])
    CNOT | (T[46], T[24])
    CNOT | (U[2], T[36])
    CNOT | (T[7], T[30])
    CNOT | (T[13], T[18])
    CNOT | (T[58], T[59])
    CNOT | (T[40], T[23])
    CNOT | (T[46], T[49])
    CNOT | (T[41], T[33])
    CNOT | (T[42], T[50])
    CNOT | (T[22], T[29])
    CNOT | (T[13], T[28])
    CNOT | (T[56], T[58])
    CNOT | (T[47], T[49])
    CNOT | (T[51], T[59])
    CNOT | (T[18], T[35])
    CNOT | (T[40], T[32])
    CNOT | (T[21], T[33])
    CNOT | (T[16], T[13])
    CNOT | (T[40], T[28])
    CNOT | (T[55], T[58])
    CNOT | (T[39], T[13])
    QAND_gate(eng, T[21], T[24], T[35], resource_check)
    QAND_gate(eng, T[22], T[49], T[65], resource_check)
    QAND_gate(eng, T[23], T[50], T[61], resource_check)
    QAND_gate(eng, T[25], T[26], T[36], resource_check)
    QAND_gate(eng, T[27], T[48], T[62], resource_check)
    QAND_gate(eng, T[28], T[45], T[66], resource_check)
    QAND_gate(eng, T[29], T[30], T[37], resource_check)
    QAND_gate(eng, T[31], T[58], T[67], resource_check)
    QAND_gate(eng, T[32], T[59], T[63], resource_check)
    QAND_gate(eng, T[33], T[34], T[38], resource_check)
    QAND_gate(eng, T[13], T[57], T[64], resource_check)
    QAND_gate(eng, T[40], T[54], T[60], resource_check)
    CNOT | (T[60], S[0])
    CNOT | (T[61], S[1])
    CNOT | (T[62], S[2])
    CNOT | (T[63], S[3])
    CNOT | (T[64], S[4])
    CNOT | (T[65], S[5])
    CNOT | (T[66], S[6])
    CNOT | (T[67], S[7])
    CNOT | (T[35], S[1])
    CNOT | (T[38], S[0])
    CNOT | (T[38], S[4])
    CNOT | (S[3], S[7])
    CNOT | (T[35], S[5])
    CNOT | (S[0], S[5])
    CNOT | (T[37], S[3])
    CNOT | (S[6], S[2])
    CNOT | (S[7], S[2])
    CNOT | (S[4], S[6])
    CNOT | (S[7], S[4])
    CNOT | (S[0], S[7])
    CNOT | (S[1], S[0])
    CNOT | (T[36], S[6])
    CNOT | (S[3], S[1])
    CNOT | (S[1], S[4])
    CNOT | (S[6], S[7])
    CNOT | (S[0], S[3])
    CNOT | (S[2], S[5])
    X | S[1]
    X | S[2]
    X | S[6]
    X | S[7]
    QAND_Adj(eng, T[40], T[54], T[60], resource_check)
    QAND_Adj(eng, T[13], T[57], T[64], resource_check)
    QAND_Adj(eng, T[33], T[34], T[38], resource_check)
    QAND_Adj(eng, T[32], T[59], T[63], resource_check)
    QAND_Adj(eng, T[31], T[58], T[67], resource_check)
    QAND_Adj(eng, T[29], T[30], T[37], resource_check)
    QAND_Adj(eng, T[28], T[45], T[66], resource_check)
    QAND_Adj(eng, T[27], T[48], T[62], resource_check)
    QAND_Adj(eng, T[25], T[26], T[36], resource_check)
    QAND_Adj(eng, T[23], T[50], T[61], resource_check)
    QAND_Adj(eng, T[22], T[49], T[65], resource_check)
    QAND_Adj(eng, T[21], T[24], T[35], resource_check)
    CNOT | (T[39], T[13])
    CNOT | (T[55], T[58])
    CNOT | (T[40], T[28])
    CNOT | (T[16], T[13])
    CNOT | (T[21], T[33])
    CNOT | (T[40], T[32])
    CNOT | (T[18], T[35])
    CNOT | (T[51], T[59])
    CNOT | (T[47], T[49])
    CNOT | (T[56], T[58])
    CNOT | (T[13], T[28])
    CNOT | (T[22], T[29])
    CNOT | (T[42], T[50])
    CNOT | (T[41], T[33])
    CNOT | (T[46], T[49])
    CNOT | (T[40], T[23])
    CNOT | (T[58], T[59])
    CNOT | (T[13], T[18])
    CNOT | (T[7], T[30])
    CNOT | (U[2], T[36])
    CNOT | (T[46], T[24])
    CNOT | (T[5], T[34])
    CNOT | (T[44], T[45])
    CNOT | (T[9], T[32])
    CNOT | (T[39], T[22])
    CNOT | (T[49], T[50])
    CNOT | (T[16], T[40])
    CNOT | (T[59], T[53])
    CNOT | (T[13], T[21])
    CNOT | (T[18], T[41])
    CNOT | (T[17], T[31])
    CNOT | (T[16], T[37])
    CNOT | (T[47], T[24])
    CNOT | (T[5], T[7])
    CNOT | (T[44], T[26])
    CNOT | (T[51], T[30])
    CNOT | (U[2], T[9])
    CNOT | (T[50], T[45])
    CNOT | (T[40], T[29])
    CNOT | (T[18], T[22])
    CNOT | (T[53], T[54])
    CNOT | (T[13], T[25])
    CNOT | (T[41], T[28])
    CNOT | (T[8], T[23])
    CNOT | (T[16], T[22])
    CNOT | (T[5], T[36])
    CNOT | (T[42], T[24])
    CNOT | (T[17], T[21])
    CNOT | (T[7], T[9])
    CNOT | (T[56], T[30])
    CNOT | (T[45], T[48])
    CNOT | (T[50], T[26])
    CNOT | (T[39], T[40])
    CNOT | (T[54], T[57])
    CNOT | (T[53], T[34])
    CNOT | (T[13], T[31])
    CNOT | (T[41], T[18])
    CNOT | (T[6], T[25])
    CNOT | (T[17], T[29])
    CNOT | (T[4], T[8])
    CNOT | (T[39], T[27])
    CNOT | (T[7], T[38])
    CNOT | (T[52], T[58])
    CNOT | (T[43], T[49])
    CNOT | (T[9], T[36])
    CNOT | (T[16], T[24])
    CNOT | (T[59], T[30])
    CNOT | (T[48], T[26])
    CNOT | (T[40], T[21])
    CNOT | (T[57], T[34])
    CNOT | (T[41], T[13])
    CNOT | (T[55], T[30])
    CNOT | (T[8], T[6])
    CNOT | (T[39], T[31])
    CNOT | (U[2], T[5])
    CNOT | (T[22], T[29])
    CNOT | (T[9], T[38])
    CNOT | (T[50], T[24])
    CNOT | (T[49], T[45])
    CNOT | (T[59], T[53])
    CNOT | (T[47], T[48])
    CNOT | (T[58], T[54])
    CNOT | (T[40], T[25])
    CNOT | (T[41], T[27])
    CNOT | (T[21], T[33])
    CNOT | (T[56], T[57])
    CNOT | (T[18], T[26])
    CNOT | (T[13], T[16])
    QAND_Adj(eng, T[9], T[13], T[59], resource_check)
    QAND_Adj(eng, T[7], T[16], T[58], resource_check)
    QAND_Adj(eng, T[5], T[18], T[57], resource_check)
    QAND_Adj(eng, T[37], T[38], T[56], resource_check)
    QAND_Adj(eng, T[35], T[36], T[55], resource_check)
    QAND_Adj(eng, U[2], T[17], T[54], resource_check)
    QAND_Adj(eng, T[33], T[34], T[53], resource_check)
    QAND_Adj(eng, T[31], T[32], T[52], resource_check)
    QAND_Adj(eng, T[29], T[30], T[51], resource_check)
    QAND_Adj(eng, T[8], T[28], T[50], resource_check)
    QAND_Adj(eng, T[6], T[27], T[49], resource_check)
    QAND_Adj(eng, T[4], T[26], T[48], resource_check)
    QAND_Adj(eng, T[24], T[25], T[47], resource_check)
    QAND_Adj(eng, T[22], T[23], T[46], resource_check)
    QAND_Adj(eng, U[0], T[21], T[45], resource_check)
    QAND_Adj(eng, T[19], T[20], T[44], resource_check)
    QAND_Adj(eng, T[2], T[3], T[43], resource_check)
    QAND_Adj(eng, T[0], T[1], T[42], resource_check)
    QAND_Adj(eng, U[1], U[6], T[41], resource_check)
    QAND_Adj(eng, U[3], U[7], T[40], resource_check)
    QAND_Adj(eng, U[4], U[5], T[39], resource_check)
    CNOT | (T[13], T[28])
    CNOT | (T[18], U[6])
    CNOT | (T[24], T[37])
    CNOT | (T[18], T[26])
    CNOT | (T[17], U[3])
    CNOT | (T[16], T[13])
    CNOT | (T[16], T[27])
    CNOT | (U[3], T[3])
    CNOT | (T[13], T[24])
    CNOT | (T[17], T[18])
    CNOT | (T[35], T[22])
    CNOT | (T[19], T[33])
    CNOT | (T[31], T[2])
    CNOT | (T[0], T[29])
    CNOT | (T[6], T[14])
    CNOT | (T[5], T[16])
    CNOT | (U[0], U[3])
    CNOT | (T[17], T[13])
    CNOT | (T[17], T[21])
    CNOT | (T[38], T[3])
    CNOT | (T[8], T[10])
    CNOT | (T[9], T[1])
    CNOT | (U[1], T[35])
    CNOT | (T[19], U[5])
    CNOT | (T[5], T[0])
    CNOT | (T[18], T[16])
    CNOT | (T[7], T[14])
    CNOT | (T[13], T[31])
    CNOT | (T[4], U[0])
    CNOT | (T[7], T[32])
    CNOT | (T[9], T[38])
    CNOT | (T[8], T[25])
    CNOT | (T[34], T[35])
    CNOT | (T[0], U[4])
    CNOT | (T[6], T[1])
    CNOT | (T[16], U[1])
    CNOT | (T[18], T[19])
    CNOT | (T[14], T[17])
    CNOT | (U[2], T[13])
    CNOT | (U[0], T[20])
    CNOT | (T[4], T[12])
    CNOT | (T[7], U[4])
    CNOT | (T[8], T[2])
    CNOT | (U[2], T[34])
    CNOT | (T[9], T[10])
    CNOT | (T[6], U[5])
    CNOT | (T[16], T[0])
    CNOT | (T[14], T[18])
    CNOT | (T[13], U[1])
    CNOT | (U[0], T[1])
    CNOT | (U[2], T[30])
    CNOT | (T[4], T[23])
    CNOT | (T[7], T[38])
    CNOT | (T[9], T[36])
    CNOT | (T[6], T[2])
    CNOT | (T[8], U[3])
    CNOT | (T[5], T[34])
    CNOT | (T[11], T[17])
    CNOT | (T[0], U[4])
    CNOT | (T[10], T[18])
    CNOT | (T[12], T[16])
    CNOT | (T[13], U[7])
    CNOT | (U[0], U[5])
    CNOT | (T[5], T[36])
    CNOT | (U[2], T[32])
    CNOT | (T[7], T[30])
    CNOT | (T[6], U[3])
    CNOT | (T[9], U[7])
    CNOT | (T[34], T[35])
    CNOT | (T[0], T[29])
    CNOT | (T[18], T[16])
    CNOT | (T[4], T[12])
    CNOT | (T[8], T[10])
    CNOT | (U[0], U[6])
    CNOT | (T[17], T[13])
    CNOT | (T[5], T[30])
    CNOT | (T[38], T[3])
    CNOT | (T[9], T[32])
    CNOT | (T[19], T[33])
    CNOT | (T[7], U[7])
    CNOT | (T[6], T[14])
    CNOT | (U[1], T[35])
    CNOT | (T[8], T[0])
    CNOT | (T[15], T[18])
    CNOT | (T[16], T[13])
    CNOT | (T[4], U[0])
    CNOT | (T[6], T[25])
    CNOT | (U[2], U[4])
    CNOT | (T[24], T[37])
    CNOT | (T[8], T[23])
    CNOT | (T[5], T[1])
    CNOT | (T[31], T[2])
    CNOT | (U[3], T[3])
    CNOT | (T[19], U[5])
    CNOT | (T[7], T[14])
    CNOT | (T[35], T[22])
    CNOT | (T[9], T[10])
    CNOT | (T[15], T[17])
    CNOT | (T[4], T[0])
    CNOT | (U[0], T[13])
    QAND_Adj(eng, T[8], T[9], T[18], resource_check)
    QAND_Adj(eng, T[6], T[7], T[17], resource_check)
    QAND_Adj(eng, T[4], T[5], T[16], resource_check)
    QAND_Adj(eng, T[2], T[3], T[15], resource_check)
    QAND_Adj(eng, T[0], T[1], T[14], resource_check)
    QAND_Adj(eng, U[0], U[2], T[13], resource_check)
    QAND_Adj(eng, U[1], U[6], T[12], resource_check)
    QAND_Adj(eng, U[3], U[7], T[11], resource_check)
    QAND_Adj(eng, U[4], U[5], T[10], resource_check)
    CNOT | (U[7], U[4])
    CNOT | (U[0], U[3])
    CNOT | (U[0], U[5])
    CNOT | (U[5], T[0])
    CNOT | (U[3], T[2])
    CNOT | (U[4], T[9])
    CNOT | (U[1], U[2])
    CNOT | (U[2], T[5])
    CNOT | (U[2], T[9])
    CNOT | (U[2], T[3])
    CNOT | (U[4], T[1])
    CNOT | (U[4], T[7])
    CNOT | (U[1], U[6])
    CNOT | (U[1], U[0])
    CNOT | (U[3], T[0])
    CNOT | (U[7], U[1])
    CNOT | (U[0], T[6])
    CNOT | (U[1], T[7])
    CNOT | (U[0], T[4])
    CNOT | (U[3], U[4])
    CNOT | (U[6], U[5])
    CNOT | (U[5], U[2])
    CNOT | (U[4], U[2])
    CNOT | (U[0], U[3])
    CNOT | (U[5], T[8])
    CNOT | (U[3], T[8])
    CNOT | (U[1], T[3])
    CNOT | (U[5], T[6])
    CNOT | (U[6], T[4])
    CNOT | (U[2], U[1])
    CNOT | (U[6], U[4])
    
    
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
    Tn = 68
    for i in range(16):
        T_Depth_3_CStar_S_Box_and_Inv_new(eng, State_Registers[8*i:8+8*i], T_State[Tn*i:Tn+Tn*i], Ancilla_State[8*i:8+8*i], Forward, resource_check)
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
    Tn = 68
    for i in range(16):
        # Inv_SubBytes
        T_Depth_3_CStar_S_Box_and_Inv_new(eng, State_Registers[8*i:8+8*i], T_State[Tn*i:Tn+Tn*i], Ancilla_State[8*i:8+8*i], Inv, resource_check)
        # SubBytes
        T_Depth_3_CStar_S_Box_and_Inv_new(eng, Ancilla_State[256+8*i:264+8*i], T_State[16*Tn+Tn*i:16*Tn+Tn+Tn*i], Ancilla_State[128+8*i:136+8*i], Forward, resource_check)
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
    Tn = 68
    for i in range(16):
        # Inv_SubBytes
        T_Depth_3_CStar_S_Box_and_Inv_new(eng, Ancilla_State[128+8*i:136+8*i], T_State[Tn*i:Tn+Tn*i], Ancilla_State[256+8*i:264+8*i], Inv, resource_check)
        
    if resource_check == 0:
        ShiftRows(eng, Ancilla_State[128:256])
    XOR_State(State_Registers, Ancilla_State[128:256])


"""------------------------AES-128-----------------------"""

def AES_128_Encrypt(eng, State_Registers, resource_check):
    Tn = 68
    Ancilla_State = eng.allocate_qureg(128*3)
    T_State = eng.allocate_qureg(Tn*16+Tn*16)

    Round_1(eng, State_Registers, Ancilla_State, T_State, resource_check)
    # print(f"round{1} finished!")
    for r in range(2, 11):
        
        Round_2_10(eng, r, State_Registers, Ancilla_State, T_State, resource_check)
        # print(f"round{r} finished!")

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

    
