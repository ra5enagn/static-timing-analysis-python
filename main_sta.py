#nldm in Nanoseconds, Volts, milliAmps. 


#calling the dependencies
import argparse #library to reade the arguments from commad line
import re #regular expression library used in converting strings into list of strings
import time #flex library  to show the run time of the program

class Node:
  #class to hold the data of the Netlist file every gate is a node
  def __init__(self):
    self.name = '' #stores the type of gate
    self.Cload = 0.0 #fanout load
    self.incap = 0.0 #gate capacitance of a input
    self.inputs = [] #list of all inputs of the node
    self.outputs = [] #list of all outputs of the node
    self.Tau_in = [] #input Slew Rate
    self.inp_arrival = [] #when the signal has reached the inputs
    self.outp_arrival = [] #intput arrival time + device delay
    self.max_out_arrival = 0.0 #same as outp_arrival but adding the max possible delay of the device
    self.max_out_arrival_index = 0 #stores the curresponfin index of max_out_arrival in the outp_arrival list
    self.delay = 0.0 #gate delay
    self.Tau_out = 0.0 #output slew after calculation.
    self.required_input_arrival = 0.0 #given to be help and is task specific holds input required time
    self.required_output_arrival = [] #given to be help and is task specific holds output required time
    self.min_required_output_arrival = 0.0 # holds the minimum of the required_output_arrival list
    self.slack = [] #slack calculation
    self.min_slack = 0.0 #minimum slack of the gate
    self.primary_in = False #boolean for primary input
    self.primary_out = False #boolean for primary output

  def node_display (self):
    #This class function is used as a minor display function for debugging purposes

    print (f'The name of this node is {self.name}')
    print (f'The output is connected to nodes: {self.outputs}')
    print (f'The input is connected to nodes: {self.inputs}')
    print (f'The input capacitance is: {self.incap} and op cap :{self.Cload}')
    print(f'The tau in = {self.Tau_in} and Tau_out = {self.Tau_out}')
    print(f'The input arival time is {self.inp_arrival} and output arrival time is {self.outp_arrival}')
    print(f'The slack is {self.min_slack}')
    if self.primary_in:
      print(f'This is a Primary Input node')
    if self.primary_out:
      print('This is a Primary Output node')
    print('###\n\n')

class nldm_data:
  #class to hold the data of the NLDM file
  def __init__(self):
    self.name = '' #stores teh gate type
    self.capacitance = 0.0 #stores the input capacitance of the gate
    self.delay_index_1 = [] #stores the slew and Cload values for the x and y co-ordinates of delay
    self.delay_values = [] #stores the delay values
    self.slew_index_1 = [] #stores the slew and Cload values for the x and y co-ordinates of slew
    self.slew_values = [] #stores teh slews
    self.inputs = 1 # to store the input numbe which is defaulted to 1
    self.etc = '_X1'

def read_ckt(netlist_name):
  #this function reads the netlist and assigns then to the class object
  #creating a set of delimiters
  delimiters = r"[(,)=\n\r]"
  input_counter=1;
  output_counter=1;
  gate_counter=1;
  nodes = {}
  # file handling for reading in the Netlist
  try:#check if the file is present of not and prevent
    Netlist = open(netlist_name, "r")
  except FileNotFoundError:
    print('\n\n\nAre you sure about the netlist file name? please check it and retry\n\n')
    exit(0)
  line = Netlist.readline()
  for line in Netlist:
    line=line.replace(" ", "") #removes all spaces
    if line.startswith('#') or line == '\n': #skips emppty lines
      continue
    values = list(filter(None,re.split(delimiters,line))) #seperates the string in a list of strings based on the seperation parameter
    if values[0]=='INPUT':  #hardcoding the input and output formats to be stored first
      ipname = values[1]
      if ipname not in nodes:
        nodes[ipname] = Node() #this creates the object of the class node only if it is not already present else it will update the value
      nodes[ipname].primary_in = True
      nodes[ipname].name = 'INPUT'
      input_counter += 1
    elif values[0] == 'OUTPUT':
      opname = values[1]
      if opname not in nodes:
        nodes[opname] = Node()
      nodes[opname].primary_out = True
      nodes[opname].name = 'OUTPUT'
      output_counter += 1
    else:#after hardcoding the input and the outputs we move on to the rest of the gates and ethis loops sorts them out
      gatename = values[0]
      #if the node does not exist in out list we need to creat one
      if gatename not in nodes:
        nodes[gatename] = Node()
      gatetype = values[1]
      if gatetype == 'NOT': #since a not gate is not store in the NLDM as a NOT gate, this forces the change during the storage of the netlist from NOT to INV
        gatetype = 'INV'
      nodes[gatename].name = gatetype
      nodes[gatename].inputs.extend(values[2:len(values)]) #hardcoded to ignore the 1st 2 values and does not take into multinet output
      #the following loop appens all the inpurs of the gate
      for input_count in range(2,len(values)):
        if values[input_count] not in nodes:
          nodes[values[input_count]] = Node()
        nodes[values[input_count]].outputs.append(values[0])

      gate_counter += 1

  Netlist.close()

  return nodes

