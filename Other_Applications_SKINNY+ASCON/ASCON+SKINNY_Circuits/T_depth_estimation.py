############################## A Resource Estimator for a detailed NCT circuit ###########################
############################## In the output layer structure, the number of Toffoli layers is equal to the Toffoli-depth #####################

# Gate form : [operation,controlled,target, depth, T-depth]
# Gates: 'T', 'TD': T dagger, 'S', 'SD': S dagger, 'H', 'CNOT', 'X': Pauli-X, 'Y': Pauli-Y, 'Z': Pauli-Z, 'MM': Multiple Measurement
# Here 'MM(a,b,c)' is used for QAND^{dagger}. The operations are:
# First measure qubit a, the apply gates on qubits a,b,c depenting on the measurement result.
# By this multiple measurment, we ensure that in resource estimation for depth, the subsequent gates will not be applied before the measurement of qubit a.

import numpy as np
import re
# use for deepcopy, faster than copy.deepcopy()
import pickle

def extract_operations(input_str):
    # regular expression
	pattern = re.compile(r'(\w+)\(([^)]+)\)')

	# match
	matches = pattern.findall(input_str)

	# extract
	width = 0
	gates = []

	for match in matches:
		wires = [int(num) for num in match[1].split(',')]

		for w in wires:
			if width < w:
				width =w
		gates.append([match[0], wires , 0, 0])

	return [gates, width+1]

def dagger_check(op1, op2):
	if op1[1][:2] == op2[1][:2]:

		if op1[0] == "T" and op2[0] == "TD":
			return True
		elif op1[0] == "TD" and op2[0] == "T":
			return True
		elif op1[0] == "S" and op2[0] == "SD":
			return True
		elif op1[0] == "SD" and op2[0] == "S":
			return True
		else:
			return False
	else :
		return False

def Simplify_GateSequence(Gate_seq, width):
	Wires = [[] for i in range(width)]
	Eliminated_Index = [0]*len(Gate_seq)
	print("######## Finding Cancellation of Consecutive Gates: #########")
	print("##### Form: [gate index1, gate index2, gate type] #####\n")

	for i in range(len(Gate_seq)):
		gate = Gate_seq[i]
		if gate[0] == "CNOT":
			index1 = gate[1][0]
			index2 = gate[1][1]
			Wires[index1].append([i,"CNOT",index2])
			Wires[index2].append([i,"CNOT",index1+width])
		elif gate[0] == "TD":
			index = gate[1][0]
			Wires[index].append([i,"T",-1])
		elif gate[0] == "SD":
			index = gate[1][0]
			Wires[index].append([i,"S",-1])
		elif gate[0] == "MM":
			for index in gate[1]:
				Wires[index].append([i,"MM",1])
		else :
			index = gate[1][0]
			Wires[index].append([i,gate[0],1])
		
	# print(Wires)
	eliminated_flag = True
	while eliminated_flag == True:
		eliminated_flag = False
		eliminated_flag = Simplify_Wire(Wires, Eliminated_Index,width, eliminated_flag)

#	print(Eliminated_Index)

	Gate_seq_new = []
	for i in range(len(Gate_seq)):
		if Eliminated_Index[i] == 0:
			Gate_seq_new.append(Gate_seq[i])
		elif Eliminated_Index[i] == -1:
			if Gate_seq[i][0] == "T":
				Gate_seq[i][0] = "S"
			else:
				Gate_seq[i][0] = "SD"
			Gate_seq_new.append(Gate_seq[i]) 	
	
	print("######### Simplification Finished #########\n")
	return Gate_seq_new

