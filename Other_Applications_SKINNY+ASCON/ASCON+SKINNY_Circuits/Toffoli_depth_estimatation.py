############################## A Resource Estimator for a detailed NCT circuit ###########################
############################## In the output layer structure, the number of Toffoli layers is equal to the Toffoli-depth #####################

# Gate form : [operation,controlled,target, depth, Toffoli-depth]
# Gates: 'X': NOT gate ; 'CNOT'; 'TF': Toffoli gate

import numpy as np
import re
# use for deepcopy, faster than copy.deepcopy()
import pickle

# Input form: gate sequence "H(1), CNOT(2,3), T(3),..."
def extract_elements(input_str):

	pattern = re.compile(r'(\w+)\(([^)]+)\)')

	matches = pattern.findall(input_str)

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

# def merge_layer(layer1, layer2):
# 	flag_merge = False
# 	layer1_index = [0]*len(layer1)
# 	layer2_index = [0]*len(layer2)
# 	for i in range(len(layer1)):
# 		gate = layer1[i]
# 		if gate[0] == "CNOT" or gate[0] == "H" or gate[0] == "X":
# 			for j in range(len(layer2)):
# 				if layer2[j][:2] == gate[:2]:
# 					flag_merge = True
# 					layer1_index[i] = 1  # 1: delete
# 					layer2_index[j] = 1
# 		elif gate[0] == "T" or gate[0] == "TD":
# 			for j in range(len(layer2)):
# 				if dagger_check(gate,layer2[j]):
# 					flag_merge = True
# 					layer1_index[i] = 1
# 					layer2_index[j] = 1
# 				if layer2[j][:2] == gate[:2]:
# 					flag_merge = True
# 					layer1_index[i] = 2  # 2: T^2->S, TD^2->SD
# 					layer2_index[j] = 1  
# 		else:
# 			for j in range(len(layer2)):
# 				if dagger_check(gate,layer2[j]):
# 					flag_merge = True
# 					layer1_index[i] = 1
# 					layer2_index[j] = 1
# 	for i in range(len(layer1)-1,-1,-1):
# 		if layer1_index[i] == 1:
# 			layer1.pop(i)
# 		elif layer1_index[i] == 2:
# 			if layer1[i][0] == "T":
# 				layer1[i][0] = "S"
# 			else :
# 				layer1[i][0] = "SD"
# 	for i in range(len(layer2)-1,-1,-1):
# 		if layer2_index[i] == 1:
# 			layer2.pop(i)
# 	return flag_merge

# def new_Simplify_GateSequence(Gate_seq, width):
# 	Layers = Layer_Classify(Gate_seq,width,0)

# 	new_seq = []
	
# 	for i in range(20,40):	
# 		print(Layers[i])
# 	for layer in Layers:
# 		new_seq = new_seq+layer

# 	#print(new_seq)

# 	flag = True
# 	while flag == True:
# 		flag = False
# 		for i in range(len(Layers)-1):
# 			layer = Layers[i]
# 			layer_next = Layers[i+1]
# 			flag = merge_layer(layer, layer_next)
# 			if flag == True:
# 				print("################")
# 				if layer_next == []:
# 					Layers.pop(i+1)
# 				if layer == []:
# 					Layers.pop(i)
# 				new_seq = []
# 				for layer in Layers:	
# 					new_seq = new_seq+layer
# 				Layers = Layer_Classify(new_seq,width,0)
# 				break
	
# 	new_seq = []

# 	# for layer in Layers:	
# 	# 	print(layer)
# 	for layer in Layers:
# 		new_seq = new_seq+layer
# 	return new_seq