def read_NLDM(NLDM_name):
  #reads the NLDM file
  NLDM_Data = {}
  try:
    NLDM = open(NLDM_name, "r")
  except FileNotFoundError:
    print('\n\n\nAre you sure about the NLDM file name? please check it and retry\n\n')
    exit(0)
  delimiters = r"[(,)=\n\r_:\t;]"
  flag = False
  line = NLDM.readline()
  for line in NLDM:
    values = list(filter(None,re.split(delimiters,line))) #makes the sting into a list of strings and removes "falsy" values
    line=line.replace(" ", "") #removes spaces
    if line.startswith('#') or line == '\n':#ignores the commented lines
      continue
    if line.startswith('cell'):

      if values[1][-1].isdigit() == True:
        flag =1
        name = values[1][:len(values[1])-1]
      else:
        name = values[1]
      if name == 'BUF': #forces the name change in the NLDM file from BUF to BUFF this has been done done due to C7552.bench
        name = 'BUFF'
      NLDM_Data[name] = nldm_data() #creates new object as needed and the rest of the code stores the delay and the slew values and capacitance
      NLDM_Data[name].name = name
      if flag == 1:
        NLDM_Data[name].inputs = 2
        flag = 0
      for i in range(0,4):
        line = next(NLDM)
        while line == '\n':
          line = next(NLDM)
        line=line.replace(" ", "")
        value2 = list(filter(None,re.split(delimiters,line)))
        if value2[0] == 'capacitance':
          NLDM_Data[name].capacitance = value2[1]
          #print(NLDM_Data[name].capacitance)
        elif value2[0] == 'cell' and value2[1] == 'delay':
          delay_xlength = value2[3]
          delay_ylength = value2[4]
          line = next(NLDM)
          while line == '\n':
            line = next(NLDM)
          line=line.replace(" ", "")
          line=line.replace("\"", "")
          value2 = list(filter(None,re.split(delimiters,line)))
          #values2 = [float(val) for val in value2]
          #print(value2)
          for j in range(0,2):
            temp_val = [float(temp) for temp in value2[2:len(value2)]]
            NLDM_Data[name].delay_index_1.append(temp_val)
            line = next(NLDM)
            while line == '\n':
              line = next(NLDM)
            line=line.replace(" ", "")
            line=line.replace("\"", "")
            value2 = list(filter(None,re.split(delimiters,line)))
          for j in range(0,int(delay_xlength)):
            if value2[0] == 'values':
              NLDM_Data[name].delay_values.append([float(temp) for temp in value2[1:int(delay_xlength)+1]])
            else:
              NLDM_Data[name].delay_values.append([float(temp) for temp in value2[0:int(delay_xlength)]])
            line = next(NLDM)
            while line == '\n':
              line = next(NLDM)
            line=line.replace(" ", "")
            line=line.replace("\"", "")
            value2 = list(filter(None,re.split(delimiters,line)))
        elif value2[0] == 'output' and value2[1] == 'slew':
          slew_xlength = value2[3]
          slew_ylength = value2[4]
          line = next(NLDM)
          while line == '\n':
            line = next(NLDM)
          line=line.replace(" ", "")
          line=line.replace("\"", "")
          value2 = list(filter(None,re.split(delimiters,line)))
          for j in range(0,2):
            NLDM_Data[name].slew_index_1.append([float(temp) for temp in value2[2:len(value2)]])
            line = next(NLDM)
            while line == '\n':
              line = next(NLDM)
            line=line.replace(" ", "")
            line=line.replace("\"", "")
            value2 = list(filter(None,re.split(delimiters,line)))
          for j in range(0,int(slew_xlength)):
            if value2[0] == 'values':
              NLDM_Data[name].slew_values.append([float(temp) for temp in value2[1:int(slew_xlength)+1]])
            else:
              NLDM_Data[name].slew_values.append([float(temp) for temp in value2[0:int(slew_xlength)]])
            line = next(NLDM)
            while line == '\n':
              line = next(NLDM)
            line=line.replace(" ", "")
            line=line.replace("\"", "")
            value2 = list(filter(None,re.split(delimiters,line)))
  return(NLDM_Data)

