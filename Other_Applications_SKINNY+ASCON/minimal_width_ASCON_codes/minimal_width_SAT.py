# coding : utf-8

# SAT-based method to finding minimal-width NCT implementation with different Toffoli-counts

# need Sagemath environment(Linux)
from sage.all import * 
import os

"""
Auxiliary function
"""
############################################################
"""
The file save path: file *.eqs, *.cnf, *.out 
Need to install two tools:
(1) the ANF-to-CNF converter: Bosphorus
    https://github.com/meelgroup/bosphorus
(2) the SAT Solver: Kissat
    https://github.com/arminbiere/kissat
"""
def pre_work():
    # the save path 
    if not os.path.isdir("minimal_width_eqs"):
        os.mkdir("minimal_width_eqs")
    if os.path.exists("kissat") and os.path.exists("bosphorus"):
        os.system("chmod +x bosphorus kissat")
    else:
        print("##### Please install Bosphorus(ANF-to-CNF converter) and Kissat(SAT Solver) #####")
        print("##### Then place the executable file in the current directory #####")
        print("##### https://github.com/meelgroup/bosphorus #####")
        print("##### https://github.com/arminbiere/kissat #####")
        exit()

"""
The monomial string list(#monimial: 2^n) 
Input : n=2
Output: ["1", "x1", "x2", "x1*x2"]
"""
def get_terms_str(n):
    from itertools import combinations
    inputs = [i for i in range(n)]
    x_terms = ["1"]
    for ki in range(1, n + 1):
        # C(n, k), 1*2, 1*3, 2*3...
        numbers = list(combinations(inputs, ki))
        for num_tuple in numbers:
            xi_list = ["x" + str(i) for i in num_tuple]
            xi_str = "*".join(xi_list)
            x_terms.append(xi_str)
    return x_terms

"""
The monomial defined on Boolean polynomial ring
Input : n=2
Output: [1, x1, x2, x1*x2]
"""
def get_terms_Boolean(n, B):
    x_items_str = get_terms_str(n=n)
    # the first is 1
    x_items_poly = [1]
    for x_items in x_items_str[1:]:
        x_list = x_items.split("*")
        xi = B(x_list[0])
        for xj in x_list[1:]:
            xi = xi * B(xj)
        x_items_poly.append(xi)
    return x_items_poly

"""
Extract the coefficients of monomials as equations
Input : a0*x0+a1*x0+a2*x0*x1=0, n=2(at most 2^n eqs)
Output: [a0+a1, a2]
"""
def poly_to_eqs(poly, n):
    x_items_str = get_terms_str(n = n)
    monomial_list = str(poly).replace(" ", "").split("+")
    # the coefficients list of monomials
    monomial_coeffes = {}
    for xi in x_items_str:
        monomial_coeffes[xi] = []

    # each monomial coefficients list
    for monomial in monomial_list:
        # the coefficient is "1" not "a"
        if monomial[0] == "x":
            monomial_coeffes[monomial].append("1")
            continue
        # the first x (forward is coefficient)
        first_x_index = monomial.find("x")
        # is "1" or "a" (not "x")
        if first_x_index == -1:
            monomial_coeffes["1"].append(monomial)
            continue
        # split item("x") and coefficient("a" or "1")
        xi = monomial[first_x_index:]
        coeff = monomial[:first_x_index-1]
        monomial_coeffes[xi].append(coeff)

    basic_eqs = []
    # merge coefficients list
    for xi in monomial_coeffes.keys():
        eq = "+".join(monomial_coeffes[xi])
        if len(eq) == 0:
            continue 
        basic_eqs.append(eq)
    return basic_eqs

"""
Operation "+" and "*" defined on Boolean polynomial ring
"""
def Boolean_Inner_Product(A, X):
    l = len(A)
    AX = 0
    for i in range(l):
        AX = AX + A[i] * X[i]
    return AX