def Simplify_GateSequence(Gate_seq, width):
	Wires = [[] for i in range(width)]
	Eliminated_Index = [0]*len(Gate_seq)

	print("######## Finding Cancellation of Consecutive Gates:#########")
	print("##### Form: [gate index1, gate index2, gate type] #####\n")

	for i in range(len(Gate_seq)):
		gate = Gate_seq[i]
		if gate[0] == "CNOT":
			index1 = gate[1][0]
			index2 = gate[1][1]
			Wires[index1].append([i,"CNOT",index1+index2*width])
			Wires[index2].append([i,"CNOT",index1+index2*width])
		elif gate[0] == "TF":
			if gate[1][0] < gate[1][1]:
				index1 = gate[1][0]
				index2 = gate[1][1]
			else:
				index1 = gate[1][1]
				index2 = gate[1][0]
			index_targ = gate[1][2]


			index = index1+index2*width+index_targ*width**2
			Wires[index1].append([i,"TF",index])
			Wires[index2].append([i,"TF",index])
			Wires[index_targ].append([i,"TF",index])
		else :
			index = gate[1][0]
			Wires[index].append([i,gate[0],1])
	
	eliminated_flag = True
	while eliminated_flag == True:
		eliminated_flag = False
		eliminated_flag = Simplify_Wire(Wires, Eliminated_Index,width, eliminated_flag)

#	print(Eliminated_Index)

	Gate_seq_new = []
	for i in range(len(Gate_seq)):
		if Eliminated_Index[i] == 0:
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
				gate = wire_gates[i]  # gate: [i, "X", 1] [i, "CNOT", 2+1*width], [i, "TF", 1+2*width+3*width^2]
				gate_next = wire_gates[i+1]
				if gate[1] == gate_next[1] and gate[2] == gate_next[2]:
					if gate[1] == "TF":
						if Eliminated_Index[gate[0]] == 1 and Eliminated_Index[gate_next[0]] == 1:
						#	print([gate[0],gate_next[0], gate[1]])
							wire_new.pop(i+1)
							wire_new.pop(i)
							Flag = True
							whole_flag = True
							break						
						else:
							gate_index1 = gate[0]
							gate_index2 = gate_next[0]
							targ = gate[2]//(width**2)
							c1=gate[2]%width
							c2=(gate[2]%(width**2))//width
							if c1 == w:
								other1 = c2
								other2 = targ
							elif c2 == w:
								other1 = c1
								other2 = targ
							else:
								other1 = c1
								other2 = c2

							for j in range(len(Wires[other1])-1):
								if Wires[other1][j][0] == gate_index1 and Wires[other1][j+1][0] == gate_index2:
									Flag = True
							if Flag == True:
								Flag = False	
								for j in range(len(Wires[other2])-1):
									if Wires[other2][j][0] == gate_index1 and Wires[other2][j+1][0] == gate_index2:
								
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
					elif gate[1] == "CNOT":
						
						if Eliminated_Index[gate[0]] == 1 and Eliminated_Index[gate_next[0]] == 1:
							#print([gate,gate_next,w])
							wire_new.pop(i+1)
							wire_new.pop(i)
							Flag = True
							whole_flag = True
							break
						else:	
							targ = gate[2]//width
							if w == targ:
								other = gate[2]%width
							else :
								other = targ
							gate_index1 = gate[0]
							gate_index2 = gate_next[0]

							for j in range(len(Wires[other])-1):
								if Wires[other][j][0] == gate_index1 and Wires[other][j+1][0] == gate_index2:
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
					else:
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

# def GateSeq_To_QsharpVersion(Gate_seq, f, index0):

#     for gate in Gate_seq:
#         if gate[0] == "TD":
#             f.write("Adjoint T(x[%d]);\n"%(gate[1][0-index0]))
#         elif gate[0] == "CNOT":
#             f.write("CNOT(x[%d],x[%d]);\n"%(gate[1][0-index0],gate[1][1-index0]))
#         else:
#             f.write("%s(x[%d]);\n"%(gate[0],gate[1][0-index0]))

#     f.close()