def netlist_txt (nodes1):
  #this function stores the Netlist of that has been read in into a txt file
  nodes= nodes1
  f = open("ckt_details.txt", "w")

  primary_input_count = 0
  primary_output_count = 0
  gates ={}
  for node in nodes: #counts the number of every gate in the netlist
    if nodes[node].primary_out:
      primary_output_count += 1
    if nodes[node].primary_in:
      primary_input_count += 1
    if nodes[node].name not in ('INPUT', 'OUTPUT'):
      if nodes[node].name not in gates:
        gates[nodes[node].name] = 1
      else:
        gates[nodes[node].name] += 1
  f.writelines([f'{primary_input_count} primary inputs \n',f'{primary_output_count} primary outputs \n'])#this starts writing lines in to the txt file
  for gate in gates:
    f.writelines([f'{gates[gate]} {gate} gates\n'])
  #fanout list
  f.writelines(['\nFanout...\n'])#fanout section of the output is here
  for node in nodes: #iterates through all nodes
    #print(node)
    if len(nodes[node].outputs) == 0 or nodes[node].primary_in == True:
      continue
    out_list = nodes[node].name+'-'+node+':'
    output_nodes = nodes[node].outputs
    for i in range (0,len(output_nodes)-1): #loop to figure out the fanout of the current target
      if nodes[output_nodes[i]].primary_out:# and nodes[node].primary_out:
        out_list = out_list + 'OUTPUT' + '-' + output_nodes[i] + ','
      else:
        out_list = out_list + nodes[output_nodes[i]].name + '-' + output_nodes[i] + ','
    if nodes[output_nodes[len(output_nodes)-1]].primary_out and nodes[node].primary_out:
      out_list = out_list + 'OUTPUT' + '-' + output_nodes[len(output_nodes)-1]
    else:
      out_list = out_list + nodes[output_nodes[len(output_nodes)-1]].name + '-' + output_nodes[len(output_nodes)-1]
    f.writelines(out_list)
    f.write('\n')
  #Fanin list
  f.writelines(['\nFanin...\n'])#fanout section of the output is here
  for node in nodes:
    #print(nodes[node].inputs)
    if len(nodes[node].inputs) == 0 or nodes[node].primary_in == True:
      continue
    input_nodes = nodes[node].inputs
    #print(input_nodes)
    in_list = nodes[node].name+'-'+node+':'
    for i in range (0,len(input_nodes)-1):
      in_list = in_list + nodes[input_nodes[i]].name + '-' + input_nodes[i] + ','
    in_list = in_list + nodes[input_nodes[len(input_nodes)-1]].name + '-' + input_nodes[len(input_nodes)-1]
    f.writelines(in_list)
    f.write('\n')
  f.close()

