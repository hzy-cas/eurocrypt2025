from classical_to_quantum import *

# SKINNY-128 Sbox 8-bit
def SKINNY128_Sbox_quantum():
    n = 8
    BV = BooleanPolynomialRing(names=[f"X{i}" for i in range(n)])
    X0,X1,X2,X3,X4,X5,X6,X7 = BV("X0"),BV("X1"),BV("X2"),BV("X3"),BV("X4"),BV("X5"),BV("X6"),BV("X7")
    SKINNY128_Sbox_ANF = [
        X0*X1*X2*X3*X4 + X0*X1*X2*X3*X5 + X0*X1*X2*X3*X6*X7 + X0*X1*X2*X3*X6 + X0*X1*X2*X3*X7 + X0*X1*X2*X3 + X0*X1*X2*X5 + X0*X1*X2 + X0*X1*X3*X4 + X0*X1*X3*X5 + X0*X1*X3*X6*X7 + X0*X1*X3*X6 + X0*X1*X3*X7 + X0*X1*X3 + X0*X1*X4*X6 + X0*X1*X4 + X0*X1*X5 + X0*X1*X6*X7 + X0*X1*X7 + X0*X1 + X0*X2*X3*X4 + X0*X2*X3*X5 + X0*X2*X3*X6*X7 + X0*X2*X3*X6 + X0*X2*X3*X7 + X0*X2*X3 + X0*X2*X5 + X0*X2 + X0*X3*X4*X6 + X0*X3*X5*X6 + X0*X3*X7 + X0*X3 + X0*X5*X6 + X0*X6 + X0*X7 + X0 + X1*X2*X3*X4*X6 + X1*X2*X3*X6 + X1*X2*X4*X6 + X1*X2*X4 + X1*X2*X5 + X1*X2*X6*X7 + X1*X2*X7 + X1*X2 + X1*X3*X4*X6 + X1*X3*X6 + X1*X5*X6 + X1*X6 + X1*X7 + X1 + X2*X3*X4 + X2*X3*X5*X6 + X2*X3*X5 + X2*X3*X6*X7 + X2*X5*X6 + X2*X6 + X2*X7 + X3*X4*X6 + X3*X6 + X5*X6 + X6 + X7 + 1
        , X0*X1*X2*X4 + X0*X1*X2*X6*X7 + X0*X1*X2*X6 + X0*X1*X2*X7 + X0*X1*X4 + X0*X1*X6*X7 + X0*X1*X6 + X0*X1*X7 + X0*X2*X4 + X0*X2*X6*X7 + X0*X2*X6 + X0*X2*X7 + X0*X4*X6 + X0*X6 + X1*X2*X3*X4 + X1*X2*X3*X6*X7 + X1*X2*X3*X6 + X1*X2*X3*X7 + X1*X2*X5 + X1*X2 + X1*X3*X4 + X1*X3*X6*X7 + X1*X3*X6 + X1*X3*X7 + X1*X5 + X1 + X2*X3*X4*X6 + X2*X3*X6 + X2*X4*X6 + X2*X4 + X2*X5 + X2*X6*X7 + X2*X7 + X2 + X3*X4*X6 + X3*X6 + X5*X6 + X6 + X7
        , X1*X2 + X1 + X2 + X6 + 1
        , X0*X3 + X0 + X1 + X2*X3 + X2
        , X0*X4 + X0*X6*X7 + X0*X6 + X0*X7 + X2*X3*X4 + X2*X3*X6*X7 + X2*X3*X6 + X2*X3*X7 + X2*X4 + X2*X6*X7 + X2*X6 + X2*X7 + X3*X4 + X3*X6*X7 + X3*X6 + X3*X7 + X3 + X4*X5 + X4 + X5*X6*X7 + X5*X6 + X5*X7 + X6*X7 + X6 + X7
        , X0 + X2*X3 + X2 + X3 + 1
        , X4 + X6*X7 + X6 + X7 + 1
        , X0*X4 + X0*X6*X7 + X0*X6 + X0*X7 + X2*X3*X4 + X2*X3*X6*X7 + X2*X3*X6 + X2*X3*X7 + X2*X4 + X2*X6*X7 + X2*X6 + X2*X7 + X3*X4 + X3*X6*X7 + X3*X6 + X3*X7 + X5]

    # classical AND-layer structure
    L = [['X0','X1','X2','X3','X4','X5','X6','X7']
        , ['X7', 'X6', 'X2', 'X1+X3', 'X3', 'X2', 'X0', 'X3']
        , ['X0+X6+X7+M1+M3', 'X1+X2+X6+X7+M1+M2', 'X0+X4+X7+M0+M1+M3', 'X1+X2+X6+M1+M2', 'X3+X4+X6+X7+M0', 'X0+X2+X4+X6+X7+M0+M2', 'X4+X5+X6+X7+M0', 'X5']
        , ['X1+X2+X6+M1+M2', 'X1+X2+X4+X5+X7+M0+M1+M2+M3+M6', 'M5+M7', 'X1+X2+X4+X5+X7+M0+M1+M2+M3+M6']
        , ['X0+X2+X6+M1+M3+M4+M5+M7+M8+M9', 'X7+M8','X1+X2+X6+M1+M2', 'X0+X1+X2+M2+M3','X3+X5+M3+M6+M7', 'X0+X2+X3+M2','X4+X6+X7+M0', 'X4+X5+X6+X7+M0+M3+M6']]
    qc_info = classical_to_quantum(n=8, m=8, s=3, C=L)

    generate_quantum_circuit(qc_info=qc_info, outputs_ANF=SKINNY128_Sbox_ANF, filename="SKINNY128_Sbox_forward_NCT.qasm")

# ASCON Sbox 5-bit
def ASCON_Sbox_quantum():
    n = 5
    BV = BooleanPolynomialRing(names=[f"X{i}" for i in range(n)])
    X0,X1,X2,X3,X4 = BV("X0"),BV("X1"),BV("X2"),BV("X3"),BV("X4")
    ASCON_Sbox_ANF = [
        X0*X1+X0+X1*X2+X1*X4+X1+X2+X3
        , X0+X1*X2+X1*X3+X1+X2*X3+X2+X3+X4
        , X1+X2+X3*X4+X4+1
        , X0*X3+X0*X4+X0+X1+X2+X3+X4
        , X0*X1+X1*X4+X1+X3+X4]

    # classical AND-layer structure
    L = [['X0', 'X1', 'X2', 'X3', 'X4']
        , ['X0+X4', 'X3+X4', 'X0+X1+X3', 'X0+X4', 'X1+X2+X3+X4', 'X1+X2+X4', 'X0+X3+X4', 'X0', 'X1+X2', 'X2']
        , ['X1+X3+X4+M0+M1+M4', 'X2+X3+X4+M0+M2+M3+M4', 'X0+X1+X2+M0+M3', 'X1+X2+X3+X4+M3', 'X0+X1+X3+M0+M1']]
    qc_info = classical_to_quantum(n=5, m=5, s=1, C=L)

    generate_quantum_circuit(qc_info=qc_info, outputs_ANF=ASCON_Sbox_ANF, filename="ASCON_Sbox_forward_NCT.qasm")
    
SKINNY128_Sbox_quantum()
ASCON_Sbox_quantum()