def Simplify_Wire(Wires,Eliminated_Index,width, whole_flag):
	for w in range(len(Wires)):
		wire_gates = Wires[w]

		Flag = True
		while Flag == True:
			Flag = False
			wire_new = pickle.loads(pickle.dumps(wire_gates))
			for i in range(len(wire_gates)-1):
				gate = wire_gates[i]  # gate: [i, "T", -1] [i, "CNOT", 2]
				gate_next = wire_gates[i+1]
				if gate[1] == gate_next[1]:
					if gate[2] !=0 and gate[2] + gate_next[2] == 0:
						print([gate[0],gate_next[0], gate[1]])
						Eliminated_Index[gate[0]] = 1  # 1 means being eliminated
						Eliminated_Index[gate_next[0]] = 1
						wire_new.pop(i+1)
						wire_new.pop(i)
						Flag = True
						whole_flag = True
						break
					elif gate[2] == gate_next[2]:
						if gate[1] == "T":
							print([gate[0],gate_next[0], gate[1]])
							Eliminated_Index[gate[0]] = -1 # -1 means being changed from T to S, T^dagger to S^dagger
							Eliminated_Index[gate_next[0]] = 1
							wire_new[i] = [gate[0],"S",gate[2]]
							wire_new.pop(i+1)
							Flag = True
							whole_flag = True
							break
						elif gate[1] == "CNOT":
							
							if Eliminated_Index[gate[0]] == 1 and Eliminated_Index[gate_next[0]] == 1:
								#print([gate,gate_next])
								wire_new.pop(i+1)
								wire_new.pop(i)
								Flag = True
								whole_flag = True
								break
							else:	
								targ = gate[2]%width
								gate_index1 = gate[0]
								gate_index2 = gate_next[0]
								for j in range(len(Wires[targ])-1):
									if Wires[targ][j][0] == gate_index1 and Wires[targ][j+1][0] == gate_index2:
								#		print(gate_index1)
								#		print(gate_index2)
								#		Wires[targ].pop(j+1)
								#		Wires[targ].pop(j)
										Eliminated_Index[gate[0]] = 1
										Eliminated_Index[gate_next[0]] = 1
										print([gate[0],gate_next[0], gate[1]])
										wire_new.pop(i+1)
										wire_new.pop(i)
										Flag = True
										whole_flag = True
										break
								if Flag == True:
									break
						elif gate[1] in ["H", "X", "Y", "Z"]:
							Eliminated_Index[gate[0]] = 1
							Eliminated_Index[gate_next[0]] = 1
							print([gate[0],gate_next[0], gate[1]])
							wire_new.pop(i+1)
							wire_new.pop(i)
							Flag = True
							whole_flag = True
							break 
			wire_gates = pickle.loads(pickle.dumps(wire_new))
		
		Wires[w] = wire_gates

	return whole_flag

def TDepth_Eval(Gate_seq, width):
	Wires_TDepth=[0]*width
	TDepth = 0
	for gate in Gate_seq:
		if gate[0] == "CNOT" or gate[0] == "MM":
			a = max(Wires_TDepth[wire] for wire in gate[1])
			current_D = a
			for w in gate[1]:
				Wires_TDepth[w] = current_D
			gate[2] = current_D
		elif gate[0] == "T" or gate[0] == "TD":
			a = gate[1][0]
			Wires_TDepth[a] += 1
			#TDepth += 1
			gate[2] = Wires_TDepth[a]
		else:
			a = gate[1][0]
			gate[2] = Wires_TDepth[a]

	return max(Wires_TDepth)

def FullDepth_Eval(Gate_seq, width):
	Wires_FDepth=[0]*width
	FDepth = 0
	for gate in Gate_seq:
		if gate[0] == "CNOT" or gate[0] == "MM":
			a = max(Wires_FDepth[wire] for wire in gate[1])
			a += 1
			for w in gate[1]:
				Wires_FDepth[w] = a
		#	gate[4] = current_D
		else:
			a = gate[1][0]
			Wires_FDepth[a] += 1
			#TDepth += 1
		#	gate[4] = Wires_FDepth[a]
		
	return max(Wires_FDepth)