def delay_txt (NLDM1):
    #this function stores the NLDM of that has been read in into a txt file
  NLDM= NLDM1
  f = open("delay_LUT.txt", "w")

  for gates in NLDM: #iterates over every gate type in the NLDM dictionary and store the delay values only
    outline = 'cell : ' + NLDM[gates].name + str(NLDM[gates].inputs) + NLDM[gates].etc
    #outline += '\n' + 'capacitance : ' + str(NLDM[gates].capacitance) + '\n'
    outline += '\n' + 'input slew : '
    for slew_val in NLDM[gates].delay_index_1[0]:
      outline += str(slew_val) + ','
    outline = outline[:-1]
    outline += ';\n' + 'load cap : '
    for cap_val in NLDM[gates].delay_index_1[1]:
      outline += str(cap_val) + ','
    outline = outline[:-1]
    outline += ';\n\n' + 'delays : \n'
    for row in range(0,len(NLDM[gates].delay_values)):
      for col in NLDM[gates].delay_values[row]:
        outline += str(col)+','
      outline = outline[:-1]
      outline += ';\n\n'
      f.write(outline)
      outline = ''
    f.write('\n')
  f.close()

def slew_txt (NLDM1):
  #iterates over every gate type in the NLDM dictionary and store the slew values only
  NLDM= dict(sorted(NLDM1.items()))
  f = open("slew_LUT.txt", "w")

  for gates in NLDM:
    outline = 'cell : ' + NLDM[gates].name + str(NLDM[gates].inputs) + NLDM[gates].etc
    outline += '\n' + 'input slew : '
    for slew_val in NLDM[gates].delay_index_1[0]:
      outline += str(slew_val) + ','
    outline = outline[:-1]
    outline += ';\n' + 'load cap : '
    for cap_val in NLDM[gates].delay_index_1[1]:
      outline += str(cap_val) + ','
    outline = outline[:-1]
    outline += ';\n\n' + 'slews : \n'
    for row in range(0,len(NLDM[gates].slew_values)):
      for col in NLDM[gates].slew_values[row]:
        outline += str(col)+','
      outline = outline[:-1]
      outline += ';\n\n'
      f.write(outline)
      outline = ''
    f.write('\n')
  f.close()

def cell_assignment(nodes,NLDM):
  #this funtion does the job of initializin the sizes of the class varialbles and also does a priliminary pass assign output of one gate to coorresponding input of another
  for node in nodes:
    if nodes[node].primary_in: #hard codes the values for primary input
      nodes[node].Tau_in.append(0.002)
      nodes[node].Tau_out = 0.002
      nodes[node].inp_arrival.append(0.000)
      nodes[node].outp_arrival.append(0.000)
      continue
    else:#assign the input and output lengths of the list in the class nodes
      name = nodes[node].name
      nodes[node].incap = float(NLDM[name].capacitance)
      len_in = len(nodes[node].inputs)
      nodes[node].Tau_in = [0]*len_in
      nodes[node].inp_arrival = [0]*len_in
    nodes[node].min_required_output_arrival = [-1]*len(nodes[node].inputs)
  for node in nodes: 
    Cload=0.0
    if nodes[node].primary_out: #assigns the output oad of the primary outputs as 4*inpput capacitance of inverter
      nodes[node].Cload = 4*float(NLDM['INV'].capacitance)
    else: #rest of the cloades come from their respective fanouts
      if len(nodes[node].outputs):
        for child in nodes[node].outputs:
          Cload += nodes[child].incap
      nodes[node].Cload = Cload
  for node in nodes: #loop to assign thge siges of the Tau in and input arrivals based on fan in
    if nodes[node].inputs and not nodes[node].primary_in:
      for i in range(len(nodes[node].inputs)):
        nodes[node].Tau_in[i] = nodes[nodes[node].inputs[i]].Tau_out
        nodes[node].inp_arrival[i] = nodes[nodes[node].inputs[i]].max_out_arrival

  return(nodes)

