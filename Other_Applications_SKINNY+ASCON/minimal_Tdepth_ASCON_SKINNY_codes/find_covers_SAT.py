# coding : utf-8

# Algorithm2: Top-down approach
# SAT-based method to find covers

# Need Sagemath environment(Linux)
from sage.all import * 
from math import log2 
from math import ceil 

"""
Basic notations
 
M_{k} = {f | deg(f) in [2^{k-1}+1, 2^k]}, k > 0(AND-depth-k)
M_{0} denote the set of all affine polynomials 
M_{<=k} is union set of M_{0}, M_{1},..., M_{k}

A max-depth cover of f is a set of depth-decreasing factorable Boolean polynomials C = {C1, C2,..., Ck}, Ci in M_{d} such that:
    f  = C1 + C2 + ... + Ck + R 
    Ci = Di1 * Di2 
    Di1, Di2, R in M_{<=d-1}
"""

############################################################
"""
Auxiliary function
"""
############################################################
"""
f  = C1 + C2 + ... + Ck + R 
Ci = Di1 * Di2 

k: size of the covers
C: covers 
D: factors of the covers 
R: Remainder
"""
class Max_Depth_Cover:
    def __init__(self, f) -> None:
        self.f    = f 
        self.maxd = ceil(log2(f.degree()))
        self.k    = 0
        self.C    = []
        self.D    = []
        self.R    = []

"""
The file save path: file *.eqs, *.cnf, *.out 
Need two tools:
(1) the ANF-to-CNF conveter: Bosphorus
    https://github.com/meelgroup/bosphorus
(2) the SAT Solver: Kissat
    https://github.com/arminbiere/kissat
"""
def pre_work():
    # the save path 
    if not os.path.isdir("covers_eqs"):
        os.mkdir("covers_eqs")
    if os.path.exists("kissat") and os.path.exists("bosphorus"):
        os.system("chmod +x bosphorus kissat")
    else:
        print("##### Please install Bosphorus(ANF-to-CNF converter) and Kissat(SAT Solver) #####")
        print("##### Then place the executable file in the current directory #####")
        print("##### https://github.com/meelgroup/bosphorus #####")
        print("##### https://github.com/arminbiere/kissat #####")
        exit()

"""
A is a dim-2 list
B is a dim-1 list
"""
def list2_to_1(A):
    B_ = []
    for Ai in A:
        B_ += Ai 
    return B_

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
The monomial string list(number is 2^n) 
Input : n = 2
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
Boolean monomials in different AND-depth layer
Input : n = 2
Output: [[1, x0, x1], [x0*x1]]
"""
def get_M_Boolean_monomials(n, B):
    from scipy.special import comb
    terms = get_terms_Boolean(n=n, B=B)
    M = []
    maxd = ceil(log2(n))

    idx = 0
    for d in range(maxd + 1):
        left = 1 + pow(2, d - 1)
        right = 1 + pow(2, d)
        if d == 0:
            left, right = 0, 2

        term_number = 0 
        for i in range(left, right):
            term_number += comb(n, i)

        M.append(terms[idx:idx+int(term_number)])
        idx += int(term_number)
    
    return M

"""
Extract the coefficients of monomials as equations
eqs_basis: consider the basis of Boolean equations(default all monomials)
Input : a0*x0+a1*x0+a2*x0*x1, n=2, eqs_basis=[x0*x1](at most 2^n eqs)
Output: [a2] # the "a0*x0+a1*x0" not be considered(AND-depth<2)
"""
def poly_to_eqs(poly, n, eqs_basis=[]):
    x_items_str = get_terms_str(n=n)
    monomial_list = str(poly).replace(" ", "").split("+")
    # the coefficients list of monomials
    monomial_coeffes = {}
    for xi in x_items_str:
        monomial_coeffes[xi] = []
    monomial_coeffes["1"] = []
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
    if len(eqs_basis) == 0:
        eqs_basis = x_items_str

    # merge coefficients list
    for xi in eqs_basis:
        eq = "+".join(monomial_coeffes[str(xi)])
        if len(eq) == 0:
            continue 
        basic_eqs.append(eq)
    return basic_eqs

"""
Read output from SAT Solver kissat
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

############################################################
"""
The SAT-based method to find covers with small size
Boolean equations:
    f + C1 + C2 + ... + Ck + R = 0
    Ci = D^1_i * D^2_i

    f in M_{d}
    D^1_i, D^2_i, R in M_{<=d-1}

f : target Boolean polynomial with AND-depth-d
n : number of input variables
d : the AND-depth of f
k : the size of max-depth cover
BA: set of Boolean variables cofficients {a0, a1,...}(need to be solved)
M : Boolean polynomials in different AND-depth layer
"""
def find_covers_eqs(f, n, d, k, BA, M, prefix):
    factor_basis = list2_to_1(M[:d])
    cover_basis  = list2_to_1(M[:d+1])

    # only consider AND-depth-d Boolean equations
    max_depth_basis = M[d]

    n1 = len(factor_basis)
    n2 = len(cover_basis)

    # coefficient numbers of "Ci = Di1 * Di2"
    cn = 2*n1 + n2

    # use max-depth cover to generate f
    f_star = 0
    eqs = []
    for i in range(k):
        Di1_coeffes = [BA[i*cn+j]      for j in range(n1)]
        Di2_coeffes = [BA[i*cn+n1+j]   for j in range(n1)]
        Ci_coeffes  = [BA[i*cn+2*n1+j] for j in range(n2)]

        Di1 = Boolean_Inner_Product(Di1_coeffes, factor_basis)
        Di2 = Boolean_Inner_Product(Di2_coeffes, factor_basis)
        Ci  = Boolean_Inner_Product(Ci_coeffes, cover_basis)
        
        Ci_star = Di1 * Di2
        # middle polynomial
        eqs += poly_to_eqs(Ci+Ci_star, n)
        f_star += Ci

    # allow to have remainder R in M_{<=d-1}
    eqs += poly_to_eqs(poly=f+f_star, n=n, eqs_basis=max_depth_basis)
    
    eqs_save = "\n".join(eqs).replace("a", "x")
    with open(f"{prefix}.eqs", "w") as ff:
        ff.write(eqs_save)
    