"""
Read the output from the SAT Solver kissat
"""
def get_values_from_kissat(an, file_name):
    with open(file_name, encoding="utf-8") as f:
        content = f.read()
        if "UNSATISFIABLE" in content or "caught signal" in content:
            print("UNSAT")
            return [0 for i in range(an)]

        vals_str = content.split("s SATISFIABLE\n")[1].split("c ---- [ profiling ] ---------------------------------------------------------\n")[0]
    vals_str = vals_str.replace("v","").replace("c","").replace("\n"," ")
    vals_list = vals_str.split(" ")
    # the values of coefficients
    vals = []
    for si in vals_list:
        if len(si) < 1:
            continue
        # values {0, 1} 
        # -1 -> the first value is 0
        # 2  -> the second value is 1
        vals.append(0 if "-" in si else 1)
        if len(vals) > an:
            break
   
    return vals

"""
Have and only have one variable being equal to 1
"""
def exactly_one(coeffes):
        one_eqs = [str(1 + sum(coeffes))]
        for i in range(len(coeffes)):
            for j in range(i+1, len(coeffes)):
                one_eqs.append(str(coeffes[i] * coeffes[j]))
        return one_eqs
    
"""
Determinant of Cij = 1
Make sure that the linear parts are invertible, 
hence can be implemented in-place by some CNOT gates
"""
def mat_inv_eqs(Cij):
    det = matrix(Cij).determinant()
    return [str(1+det)]

############################################################
"""
Break Symmetry
Toffoli(a, b, c) == Toffoli(b, a, c) because a * b = b * a
"""
def Toffoli_simplify(a_coeffes, b_coeffes):
    # uncomment the line below can remove the simplify Boolean equations
    # return []

    NOT1, NOT2 = a_coeffes[0], b_coeffes[0]
    simplity_eqs = [str(NOT1), str(NOT2)]

    # the index 0 is the NOT gate(+1), so start from 1
    a1, a2 = a_coeffes[1], a_coeffes[2]
    b1, b2 = b_coeffes[1], b_coeffes[2]

    # seq(Q[2i]) > seq(Q[2i+1]): a[l+N] * (a[l]+1) = 0
    simplity_eqs += [
        str((a1 + 1) * b1)
      , str((a1 + b1 + 1) * (a2 + 1) * b2)
    ]

    return simplity_eqs