def ToffoliDepth_Eval(Gate_seq, width):
    Wires_TFDepth=[0]*width
    TFDepth = 0
    for gate in Gate_seq:
        if gate[0] == "CNOT":
            a = gate[1][0]
            b = gate[1][1]
            if Wires_TFDepth[a] > Wires_TFDepth[b]:
                current_D = Wires_TFDepth[a]
                Wires_TFDepth[b] = current_D
            else :
                current_D = Wires_TFDepth[b]
                Wires_TFDepth[a] = current_D
            gate[2] = current_D
        elif gate[0] == "TF":
            current_D = max([Wires_TFDepth[w] for w in gate[1]])
            current_D += 1
            for w in gate[1]:
                Wires_TFDepth[w] = current_D

            gate[2] = current_D
        else:
            a = gate[1][0]
            gate[2] = Wires_TFDepth[a]

    return max(Wires_TFDepth)

def FullDepth_Eval(Gate_seq, width):
	Wires_FDepth=[0]*width
	FDepth = 0
	for gate in Gate_seq:
		if gate[0] == "CNOT":
			a = gate[1][0]
			b = gate[1][1]
			if Wires_FDepth[a] > Wires_FDepth[b]:
				Wires_FDepth[a] += 1
				Wires_FDepth[b] = Wires_FDepth[a]

			else :
				Wires_FDepth[b] += 1
				Wires_FDepth[a] = Wires_FDepth[b]
		elif gate[0] == "TF":
			current_D = max(Wires_FDepth[w] for w in gate[1])
			current_D += 1
			for w in gate[1]:
				Wires_FDepth[w] = current_D
		else:
			a = gate[1][0]
			Wires_FDepth[a] += 1
	
	return max(Wires_FDepth)

def PartialDepth_Classify(Gate_seq, width, initial_depth):
	Wires_FDepth=[0]*width
	FDepth = 0
	Layers = []
	for gate in Gate_seq:
		if gate[0] == "CNOT" or gate[0] == "MT":
			d_max = max(Wires_FDepth[wire] for wire in gate[1])
			
			# b = gate[2]
			d_max += 1
			for wire in gate[1]:
				Wires_FDepth[wire] = d_max
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
	Layers = []
	for gate in Gate_seq:
		if gate[0] == "CNOT" or gate[0] == "MT":
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
def Gates_Layers_Classified_Toffoli(Gate_seq, TFDepth): 
	TF_Layers = [[] for i in range(TFDepth)]
	Clifford_Layers = [[] for i in range(TFDepth+1)]
	for gate in Gate_seq:
		if gate[0] == "TF":
			d = gate[2]  # TF-depth of a Toffoli gate, put it in the (d-1)-th TF layer
			TF_Layers[d-1].append(pickle.loads(pickle.dumps(gate)))
		else :
			d = gate[2]
			Clifford_Layers[d].append(pickle.loads(pickle.dumps(gate)))
	return [TF_Layers,Clifford_Layers]

def Gates_to_Layers_Toffoli_optimial(Gate_seq, width):
	TFDepth = ToffoliDepth_Eval(Gate_seq, width)
	
	Two_Parts = Gates_Layers_Classified_Toffoli(Gate_seq, TFDepth)
	TF_Part = Two_Parts[0]
	Clifford_Part = Two_Parts[1]
	
	initial_depth = 0
	Layers = []

	for i in range(TFDepth):
		partial_gseq = Clifford_Part[i]
		MT_gate = ["MT",[],i+1,0]
		for tf_gate in TF_Part[i]:
			MT_gate[1].append(tf_gate[1][0])
			MT_gate[1].append(tf_gate[1][1])
			MT_gate[1].append(tf_gate[1][2])
			
		partial_gseq.append(MT_gate)

		Layers0 = PartialDepth_Classify(partial_gseq, width, initial_depth)
		Layers.extend(pickle.loads(pickle.dumps(Layers0)))
		initial_depth = len(Layers)

	initial_depth = len(Layers)
	Layers0 = PartialDepth_Classify(Clifford_Part[TFDepth],width,initial_depth)
	Layers.extend(pickle.loads(pickle.dumps(Layers0)))

	return Layers