"""
Get the covers result
"""
def find_covers_result(f, n, d, k, M, prefix):
    result = []
    factor_basis = list2_to_1(M[:d])
    cover_basis  = list2_to_1(M[:d+1])

    n1 = len(factor_basis)
    n2 = len(cover_basis)

    cn = 2*n1 + n2

    VA = get_values_from_kissat(an=k*cn, file_name=f"{prefix}.out")
    f_star = 0

    factors = []
    result.append("##### Covers of f and factors of covers #####")
    for i in range(k):
        Di1_coeffes = [VA[i*cn+j]      for j in range(n1)]
        Di2_coeffes = [VA[i*cn+n1+j]   for j in range(n1)]
 
        Di1 = Boolean_Inner_Product(Di1_coeffes, factor_basis)
        Di2 = Boolean_Inner_Product(Di2_coeffes, factor_basis)

        f_star += Di1 * Di2

        result.append(f"D_{i+1}_1 = {Di1}")
        result.append(f"D_{i+1}_2 = {Di1}")
        factors += [Di1, Di2]

    R = f + f_star
    result.append(f"R = {R}")

    return factors, R

############################################################
"""
d -> d-1 -> d-2

f : target Boolean polynomial with AND-depth-d
n : number of input variables
k1: the size of max-depth cover
k2: the size of second max-depth cover(2*k1 {D^1_i, D^2_i}, i = 1, 2,..., k1)
d : the AND-depth of f
BA: set of Boolean variables cofficients {a0, a1,...}(need to be solved)

Note that the second max-depth cover is mutual influence between {D, R}
So we only constraint the factor D, let R is free
"""
def find_covers_two_layer_eqs(f, n, d, k1, k2, BA, M, prefix):
    # d -> d-1
    factor1_basis    = list2_to_1(M[:d])
    cover1_basis     = list2_to_1(M[:d+1])
    max_depth1_basis = list2_to_1(M[d])

    # d-1 -> d-2
    factor2_basis    = list2_to_1(M[:d-1])
    max_depth2_basis = list2_to_1(M[d-1])
    n1 = len(factor1_basis)
    n2 = len(cover1_basis)
    n3 = len(factor2_basis)
    
    f_star = 0
    eqs = []
    ai = 0
    for i in range(k1):
        Di1_coeffes = [BA[ai+j]      for j in range(n1)]
        Di2_coeffes = [BA[ai+n1+j]   for j in range(n1)]
        Ci_coeffes  = [BA[ai+2*n1+j] for j in range(n2)]
        ai += 2*n1 + n2

        Di1 = Boolean_Inner_Product(Di1_coeffes, factor1_basis)
        Di2 = Boolean_Inner_Product(Di2_coeffes, factor1_basis)
        Ci  = Boolean_Inner_Product(Ci_coeffes, cover1_basis)
        
        Ci_star  = Di1 * Di2
        # middle polynomial
        eqs += poly_to_eqs(Ci+Ci_star, n)
        f_star += Ci

        # Di1 = Dj1 * Dj2 + ...
        Di1_star = 0
        for j in range(k2[2*i]):
            Dj1_coeffes = [BA[ai+2*j*n3+l]    for l in range(n3)]
            Dj2_coeffes = [BA[ai+2*j*n3+n3+l] for l in range(n3)]

            Dj1 = Boolean_Inner_Product(Dj1_coeffes, factor2_basis)
            Dj2 = Boolean_Inner_Product(Dj2_coeffes, factor2_basis)
            Di1_star += Dj1 * Dj2 
        
        ai += 2*n3 * k2[2*i]
        eqs += poly_to_eqs(poly=Di1_star+Di1, n=n, eqs_basis=max_depth2_basis)

        # Di2 = Dj1 * Dj2 + ...
        Di2_star = 0
        for j in range(k2[2*i+1]):
            Dj1_coeffes = [BA[ai+2*j*n3+l]    for l in range(n3)]
            Dj2_coeffes = [BA[ai+2*j*n3+n3+l] for l in range(n3)]

            Dj1 = Boolean_Inner_Product(Dj1_coeffes, factor2_basis)
            Dj2 = Boolean_Inner_Product(Dj2_coeffes, factor2_basis)
            Di2_star += Dj1 * Dj2 
        
        ai += 2*n3 * k2[2*i]
        eqs += poly_to_eqs(poly=Di2_star+Di2, n=n, eqs_basis=max_depth2_basis)

    # R_star = 0
    # for j in range(k2[2*k1]):
    #     Dj1_coeffes = [BA[ai+2*j*n3+l]    for l in range(n3)]
    #     Dj2_coeffes = [BA[ai+2*j*n3+n3+l] for l in range(n3)]

    #     Dj1 = Boolean_Inner_Product(Dj1_coeffes, factor2_basis)
    #     Dj2 = Boolean_Inner_Product(Dj2_coeffes, factor2_basis)
    #     R_star += Dj1 * Dj2 
    
    # if k2[2*k1] > 0:
    #     eqs += poly_to_eqs(poly=R_star+f+f_star, n=n, eqs_basis=max_depth2_basis)
 
    eqs += poly_to_eqs(poly=f+f_star, n=n, eqs_basis=max_depth1_basis)
    
    with open(f"{prefix}.eqs", "w") as f:
        f.write("\n".join(eqs).replace("a", "x"))