############################################################
"""
The minimal width w NCT qcircuit with Toffoli-count k
The decision problem:
    Whether there exists an NCT circuit that implements F with width w and Toffoli-count k.
Encode the decision problem into a SAT problem, using the meet-in-the-middle strategy

F: an invertible Boolean function
n: the number of inputs
w: n+1 (F is odd), n (F is even)
k: Toffoli-count
"""
def minimal_width_NCT_eqs(F, n, w, k, B, name):
    # ancilla qubits full of 0
    F += [0 for _ in range(w-n)]
    basis = get_terms_Boolean(n=n, B=B)
    # k+1 Affine, k Toffoli
    # from front to back(|LT|->|LT|->...)
    k1 = k // 2 
    # from back to front(|L|...<-|TL|<-|TL|)
    k2 = k - k // 2
    # k1 >= k2(eg: k=7(4+3), k=8(4+4))
    if k / 2 > k // 2:
        k1 += 1 
        k2 -= 1 

    # number of coefficient variables
    an = w*(w+1)*(k+1)+(w+1)*k*pow(2, n)
    BA = [B(f"a{i}") for i in range(an)]
    ai = 0
    # basic coefficients start
    bi = w*(w+1)*(k+1)

    eqs = []
    CNOT_eqs = []
    # from front to back(|LT|->|LT|->...)
    # initial wires [x, 0] (ancilla qubits)
    X1 = basis[1:1+n] + [0 for i in range(w-n)]
 
    for i in range(k1):
        # linear layer
        LX = [0 for j in range(w)]
        BX = [0 for j in range(w)]
        # Cij: linear(not affine) coefficients matrix(w x w)
        Cij = []
        coeffes = []
        for j in range(w):
            affine_coeffes = BA[ai:ai+w+1]
            coeffes.append(affine_coeffes)
            X_coeffes = BA[bi:bi+pow(2, n)]
            ai += w + 1
            bi += pow(2, n)
  
            Cij.append(affine_coeffes[1:])
            # a0 + a1*x1 + ... + aw*xw
            LX[j] = Boolean_Inner_Product(affine_coeffes, [1]+X1)
            BX[j] = Boolean_Inner_Product(X_coeffes, basis)
            # coefficient eqs
            eqs += poly_to_eqs(poly=LX[j]+BX[j], n=n)

        CNOT_eqs += mat_inv_eqs(Cij=Cij) 
        CNOT_eqs += Toffoli_simplify(a_coeffes=coeffes[1], b_coeffes=coeffes[2])
        
        # nonlinear layer, 1 Toffoli gate
        T = BX[0] + BX[1]*BX[2]
        T_coeffes = BA[bi:bi+pow(2, n)]
        bi += pow(2, n)
  
        BT = Boolean_Inner_Product(T_coeffes, basis)
        eqs += poly_to_eqs(poly=T+BT, n=n)

        X1 = BX[:]
        X1[0] = BT

    # from back to front(|L|...<-|TL|<-|TL|)
    # final wires [targets, 0] (ancilla qubits)
    X2 = F[:] + [0 for i in range(w-n)]
    for i in range(k2):
        # linear layer
        LX = [0 for j in range(w)]
        BX = [0 for j in range(w)]
        Cij = []
        coeffes = []
        for j in range(w):
            affine_coeffes = BA[ai:ai+w+1]
            ai += w + 1

            coeffes.append(affine_coeffes)
            X_coeffes = BA[bi:bi+pow(2, n)]
            bi += pow(2, n)

            Cij.append(affine_coeffes[1:])
            LX[j] = Boolean_Inner_Product(affine_coeffes, [1]+X2)
            BX[j] = Boolean_Inner_Product(X_coeffes, basis)
   
            eqs += poly_to_eqs(poly=LX[j]+BX[j], n=n)
        
        CNOT_eqs += mat_inv_eqs(Cij=Cij) 
        if i > 1:
            CNOT_eqs += Toffoli_simplify(a_coeffes=coeffes[1], b_coeffes=coeffes[2])
        
        # nonlinear layer, 1 Toffoli gate
        T = BX[0] + BX[1]*BX[2]
        T_coeffes = BA[bi:bi+pow(2, n)]
        bi += pow(2, n)
        BT = Boolean_Inner_Product(T_coeffes, basis)
        eqs += poly_to_eqs(poly=T+BT, n=n)

        X2 = BX[:]
        X2[0] = BT

    Cij = []

    # affine function for the middle output (X1=AX2)
    for i in range(w):
        affine_coeffes = BA[ai:ai+w+1]
        ai += w + 1

        Cij.append(affine_coeffes[1:])
        AX2 = Boolean_Inner_Product(affine_coeffes, [1]+X2)
        eqs += poly_to_eqs(poly=AX2+X1[i], n=n)
        
    CNOT_eqs += mat_inv_eqs(Cij=Cij)
    eqs += CNOT_eqs

    prefix = f"./minimal_width_eqs/{name}_w{w}k{k}"
    with open(f"{prefix}.eqs", "w") as f:
        f.write("\n".join(eqs).replace("a", "x"))
    return eqs