def Gates_to_Layers_Toffoli_optimial_new(Gate_seq, width):
	TFDepth = ToffoliDepth_Eval(Gate_seq, width)
	
	Two_Parts = Gates_Layers_Classified_Toffoli(Gate_seq, TFDepth)
	TF_Part = Two_Parts[0]
	Clifford_Part = Two_Parts[1]
	
	initial_depth = 0
	Layers = []

	new_gseq = []

	for i in range(TFDepth):
		partial_gseq = Clifford_Part[i]
		MT_gate = ["MT",[],i+1,0]
		for tf_gate in TF_Part[i]:
			MT_gate[1].append(tf_gate[1][0])
			MT_gate[1].append(tf_gate[1][1])
			MT_gate[1].append(tf_gate[1][2])
			
		partial_gseq.append(MT_gate)

		new_gseq = new_gseq+ partial_gseq

#		print(new_gseq)

#		Layers0 = PartialDepth_Classify(partial_gseq, width, initial_depth)
#		Layers.extend(pickle.loads(pickle.dumps(Layers0)))
#		initial_depth = len(Layers)
		
	new_gseq = new_gseq+Clifford_Part[TFDepth]

#	initial_depth = len(Layers)
	Layers0 = PartialDepth_Classify(new_gseq,width,0)
	Layers.extend(pickle.loads(pickle.dumps(Layers0)))

	return Layers

def Output_Layers(Layers):
	for layer in Layers:
		TFlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				TFlayer_flag = True
				TFlayer_depth = gate[2]
		gate_str = ""
		if TFlayer_flag == True:
			print("#----------- Layer: %d, Toffoli-Layer: %d ------------"%(layer[0][3], TFlayer_depth))
			for gate in layer:
				if gate[0] == "MT" :
					if gate_str == "":
						gate_str += ("TF(%d,%d,%d)"%(gate[1][0],gate[1][1],gate[1][2]))
						for j in range(3,len(gate[1]),3):
							gate_str += (", TF(%d,%d,%d)"%(gate[1][j],gate[1][j+1],gate[1][j+2]))

					else:
						for j in range(0,len(gate[1]),3):
							gate_str += (", TF(%d,%d,%d)"%(gate[1][j],gate[1][j+1],gate[1][j+2]))
							
				elif gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
				else:
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))

			print(gate_str)
		else:
			print("#----------- Layer: %d #--------------#"%(layer[0][3])) 
			for gate in layer:
				if gate[0] != "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))
				else :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
			print(gate_str)

def Output_Layers_AlgebraicForm(Layers):
	for layer in Layers:
		TFlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				TFlayer_flag = True
				TFlayer_depth = gate[2]
		gate_str = ""
		if TFlayer_flag == True:
			print("#----------- Layer: %d, Toffoli-Layer: %d ------------"%(layer[0][3], TFlayer_depth))
			for gate in layer:
				if gate[0] == "MT" :
					if gate_str == "":
						gate_str += ("f%d=f%d*f%d+f%d"%(gate[1][2], gate[1][0],gate[1][1],gate[1][2]))
						for j in range(3,len(gate[1]),3):
							gate_str += ("; f%d=f%d*f%d+f%d"%(gate[1][j+2],gate[1][j],gate[1][j+1],gate[1][j+2]))

					else:
						for j in range(0,len(gate[1]),3):
							gate_str += ("; f%d=f%d*f%d+f%d"%(gate[1][j+2],gate[1][j],gate[1][j+1],gate[1][j+2]))
							
				elif gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("f%d=f%d+f%d"%(gate[1][1],gate[1][0],gate[1][1]))
					else:
						gate_str += ("; f%d=f%d+f%d"%(gate[1][1],gate[1][0],gate[1][1]))
				else:
					if gate_str == "":
						gate_str += ("f%d=f%d+1"%(gate[1][0],gate[1][0]))
					else:
						gate_str += ("; f%d=f%d+1"%(gate[1][0],gate[1][0]))

			print(gate_str)
		else:
			print("#----------- Layer: %d #--------------#"%(layer[0][3])) 
			for gate in layer:
				if gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("f%d=f%d+f%d"%(gate[1][1],gate[1][0],gate[1][1]))
					else:
						gate_str += ("; f%d=f%d+f%d"%(gate[1][1],gate[1][0],gate[1][1]))
				else:
					if gate_str == "":
						gate_str += ("f%d=f%d+1"%(gate[1][0],gate[1][0]))
					else:
						gate_str += ("; f%d=f%d+1"%(gate[1][0],gate[1][0]))
			print(gate_str)