def node_delay(node,nldm,name):
  #this function calculates the delay through the entire ckt bu level by lvel traversal from inputs to outputs
  delay_list=[]#list that maintains the delays at the primary outputs
  for i in range(len(node.Tau_in)):
    flag = 0
    if node.Tau_in[i] > nldm.delay_index_1[0][-1] and node.Cload > nldm.delay_index_1[1][-1]: #setting the extrapolation values if the slew in and cload are larger than the possible values given
      c1 = nldm.delay_index_1[1][-2] #setting the extrapolation point from the bottom right corner of the tabel
      c2 = nldm.delay_index_1[1][-1]
      t2 = nldm.delay_index_1[0][-1]
      t1 = nldm.delay_index_1[0][-2]
      xindex = 0
      yindex = 0
    elif node.Tau_in[i] < nldm.delay_index_1[0][0] and node.Cload < nldm.delay_index_1[1][0]:#setting the extrapolation values if the slew in and cload are smaller than the possible values given
      c1 = nldm.delay_index_1[1][0]#setting the extrapolation point from the top left corner of the tabel
      c2 = nldm.delay_index_1[1][1]
      t2 = nldm.delay_index_1[0][1]
      t1 = nldm.delay_index_1[0][0]
      xindex = 2
      yindex = 2
    elif node.Tau_in[i] in nldm.delay_index_1[0] and node.Cload in nldm.delay_index_1[1]:# if exact match of the slew in and output capacitance then use them
      delay= nldm.delay_values[nldm.delay_index_1[0].index(node.Tau_in)][nldm.delay_index_1[1].index(node.Cload)]
      flag = 1
    else: #if the slew in and Cload vlaues fall within the possibility range but between 2 vales then we interpolate by using 1 vales above and 1 below
      xindex = 0
      yindex = 0
      while xindex < len(nldm.delay_index_1[0])-1:
        if node.Tau_in[i] < nldm.delay_index_1[0][xindex]:
          break;
        xindex+=1
      while yindex < len(nldm.delay_index_1[1])-1:
        if node.Cload < nldm.delay_index_1[1][yindex]:
          break;
        yindex+=1
    if flag == 0:
      c1 = nldm.delay_index_1[1][yindex-1]
      c2 = nldm.delay_index_1[1][yindex]
      t2 = nldm.delay_index_1[0][xindex]
      t1 = nldm.delay_index_1[0][xindex-1]
  
    delay11=nldm.delay_values[xindex-1][yindex-1]
    delay12=nldm.delay_values[xindex-1][yindex]
    delay21=nldm.delay_values[xindex][yindex-1]
    delay22=nldm.delay_values[xindex][yindex]

    #interpolation from pdf
    d1 = delay11*(c2-node.Cload)*(t2-node.Tau_in[i])
    d2 = delay12*(node.Cload-c1)*(t2-node.Tau_in[i])
    d3 = delay21*(c2-node.Cload)*(node.Tau_in[i]-t1)
    d4 = delay22*(node.Cload-c1)*(node.Tau_in[i]-t1)
    delay = (d1+d2+d3+d4)/((c2-c1)*(t2-t1)) #extrapolation formula

    if delay < 0: #if negative delay; since not possible we force it 0
      delay = 0
    if len(node.inputs)>2: #fanout of more than 2 then we need to adjust thedelay accordingly
      delay = delay * len(node.inputs)/2
    delay_list.append(delay)#delay for all inputs of the gate
  return(delay_list)