"""
Get the minimal width-w NCT qcircuit with Toffoli-count k
"""
def minimal_width_NCT_result(F, n, w, k, B, name):
    prefix = f"./minimal_width_eqs/{name}_w{w}k{k}"
    basis  = get_terms_Boolean(n=n, B=B)

    # coefficients number
    an = w*(w+1)*(k+1)
    VA = get_values_from_kissat(an=an, file_name=f"{prefix}.out")
    ai = 0

    # k+1 Affine, k Toffoli
    # from front to back(|LT|->|LT|->...)
    k1 = k // 2 
    # from back to front(|L|...<-|TL|<-|TL|)
    k2 = k - k // 2
    # k1 >= k2(eg: k=7(4+3), k=8(4+4))
    if k / 2 > k // 2:
        k1 += 1 
        k2 -= 1 
    
    # y = Ax + b(affine) 
    As = [0 for i in range(k+1)]
    bs = [0 for i in range(k+1)]
    # from front to back(|LT|->|LT|->...)
    # initial wires [x, 0] (ancilla qubits)
    X1 = basis[1:1+n] + [0 for i in range(w-n)]
    for i in range(k1):
        LX = [0 for j in range(w)]
        Asi, bsi = [], []
        for j in range(w):
            linear_coeffes = VA[ai:ai+w+1]
            Asi.append(linear_coeffes[1:])
            bsi.append(linear_coeffes[0])
            ai += w + 1
            LX[j] = Boolean_Inner_Product(linear_coeffes, [1]+X1)

        As[i] = Asi
        bs[i] = bsi
        T  = LX[0] + LX[1]*LX[2]
        X1 = LX[:]
        X1[0] = T

    # from back to front(|L|...<-|TL|<-|TL|)
    # final wires [targets, 0] (ancilla qubits)
    X2 = F[:] + [0 for i in range(w-n)]
    for i in range(k2):
        LX = [0 for j in range(w)]
        Asi, bsi = [], []
        for j in range(w):
            linear_coeffes = VA[ai:ai+w+1]
            Asi.append(linear_coeffes[1:])
            bsi.append(linear_coeffes[0])
            ai += w + 1
            LX[j] = Boolean_Inner_Product(linear_coeffes, [1]+X2)

        # x = Ay + b, y = A^{-1}(x+b)
        # Asi^{-1}
        As[k-i] = matrix(GF(2), Asi).inverse()
        # Asi^{-1}b
        bs[k-i] = As[k-i] * vector(GF(2), bsi)

        T  = LX[0] + LX[1]*LX[2]
        X2 = LX[:]
        X2[0] = T

    Asi, bsi = [], []
    # linear(affine) for the middle output
    for i in range(w):
        linear_coeffes = VA[ai:ai+w+1]
        Asi.append(linear_coeffes[1:])
        bsi.append(linear_coeffes[0])
        ai += w + 1

    # x = Ay + b, y = A^{-1}(x+b)
    As[k1] = matrix(GF(2), Asi).inverse()
    bs[k1] = As[k1] * vector(GF(2), bsi)

    # the implementation result
    result = []
    result.append("\n############################################")
    result.append("##### Minimal-width NCT implementation #####")
    result.append(f"##### {prefix} #####")
    result.append("##### Affine A, b #####")
    for i in range(k+1):
        result.append(f"A[{i}] = {[list(row) for row in As[i]]}")
        result.append(f"b[{i}] = {list(bs[i])}")

    result.append("##### Layer result #####")
    X = basis[1:1+n] + [0 for i in range(w-n)]
    # build the path 
    for i in range(k):
        LX = [Boolean_Inner_Product(A=[bs[i][j]]+list(As[i][j]), X=[1]+X) 
              for j in range(w)]
        LX[0] = LX[0] + LX[1]*LX[2]
        X = LX[:]
        result.append(f"########## After Layer-{i} ##########")
        for j in range(w):
            result.append(f"X[{j}] = {X[j]}")

    # final targets(without Toffoli, only linear)
    LX = [Boolean_Inner_Product(A=[bs[k][j]]+list(As[k][j]), X=[1]+X) 
              for j in range(w)]

    X = LX[:]
    result.append("########## After Layer-final ##########")
    for i in range(w):
        result.append(f"X[{i}] = {X[i]}")
    
    result.append("########## Verity-final ##########")
    result.append(", ".join([str(X[i] + F[i])for i in range(len(F))]))
    result.append("##############################")

    print("\n".join(result))

    with open(f"{prefix}_result.txt", "w") as ff:
        ff.write("\n".join(result))