def PartialDepth_Classify(Gate_seq, width, initial_depth):
	Wires_FDepth=[0]*width
	FDepth = 0
	Layers = []
	for gate in Gate_seq:
		if gate[0] == "CNOT" or gate[0] == "MT" or gate[0] == "MM":
			d_max = max(Wires_FDepth[wire%width] for wire in gate[1])
			# b = gate[2]
			d_max += 1
			for wire in gate[1]:
				Wires_FDepth[wire%width] = d_max
			gate[3] = initial_depth + d_max
			if (len(Layers) < d_max):
				Layers.append([gate])
			else:
				Layers[d_max-1].append(gate)

		else:
			a = gate[1][0]
			Wires_FDepth[a] += 1
			FDepth += 1
			#TDepth += 1
			gate[3] = initial_depth + Wires_FDepth[a]
			if (len(Layers) < Wires_FDepth[a]):
				Layers.append([gate])
			else:
				Layers[Wires_FDepth[a]-1].append(gate)
		
	return Layers

def Layer_Classify(Gate_seq, width, initial_depth):
	Wires_FDepth=[0]*width
	FDepth = 0
	Layers =[]
	for gate in Gate_seq:
		if gate[0] == "CNOT" or gate[0] == "MT" or gate[0] == "MM":
			d_max = max(Wires_FDepth[wire%width] for wire in gate[1])
			# b = gate[2]
			d_max += 1
			for wire in gate[1]:
				Wires_FDepth[wire%width] = d_max
			#gate[3] = initial_depth + d_max
			if (len(Layers) < d_max):
				Layers.append([gate])
			else:
				Layers[d_max-1].append(gate)

		else:
			a = gate[1][0]
			Wires_FDepth[a] += 1
			FDepth += 1
			#TDepth += 1
			#gate[3] = initial_depth + Wires_FDepth[a]
			if (len(Layers) < Wires_FDepth[a]):
				Layers.append([gate])
			else:
				Layers[Wires_FDepth[a]-1].append(gate)
		
	return Layers

# Divided the gates into different T-layers
def Gates_Layers_Classified_T(Gate_seq, TDepth): 
	T_Layers = [[] for i in range(TDepth)]
	Clifford_Layers = [[] for i in range(TDepth+1)]
	for gate in Gate_seq:
		if gate[0] == "T" or gate[0] == "TD":
			d = gate[2]  # T-depth of a T or TD gate, put it in the (d-1)-th T layer
			T_Layers[d-1].append(pickle.loads(pickle.dumps(gate)))
		else :
			d = gate[2]
			Clifford_Layers[d].append(pickle.loads(pickle.dumps(gate)))
	return [T_Layers,Clifford_Layers]

def Gates_to_Layers_T_optimial(Gate_seq, width):
	TDepth = TDepth_Eval(Gate_seq, width)
	Two_Parts = Gates_Layers_Classified_T(Gate_seq, TDepth)
	T_Part = Two_Parts[0]
	Clifford_Part = Two_Parts[1]
	
#	print(len(T_Part))
#	print(len(Clifford_Part))
	
	initial_depth = 0
	Layers = []

	for i in range(TDepth):
		partial_gseq = Clifford_Part[i]
		MT_gate = ["MT",[],i+1,0]
		for t_gate in T_Part[i]:
			if t_gate[0] == "T":
				MT_gate[1].append(t_gate[1][0])
			else :
				MT_gate[1].append(t_gate[1][0]+width)
		partial_gseq.append(MT_gate)
		Layers0 = PartialDepth_Classify(partial_gseq, width, initial_depth)
		Layers.extend(pickle.loads(pickle.dumps(Layers0)))
		initial_depth = len(Layers)

	initial_depth = len(Layers)
	Layers0 = PartialDepth_Classify(Clifford_Part[TDepth],width,initial_depth)
	Layers.extend(pickle.loads(pickle.dumps(Layers0)))

	return Layers

def Gates_to_Layers_T_optimial_new(Gate_seq, width):
	TDepth = TDepth_Eval(Gate_seq, width)
	Two_Parts = Gates_Layers_Classified_T(Gate_seq, TDepth)
	T_Part = Two_Parts[0]
	Clifford_Part = Two_Parts[1]
	