def node_slew(node,nldm):
  #this function calculates the slew for th gate only where the output arrival time is the max
  max_tau_in = node.Tau_in[node.max_out_arrival_index]
  if max_tau_in > nldm.slew_index_1[0][-1] and node.Cload > nldm.slew_index_1[1][-1]:#setting the extrapolation values if the slew in and cload are larger than the possible values given
    c1 = nldm.slew_index_1[1][-2]#setting the extrapolation point from the bottom right corner of the tabel
    c2 = nldm.slew_index_1[1][-1]
    t2 = nldm.slew_index_1[0][-1]
    t1 = nldm.slew_index_1[0][-2]
    xindex = 0
    yindex = 0
  elif max_tau_in < nldm.slew_index_1[0][0] and node.Cload < nldm.slew_index_1[1][0]:
    c1 = nldm.slew_index_1[1][0]
    c2 = nldm.slew_index_1[1][1]
    t2 = nldm.slew_index_1[0][1]
    t1 = nldm.slew_index_1[0][0]
    xindex = 2
    yindex = 2
  elif max_tau_in in nldm.slew_index_1[0] and node.Cload in nldm.slew_index_1[1]:#if exact match of the slew in and output capacitance then use them
    slew= nldm.slew_values[nldm.slew_index_1[0].index(node.Tau_in)][nldm.slew_index_1[1].index(node.Cload)]
    return(slew)
  else:#if the slew in and Cload vlaues fall within the possibility range but between 2 vales then we interpolate by using 1 vales above and 1 below
    xindex = 0
    yindex = 0
    while xindex < len(nldm.slew_index_1[0])-1:
      if max_tau_in < nldm.slew_index_1[0][xindex]:
        break;
      xindex+=1
    while yindex < len(nldm.slew_index_1[1])-1:
      if node.Cload < nldm.slew_index_1[1][yindex]:
        break;
      yindex+=1

    c1 = nldm.slew_index_1[1][yindex-1]
    c2 = nldm.slew_index_1[1][yindex]
    t2 = nldm.slew_index_1[0][xindex]
    t1 = nldm.slew_index_1[0][xindex-1]
  
  slew11=nldm.slew_values[xindex-1][yindex-1]
  slew12=nldm.slew_values[xindex-1][yindex]
  slew21=nldm.slew_values[xindex][yindex-1]
  slew22=nldm.slew_values[xindex][yindex]
  
  #interpolation from pdf
  d1 = slew11*(c2-node.Cload)*(t2-max_tau_in)
  d2 = slew12*(node.Cload-c1)*(t2-max_tau_in)
  d3 = slew21*(c2-node.Cload)*(max_tau_in-t1)
  d4 = slew22*(node.Cload-c1)*(max_tau_in-t1)
  slew = (d1+d2+d3+d4)/((c2-c1)*(t2-t1))#extrapolation formula

  if slew < 0.002: #if output slew less the slew at primary input; since not possible we force it input slew rate
    slew = 0.002
  if len(node.inputs)>2: 
    slew = slew * len(node.inputs)/2  
  return(slew)

def topo_forward(nodes,NLDM):
  #forward traversal to find the delay of the entire CKT
  q =[]#queue from which we maintain the order of the gates to traverse in
  s=set()#set of nodes that may possibly come next
  output_delay = [] #list of the delay's at the primary outputs
  for node in nodes:# loop to all nodes to find nodes whose inputs are primary input only and add them to the que first
    if nodes[node].inputs:
      if all(nodes[inputs].primary_in for inputs in nodes[node].inputs):
        if node not in q:#check to not alllow duplicates
          q.append(node)
  while q:
    node = q.pop(0) #remove each node that we have traversed to no redo the same node
    delay_list=node_delay(nodes[node],NLDM[nodes[node].name],node) #calls the delay calc function to get the delay values of the gate with multiple inputs
    nodes[node].outp_arrival=[0]*len(nodes[node].inp_arrival);#fixinf the size of the list to address element by element
    for i in range(len(nodes[node].inputs)):
      nodes[node].outp_arrival[i] = nodes[node].inp_arrival[i] + delay_list[i]
      if nodes[node].max_out_arrival<nodes[node].outp_arrival[i]:#condtion to only store the max delay through the gate and its index
        nodes[node].max_out_arrival = nodes[node].outp_arrival[i]
        nodes[node].max_out_arrival_index = i
    nodes[node].Tau_out = node_slew(nodes[node],NLDM[nodes[node].name]) #after delay of the gate is found we nee the slew out usin only the max delay possible
    for j in range(len(nodes[node].outputs)):#loop to go though the next level and add to the set
      child = nodes[node].outputs[j]
      location = nodes[child].inputs.index(node)
      nodes[child].Tau_in[location] = nodes[node].Tau_out
      nodes[child].inp_arrival[location] = nodes[node].max_out_arrival
      s.add(child)
    dummy_var=[] #temperory holder of values
    for element in s: #loop to check if the next gate has all it sinout known or not if yes add that to the q and remove from set
      flag = 0
      if nodes[element].inputs:
        for inp in nodes[element].inp_arrival:
          if inp <= 0.000:
            ip_node=nodes[element].inp_arrival.index(inp)
            if not nodes[nodes[element].inputs[ip_node]].primary_in:
              flag = 1
        if element not in q:
          if flag == 0:
            q.append(element)
            dummy_var.append(element)
    for dv in dummy_var:#loop to remove queued elemts from the set
      s.remove(dv)
    if nodes[node].primary_out:
      output_delay.append(nodes[node].outp_arrival)

  return(nodes,max(output_delay))#returns the max cirtcuit delay

