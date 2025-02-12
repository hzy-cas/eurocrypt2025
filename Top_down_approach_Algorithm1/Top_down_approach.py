# coding : utf-8

# Algorithm2: Top-down approach

from sage.all import * 
from find_covers_SAT import *
import os

############################################################
"""
construct from AND-depth-1 to maxd
"""
def construct_from_Max_Depth_Cover(F, Covers_Layer, AND_count, maxd, name):
    result = [f"##### {name} AND-count: {AND_count} #####"]
    # format is (1) C=D*D (2) f=C1+C2...+Ck+R
    f_idx, C_idx, D_idx, R_idx = 0, 0, 0, 0 
    # polynomials and their name
    poly_to_name = dict()
    for d in range(2, maxd + 1):
        result.append(f"##### AND-depth-{d-1} -> {d} #####")
        for g in Covers_Layer[d]:
            for i in range(g.k):
                if f"{g.D[2*i]}" not in poly_to_name:
                    D1 = f"D{D_idx}" 
                    result.append(f"{D1} = {g.D[2*i]}")
                    D_idx += 1
                else:
                    D1 = poly_to_name[f"{g.D[2*i]}"]    

                if f"{g.D[2*i+1]}" not in poly_to_name:
                    D2 = f"D{D_idx}" 
                    result.append(f"{D2} = {g.D[2*i+1]}")
                    D_idx += 1
                else:
                    D2 = poly_to_name[f"{g.D[2*i+1]}"]    
                result.append(f"C{C_idx+i} = {D1} * {D2}")
            
            poly_to_name[f"{g.f}"] = f"f{f_idx}"

            if f"{g.R}" not in poly_to_name:
                R = f"R{R_idx}"
                result.append(f"{R} = {g.R}")
                R_idx += 1
            else:
                R = poly_to_name[f"{g.R}"]
         
            result.append(f"f{f_idx} = {' + '.join([f'C{C_idx+j}' for j in range(g.k)])} + {R}")
            C_idx += g.k
            f_idx += 1

    result.append("##### Boolean function F #####")
    for i in range(len(F)):
        result.append(f"F{i} = {poly_to_name[f'{F[i]}']}")
    
    with open(f"{name}_result.txt", "w") as f:
        f.write("\n".join(result))
    
    print(f'The result has been saved in "{name}_result.txt"')

"""
Top-down approach
Basic strategy find covers with small size
d -> d - 1 -> ... -> 1
Usually finally Boolean polynomials with AND-depth-1 will be left, so repeat find max-depth cover until AND-depth-1, then implement all monomials with degree-2
"""
def Top_down_approach_basic(F, n, B, name):
    pre_work()

    # round up, eg: deg=5,6,7,8 => maxd=3
    maxd = ceil(log2(max([f.degree() for f in F])))
    # different AND-depth Boolean polynomials
    M = get_M_Boolean_monomials(n=n, B=B)
    # candidate set
    H = F[:] 
    # number of monomials with degree-2
    AND_count = n*(n - 1) // 2
    
    # Boolean variable for coefficients
    BA = [B(f"a{i}") for i in range(5000)]
    
    # SAT Solver run time, for fast find covers
    timeout = 60
    idx = 0
    Covers_Layer = [[] for d in range(maxd + 1)]
    # AND-depth Top-down
    for d in range(maxd, 1, -1):
        # select from H, depth-d: [2^(d-1)+1, 2^d]
        G = [h for h in H if h.degree() in range(2**(d-1)+1, 2**d+1)] 
        for g in G: 
            g_Max_depth_cover = Max_Depth_Cover(g)
            # basic strategy find covers with small size
            for k in range(1, 10):
                prefix = f"covers_eqs/{name}_{idx}_d{d}_k{k}"
                find_covers_eqs(f=g, n=n, d=d, k=k, BA=BA, M=M, prefix=prefix) 
    
                os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
                os.system(f"timeout {timeout} ./kissat {prefix}.cnf > {prefix}.out --sat")

                if not os.path.exists(f"{prefix}.out"):
                    continue
                with open(f"{prefix}.out", "r") as ff:
                    content = ff.read()
                
                # k covers UNSAT or timeout
                if "UNSATISFIABLE" in content or "SATISFIABLE" not in content:
                    os.system(f"rm {prefix}.out")
                    continue 
                
                AND_count += k
                # SAT result, add factors and remainder to H
                factors, R = find_covers_result(f=g, n=n, d=d, k=k, M=M, prefix=prefix) 
                H += factors + [R]

                # update Max Depth Cover 
                g_Max_depth_cover.k = k
                g_Max_depth_cover.D = factors
                g_Max_depth_cover.R = R 
                Covers_Layer[d].append(g_Max_depth_cover)
                break
            idx += 1

    ############################################################
    construct_from_Max_Depth_Cover(F=F, Covers_Layer=Covers_Layer, AND_count=AND_count, maxd=maxd, name=name)
    os.system(f"rm covers_eqs/*.eqs covers_eqs/*.cnf")

