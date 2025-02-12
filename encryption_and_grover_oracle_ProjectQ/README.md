The following steps explain how to generate the data for Tables 8 and 9 using the respective scripts. You can check the results with those saved  in the `./results` directory.

## Generating Data for Table 8

1. **First Row of Table 8**  
   Run the following script:  
   ```
   python TC24_Grover_AES128_Pipeline.py

2. **Second Row of Table 8**  
   Run the following script:  
   
   ```
   python ours_Grover_AES128_Pipeline.py



## Generating Data for Table 9

1. **First Row of Table 9**
   Run the following script:
   ```
   python TC24_Enc_AES128_IU.py
   ```

2. **Second Row of Table 9**
   Run the following script:
   ```
   python ours_Enc_AES128_IU.py
   ```


## In the outputs:

- **H+S+X** corresponds to #1qClifford.

- **T+T^\dagger** corresponds to #T.

- **CX** corresponds #CNOT.

- **CCX** corresponds to #M, which is the number of measurements. As we mentioned in the paper, in $QAND^{\dagger}$  we replace the measurement by a Toffoli gate for obtaining correct full depth. 

- **depth_of_dag** corresponds to Full Depth.

- ProjectQ cannot return T-depth, hence the T-depth in the tables are manually calculated.

  a) The T-depths in Table 8 are calculated by the formula $20\times TD$, where $TD$ is the T-depth of the S-box implementation. $TD=3$ for all these circuits.

  b) The T-depths in Table 9 are calculated by the formula $11\times TD$, where $TD$ is the T-depth of the S-box implementation. $TD=3$ for all these circuits.

- There is a bug about the width outputted by ProjectQ (see Width_Bug_ProjectQ.pdf for details.), 

  hence the output Max. width (number of qubits) is not the correct width.

  The widths presented in these tables, are all calculated manually.

  a) The widths in Table 8 are calculated by the formula  $128\times 11+128+20\times k$, where $k$ is the number of ancilla qubits. For the T-depth-3 circuit in [54], $k=129-16=113$. For ours T-depth-3 circuit, $k=97-16=81$.  

  b) The widths in Table 9 are calculated by the formula $512+32\times k$, where $k$ is the number of ancilla qubits. For the T-depth-3 circuit in [54], $k=129-16=113$. For ours T-depth-3 circuit, $k=97-16=81$.  





