The files contained in the submission folder are:

1. main_sta.py

This is a python code which needs to be implemented to perform parsing of the data and the Static Timing Analysis of a circuit using the Netlist and NLDM.lib files provided. This code will generate ckt_details.txt, delay_LUT.txt or slew_LUT.txt files as an output, depending on the input command provided. It will also generate a ckt_traversal.txt file, which mentions the total delay of the circuit, slack values for each gate and the critical path in the circuit.
All the files will be generated in the same directory.

Commands to run the code:
	a. python3.7 main_sta.py --read_ckt <.bench_file>
		Command to read data from the netlist and store it in ckt_details.txt file. <.bench_file> must contain the path to the Netlist file.

	b. python3.7 main_sta.py –-read_nldm <sample_NLDM.lib>
		Command to read data from the NLDM file. <sample_NLDM.lib> must contain the path to the NLDM file.

	c. python3.7 main_sta.py --delays <sample_NLDM.lib>
		Command to read delay data from the NLDM file and store it in delay_LUT.txt file. <sample_NLDM.lib> must contain the path to the NLDM file.

	d. python3.7 main_sta.py --slews <sample_NLDM.lib>
		Command to read slews data from the NLDM file and store it in slew_LUT.txt file. <sample_NLDM.lib> must contain the path to the NLDM file.

	e. python3.7 main_sta.py –-crit_path 
		This command automatically generates a critical path and stores it in ckt_traversal.txt file. This command is run by default and needs to be added only to stop the 			generation of the critical path.

2. README.txt

This is a readme file for the guidance for implementation of the program.

3. requirements.txt

This is a requirements file that mentions the dependancies needed to implement the code.