#	print(len(T_Part))
#	print(len(Clifford_Part))
	
	initial_depth = 0
	Layers = []
	new_gseq = []

	for i in range(TDepth):
		partial_gseq = Clifford_Part[i]
		MT_gate = ["MT",[],i+1,0]
		for t_gate in T_Part[i]:
			if t_gate[0] == "T":
				MT_gate[1].append(t_gate[1][0])
			else :
				MT_gate[1].append(t_gate[1][0]+width)
		partial_gseq.append(MT_gate)
		new_gseq = new_gseq + partial_gseq
#		Layers0 = PartialDepth_Classify(partial_gseq, width, initial_depth)
#		Layers.extend(pickle.loads(pickle.dumps(Layers0)))
#		initial_depth = len(Layers)
	new_gseq = new_gseq + Clifford_Part[TDepth]
#	initial_depth = len(Layers)
	Layers0 = PartialDepth_Classify(new_gseq,width,0)
	Layers.extend(pickle.loads(pickle.dumps(Layers0)))

	return Layers

def Output_Layers(Layers, width):
	for layer in Layers:
		Tlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				Tlayer_flag = True
				Tlayer_depth = gate[2]
		gate_str = ""
		if Tlayer_flag == True:
			print("#----------- Layer: %d, T-Layer: %d ------------"%(layer[0][3], Tlayer_depth))
			for gate in layer:
				if gate[0] == "MT" :
					if gate_str == "":
						if gate[1][0] > (width-1):
							gate_str += ("TD(%d)"%(gate[1][0]%width))
						else :
							gate_str += ("T(%d)"%(gate[1][0]))
						for j in range(1,len(gate[1])):
							if gate[1][j] > width-1:
								gate_str += (", TD(%d)"%(gate[1][j]%width))
							else :
								gate_str += (", T(%d)"%(gate[1][j]))
					else:
						for j in range(len(gate[1])):
							if gate[1][j] > width-1:
								gate_str += (", TD(%d)"%(gate[1][j]%width))
							else :
								gate_str += (", T(%d)"%(gate[1][j]))

				elif gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
				elif gate[0] == "MM":
					if gate_str == "":
						gate_str += ("%s("%(gate[0]))
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
					else:
						gate_str += (", %s("%(gate[0]))
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
				else:
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))

			print(gate_str)

		else:
			print("#----------- Layer: %d #--------------#"%(layer[0][3])) 
			for gate in layer:
				if gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
				elif gate[0] == "MM":
					if gate_str == "":
						gate_str += ("%s("%(gate[0]))
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
					else:
						gate_str += (", %s("%(gate[0]))
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
				else:
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))

			print(gate_str)

# Output normal format to file
def File_Output_Layers(Layers, width, f):
	for layer in Layers:
		Tlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				Tlayer_flag = True
				Tlayer_depth = gate[2]
		gate_str = ""
		if Tlayer_flag == True:
			f.write("\n#----------- Layer: %d, T-Layer: %d ------------\n"%(layer[0][3], Tlayer_depth))
			for gate in layer:
				if gate[0] == "MT" :
					if gate_str == "":
						if gate[1][0] > (width-1):
							gate_str += ("TD(%d)"%(gate[1][0]%width))
						else :
							gate_str += ("T(%d)"%(gate[1][0]))
						for j in range(1,len(gate[1])):
							if gate[1][j] > width-1:
								gate_str += (", TD(%d)"%(gate[1][j]%width))
							else :
								gate_str += (", T(%d)"%(gate[1][j]))
					else:
						for j in range(len(gate[1])):
							if gate[1][j] > width-1:
								gate_str += (", TD(%d)"%(gate[1][j]%width))
							else :
								gate_str += (", T(%d)"%(gate[1][j]))

				elif gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
				elif gate[0] == "MM":
					if gate_str == "":
						gate_str += ("%s("%(gate[0]))
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
					else:
						gate_str += (", %s("%(gate[0]))
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
				else:
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))

			f.write(gate_str)

		else:
			f.write("\n#----------- Layer: %d #--------------#\n"%(layer[0][3])) 
			for gate in layer:
				if gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
				elif gate[0] == "MM":
					if gate_str == "":
						gate_str += ("%s("%(gate[0]))
						k = -1
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
					else:
						gate_str += (", %s("%(gate[0]))
						k = -1
						for k in range(len(gate[1])-1):
							gate_str += ("%d,"%(gate[1][k]))
						gate_str += ("%d)"%gate[1][k+1])
				else:
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))
			f.write(gate_str)