# Output normal format to file
def File_Output_Layers(Layers, width, f):
	for layer in Layers:
		TFlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				TFlayer_flag = True
				TFlayer_depth = gate[2]
		gate_str = ""
		if TFlayer_flag == True:
			f.write("\n#----------- Layer: %d, Toffoli-Layer: %d ------------#\n"%(layer[0][3], TFlayer_depth))
			for gate in layer:
				if gate[0] == "MT" :
					if gate_str == "":
						gate_str += ("TF(%d,%d,%d)"%(gate[1][0],gate[1][1],gate[1][2]))
						for j in range(3,len(gate[1]),3):
							gate_str += (", TF(%d,%d,%d)"%(gate[1][j],gate[1][j+1],gate[1][j+2]))

					else:
						for j in range(0,len(gate[1]),3):
							gate_str += (", TF(%d,%d,%d)"%(gate[1][j],gate[1][j+1],gate[1][j+2]))
							
				elif gate[0] == "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
				else:
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))

			f.write(gate_str)

		else:
			f.write("\n#----------- Layer: %d #--------------#\n"%(layer[0][3])) 
			for gate in layer:
				if gate[0] != "CNOT" :
					if gate_str == "":
						gate_str += ("%s(%d)"%(gate[0],gate[1][0]))
					else:
						gate_str += (", %s(%d)"%(gate[0],gate[1][0]))
				else :
					if gate_str == "":
						gate_str += ("%s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
					else:
						gate_str += (", %s(%d,%d)"%(gate[0],gate[1][0],gate[1][1]))
			f.write(gate_str)

# Output QASM2.0 format to file
# # end_symbol between gates, eg: "x q[0];x q[1];" or "x q[0];\nx q[1];"
def File_Output_Layers_QASM(Layers, width, filename, end_symbol="\n"):
	# rows with QASM format
	rows = ['OPENQASM 2.0;', 'include "qelib1.inc";', f'qreg q[{width}];']

	for layer in Layers:
		TFlayer_flag = False
		for gate in layer:
			if gate[0] == "MT":
				TFlayer_flag = True
				TFlayer_depth = gate[2]
		
		if TFlayer_flag == True:
			rows.append(f"\n//--------------- Layer: {layer[0][3]}, Toffoli-Layer: {TFlayer_depth} ---------------//")
		else:
			rows.append(f"\n//--------------- Layer: {layer[0][3]} ---------------//") 
		# all gates in this layer
		layer_gates = []
		for gate in layer:
			if gate[0] == "MT" :
				for j in range(0,len(gate[1]),3):
					layer_gates.append(f"ccx q[{gate[1][j]}],q[{gate[1][j+1]}],q[{gate[1][j+2]}];")			
			elif gate[0] == "CNOT":
				layer_gates.append(f"cx q[{gate[1][0]}],q[{gate[1][1]}];")
			else:
				layer_gates.append(f"x q[{gate[1][0]}];")
		rows.append(end_symbol.join(layer_gates))
	# save to file
	with open(filename, "w") as f:
		f.write("\n".join(rows))

# def Input_Check(g_seq,width,f):
#     for gate in g_seq:
#         if gate[0] == "CNOT":
#             f.write("A = np.dot(%s[%d][%d],A)\n"%(gate[0],gate[1][0],gate[1][1]))
#         else:
#             f.write("A = np.dot(%s[%d],A)\n"%(gate[0],gate[1][0]))
#     f.close()            

def Metrics_Present(Gate_seq, width):
	print("######### The Costs of the Circuit ###########")

	NOT_count = 0 
	CNOT_count = 0 
	Toffoli_count =0
	for gate in Gate_seq:
		if gate[0] == "X":
			NOT_count += 1
		elif gate[0] == "CNOT":
			CNOT_count += 1
		else:
			Toffoli_count += 1
	full_depth = FullDepth_Eval(Gate_seq, width)
	Toffoli_depth = ToffoliDepth_Eval(Gate_seq, width)
	Layers = Gates_to_Layers_Toffoli_optimial_new(Gate_seq,width)
	print("NOT-count: %d"%(NOT_count))
	print("CNOT-count: %d"%(CNOT_count))
	print("Toffoli-count: %d"%(Toffoli_count))
	print("Width: %d"%(SIZE))
	print("Toffoli-depth: %d"%(Toffoli_depth))
	print("Current Depth: %d"%(len(Layers)))
	print("Full depth: %d"%(full_depth))

	return Layers

"""
NCT gates, from ours to QASM format
Ours: (X, CNOT, TF)
QASM: (x, cx,   cxx)
"""
def Ours_to_QASM_NCT(s, filename):
    import re
    ours_gates_map = {
        "X" : "x"
        , "CNOT" : "cx"
        , "TF" : "ccx"
    }
    # regular expression
    pattern = re.compile(r'(\w+)\(([^)]+)\)')
    # match
    matches = pattern.findall(s)

    # rows with QASM format
    rows = ['OPENQASM 2.0;', 'include "qelib1.inc";', f'qreg q[{0}];']
    width = 0

    for match in matches:
        gate, idxs = match[0], [int(num) for num in match[1].split(',')]
        width = max(width, max(idxs))
        qubits = [f"q[{j}]" for j in idxs]

        # map to QASM format
        g = ours_gates_map[gate]
        rows.append(f"{g} {','.join(qubits)};")

    rows[2] = f'qreg q[{width+1}];'
    
    with open(filename, "w") as f:
        f.write("\n".join(rows))
    return "\n".join(rows)

def QASM_to_Ours_NCT(filename):
	def replace_symbol(s):
		t = s.replace(", ", ",").replace("  ", "")
		t = t.replace(";", "").replace("q[", "").replace("]", "")
		return t
	with open(filename, "r") as f:
		rows = f.read().split("\n")
	gates = []
	for row in rows:
		row = replace_symbol(row)
		if "ccx " in row:
			gates.append(f"TF({row.split(' ')[1]})")
		elif "cx " in row:
			gates.append(f"CNOT({row.split(' ')[1]})")
		elif "x " in row:
			gates.append(f"X({row.split(' ')[1]})")

	return ",".join(gates)

##################################################################

circuits_names = ['C7X_gates', 'SHA3_gates_12NOT', 'AES_9qubits', 'AES_pair_16qubit', 'AES_AC23_1', 'AES_AC23_2', 'AES_TF3_C0', 'AES_TF3_C1', 'AES_TF4_C0', 'AES_TF4_C1']

# supplementary cipher
circuits_names = ["SKINNY128_T3", "SKINNY128_8qubit", "ASCON_T1", "ASCON_5qubit"]

for name in circuits_names:
	input_filename = f"./NCT_quantum_circuit/{name}_NCT.qasm"
	s = QASM_to_Ours_NCT(input_filename)

	[g_seq, SIZE] = extract_elements(s)
	g_seq_sim = Simplify_GateSequence(g_seq, SIZE)
	Layers = Metrics_Present(g_seq_sim, SIZE)

	print("\n########## Outputting the layer structure ##########")  

	output_filename = f"./NCT_layer/{name}_Layer_NCT.qasm"
	# (1) end_symbol="\n" the standard format(one gate in one row, recommend)
	# (2) end_symbol=""   the compact display layer structure
	File_Output_Layers_QASM(Layers, SIZE, output_filename, end_symbol="\n")

	print(f'The layer structure is outputted in the file "{output_filename}".')
