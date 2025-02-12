# Supplementary Codes

The codes need Sagemath environment

The correctness of the NCT circuits of the S-boxes of ASCON and SKINNY-128 can be verified by running:

```sh
python3 verify_NCT_circuit.py
```
## 1. Generating new minimal-T-depth quantum circuits

In `minimal_Tdepth_ASCON_SKINNY_codes/`, we use the`Max-Covers` SAT-based method to get the classical implementations for the SKINNY-128 S-box and the ASCON S-box.
SKINNY-128 S-box: AND-depth-3
ASCON S-box:    AND-depth-1

We provide the output file `covers_eqs/*.out` from the SAT Solver to get classical result:

```sh
python3 Sbox_classical.py
```

If you want to [generate, convert, solve] Boolean equations and get the result, you need to install two tools:
(1) the ANF-to-CNF conveter: Bosphorus
    [https://github.com/meelgroup/bosphorus]
(2) the SAT Solver: Kissat
    [https://github.com/arminbiere/kissat]

Then uncomment three lines(35, 36, 37)/(64, 65, 66) in `Sbox_classical.py` and run the code again
line-35: generate *.eqs         (code)
line-36: convert *.eqs to *.cnf (bosphorus)
line-36: solve *.cnf to *.out   (kissat)

```py
# find_common_covers_eqs(F=SKINNY128_Sbox_ANF, n=n, maxd=3, ks=[4,4,2], BA=BA, M=M, prefix=prefix)
# os.system(f"./bosphorus --anfread {prefix}.eqs --cnfwrite {prefix}.cnf --verb 0")
# os.system(f"./kissat {prefix}.cnf > {prefix}.out --sat")
```

We use the`ClassicalToQuantum` algorithm to convert classical circuits to forward NCT circuits

```sh
python3 Sbox_quantum.py
```

Then generate Clifford+T circuit and layer structure.

At last, we obtain 

1) A Toffoli-depth-1 NCT circuit (width 15, including uncomputation) and a T-depth-1 Clifford+T circuit (width 20, including uncomputation) for the ASCON S-box,
2) A Toffoli-depth-5 NCT circuit (width 25, including uncomputation) and a T-depth-3 Clifford+T circuit (width 29, including uncomputation) for the SKINNY-128 S-box.

## 2. Generating new minimal-width quantum circuits

In  `minimal_width_ASCON_codes/`, we use the SAT-based method to get the minimal-width NCT circuit for the ASCON Sbox (setting width=5, Toffoli-count=7).

```sh
python3 minimal_width_SAT.py
```

We provide the output file `minimal_width_eqs/*.out` to get the result from the SAT Solver

The Parallel SAT solver: [https://github.com/shaowei-cai-group/ParKissat-RS]



For SKINNY-128, we use the tensor decomposition tool given in [35] to obtain the 8-qubit MCT implementation. 



By decomposing MCT gates accordingly,  we obtain 

1) A 5-qubit NCT circuit (Toffoli-depth 7)and a 5-qubit Clifford+T circuit (T-depth 21)for the ASCON S-box,
2) An 8-qubit NCT circuit (Toffoli-depth 1092) and an 8-qubit Clifford+T circuit (T-depth 1901) for the SKINNY-128 S-box.

## 3. New NCT and Clifford+T circuits for ASCON and SKINNY-128

In  `ASCON+SKINNY_Circuits/`, we provide the sepcific NCT circuits and Clifford+T circuits for the ASCON S-box and the SKINNY-128 S-box in .qasm format. There specific quantum resource costs can be found in `Clifford+T_Costs_ASCON+SKINNY.txt` and `NCT_Costs_ASCON+SKINNY.txt`.