# Output QASM2.0 format to file
# symbol between gates, eg: "x q[0];x q[1];" or "x q[0];\nx q[1];"
def File_Output_Layers_QASM(Layers, width, filename, end_symbol="\n"):
	# rows with QASM format
	rows = ['OPENQASM 2.0;', 'include "qelib1.inc";', f'qreg q[{width}];', f'creg c[0];']
	# measure count
	cnt = 0
	for layer in Layers:
		Tlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				Tlayer_flag = True
				Tlayer_depth = gate[2]
		if Tlayer_flag == True:
			rows.append(f"\n//--------------- Layer: {layer[0][3]}, T-Layer: {Tlayer_depth} ---------------//")
		else:
			rows.append(f"\n//--------------- Layer: {layer[0][3]} ---------------//") 
		# all gates in this layer
		layer_gates = []
		for gate in layer:
			if gate[0] == "MT":
				for j in range(len(gate[1])):
					if gate[1][j] > width-1:
						layer_gates.append(f"tdg q[{gate[1][j]%width}];")
					else :
						layer_gates.append(f"t q[{gate[1][j]}];")
			elif gate[0] == "CNOT" :
				layer_gates.append(f"cx q[{gate[1][0]}],q[{gate[1][1]}];")
			# Measure
			elif gate[0] == "MM":
				qubits = [f"q[{j}]" for j in gate[1]]
				measure_str = f"measure {qubits[0]}->c[{cnt}];"
				# barrier
				barrier_str = "barrier " + ",".join(qubits) + ";"
				cnt += 1
				layer_gates += [measure_str, barrier_str]
			# "H", "S", "SD", "X", "Y", "Z"
			else:
				if gate[0] == "SD":
					gate[0] = "sdg"
				layer_gates.append(f"{gate[0]} q[{gate[1][0]}];".lower())
		rows.append(end_symbol.join(layer_gates))
	if cnt > 0:
		rows[3] = f'creg c[{cnt}];'
	else:
		rows.remove('creg c[0];')
	# save to file
	with open(filename, "w") as f:
		f.write("\n".join(rows))

def Input_Check(g_seq,width,f):
    for gate in g_seq:
        if gate[0] == "CNOT":
            f.write("A = np.dot(%s[%d][%d],A)\n"%(gate[0],gate[1][0],gate[1][1]))
        else:
            f.write("A = np.dot(%s[%d],A)\n"%(gate[0],gate[1][0]))
    f.close()            