############################################################
"""
Test program
"""
def test_minimal_width_SAT():
    pre_work()
    a_variable = ["a" + str(i) for i in range(6000)]
    x_variable = ["x" + str(i) for i in range(8)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))

    x0,x1,x2,x3,x4 = B("x0"),B("x1"),B("x2"),B("x3"),B("x4")

    # Boolean functions
    ANFs = {
        # w=5, k=7(still can find the implementation without the restriction "no CNOTs")
        "keccak" : [x0+x1*x2+x2
                , x1+x2*x3+x3
                , x2+x3*x4+x4
                , x0*x4+x0+x3
                , x0*x1+x1+x4]
        

        # 5-bit (even) w=5, k=7
        , "sub_part1" : [x0*x1*x2*x4 + x0*x1*x3*x4 + x0*x1*x3 + x0*x1*x4 + x0*x1 + x0*x2*x3*x4 + x0*x2 + x0*x3 + x1*x2
        , x0*x1*x3*x4 + x0*x1*x3 + x0*x1 + x0*x2*x4 + x0*x2 + x0*x3*x4 + x0*x3 + x0 + x1*x2 + x1
        , x0*x1 + x0*x2*x4 + x0*x2 + x1*x2 + x1 + x2 + 1
        , x0*x4 + x0 + x1 + x3 + 1
        , x4 + 1]

        # 4-bit
        # (odd permutation) w=5, k=5
        , "sub_part2" : [x0*x1*x2 + x0*x3 + x0 + x1*x2*x3 + x1*x3 + x1 + x2 + x3 + 1
        , x0*x1*x2 + x0*x3 + x1*x2*x3 + x1*x3 + x2*x3 + x2 + x3
        , x0*x1*x2 + x1*x2*x3 + x3
        , x0*x2*x3 + x0*x2 + x0*x3 + x0 + x1*x2*x3 + x1*x2 + x1*x3]
        }

    ############################################################
    n = 5
    w = 5
    k = 7
    name = "keccak"
    F = ANFs[name]
    minimal_width_NCT_eqs(F=F, n=n, w=w, k=k, B=B, name=name)

    prefix = f"minimal_width_eqs/{name}_w{w}k{k}"

    os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
    os.system(f"./kissat {prefix}.cnf --sat > {prefix}.out")
    
    minimal_width_NCT_result(F=F, n=n, w=w, k=k, B=B, name=name)


def ASCON_minimal_width_SAT():
    # pre_work()
    a_variable = ["a" + str(i) for i in range(6000)]
    x_variable = ["x" + str(i) for i in range(8)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))

    x0,x1,x2,x3,x4 = B("x0"),B("x1"),B("x2"),B("x3"),B("x4")

    n = 5
    w = 5
    k = 7
    name = "ASCON"
    ASCON_Sbox_ANF = [
        x0*x1+x0+x1*x2+x1*x4+x1+x2+x3
        , x0+x1*x2+x1*x3+x1+x2*x3+x2+x3+x4
        , x1+x2+x3*x4+x4+1
        , x0*x3+x0*x4+x0+x1+x2+x3+x4
        , x0*x1+x1*x4+x1+x3+x4]
    
    prefix = f"minimal_width_eqs/{name}_w{w}k{k}"
    # minimal_width_NCT_eqs(F=ASCON_Sbox_ANF, n=n, w=w, k=k, B=B, name=name)
    # os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
    # os.system(f"./kissat {prefix}.cnf --sat > {prefix}.out")
    minimal_width_NCT_result(F=ASCON_Sbox_ANF, n=n, w=w, k=k, B=B, name=name)

