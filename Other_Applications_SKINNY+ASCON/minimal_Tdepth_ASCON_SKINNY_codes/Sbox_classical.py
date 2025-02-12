# coding : utf-8

# SKINNY-128 Sbox

import os
from find_covers_SAT import *

def SKINNY128_Sbox_classical():
    print("SKINNY128 Sbox classical result:")
    # pre_work()
    n = 8
    a_variable = ["a" + str(i) for i in range(10000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    x0,x1,x2,x3 = B("x0"),B("x1"),B("x2"),B("x3")
    x4,x5,x6,x7 = B("x4"),B("x5"),B("x6"),B("x7")

    M = get_M_Boolean_monomials(n=n, B=B)

    # ANF of SKINNY-128
    SKINNY128_Sbox_ANF = [
        x0*x1*x2*x3*x4 + x0*x1*x2*x3*x5 + x0*x1*x2*x3*x6*x7 + x0*x1*x2*x3*x6 + x0*x1*x2*x3*x7 + x0*x1*x2*x3 + x0*x1*x2*x5 + x0*x1*x2 + x0*x1*x3*x4 + x0*x1*x3*x5 + x0*x1*x3*x6*x7 + x0*x1*x3*x6 + x0*x1*x3*x7 + x0*x1*x3 + x0*x1*x4*x6 + x0*x1*x4 + x0*x1*x5 + x0*x1*x6*x7 + x0*x1*x7 + x0*x1 + x0*x2*x3*x4 + x0*x2*x3*x5 + x0*x2*x3*x6*x7 + x0*x2*x3*x6 + x0*x2*x3*x7 + x0*x2*x3 + x0*x2*x5 + x0*x2 + x0*x3*x4*x6 + x0*x3*x5*x6 + x0*x3*x7 + x0*x3 + x0*x5*x6 + x0*x6 + x0*x7 + x0 + x1*x2*x3*x4*x6 + x1*x2*x3*x6 + x1*x2*x4*x6 + x1*x2*x4 + x1*x2*x5 + x1*x2*x6*x7 + x1*x2*x7 + x1*x2 + x1*x3*x4*x6 + x1*x3*x6 + x1*x5*x6 + x1*x6 + x1*x7 + x1 + x2*x3*x4 + x2*x3*x5*x6 + x2*x3*x5 + x2*x3*x6*x7 + x2*x5*x6 + x2*x6 + x2*x7 + x3*x4*x6 + x3*x6 + x5*x6 + x6 + x7 + 1
        , x0*x1*x2*x4 + x0*x1*x2*x6*x7 + x0*x1*x2*x6 + x0*x1*x2*x7 + x0*x1*x4 + x0*x1*x6*x7 + x0*x1*x6 + x0*x1*x7 + x0*x2*x4 + x0*x2*x6*x7 + x0*x2*x6 + x0*x2*x7 + x0*x4*x6 + x0*x6 + x1*x2*x3*x4 + x1*x2*x3*x6*x7 + x1*x2*x3*x6 + x1*x2*x3*x7 + x1*x2*x5 + x1*x2 + x1*x3*x4 + x1*x3*x6*x7 + x1*x3*x6 + x1*x3*x7 + x1*x5 + x1 + x2*x3*x4*x6 + x2*x3*x6 + x2*x4*x6 + x2*x4 + x2*x5 + x2*x6*x7 + x2*x7 + x2 + x3*x4*x6 + x3*x6 + x5*x6 + x6 + x7
        , x1*x2 + x1 + x2 + x6 + 1
        , x0*x3 + x0 + x1 + x2*x3 + x2
        , x0*x4 + x0*x6*x7 + x0*x6 + x0*x7 + x2*x3*x4 + x2*x3*x6*x7 + x2*x3*x6 + x2*x3*x7 + x2*x4 + x2*x6*x7 + x2*x6 + x2*x7 + x3*x4 + x3*x6*x7 + x3*x6 + x3*x7 + x3 + x4*x5 + x4 + x5*x6*x7 + x5*x6 + x5*x7 + x6*x7 + x6 + x7
        , x0 + x2*x3 + x2 + x3 + 1
        , x4 + x6*x7 + x6 + x7 + 1
        , x0*x4 + x0*x6*x7 + x0*x6 + x0*x7 + x2*x3*x4 + x2*x3*x6*x7 + x2*x3*x6 + x2*x3*x7 + x2*x4 + x2*x6*x7 + x2*x6 + x2*x7 + x3*x4 + x3*x6*x7 + x3*x6 + x3*x7 + x5]

    prefix = "covers_eqs/SKINNY128_Sbox"
    # find_common_covers_eqs(F=SKINNY128_Sbox_ANF, n=n, maxd=3, ks=[4,4,2], BA=BA, M=M, prefix=prefix)
    # os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
    # os.system(f"./kissat {prefix}.cnf > {prefix}.out --sat")
    find_common_covers_result(F=SKINNY128_Sbox_ANF, n=n, maxd=3, ks=[4,4,2], M=M, prefix=prefix)

def ASCON_Sbox_classical():
    print("ASCON Sbox classical result:")
    # pre_work()
    n = 5
    a_variable = ["a" + str(i) for i in range(10000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    x0,x1,x2,x3,x4 = B("x0"),B("x1"),B("x2"),B("x3"),B("x4")

    M = get_M_Boolean_monomials(n=n, B=B)

    # ANF of SKINNY-128
    ASCON_Sbox_ANF = [
        x0*x1+x0+x1*x2+x1*x4+x1+x2+x3
        , x0+x1*x2+x1*x3+x1+x2*x3+x2+x3+x4
        , x1+x2+x3*x4+x4+1
        , x0*x3+x0*x4+x0+x1+x2+x3+x4
        , x0*x1+x1*x4+x1+x3+x4]

    k = 5
    prefix = "covers_eqs/ASCON_Sbox"
    # find_common_covers_eqs(F=ASCON_Sbox_ANF, n=n, maxd=1, ks=[k], BA=BA, M=M, prefix=prefix)
    # os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
    # os.system(f"./kissat {prefix}.cnf > {prefix}.out --sat")
    find_common_covers_result(F=ASCON_Sbox_ANF, n=n, maxd=1, ks=[k], M=M, prefix=prefix)


ASCON_Sbox_classical()
SKINNY128_Sbox_classical()

"""
SKINNY128 Sbox classical result:
############## AND-depth from 0 to 1 ##############
M0=(x7)*(x6)
M1=(x2)*(x1+x3)
M2=(x3)*(x2)
M3=(x0)*(x3)
############## AND-depth from 1 to 2 ##############
M4=(x0+x6+x7+M1+M3)*(x1+x2+x6+x7+M1+M2)
M5=(x0+x4+x7+M0+M1+M3)*(x1+x2+x6+M1+M2)
M6=(x3+x4+x6+x7+M0)*(x0+x2+x4+x6+x7+M0+M2)
M7=(x4+x5+x6+x7+M0)*(x5)
############## AND-depth from 2 to 3 ##############
M8=(x1+x2+x6+M1+M2)*(x1+x2+x4+x5+x7+M0+M1+M2+M3+M6)
M9=(M5+M7)*(x1+x2+x4+x5+x7+M0+M1+M2+M3+M6)
############## build final targets ################
Y0=1+x0+x2+x6+M1+M3+M4+M5+M7+M8+M9
Y1=x7+M8
Y2=1+x1+x2+x6+M1+M2
Y3=x0+x1+x2+M2+M3
Y4=x3+x5+M3+M6+M7
Y5=1+x0+x2+x3+M2
Y6=1+x4+x6+x7+M0
Y7=x4+x5+x6+x7+M0+M3+M6
###################################################

ASCON Sbox classical result:
############## AND-depth from 0 to 1 ##############
M0=(x0+x4)*(x3+x4)
M1=(x0+x1+x3)*(x0+x4)
M2=(x1+x2+x3+x4)*(x1+x2+x4)
M3=(x0+x3+x4)*(x0)
M4=(x1+x2)*(x2)
############## build final targets ################
Y0=x1+x3+x4+M0+M1+M4
Y1=x2+x3+x4+M0+M2+M3+M4
Y2=1+x0+x1+x2+M0+M3
Y3=x1+x2+x3+x4+M3
Y4=x0+x1+x3+M0+M1
###################################################
"""