"""
Get the two layer covers result
"""
def find_covers_two_layer_result(f, n, d, k1, k2, M, prefix):
    result = []
    # d -> d-1
    factor1_basis    = list2_to_1(M[:d])
    cover1_basis     = list2_to_1(M[:d+1])

    # d-1 -> d-2
    factor2_basis    = list2_to_1(M[:d-1])

    n1 = len(factor1_basis)
    n2 = len(cover1_basis)
    n3 = len(factor2_basis)

    an = k1 * (2*n1+n2) + sum(k2) * 2*n3
    VA = get_values_from_kissat(an=an, file_name=f"{prefix}.out")
 
    f_star = 0
    ai = 0
    
    factors1 = []
    factors2 = []
    R2 = []
    for i in range(k1):
        Di1_coeffes = [VA[ai+j]      for j in range(n1)]
        Di2_coeffes = [VA[ai+n1+j]   for j in range(n1)]
        ai += 2*n1 + n2

        Di1 = Boolean_Inner_Product(Di1_coeffes, factor1_basis)
        Di2 = Boolean_Inner_Product(Di2_coeffes, factor1_basis)

        f_star += Di1 * Di2

        factors1 += [Di1, Di2]
        result.append(f"D_{i+1}_{1} = {Di1}")
        result.append(f"D_{i+1}_{2} = {Di2}")
        # Di1 = Dj1 * Dj2 + ...
        Di1_star = 0
        for j in range(k2[2*i]):
            Dj1_coeffes = [VA[ai+2*j*n3+l]    for l in range(n3)]
            Dj2_coeffes = [VA[ai+2*j*n3+n3+l] for l in range(n3)]

            Dj1 = Boolean_Inner_Product(Dj1_coeffes, factor2_basis)
            Dj2 = Boolean_Inner_Product(Dj2_coeffes, factor2_basis)
            Di1_star += Dj1 * Dj2 
            factors2 += [Dj1, Dj2] 
        R2.append(Di1 + Di1_star)
        ai += 2*n3 * k2[2*i]
   
        # Di2 = Dj1 * Dj2 + ...
        Di2_star = 0
        for j in range(k2[2*i+1]):
            Dj1_coeffes = [VA[ai+2*j*n3+l]    for l in range(n3)]
            Dj2_coeffes = [VA[ai+2*j*n3+n3+l] for l in range(n3)]

            Dj1 = Boolean_Inner_Product(Dj1_coeffes, factor2_basis)
            Dj2 = Boolean_Inner_Product(Dj2_coeffes, factor2_basis)
            Di2_star += Dj1 * Dj2 
            factors2 += [Dj1, Dj2] 
        R2.append(Di2 + Di2_star)
        ai += 2*n3 * k2[2*i]

    # R_star = 0
    # for j in range(k2[2*k1]):
    #     Dj1_coeffes = [VA[ai+2*j*n3+l]    for l in range(n3)]
    #     Dj2_coeffes = [VA[ai+2*j*n3+n3+l] for l in range(n3)]

    #     Dj1 = Boolean_Inner_Product(Dj1_coeffes, factor2_basis)
    #     Dj2 = Boolean_Inner_Product(Dj2_coeffes, factor2_basis)
    #     R_star += Dj1 * Dj2 
    #     factors2 += [Dj1, Dj2] 

    R1 = f + f_star 
    result.append(f"R = {R1}")
    result.append(f"AND-depth-d-2 factors: {factors2}")
    return factors1, R1, factors2, R2

############################################################
"""
Ys = [f1, f2,..., fm]
Find common covers from inputs X(d=0) to outputs F(d=maxd)
0 -> 1 -> 2 -> ... -> maxd(AND-depth)
X -> X^2 -> X^3, X^4 -> ... -> F

F: {f1, f2,..., fm}
n : number of input variables(not large)
k : the size of max-depth cover
d : the AND-depth of f
BA: set of Boolean variables cofficients {a0, a1,...}(need to be solved)
"""
def find_common_covers_eqs(F, n, maxd, ks, BA, M, prefix):
    ai = 0
    bi = len(F) * (n + 1 + sum(ks))
    for d in range(maxd):
        bi += 2*ks[d] * (n + 1 + sum(ks[:d]))
    
    XC_star = M[0][:]
    eqs = []
    for d in range(maxd):
        factor_basis = list2_to_1(M[:d+1])
        cover_basis  = list2_to_1(M[:d+2])
        n1 = len(factor_basis)
        n2 = len(cover_basis)
        n3 = len(XC_star)

        for i in range(ks[d]):
            Di1_coeffes = [BA[ai+j]    for j in range(n3)]
            Di2_coeffes = [BA[ai+n3+j] for j in range(n3)]
            ai += 2*n3
            # without NOT gate(+1)
            eqs += [str(Di1_coeffes[0]), str(Di2_coeffes[0])]

            Di1 = Boolean_Inner_Product(Di1_coeffes, XC_star)
            Di2 = Boolean_Inner_Product(Di2_coeffes, XC_star)
            
            Di1_star_coeffes = [BA[bi+j]      for j in range(n1)]
            Di2_star_coeffes = [BA[bi+n1+j]   for j in range(n1)]
            Ci_star_coeffes  = [BA[bi+2*n1+j] for j in range(n2)]
            bi += 2*n1 + n2

            Di1_star = Boolean_Inner_Product(Di1_star_coeffes, factor_basis)
            Di2_star = Boolean_Inner_Product(Di2_star_coeffes, factor_basis)
            
            Ci  = Di1_star * Di2_star
            Ci_star = Boolean_Inner_Product(Ci_star_coeffes, cover_basis)

            # middle polynomial
            eqs += poly_to_eqs(Di1+Di1_star, n)
            eqs += poly_to_eqs(Di2+Di2_star, n)
            eqs += poly_to_eqs(Ci+Ci_star, n)
            XC_star.append(Ci_star)
    
    n3 = len(XC_star) 
    for f in F:
        f_star_coeffes = [BA[ai+i] for i in range(n3)]
        ai += n3 
        f_star = Boolean_Inner_Product(f_star_coeffes, XC_star)
        eqs += poly_to_eqs(poly=f+f_star, n=n)
    
    with open(f"{prefix}.eqs", "w") as f:
        f.write("\n".join(eqs).replace("a", "x"))

"""
Get the covers result
"""
def find_common_covers_result(F, n, maxd, ks, M, prefix):
    result = []
    an = len(F) * (n + 1 + sum(ks))
    for d in range(maxd):
        an += 2*ks[d] * (n + 1 + sum(ks[:d]))
    VA = get_values_from_kissat(an=an, file_name=f"{prefix}.out")
    
    ai = 0
    XC_star = M[0][:]
    XC_str  = ["1"] + [f"x{i}" for i in range(n)] + [f"M{i}" for i in range(sum(ks))]
    for d in range(maxd):
        n3 = len(XC_star)
        result.append(f"############## AND-depth from {d} to {d + 1} ##############")
        for i in range(ks[d]):
            Di1_coeffes = [VA[ai+j]    for j in range(n3)]
            Di2_coeffes = [VA[ai+n3+j] for j in range(n3)]
            ai += 2*n3

            Di1 = Boolean_Inner_Product(Di1_coeffes, XC_star)
            Di2 = Boolean_Inner_Product(Di2_coeffes, XC_star)
            
            Ci  = Di1 * Di2
            XC_star.append(Ci)

            # print Ci = Di1 * Di2
            Di1_terms = [XC_str[j] for j in range(n3) if Di1_coeffes[j] == 1]
            Di2_terms = [XC_str[j] for j in range(n3) if Di2_coeffes[j] == 1]
            result.append(f"M{sum(ks[:d])+i}=({'+'.join(Di1_terms)})*({'+'.join(Di2_terms)})")

    result.append(f"############## build final targets ################")
    n3 = len(XC_star) 
    for i in range(len(F)):
        f_coeffes = [VA[ai+i] for i in range(n3)]
        ai += n3 
        f = Boolean_Inner_Product(f_coeffes, XC_star)

        f_terms = [XC_str[j] for j in range(n3) if f_coeffes[j] == 1]
        result.append(f"Y{i}={'+'.join(f_terms)}")
    result.append(f"###################################################")
    print("\n".join(result))