def topo_reverse(nodes,ckt_delay):
  #reverse level by level traversel to calculate the slack
  q=[] #queue to store the current level of iteratble nodes
  s=set() 
  for node in nodes:#loop to find the output nodes and add to the queue
    if nodes[node].primary_out:
      nodes[node].required_output_arrival = [ckt_delay]#fixes the output reuird time
      q.append(node)
    else:
      nodes[node].required_output_arrival = [ckt_delay]*len(nodes[node].outputs)#fixes the length of the output arrivalrequired list
  while q:#reverse traversal loop
    node = q.pop(0)
    
    if nodes[node].inputs :# the the current node has a input list with a positive length
      len_inputs = len(nodes[node].inputs) #finding the lebngth of the inputs list
      nodes[node].slack = [0]*len_inputs
      nodes[node].required_input_arrival = [0]*len_inputs#fixing the sizes for direct access
      nodes[node].min_required_output_arrival = min(nodes[node].required_output_arrival)
       
      for i in range(len_inputs):#loop to run through the inputs of the current node and assign aarrival time
        gate_delay=nodes[node].outp_arrival[i] - nodes[node].inp_arrival[i]
        nodes[node].required_input_arrival = nodes[node].min_required_output_arrival - (gate_delay)#individual inpust arrival time calculation
        nodes[node].slack[i] = nodes[node].required_input_arrival - nodes[node].inp_arrival[i] #slack calculation 
        parent = nodes[node].inputs[i] #iterating though the input to assign the outputs of those inputs the calculated arrival time
        placement = nodes[parent].outputs.index(node)
        if nodes[parent].required_output_arrival[placement] >= nodes[node].required_input_arrival:
          nodes[parent].required_output_arrival[placement] = nodes[node].required_input_arrival
        s.add(parent)
      nodes[node].min_slack = min(nodes[node].slack)     #always setting the min slack for later easy access 
      dummy_var=[]
      for element in s:#loop to takes elements from the set s into queue q
        flag = 0
        if nodes[element].min_required_output_arrival:
          for outarr in nodes[element].required_output_arrival:
            if outarr == ckt_delay:
              flag = 1
        if element not in q:
          if flag == 0:
            q.append(element)
            dummy_var.append(element)
      for dv in dummy_var:#emptying s for the enqueued values
        s.remove(dv)

    if nodes[node].primary_in:# the node is a primary input the special handling as it does not have input nodes
      nodes[node].required_input_arrival = min(nodes[node].required_output_arrival)
      nodes[node].slack.append(nodes[node].required_input_arrival - nodes[node].inp_arrival[0])
      nodes[node].min_slack = min(nodes[node].slack)
  return(nodes) 
    #print(q)

def critical_path(nodes,ckt_delay):
  #calculates the critical path of the circuit based on the slack values, prints only 1 of them
  crit_path=[]
  q = []
  for node in nodes: #loop to take the output with the highest delay as the initial node
    if nodes[node].primary_out and nodes[node].max_out_arrival == ckt_delay:
      crit_path.append(node)
      q.append(node)
      break
  while q:#loop to go though inputs of each node in q and see which one of them has lesser slack and addint it to our critical path
    node = q.pop(0)
    s=[]
    n=[]
    if nodes[node].inputs:
      for i in range(len(nodes[node].inputs)):#loop to add all the connect nodes to the input to a set s
        s.append(nodes[nodes[node].inputs[i]].min_slack)
        n.append(nodes[node].inputs[i])
      crit_path.append(n[s.index(min(s))])
      q.append(crit_path[-1])
  return(crit_path)

def slack_calc(nodes,NLDM):
  #function that call all the needed function for calculating the slack
  nodes=cell_assignment(nodes,NLDM) #initializes the nodes and the length of lists
  nodes,max_ckt_delay=topo_forward(nodes,NLDM)#calculates the delays of every gate
  delay_list=[]#list of primary output delays
  for node in nodes:
    if nodes[node].primary_out:
      delay_list.append(nodes[node].max_out_arrival)
  ckt_delay = max(delay_list)#max of all the primary out delay will be the circuit delay
  nodes = topo_reverse(nodes,ckt_delay*1.1)#function that calculates the slack f the circuit and 1.1 is the multiplies as request for required time
  crit_path = critical_path(nodes,ckt_delay)#function that fins the critical path of the sircuit based on slack
  return(crit_path,ckt_delay)