ASCON_minimal_width_SAT()
"""
############################################
##### Minimal-width NCT implementation #####
##### ./minimal_width_eqs/ASCON_w5k7 #####
##### Affine A, b #####
A[0] = [[1, 0, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 1, 1], [0, 0, 0, 1, 0]]
b[0] = [1, 0, 0, 0, 0]
A[1] = [[1, 1, 0, 0, 0], [0, 0, 0, 0, 1], [0, 0, 1, 1, 1], [0, 1, 0, 1, 1], [1, 0, 1, 1, 1]]
b[1] = [0, 0, 0, 0, 1]
A[2] = [[1, 0, 0, 1, 1], [1, 0, 0, 0, 0], [0, 0, 1, 1, 0], [0, 1, 0, 0, 1], [1, 0, 1, 1, 1]]
b[2] = [1, 0, 0, 0, 0]
A[3] = [[0, 0, 1, 1, 0], [0, 0, 0, 0, 1], [0, 0, 1, 0, 0], [0, 1, 1, 1, 1], [1, 1, 1, 0, 1]]
b[3] = [0, 0, 0, 0, 0]
A[4] = [[0, 1, 1, 0, 1], [0, 0, 0, 1, 0], [0, 1, 1, 0, 0], [1, 0, 1, 1, 0], [0, 0, 1, 1, 1]]
b[4] = [1, 0, 0, 0, 0]
A[5] = [[0, 1, 0, 0, 0], [0, 0, 1, 1, 0], [0, 0, 1, 1, 1], [1, 1, 1, 1, 0], [0, 0, 1, 0, 1]]
b[5] = [0, 1, 0, 1, 1]
A[6] = [[1, 0, 0, 0, 1], [0, 1, 0, 1, 1], [0, 1, 1, 0, 1], [1, 0, 0, 1, 0], [0, 0, 0, 1, 0]]
b[6] = [0, 0, 0, 0, 0]
A[7] = [[1, 1, 0, 1, 1], [1, 1, 1, 1, 0], [0, 0, 1, 0, 0], [0, 0, 1, 1, 1], [0, 1, 1, 0, 1]]
b[7] = [0, 1, 0, 1, 1]
##### Layer result #####
########## After Layer-0 ##########
X[0] = x0 + x1*x2 + x2 + 1
X[1] = x1 + x2
X[2] = x2
X[3] = x2 + x3 + x4
X[4] = x3
########## After Layer-1 ##########
X[0] = x0 + x1*x2 + x1 + x3*x4 + 1
X[1] = x3
X[2] = x4
X[3] = x1 + x4
X[4] = x0 + x1*x2 + x2 + x4
########## After Layer-2 ##########
X[0] = x0*x1 + x1*x2 + x1*x3*x4 + x2 + x3*x4
X[1] = x0 + x1*x2 + x1 + x3*x4 + 1
X[2] = x1
X[3] = x0 + x1*x2 + x2 + x3 + x4
X[4] = x2 + x3*x4 + x4 + 1
########## After Layer-3 ##########
X[0] = x0 + x1*x3*x4 + x1*x4 + x2 + x3 + x4
X[1] = x2 + x3*x4 + x4 + 1
X[2] = x1
X[3] = x3
X[4] = x0*x1 + x0 + x1*x3*x4 + x3*x4 + x4
########## After Layer-4 ##########
X[0] = x0*x1 + x0 + x1*x3*x4 + x1*x3 + x1 + x2*x3 + x2 + x3
X[1] = x3
X[2] = x1 + x2 + x3*x4 + x4 + 1
X[3] = x0 + x1*x3*x4 + x1*x4 + x1 + x2 + x4
X[4] = x0*x1 + x0 + x1*x3*x4 + x1 + x3*x4 + x3 + x4
########## After Layer-5 ##########
X[0] = x0*x3 + x0*x4 + x0 + x3*x4 + x3
X[1] = x0 + x1*x3*x4 + x1*x4 + x3*x4
X[2] = x0*x1 + x1*x4 + x1 + x3 + x4 + 1
X[3] = x0*x1 + x1*x3 + x1*x4 + x1 + x2*x3 + x2 + x3*x4
X[4] = x0*x1 + x0 + x1*x3*x4 + x2 + x3
########## After Layer-6 ##########
X[0] = x0*x1 + x0*x3 + x0*x4 + x1*x2 + x1*x3 + x1*x4 + x2*x3 + x2 + x3*x4 + x3
X[1] = x1*x3 + x1 + x2*x3 + x3
X[2] = x1 + x2 + x3*x4 + x4 + 1
X[3] = x0*x1 + x0*x3 + x0*x4 + x0 + x1*x3 + x1*x4 + x1 + x2*x3 + x2 + x3
X[4] = x0*x1 + x1*x3 + x1*x4 + x1 + x2*x3 + x2 + x3*x4
########## After Layer-final ##########
X[0] = x0*x1 + x0 + x1*x2 + x1*x4 + x1 + x2 + x3
X[1] = x0 + x1*x2 + x1*x3 + x1 + x2*x3 + x2 + x3 + x4
X[2] = x1 + x2 + x3*x4 + x4 + 1
X[3] = x0*x3 + x0*x4 + x0 + x1 + x2 + x3 + x4
X[4] = x0*x1 + x1*x4 + x1 + x3 + x4
########## Verity-final ##########
0, 0, 0, 0, 0
##############################
"""