"""
AES Sbox ANF
"""
def get_AES_Sbox_ANF(X):
    x0,x1,x2,x3,x4,x5,x6,x7 = X[0],X[1],X[2],X[3],X[4],X[5],X[6],X[7]
    return [x0*x1*x2*x3*x4*x5*x7+x0*x1*x2*x3*x4*x6*x7+x0*x1*x2*x3*x4*x6+x0*x1*x2*x3*x4+x0*x1*x2*x3*x5*x7+x0*x1*x2*x3*x6+x0*x1*x2*x3+x0*x1*x2*x4*x5*x7+x0*x1*x2*x4*x6*x7+x0*x1*x2*x4*x6+x0*x1*x2*x4*x7+x0*x1*x2*x5*x6+x0*x1*x2*x5+x0*x1*x2*x6*x7+x0*x1*x2*x6+x0*x1*x3*x4*x5*x7+x0*x1*x3*x4*x6*x7+x0*x1*x3*x4*x7+x0*x1*x3*x5*x6+x0*x1*x3*x5+x0*x1*x3*x6+x0*x1*x3*x7+x0*x1*x3+x0*x1*x4*x5*x6*x7+x0*x1*x4*x6+x0*x1*x4*x7+x0*x1*x5*x6*x7+x0*x1*x5+x0*x1*x7+x0*x2*x3*x4*x5*x7+x0*x2*x3*x4*x6*x7+x0*x2*x3*x5*x6*x7+x0*x2*x3*x6*x7+x0*x2*x3*x6+x0*x2*x3+x0*x2*x4*x7+x0*x2*x4+x0*x2*x5*x6*x7+x0*x2+x0*x3*x4*x5*x7+x0*x3*x4*x5+x0*x3*x4*x6*x7+x0*x3*x4*x6+x0*x3*x4*x7+x0*x3*x5*x7+x0*x3*x6*x7+x0*x3*x6+x0*x4*x5*x6+x0*x4*x5*x7+x0*x4*x7+x0*x5*x6*x7+x0*x5*x7+x0*x6+x0*x7+x0+x1*x2*x3*x4*x5*x7+x1*x2*x3*x4*x5+x1*x2*x3*x4*x7+x1*x2*x3*x4+x1*x2*x3*x5*x6+x1*x2*x3*x6*x7+x1*x2*x3+x1*x2*x4*x5*x6+x1*x2*x4*x7+x1*x2*x5+x1*x2*x7+x1*x3*x4*x5*x7+x1*x3*x4*x7+x1*x3*x5*x6*x7+x1*x3*x5*x6+x1*x3*x5*x7+x1*x3*x5+x1*x3+x1*x4*x5*x6*x7+x1*x4*x5*x7+x1*x4*x6*x7+x1*x4*x6+x1*x4*x7+x1*x5*x6+x1*x5+x1*x6*x7+x1*x7+x2*x3*x4*x5*x7+x2*x3*x4*x6*x7+x2*x3*x4+x2*x3*x5*x6+x2*x3*x7+x2*x4*x5*x6+x2*x4*x5*x7+x2*x4*x5+x2*x4*x6+x2*x4*x7+x2*x4+x2*x5*x6*x7+x2*x5*x7+x2*x6*x7+x2+x3*x4*x5*x6*x7+x3*x4*x5*x6+x3*x4*x6*x7+x3*x5*x6*x7+x3*x5+x3*x6*x7+x3+x4*x5*x6*x7+x4*x5*x6+x4*x5*x7+x5*x6+x5*x7+x5
    , x0*x1*x2*x3*x4*x6*x7+x0*x1*x2*x3*x4*x6+x0*x1*x2*x3*x4+x0*x1*x2*x3*x5*x6*x7+x0*x1*x2*x3*x6+x0*x1*x2*x3*x7+x0*x1*x2*x3+x0*x1*x2*x4*x5+x0*x1*x2*x4*x6*x7+x0*x1*x2*x5*x6*x7+x0*x1*x2*x5*x6+x0*x1*x2*x5*x7+x0*x1*x2+x0*x1*x3*x4*x5+x0*x1*x3*x4*x6*x7+x0*x1*x3*x4*x7+x0*x1*x3*x5*x6*x7+x0*x1*x3*x5*x7+x0*x1*x3*x6+x0*x1*x3*x7+x0*x1*x4*x6*x7+x0*x1*x4+x0*x1*x6*x7+x0*x1*x6+x0*x2*x3*x4*x6*x7+x0*x2*x3*x4*x6+x0*x2*x3*x5*x6*x7+x0*x2*x3*x5*x7+x0*x2*x3*x6*x7+x0*x2*x3*x6+x0*x2*x4*x5*x6+x0*x2*x4*x5+x0*x2*x4*x6+x0*x2*x4+x0*x2*x5*x7+x0*x2*x7+x0*x2+x0*x3*x4*x5*x6*x7+x0*x3*x4*x5*x6+x0*x3*x4*x6+x0*x3*x4*x7+x0*x3*x5*x6+x0*x3*x5+x0*x3*x6+x0*x3*x7+x0*x4*x5*x6*x7+x0*x4*x5*x7+x0*x4*x5+x0*x4*x6*x7+x0*x4+x0*x5*x6+x0*x6+x0*x7+x1*x2*x3*x4*x6*x7+x1*x2*x3*x4*x6+x1*x2*x3*x5*x6*x7+x1*x2*x3*x5*x6+x1*x2*x3+x1*x2*x4*x5*x6*x7+x1*x2*x4*x5*x7+x1*x2*x4*x5+x1*x2*x6+x1*x2*x7+x1*x3*x4*x5+x1*x3*x4*x6+x1*x3*x4*x7+x1*x3*x4+x1*x3*x5*x7+x1*x3*x5+x1*x3*x6+x1*x3*x7+x1*x3+x1*x4*x5*x6*x7+x1*x4*x5*x6+x1*x4*x5*x7+x1*x4*x6*x7+x1*x4*x6+x1*x4*x7+x1*x5*x6+x1*x5*x7+x1+x2*x3*x4*x5*x6+x2*x3*x4*x5*x7+x2*x3*x4*x5+x2*x3*x4*x6*x7+x2*x3*x5*x6+x2*x3*x5*x7+x2*x3*x7+x2*x4*x5*x6*x7+x2*x4*x5*x6+x2*x4*x5*x7+x2*x4*x7+x2*x4+x2*x5*x6*x7+x2*x5*x6+x2*x5*x7+x2*x6*x7+x2*x7+x2+x3*x4*x5*x6+x3*x4*x5+x3*x4*x6*x7+x3*x4*x6+x3*x5*x6*x7+x3*x5*x7+x3*x6*x7+x3*x7+x4*x5+x4*x6*x7+x4*x6+x4+1
    , x0*x1*x2*x3*x5*x6*x7+x0*x1*x2*x3*x5*x6+x0*x1*x2*x3*x5*x7+x0*x1*x2*x3*x5+x0*x1*x2*x3*x7+x0*x1*x2*x4*x5*x6*x7+x0*x1*x2*x4*x5*x6+x0*x1*x2*x4*x5+x0*x1*x2*x6*x7+x0*x1*x2*x7+x0*x1*x2+x0*x1*x3*x4*x5*x6+x0*x1*x3*x4*x5*x7+x0*x1*x3*x4*x6+x0*x1*x3*x4+x0*x1*x3*x6*x7+x0*x1*x3*x7+x0*x1*x4*x5*x7+x0*x1*x5*x6*x7+x0*x1*x5+x0*x1*x6+x0*x2*x3*x4*x7+x0*x2*x3*x4+x0*x2*x3*x5*x6*x7+x0*x2*x3*x5*x7+x0*x2*x3*x5+x0*x2*x3*x6*x7+x0*x2*x3*x6+x0*x2*x3+x0*x2*x4*x5*x6*x7+x0*x2*x4*x5*x7+x0*x2*x4*x6*x7+x0*x2*x4*x6+x0*x2*x4+x0*x2*x5+x0*x2*x6*x7+x0*x2*x6+x0*x2+x0*x3*x4*x5*x6+x0*x3*x4*x5*x7+x0*x3*x4*x5+x0*x3*x4*x6+x0*x3*x4*x7+x0*x3*x5*x6+x0*x3*x5+x0*x3*x6*x7+x0*x3*x6+x0*x3*x7+x0*x4*x5*x6*x7+x0*x4*x5+x0*x4*x6*x7+x0*x4*x6+x0*x6*x7+x0+x1*x2*x3*x4*x5+x1*x2*x3*x4*x6+x1*x2*x3*x4*x7+x1*x2*x3*x4+x1*x2*x3*x5*x6*x7+x1*x2*x3*x5*x6+x1*x2*x3*x6*x7+x1*x2*x4*x5*x6*x7+x1*x2*x4*x5+x1*x2*x4*x6+x1*x2*x6*x7+x1*x2*x6+x1*x2*x7+x1*x3*x4*x5*x6+x1*x3*x4*x5+x1*x3*x4*x6+x1*x3*x5*x6*x7+x1*x3*x6*x7+x1*x3*x6+x1*x3+x1*x4*x5*x6*x7+x1*x4*x5*x6+x1*x4*x5+x1*x4*x6+x1*x5*x6+x1*x5*x7+x1*x6*x7+x1*x6+x1+x2*x3*x4*x5*x6*x7+x2*x3*x4*x5+x2*x3*x4+x2*x3*x5*x6*x7+x2*x3*x5*x6+x2*x3*x5*x7+x2*x3*x5+x2*x3*x6*x7+x2*x4*x5*x6*x7+x2*x4*x5*x6+x2*x4*x5*x7+x2*x4*x6+x2*x4*x7+x2*x5*x6*x7+x2*x5*x6+x2*x6*x7+x2*x6+x3*x4*x5*x6*x7+x3*x4*x5*x7+x3*x4*x6*x7+x3*x4+x3*x5*x6+x3*x5*x7+x3*x5+x3*x6*x7+x3+x4*x5*x6*x7+x4*x6*x7+x4*x7+x5*x6*x7+1
    , x0*x1*x2*x3*x4*x5*x7+x0*x1*x2*x3*x4*x7+x0*x1*x2*x3*x4+x0*x1*x2*x3*x5+x0*x1*x2*x3*x6+x0*x1*x2*x3*x7+x0*x1*x2*x4*x5*x6+x0*x1*x2*x4*x6+x0*x1*x2*x4*x7+x0*x1*x2*x4+x0*x1*x2*x5*x6+x0*x1*x2*x6*x7+x0*x1*x2+x0*x1*x3*x4*x5*x6*x7+x0*x1*x3*x4*x5*x6+x0*x1*x3*x4*x5+x0*x1*x3*x4*x7+x0*x1*x3*x4+x0*x1*x3*x5*x7+x0*x1*x3*x7+x0*x1*x3+x0*x1*x4*x6*x7+x0*x1*x4*x7+x0*x1*x4+x0*x1*x5*x6*x7+x0*x1*x5*x6+x0*x1*x5+x0*x1*x6*x7+x0*x1*x6+x0*x1*x7+x0*x1+x0*x2*x3*x4*x5*x6*x7+x0*x2*x3*x4*x5*x6+x0*x2*x3*x4*x5*x7+x0*x2*x3*x4*x5+x0*x2*x3*x4*x6+x0*x2*x3*x4+x0*x2*x3*x5*x6+x0*x2*x3+x0*x2*x4*x5*x6+x0*x2*x4*x5*x7+x0*x2*x4*x5+x0*x2*x4*x6*x7+x0*x2*x4*x7+x0*x2*x4+x0*x2*x5*x6*x7+x0*x2*x5*x6+x0*x2*x5*x7+x0*x2*x6*x7+x0*x2*x6+x0*x2+x0*x3*x4*x5*x6*x7+x0*x3*x4*x5+x0*x3*x4*x6+x0*x3*x4*x7+x0*x3*x4+x0*x3*x5+x0*x3*x7+x0*x4*x5*x6*x7+x0*x4*x6*x7+x0*x4+x0*x7+x1*x2*x3*x4*x5*x6+x1*x2*x3*x4*x5+x1*x2*x3*x4*x6*x7+x1*x2*x3*x4*x6+x1*x2*x3*x5*x6*x7+x1*x2*x3*x5*x6+x1*x2*x3*x6*x7+x1*x2*x3*x7+x1*x2*x4*x5*x6*x7+x1*x2*x4*x5*x6+x1*x2*x4*x5*x7+x1*x2*x4*x5+x1*x2*x4*x7+x1*x2*x4+x1*x2*x5+x1*x2*x6*x7+x1*x3*x4*x5*x6+x1*x3*x4*x5*x7+x1*x3*x4*x6*x7+x1*x3*x4*x7+x1*x3*x4+x1*x3*x5*x6+x1*x3*x6*x7+x1*x3*x7+x1*x3+x1*x4*x5*x6*x7+x1*x4*x5+x1*x4*x6*x7+x1*x5*x6*x7+x1*x5*x7+x1*x6+x1*x7+x2*x3*x4*x5*x6*x7+x2*x3*x4*x5*x7+x2*x3*x4*x6+x2*x3*x4*x7+x2*x3*x4+x2*x3*x5*x6*x7+x2*x3*x5+x2*x3*x6*x7+x2*x3*x6+x2*x3*x7+x2*x3+x2*x4*x5*x6+x2*x4*x5+x2*x4*x6*x7+x2*x4*x6+x2*x4*x7+x2*x4+x2*x5+x2*x6+x2*x7+x2+x3*x4*x5*x6*x7+x3*x4*x5*x6+x3*x4*x5*x7+x3*x4*x5+x3*x4*x7+x3*x4+x3*x5*x6+x3*x6+x3*x7+x4*x5*x7+x4*x5+x4+x5+x6*x7+x6+x7
    , x0*x1*x2*x3*x4*x5*x7+x0*x1*x2*x3*x4*x5+x0*x1*x2*x3*x4*x6*x7+x0*x1*x2*x3*x4+x0*x1*x2*x3*x5*x6+x0*x1*x2*x3*x5+x0*x1*x2*x3*x7+x0*x1*x2*x3+x0*x1*x2*x4*x5*x6*x7+x0*x1*x2*x4*x5*x6+x0*x1*x2*x4*x5*x7+x0*x1*x2*x4*x6+x0*x1*x2*x4*x7+x0*x1*x2*x4+x0*x1*x2*x5*x6+x0*x1*x2*x5*x7+x0*x1*x2*x6*x7+x0*x1*x2*x6+x0*x1*x2*x7+x0*x1*x2+x0*x1*x3*x4*x5*x6+x0*x1*x3*x4*x5*x7+x0*x1*x3*x4*x6+x0*x1*x3*x4*x7+x0*x1*x3*x4+x0*x1*x3*x5*x6*x7+x0*x1*x3*x5+x0*x1*x3*x6+x0*x1*x4*x5*x6*x7+x0*x1*x4*x5*x7+x0*x1*x4*x7+x0*x1*x5*x6+x0*x1*x5*x7+x0*x1*x6*x7+x0*x1+x0*x2*x3*x4*x5*x6+x0*x2*x3*x4*x5+x0*x2*x3*x4*x6*x7+x0*x2*x3*x4*x7+x0*x2*x3*x5*x6*x7+x0*x2*x3*x5*x7+x0*x2*x3*x5+x0*x2*x3*x6*x7+x0*x2*x3*x6+x0*x2*x4*x5*x6*x7+x0*x2*x4*x5*x7+x0*x2*x4+x0*x2*x5*x6*x7+x0*x2*x5*x6+x0*x2*x5+x0*x2+x0*x3*x4*x5*x6*x7+x0*x3*x4*x6*x7+x0*x3*x4*x6+x0*x3*x4+x0*x3*x5*x6*x7+x0*x3*x5*x6+x0*x3*x5*x7+x0*x4*x5*x6*x7+x0*x4*x5*x6+x0*x4*x5*x7+x0*x4*x5+x0*x4*x7+x0*x4+x0*x5*x6+x0*x5*x7+x0*x6*x7+x0*x6+x0*x7+x0+x1*x2*x3*x4*x5*x6*x7+x1*x2*x3*x4*x5*x6+x1*x2*x3*x4*x5+x1*x2*x3*x4*x7+x1*x2*x3*x4+x1*x2*x3*x5*x6+x1*x2*x3*x5*x7+x1*x2*x3*x5+x1*x2*x3*x6+x1*x2*x3*x7+x1*x2*x4*x5*x6*x7+x1*x2*x4*x5*x6+x1*x2*x4*x5*x7+x1*x2*x4*x6*x7+x1*x2*x4*x6+x1*x2*x4+x1*x2*x5*x6*x7+x1*x2*x5*x7+x1*x2*x6*x7+x1*x2*x6+x1*x2+x1*x3*x4*x5*x6*x7+x1*x3*x4*x6*x7+x1*x3*x4*x6+x1*x3*x4*x7+x1*x3*x5*x7+x1*x3*x6*x7+x1*x3*x7+x1*x4*x5*x6+x1*x4*x6*x7+x1*x4*x7+x1*x4+x1*x5*x6+x1*x5*x7+x1*x6*x7+x1+x2*x3*x4*x5*x7+x2*x3*x4*x5+x2*x3*x4*x6*x7+x2*x3*x4*x6+x2*x3*x5*x6+x2*x3*x5+x2*x3*x7+x2*x3+x2*x4*x5*x6*x7+x2*x4*x5*x6+x2*x4*x5+x2*x5*x6*x7+x2*x5*x6+x2*x6*x7+x3*x4*x5*x6*x7+x3*x4*x5+x3*x4*x6+x3*x4*x7+x3*x5*x6*x7+x3*x5*x7+x3*x6*x7+x3+x4*x5*x6*x7+x4*x5*x6+x4*x5*x7+x4*x5+x4*x6*x7+x4*x7+x5*x6+x7
    , x0*x1*x2*x3*x4*x5*x6+x0*x1*x2*x3*x4*x5*x7+x0*x1*x2*x3*x4*x5+x0*x1*x2*x3*x4*x6*x7+x0*x1*x2*x3*x4+x0*x1*x2*x3*x5*x7+x0*x1*x2*x3*x6*x7+x0*x1*x2*x3*x6+x0*x1*x2*x3*x7+x0*x1*x2*x3+x0*x1*x2*x4*x5*x6*x7+x0*x1*x2*x4*x5*x7+x0*x1*x2*x4*x5+x0*x1*x2*x4*x6*x7+x0*x1*x2*x4*x6+x0*x1*x2*x4*x7+x0*x1*x2*x4+x0*x1*x2*x5*x7+x0*x1*x2*x5+x0*x1*x2*x6+x0*x1*x3*x4*x5*x6*x7+x0*x1*x3*x4*x5*x6+x0*x1*x3*x4*x5*x7+x0*x1*x3*x4*x5+x0*x1*x3*x4*x6*x7+x0*x1*x3*x4*x6+x0*x1*x3*x5*x6+x0*x1*x3*x5+x0*x1*x3*x6*x7+x0*x1*x3+x0*x1*x4*x5*x6+x0*x1*x4*x6*x7+x0*x1*x4*x6+x0*x1*x5*x6*x7+x0*x1*x5*x6+x0*x1*x5+x0*x1*x7+x0*x1+x0*x2*x3*x4*x5*x6+x0*x2*x3*x4*x6*x7+x0*x2*x3*x4*x7+x0*x2*x3*x5*x6*x7+x0*x2*x3*x5*x6+x0*x2*x3*x5+x0*x2*x3*x6+x0*x2*x4*x5*x7+x0*x2*x4*x6*x7+x0*x2*x4*x6+x0*x2*x4*x7+x0*x2*x5*x6*x7+x0*x2*x5*x6+x0*x2*x6+x0*x2*x7+x0*x3*x4*x5*x6*x7+x0*x3*x4*x5*x7+x0*x3*x4*x5+x0*x3*x4*x6*x7+x0*x3*x4*x7+x0*x3*x5*x6*x7+x0*x3*x5*x6+x0*x3*x5*x7+x0*x3*x6+x0*x3*x7+x0*x3+x0*x4*x5*x6*x7+x0*x4*x5*x7+x0*x4*x5+x0*x4*x6+x0*x4*x7+x0*x5*x6*x7+x0*x5*x6+x0*x5*x7+x0*x6*x7+x0*x7+x0+x1*x2*x3*x4*x5*x7+x1*x2*x3*x4*x6+x1*x2*x3*x4+x1*x2*x3*x5*x6*x7+x1*x2*x3*x5*x6+x1*x2*x3*x5*x7+x1*x2*x3*x5+x1*x2*x4*x5*x6*x7+x1*x2*x4*x5+x1*x2*x4*x7+x1*x2*x4+x1*x2*x6*x7+x1*x2*x6+x1*x2+x1*x3*x4*x5*x6*x7+x1*x3*x4*x5*x6+x1*x3*x4*x5+x1*x3*x4*x6*x7+x1*x3*x4*x7+x1*x3*x4+x1*x3*x5*x7+x1*x3*x6*x7+x1*x3*x7+x1*x4*x5*x6*x7+x1*x4*x5*x6+x1*x4*x5+x1*x4*x6*x7+x1*x4*x7+x1*x5*x6+x1*x6*x7+x1*x7+x2*x3*x4*x5*x6*x7+x2*x3*x4*x5*x6+x2*x3*x4+x2*x3*x5*x6*x7+x2*x3*x5+x2*x3*x6+x2*x3*x7+x2*x4*x5*x6*x7+x2*x4*x5*x6+x2*x4*x5*x7+x2*x4*x6*x7+x2*x4*x6+x2*x4*x7+x2*x5*x6*x7+x2*x5*x6+x2*x5*x7+x2*x6*x7+x2*x7+x2+x3*x4*x5*x6*x7+x3*x4*x5*x6+x3*x4*x5*x7+x3*x4*x5+x3*x4*x6*x7+x3*x4*x6+x3*x4*x7+x3*x4+x3*x5*x6+x3*x5*x7+x3*x6*x7+x3*x6+x3*x7+x4*x5*x7+x4*x5+x4*x6*x7+x4*x7+x5*x7+x6+x7
    , x0*x1*x2*x3*x4*x6*x7+x0*x1*x2*x3*x4*x6+x0*x1*x2*x3*x5*x6*x7+x0*x1*x2*x3*x5+x0*x1*x2*x3*x7+x0*x1*x2*x4*x5*x6*x7+x0*x1*x2*x4*x5*x6+x0*x1*x2*x4*x5*x7+x0*x1*x2*x4*x7+x0*x1*x2*x5*x6*x7+x0*x1*x2*x5*x7+x0*x1*x2*x6*x7+x0*x1*x2+x0*x1*x3*x4*x5*x6*x7+x0*x1*x3*x4*x5*x6+x0*x1*x3*x4*x5*x7+x0*x1*x3*x4*x5+x0*x1*x3*x4*x6*x7+x0*x1*x3*x4+x0*x1*x3*x5*x6*x7+x0*x1*x3*x5+x0*x1*x3*x6+x0*x1*x3*x7+x0*x1*x4*x5*x7+x0*x1*x4*x6*x7+x0*x1*x4+x0*x1*x5*x6*x7+x0*x1*x5*x6+x0*x1*x5+x0*x1*x7+x0*x2*x3*x4*x5*x7+x0*x2*x3*x4*x5+x0*x2*x3*x4*x6+x0*x2*x3*x4*x7+x0*x2*x3*x4+x0*x2*x3*x5*x6*x7+x0*x2*x3*x5+x0*x2*x3*x6+x0*x2*x3*x7+x0*x2*x4*x5*x7+x0*x2*x4*x5+x0*x2*x4*x6*x7+x0*x2*x4*x6+x0*x2*x4+x0*x2*x5*x6+x0*x2*x5+x0*x2*x7+x0*x3*x4*x5*x6*x7+x0*x3*x4*x5*x7+x0*x3*x4*x5+x0*x3*x4*x6*x7+x0*x3*x4*x6+x0*x3*x4+x0*x3*x5*x6*x7+x0*x3*x5*x6+x0*x3*x6*x7+x0*x3*x6+x0*x3*x7+x0*x4*x5*x6*x7+x0*x4*x6+x0*x4+x0*x5*x7+x0*x5+x0*x6+x0*x7+x0+x1*x2*x3*x4*x5*x6+x1*x2*x3*x4*x5*x7+x1*x2*x3*x4*x6*x7+x1*x2*x3*x4*x6+x1*x2*x3*x4+x1*x2*x3*x5*x6+x1*x2*x3*x5*x7+x1*x2*x3*x6*x7+x1*x2*x3*x7+x1*x2*x4*x5*x6*x7+x1*x2*x4*x5*x6+x1*x2*x4*x6*x7+x1*x2*x4*x6+x1*x2*x4+x1*x2*x5*x6+x1*x2*x5*x7+x1*x2*x6*x7+x1*x2*x6+x1*x3*x4*x5*x6*x7+x1*x3*x4*x5*x6+x1*x3*x4*x6*x7+x1*x3*x4*x7+x1*x3*x4+x1*x3*x5*x6*x7+x1*x3*x7+x1*x3+x1*x4*x5*x6*x7+x1*x4*x5*x7+x1*x4*x5+x1*x4*x6*x7+x1*x4*x6+x1*x5*x6*x7+x1*x5+x1*x6*x7+x1+x2*x3*x4*x5*x7+x2*x3*x4*x5+x2*x3*x4*x6+x2*x3*x4*x7+x2*x3*x5*x6*x7+x2*x3*x5*x7+x2*x3*x6*x7+x2*x3*x7+x2*x3+x2*x4*x5*x6+x2*x4*x5+x2*x4*x6+x3*x4*x5*x6*x7+x3*x4*x5+x3*x4*x6*x7+x3*x4*x6+x3*x4*x7+x3*x5*x6+x3*x6*x7+x3*x6+x3*x7+x4*x5*x6+x4*x5*x7+x4*x5+x4*x6*x7+x4*x6+x4*x7+x4+x5*x7+x6*x7+x7+1
    , x0*x1*x2*x3*x4*x5*x7+x0*x1*x2*x3*x4*x5+x0*x1*x2*x3*x4*x6+x0*x1*x2*x3*x5*x6*x7+x0*x1*x2*x3*x5*x6+x0*x1*x2*x3*x5+x0*x1*x2*x3*x6*x7+x0*x1*x2*x4*x5*x7+x0*x1*x2*x4*x7+x0*x1*x2*x4+x0*x1*x2*x5*x6*x7+x0*x1*x2*x5*x6+x0*x1*x2*x6*x7+x0*x1*x2*x6+x0*x1*x2+x0*x1*x3*x4*x5*x6*x7+x0*x1*x3*x4*x5*x6+x0*x1*x3*x4*x6*x7+x0*x1*x3*x4*x7+x0*x1*x3*x5*x6+x0*x1*x3*x5*x7+x0*x1*x3*x7+x0*x1*x4*x5*x6*x7+x0*x1*x4*x5+x0*x1*x4*x6*x7+x0*x1*x4*x6+x0*x1*x4+x0*x1*x5*x6*x7+x0*x1*x5*x6+x0*x1*x5+x0*x1+x0*x2*x3*x4*x5*x7+x0*x2*x3*x4*x5+x0*x2*x3*x4*x6+x0*x2*x3*x4*x7+x0*x2*x3*x5*x6*x7+x0*x2*x3*x5*x7+x0*x2*x3*x5+x0*x2*x3*x6+x0*x2*x3*x7+x0*x2*x4*x5*x6*x7+x0*x2*x4*x5*x6+x0*x2*x4*x5+x0*x2*x4*x6*x7+x0*x2*x4+x0*x2*x5*x6*x7+x0*x2*x5*x7+x0*x2*x5+x0*x2+x0*x3*x4*x5*x6*x7+x0*x3*x4+x0*x3*x5*x6*x7+x0*x3*x5*x6+x0*x3*x5*x7+x0*x3*x5+x0*x3*x6*x7+x0*x3*x7+x0*x4*x5*x6*x7+x0*x4*x5*x6+x0*x4*x5*x7+x0*x4*x5+x0*x4*x6+x0*x5*x6*x7+x0*x5*x7+x0*x5+x0*x6*x7+x1*x2*x3*x4*x5*x7+x1*x2*x3*x4*x5+x1*x2*x3*x4*x7+x1*x2*x3*x5*x6+x1*x2*x3*x5+x1*x2*x3*x6*x7+x1*x2*x3*x6+x1*x2*x3*x7+x1*x2*x3+x1*x2*x4*x5*x6+x1*x2*x4*x6*x7+x1*x2*x4*x7+x1*x2*x5*x7+x1*x2*x5+x1*x2*x6+x1*x2+x1*x3*x4*x5*x6*x7+x1*x3*x4*x5*x7+x1*x3*x4*x6*x7+x1*x3*x4*x6+x1*x3*x4*x7+x1*x3*x5*x6+x1*x3*x6+x1*x3*x7+x1*x3+x1*x4*x5*x6*x7+x1*x4*x5*x6+x1*x4*x7+x1*x5*x6*x7+x1*x5*x6+x1*x5*x7+x1*x5+x1*x6*x7+x1*x6+x1*x7+x2*x3*x4*x5*x7+x2*x3*x5*x6*x7+x2*x3*x5*x7+x2*x3*x6*x7+x2*x4*x5*x6+x2*x4*x5*x7+x2*x4*x5+x2*x4*x7+x2*x5*x6*x7+x2*x5*x7+x2*x7+x3*x4*x5*x6*x7+x3*x4*x6+x3*x4*x7+x3*x5*x6+x3*x5*x7+x3*x5+x3*x6*x7+x3*x6+x3*x7+x3+x4*x5*x6*x7+x4*x5*x6+x4*x5+x4*x6+x4+x5*x6+x5+x6*x7+x7+1]