def critical_path_txt(nodes,crit_path,ckt_delay):
  #funtion that store the critical path values in a txt file
  f = open("ckt_traversal.txt", "w")#opens the txt file, if not there then creates one in the run directory

  f.writelines(f'Circuit delay: {ckt_delay*1000:0.6g} ps\n\n')#formato to be written where g says genral formal upto 6 digits
  f.writelines('Gate slacks:\n')
  for node in nodes:#loop for the input and the outputs to be written
    if nodes[node].primary_in:
      f.writelines(f'INPUT-{node}: {nodes[node].min_slack*1000:0.6g} ps\n')
    elif nodes[node].primary_out:
      f.writelines(f'OUTPUT-{node}: {nodes[node].min_slack*1000:0.6g} ps\n')
  for node in nodes:#loop that ignores primary input and prints the rest of the values
    if nodes[node].primary_in:
      continue
    else:
      f.writelines(f'{nodes[node].name}-{node}: {nodes[node].min_slack*1000:0.6g} ps\n')
  f.write('\nCritical path:\n\n')

  for node in crit_path[::-1]:#loop to printhe critical path list in the reverse order as it was initially stores from output to input
    f.writelines(f'{nodes[node].name}-{node},')
  f.writelines(f'OUTPUT-{crit_path[0]}')

def __main__():
  #main functionhods the argument parse and is the big boss function to rule over all other function calling the rest of the function based on the arguments
  start_time = time.time()#this is just doen to show therun time of the program
  NLDM = {} #initialising the variables to none
  nodes = {}
  #parsing through the terminal arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('--read_ckt', action='store',help = 'argument for the netlist file to be read', required=False)
  parser.add_argument('--read_nldm', action='store',help = 'argument for the netlist file to be read', required=False)
  parser.add_argument('--delays', action='store_true',help = 'argument for the NLDM file to be read for Delays', required=False)
  parser.add_argument('--slews', action='store_true',help = 'argument for the NLDM file to be read for Slews', required=False)
  parser.add_argument('--crit_path', action='store_false',help = 'argument to stop the critical path file from being generated', required=False)
  args = parser.parse_args()
  if args.read_ckt :
    nodes=read_ckt(args.read_ckt)
    netlist_txt(nodes)#reads the netlist and storesit in a ckt_details file
    print ('\nThe Netlist has been read and stored to a file ckt_details.txt\n')
  if args.read_nldm:
    NLDM = read_NLDM(args.read_nldm)#reads the nldm and does nothing else
    print ('\nThe NLDM has been read\n')
  if args.delays:
    if NLDM:
      delay_txt(NLDM)#prints the delay values from the nldm file and nldm file need to be read before we can run this command
      print ('\nThe NLDM has been read and stored to a file named delay_LUT.txt\n')
    else:
      print ('\nPlease for Heavensake read the NLDM file first; for the delay using --read_nldm argument\n')
      exit(0)
  if args.slews:
    if NLDM:
      slew_txt(NLDM)#prints the slew values from the nldm file and nldm file need to be read before we can run this command
      print ('\nThe NLDM has been read and stored to a file named slew_LUT.txt\n')
    else:
      print ('\nPlease for Heavensake read the NLDM file first; for the delay using --read_nldm argument\n')
      exit(0)
  if args.crit_path: #prints the critical path values from the netlist and nldm file, both of which have to read in first
    crit_path,ckt_delay = slack_calc(nodes,NLDM)
    critical_path_txt(nodes,crit_path,ckt_delay)
    print ('\nThe Critical path has been calculated and stored to a file named ckt_traversal.txt\n')

  print("\n\n---The program ran in %s seconds ---\n\n" % (time.time() - start_time))

__main__()#since this is python and no main fuction is needed it wont rn by itself so we have to call the main function; the boss also has big boss.