############################################################
"""
Top-down approach basic for AES Sbox 
Get an AES Sbox implementation with AND-depth-3, AND-count-98 
"""
def basic_for_AES_Sbox():
    n = 8
    a_variable = ["a" + str(i) for i in range(5000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    F = get_AES_Sbox_ANF(X=[B(f"x{i}") for i in range(n)])

    Top_down_approach_basic(F=F, n=n, B=B, name="AES_Sbox")

"""
For AES Sbox:
(1) fi = Di1 * Di2 + Ri (2) find_covers of Di1, Di2, Ri
Simultaneously (1)(2) get AND-count is not more than (1) then (2)
Obviously the former problem is more difficult to solve
"""
def find_linear_covers_for_AES_Sbox():
    pre_work()

    n = 8
    a_variable = ["a" + str(i) for i in range(5000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    F = get_AES_Sbox_ANF(X=[B(f"x{i}") for i in range(n)])
    # different AND-depth Boolean polynomials
    M = get_M_Boolean_monomials(n=n, B=B)

    eqs_to_cnfs = []
    solve_cnfs  = []
    
    for i in range(1, 256):
        # g = a1*f1 + a2*f2 + ... + a8*f8
        A = [(i >> (7 - j)) & 1 for j in range(8)]
        g = Boolean_Inner_Product(A=A, X=F)
        s = [f"{j}" for j in range(8) if A[j] == 1]
        prefix = f"covers_eqs/AES_Sbox_d3_to_1_{''.join(s)}"
        find_covers_two_layer_eqs(f=g, n=8, d=3, k1=1, k2=[1,2], BA=BA, M=M, prefix=prefix)
        eqs_to_cnfs.append(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
        solve_cnfs.append(f"timeout 20 ./kissat {prefix}.cnf > {prefix}.out --sat")
    
    with open("eqs_to_cnfs.sh", "w") as ff:
        ff.write("\n".join(eqs_to_cnfs))
    with open("solve_cnfs.sh", "w") as ff:
        ff.write("\n".join(solve_cnfs))
    os.system("cat eqs_to_cnfs.sh | parallel -j 8")
    os.system("cat solve_cnfs.sh | parallel -j 8")

    linear_123_covers_results = []
    for i in range(1, 256):
        s = [f"{j}" for j in range(8) if (i >> (7 - j)) & 1 == 1]
        prefix = f"covers_eqs/AES_Sbox_d3_to_1_{''.join(s)}"
        
        if not os.path.exists(f"{prefix}.out"):
            continue
        with open(f"{prefix}.out", "r") as ff:
                    content = ff.read()
                
        # k covers UNSAT or timeout
        if "UNSATISFIABLE" in content or "SATISFIABLE" not in content:
            os.system(f"rm {prefix}.out")
            continue 

        linear_123_covers_results.append(i)
    
    print(linear_123_covers_results) 
    os.system("rm covers_eqs/*.eqs covers_eqs/*.cnf")

"""
Top-down approach for AES Sbox 
Strategy: invertible linear combinations & covers of factors
For AES Sbox, F={f1, f2,..., f8}
(1) for any fi has a cover with size 1 => fi = Di1 * Di2 + Ri
(2) based on (1) simultaneously find covers of {Di1, Di2, Ri}
(3) Select some invertible linear combinations of F, such that the size of covers of {Di1, Di2, Ri} is 1,2,3. Find smaller size: 1,1,3
linear_123_covers_results: 
    [4, 41, 63, 111, 133, 144, 187, 189, 193, 227, 240, 241, 247]
    4 : [0,0,0,0,0,1,0,0] => f5
    41: [0,0,1,0,1,0,0,1] => f2+f4+f7
    ...
(4) finally get the total AND-count for three AND-layers: 8+8x(1+1+3)+28=76
"""
def Top_down_approach_for_AES_Sbox():
    pre_work()

    n = 8
    a_variable = ["a" + str(i) for i in range(5000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    F = get_AES_Sbox_ANF(X=[B(f"x{i}") for i in range(n)])
    maxd = 3
    # different AND-depth Boolean polynomials
    M = get_M_Boolean_monomials(n=n, B=B)
 
    # g = a1*f1 + a2*f2 + ... + a8*f8
    A = [[0,0,0,0,0,1,0,0] # 5      (√ 113)
        ,[1,0,1,1,1,0,1,1] # 023467 (√ 113)
        ,[1,0,0,0,0,1,0,1] # 057    (√ 113)
        ,[1,1,0,0,0,0,0,1] # 017    (√ 113)
        ,[1,0,0,1,0,0,0,0] # 03     (√ 113)
        ,[1,1,1,1,0,0,0,1] # 01237  (√ 113)
        ,[1,1,1,1,0,0,0,0] # 0123   (√ 113)
        ,[1,0,1,1,1,1,0,1]]# 023457 (√ 113)
        
    eqs_to_cnfs = []
    solve_cnfs  = []
    G = [Boolean_Inner_Product(A=A[i], X=F) for i in range(8)]
    k2 = [1,1,3]
    for i in range(8):
        s = [f"{j}" for j in range(8) if A[i][j] == 1]
        prefix = f"covers_eqs/AES_Sbox_d3_to_1_{''.join(s)}"
        find_covers_two_layer_eqs(f=G[i], n=n, d=maxd, k1=1, k2=k2, BA=BA, M=M, prefix=prefix)
        eqs_to_cnfs.append(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
        solve_cnfs.append(f"./kissat {prefix}.cnf > {prefix}.out --sat")
    
    with open("eqs_to_cnfs.sh", "w") as ff:
        ff.write("\n".join(eqs_to_cnfs))
    with open("solve_cnfs.sh", "w") as ff:
        ff.write("\n".join(solve_cnfs))
    os.system("cat eqs_to_cnfs.sh | parallel -j 8")
    os.system("cat solve_cnfs.sh | parallel -j 8")
    
    Covers_Layer = [[] for d in range(maxd + 1)]
    # find covers for 8 Ri(size = 3)
    for i in range(8):
        g_Max_depth_cover      = Max_Depth_Cover(G[i])
        s = [f"{j}" for j in range(8) if A[i][j] == 1]
        prefix = f"covers_eqs/AES_Sbox_d3_to_1_{''.join(s)}"
        factors1, R1, factors2, R2 = find_covers_two_layer_result(f=G[i], n=n, d=maxd, k1=1, k2=k2, M=M, prefix=prefix)
   
        g_Max_depth_cover.k = 1 
        g_Max_depth_cover.D = factors1 
        g_Max_depth_cover.R = R1 
        Covers_Layer[maxd].append(g_Max_depth_cover)

        prefix = f"covers_eqs/AES_Sbox_d2_R{i}"
        
        find_covers_eqs(f=R1, n=n, d=maxd-1, k=3, BA=BA, M=M, prefix=prefix)
        os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
        os.system(f"./kissat {prefix}.cnf > {prefix}.out --sat")
      
        R_factor, R_R = find_covers_result(f=R1, n=n, d=maxd-1, k=3, M=M, prefix=prefix)

        # for Di1, Di2, Ri construct Max depth cover
        for j in range(2):
            D_Max_depth_cover   = Max_Depth_Cover(factors1[j])
            D_Max_depth_cover.k = k2[j] 
            D_Max_depth_cover.D = factors2[2*sum(k2[:j]):2*sum(k2[:j])+2*k2[j]] 
            D_Max_depth_cover.R = R2[j]
            Covers_Layer[maxd - 1].append(D_Max_depth_cover)
 
        R_Max_depth_cover   = Max_Depth_Cover(R1)
        R_Max_depth_cover.k = 3
        R_Max_depth_cover.D = R_factor
        R_Max_depth_cover.R = R_R
        Covers_Layer[maxd - 1].append(R_Max_depth_cover)

    construct_from_Max_Depth_Cover(F=G, Covers_Layer=Covers_Layer, AND_count=76, maxd=maxd, name="AES_Sbox")

    # G=AF => F=A^-1G
    A_inv = matrix(GF(2), A).inverse()
    A_inv_F = ["\n##### F=AY => Y=A^-1F #####"]
    for i in range(8):
        A_inv_F.append(f"Y{i} = " + " + ".join([f"F{j}" for j in range(8) if A_inv[i][j] == 1 ]))
    
    with open("AES_Sbox_result.txt", "a") as f:
        f.write("\n".join(A_inv_F))
    
    os.system(f"rm covers_eqs/*.eqs covers_eqs/*.cnf")

"""
The common covers for GF(2^4) Inv
"""
def Top_down_approach_for_GF24_Inv():
    n = 4
    a_variable = ["a" + str(i) for i in range(5000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    x0,x1,x2,x3 = B("x0"),B("x1"),B("x2"),B("x3")
    GF24_Inv = [x1*x2*x3+x0*x2+x1*x2+x2+x3
            , x0*x2*x3+x0*x2+x1*x2+x1*x3+x3
            , x0*x1*x3+x0*x2+x0*x3+x0+x1
            , x0*x1*x2+x0*x2+x0*x3+x1*x3+x1]
    M = get_M_Boolean_monomials(n=n, B=B)
    prefix = "covers_eqs/GF24_Inv"
    find_common_covers_eqs(F=GF24_Inv, n=n, maxd=2, ks=[2,4], BA=BA, M=M, prefix=prefix)

    os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
    os.system(f"./kissat {prefix}.cnf > {prefix}.out --sat")

    find_common_covers_result(F=GF24_Inv, n=n, maxd=2, ks=[2,4], M=M, prefix=prefix)

############################################################
"""
Test Program
(1) There are three instances:
    basic_for_AES_Sbox()
    Top_down_approach_for_AES_Sbox()
    Top_down_approach_for_GF24_Inv()
(2) You can also choose other Boolean functions for:
    Top_down_approach_basic(F=F, n=n, B=B, name="test")
"""
def test_Top_down_approach():
    # basic_for_AES_Sbox()
    # Top_down_approach_for_AES_Sbox()
    Top_down_approach_for_GF24_Inv()

    # n = 8
    # a_variable = ["a" + str(i) for i in range(5000)]
    # x_variable = ["x" + str(i) for i in range(n)]

    # # Boolean polynomial ring variable (a, x)
    # B = BooleanPolynomialRing(names=(a_variable + x_variable))
    # # Boolean functions
    # F = []

    # Top_down_approach_basic(F=F, n=n, B=B, name="test")