def Matrix_Output_Layers(Layers, width, f):
	for layer in Layers:
		Tlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				Tlayer_flag = True
				Tlayer_depth = gate[2]
		gate_str = ""
		if Tlayer_flag == True:
			f.write("\n#----------- Layer: %d, T-Layer: %d ------------\n"%(layer[0][3], Tlayer_depth))
			for gate in layer:
				if gate[0] == "MT" :
					if gate_str == "":
						if gate[1][0] > (width-1):
							gate_str += ("A=np.dot(TD[%d],A)\n"%(gate[1][0]%width))
						else :
							gate_str += ("A=np.dot(T[%d],A)\n"%(gate[1][0]))
						for j in range(1,len(gate[1])):
							if gate[1][j] > width-1:
								gate_str += ("A=np.dot(TD[%d],A)\n"%(gate[1][j]%width))
							else :
								gate_str += ("A=np.dot(T[%d],A)\n"%(gate[1][j]))
					else:
						for j in range(len(gate[1])):
							if gate[1][j] > width-1:
								gate_str += ("A=np.dot(TD[%d],A)\n"%(gate[1][j]%width))
							else :
								gate_str += ("A=np.dot(T[%d],A)\n"%(gate[1][j]))

				elif gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("A=np.dot(%s[%d][%d],A)\n"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += ("A=np.dot(%s[%d][%d],A)\n"%(gate[0],gate[1][0],gate[1][1]))
				else:
					if gate_str == "":
						gate_str += ("A=np.dot(%s[%d],A)\n"%(gate[0],gate[1][0]))
					else:
						gate_str += ("A=np.dot(%s[%d],A)\n"%(gate[0],gate[1][0]))

			f.write(gate_str)

		else:
			f.write("\n#----------- Layer: %d #--------------#\n"%(layer[0][3])) 
			for gate in layer:
				if gate[0] != "CNOT" :
					if gate_str == "":
						gate_str += ("A=np.dot(%s[%d],A)\n"%(gate[0],gate[1][0]))
					else:
						gate_str += ("A=np.dot(%s[%d],A)\n"%(gate[0],gate[1][0]))
				else :
					if gate_str == "":
						gate_str += ("A=np.dot(%s[%d][%d],A)\n"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += ("A=np.dot(%s[%d][%d],A)\n"%(gate[0],gate[1][0],gate[1][1]))
			f.write(gate_str)

def Metrics_Present(Gate_seq, width):

	CNOT_count = 0 
	T_count = 0
	OneClifford_count = 0
	M_count = 0

	print("######### The Costs of the Circuit ###########")

	for gate in Gate_seq:
		if gate[0] in ["X", "Y", "Z", "S", "SD", "H"]:
			OneClifford_count += 1
		elif gate[0] == "CNOT":
			CNOT_count += 1
		elif gate[0] == "T" or gate[0] == "TD":
			T_count += 1
		elif gate[0] == "MM":
			M_count +=1
	full_depth = FullDepth_Eval(Gate_seq, width)
	T_depth = TDepth_Eval(Gate_seq, width)
	Layers = Gates_to_Layers_T_optimial(Gate_seq,width)
#	Layers = Gates_to_Layers_T_optimial_new(Gate_seq,width)
	print("1qClifford-count: %d"%(OneClifford_count))
	print("CNOT-count: %d"%(CNOT_count))
	print("T-count: %d"%(T_count))
	print("Measurment-count: %d"%(M_count))
	print("Width: %d"%(SIZE))
	print("T-depth: %d"%(T_depth))
	print("Current Depth: %d"%(len(Layers)))
	print("Full depth: %d"%(full_depth))

	return Layers

"""
Clifforf+T gates, from ours to QASM format
Ours: (X, Y, Z, H, S, SD,  T, TD,  CNOT) + MM
QASM: (x, y, z, h, s, sdg, t, tdg, cx)   + (measure, barrier)
#################### rules ####################
Ours like "H(5),CNOT(3,4),X(25),MM(24,16,17)"
"""
def Ours_to_QASM_CliffordT(s, filename):
    ours_gates_map = {
         "X" : "x"
        , "Y" : "y"
        , "Z" : "z"
        , "H" : "h"
        , "S" : "s"
        , "SD" : "sdg"
        , "T" : "t"
        , "TD" : "tdg"
        , "CNOT" : "cx"
    }
    
    import re
    # regular expression
    pattern = re.compile(r'(\w+)\(([^)]+)\)')
    # match
    matches = pattern.findall(s)

    # rows with QASM format
    rows = ['OPENQASM 2.0;', 'include "qelib1.inc";', f'qreg q[{0}];', f'creg c[0];']
    width = 0
    # measure count
    cnt = 0
    for match in matches:
        gate, idxs = match[0], [int(num) for num in match[1].split(',')]
        width = max(width, max(idxs))
        qubits = [f"q[{j}]" for j in idxs]

        if gate == "MM":
            measure_str = f"measure {qubits[0]}->c[{cnt}];"
            # barrier
            barrier_str = "barrier " + ",".join(qubits) + ";"
            cnt += 1
            rows += [measure_str, barrier_str]
        elif gate in ours_gates_map:
            g = ours_gates_map[gate]
            rows.append(f"{g} {','.join(qubits)};")
            
    if cnt > 0:
        rows[3] = f'creg c[{cnt}];'
    else:
        rows.remove('creg c[0];')
    rows[2] = f'qreg q[{width+1}];'
    
    with open(filename, "w") as f:
        f.write("\n".join(rows))
    return ""#"\n".join(rows)

"""
Clifforf+T gates, from QASM to ours format
QASM: (x, y, z, h, s, sdg, t, tdg, cx)   + (measure, barrier)
Ours: (X, Y, Z, H, S, SD,  T, TD,  CNOT) + MM
#################### *.qasm rules ####################
qubits use "q", classical bits use "c"
one row only has one gate, end with ";"
the "measure" and "barrier" are together(for QAND^{dagger}(a, b, c) <=> MM(a, b, c))
eg: "measure q[0]->c[0];\nbarrier q[0],q[1],q[2];" 
######################################################
```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[1];
h q[0];
h q[1];
measure q[0]->c[0];
barrier q[0],q[1],q[2];
x q[0];
cx q[2],q[1];
h q[1];
```
"""
def QASM_to_Ours_CliffordT(filename):
    def replace_symbol(s):
        t = s.replace(", ", ",").replace("  ", "")
        t = t.replace(";", "").replace("q[", "").replace("]", "")
        return t
    with open(filename, "r") as f:
        rows = f.read().split("\n")
    # the rules for gates mapping
    qasm_gates_map = {
        "x" : "X"
        , "y" : "Y"
        , "z" : "Z"
        , "h" : "H"
        , "s" : "S"
        , "sdg" : "SD"
        , "t" : "T"
        , "tdg" : "TD"
        , "cx" : "CNOT"
    }
    
    gates = []
    n = len(rows)
    i = 0
    while i < n: 
        row = replace_symbol(rows[i])
        # blank lines or comments
        if len(row) == 0 or row[:2] == "//":
            i += 1
            continue
        gate, qubits = row.split(' ')
        if gate == "measure":
            # "measure q[0]->c[0];""
            qubits = qubits.split('->')[0]
            # next is barrier, "barrier q[0],q[1],q[2];"
            if i + 1 < n and rows[i+1][:2] != "//" and "barrier " in rows[i+1]:
                row_next = replace_symbol(rows[i+1])
                qubits = row_next.split(" ")[1]
                i += 1 
            gates.append(f"MM({qubits})")
        elif gate in qasm_gates_map:
            g = qasm_gates_map[gate]
            gates.append(f"{g}({qubits})")            
        i += 1

    return ",".join(gates)

##########################################################################

circuits_names = ['C7X_gates', 'SHA3_gates_12NOT', 'SHA3_eprint2023', 'AES_9qubits', 'AES_Tpar_9qubit', 'AES_pair_16qubit', 'AES_pair_16qubit_Sim_Tpar', 'AES_AC22_T3_C0', 'AES_AC22_T3_C1', 'AES_AC23_1_C0', 'AES_AC23_1_C1', 'AES_AC23_2_C0', 'AES_AC23_2_C1', 'AES_TC24_T4_C0', 'AES_TC24_T4_C1', 'AES_TC24_T3_C1', 'AES_T3_C0', 'AES_T3_C1', 'AES_T4_C0', 'AES_T4_C1']

# supplementary cipher
circuits_names = ["SKINNY128_T3", "SKINNY128_8qubit", "ASCON_T1", "ASCON_5qubit"]

for name in circuits_names:
	input_filename = f"./CliffordT_quantum_circuit/{name}_CliffordT.qasm"
	s = QASM_to_Ours_CliffordT(input_filename)

	[g_seq, SIZE] = extract_operations(s)
	g_seq_sim = Simplify_GateSequence(g_seq, SIZE)
	Layers = Metrics_Present(g_seq_sim, SIZE)

	print("\n########## Outputting the layer structure ##########")  

	output_filename = f"./CliffordT_layer/{name}_Layer_CliffordT.qasm"
	# (1) end_symbol="\n" the standard format(one gate in one row, recommend)
	# (2) end_symbol=""   the compact display layer structure
	File_Output_Layers_QASM(Layers, SIZE, output_filename, end_symbol="\n")

	print(f'The layer structure is outputted in the file "{output_filename}".')

