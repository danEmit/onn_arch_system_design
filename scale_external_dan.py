import time 
from scalesim.scale_sim import scalesim
import scalesim.global_vars as global_vars
import numpy as np
import pandas as pd
import os


text_output = ""

def add_to_text_output(string_output):
		print(string_output)
		global text_output
		text_output += "\n" + string_output

def count_SRAM_trace_clock_cycles(SRAM_demand_mat):
	numLayers = len(SRAM_demand_mat)
	SRAM_cycles = [0] * numLayers
	inactive = -1
	for layer in range(numLayers):
		clock_cycle = 0
		SRAM_demand_mat_singleLayer = SRAM_demand_mat[layer]

		num_access_cols = SRAM_demand_mat_singleLayer.shape[1]
		clock_cycle_status = np.sum(SRAM_demand_mat_singleLayer == inactive, axis = 1) != num_access_cols
		num_active_clock_cycle = np.sum(clock_cycle_status)

		SRAM_cycles[layer] = num_active_clock_cycle
	
	return(SRAM_cycles)

def analyze_all_SRAM_traces_together(filter_SRAM_demand, input_SRAM_demand, output_SRAM_demand):
	numLayers = len(filter_SRAM_demand)
	SRAM_cycles = [0] * numLayers
	inactive = -1
	for layer in range(numLayers):
		filter_SRAM_status = np.sum(filter_SRAM_demand[layer] == inactive, axis = 1) != filter_SRAM_demand[layer].shape[1]
		input_SRAM_status = np.sum(input_SRAM_demand[layer] == inactive, axis = 1) != input_SRAM_demand[layer].shape[1]
		output_SRAM_status = np.sum(output_SRAM_demand[layer] == inactive, axis = 1) != output_SRAM_demand[layer].shape[1]
		num_clock_cycles = len(filter_SRAM_status)

		compute_clock_cycle_count = 0
		program_clock_cycle_count = 0 
		compute_instance_count = 0
		program_instance_count = 0 

		mode = "nothing"
		for clock_cycle in range(num_clock_cycles):
			if mode == "nothing":
				if filter_SRAM_status[clock_cycle]:
					mode = "program"
					program_instance_count += 1
					program_clock_cycle_count += 1
			elif mode == "program": ## note that there is some chance here that the new 
				#clock cycle is the (first and) last compute cycle 
				if output_SRAM_status[clock_cycle]:
					mode = "compute_end"
					compute_instance_count += 1
					compute_clock_cycle_count += 1
				elif input_SRAM_status[clock_cycle]:
					mode = "compute_start"
					compute_instance_count += 1
					compute_clock_cycle_count += 1
				else:
					program_clock_cycle_count += 1
			elif mode == "compute_start":
				compute_clock_cycle_count += 1
				if output_SRAM_status[clock_cycle]:
					mode = "compute_end"
			elif mode == "compute_end":
				if output_SRAM_status[clock_cycle]:
					compute_clock_cycle_count += 1
				elif filter_SRAM_status[clock_cycle]:
					mode = "program"
					program_instance_count += 1
					program_clock_cycle_count += 1
				else:
					mode = "nothing"


		program_clock_cycle_count_alternate = np.sum(filter_SRAM_status)
		if (program_clock_cycle_count_alternate != program_clock_cycle_count):
			print("ERROR, different methods of calculating program clock cycle count give different results")
		if (program_instance_count != compute_instance_count):
			print("ERROR, program instance count not equal to compute instance count")
		
		SRAM_cycles[layer] = [program_instance_count, program_clock_cycle_count, compute_clock_cycle_count]

	SRAM_cycles = np.array(SRAM_cycles)
	return(np.array(SRAM_cycles))


def analyze_memory_writes():
	# here are some magic numbers. they are important!
	SRAM_IFMAP_READS = 2;  SRAM_FILTER_READS = 5;  SRAM_OFMAP_WRITES = 8
	DRAM_IFMAP_READS = 11; DRAM_FILTER_READS = 14; DRAM_OFMAP_WRITES = 17

	sram_ifmap_reads = 0; sram_filter_reads = 0; sram_ofmap_writes = 0
	dram_ifmap_reads = 0; dram_filter_reads = 0; dram_ofmap_writes = 0

	for index, row in enumerate(global_vars.memoryAccess):
		sram_ifmap_reads  += row[SRAM_IFMAP_READS]
		sram_filter_reads += row[SRAM_FILTER_READS]
		sram_ofmap_writes += row[SRAM_OFMAP_WRITES]

		dram_ifmap_reads  += row[DRAM_IFMAP_READS] 
		dram_filter_reads += row[DRAM_FILTER_READS]
		dram_ofmap_writes += row[DRAM_OFMAP_WRITES]

	return([sram_ifmap_reads, sram_filter_reads, sram_ofmap_writes, dram_ifmap_reads, dram_filter_reads, dram_ofmap_writes])

def analyze_outputs(compute_type):
	input_demand_mat = global_vars.ifmap_demand_mat
	filter_demand_mat = global_vars.filter_demand_mat
	output_demand_mat = global_vars.ofmap_demand_mat
	input_demand_mat_non_skew = global_vars.ifmap_demand_mat_non_skew


	memory_accesses = analyze_memory_writes()
	analog_compute_counts_layer = count_SRAM_trace_clock_cycles(input_demand_mat_non_skew)
	analog_compute_counts_total = sum(analog_compute_counts_layer)

	if compute_type == "digital":
		totals = memory_accesses
		runspecs_names = ["SRAM Input Reads", "SRAM Filter Reads", "SRAM Output Writes", \
			"DRAM Input Reads", "DRAM Filter Reads", "DRAM Output Writes",\
					"Total Program/Compute Instances", "Total Programming Clock Cycles", \
					"Total Compute Clock Cycles Analog", "Total Compute Clock Cycles Digital"]

		SRAM_accesses_layer = analyze_all_SRAM_traces_together(filter_demand_mat, input_demand_mat, output_demand_mat)
		SRAM_accesses_total = np.sum(SRAM_accesses_layer, axis = 0)
		totals.extend([SRAM_accesses_total[0], SRAM_accesses_total[1], analog_compute_counts_total, SRAM_accesses_total[2]])
	
	else:
		runspecs_names = ["DRAM Input Reads", "Total Compute Clock Cycles Analog"]
		totals = [memory_accesses[3], analog_compute_counts_total]

	return(pd.DataFrame(totals, runspecs_names))



def run_scale_sim(hardware_arch, NN_layers, compute_type):
	#print("\nBeginning ScaleSim Execution")
	dummy_config_file = "../SS_adaptation/dummy/scale.cfg"
	dummy_NN_file = "../SS_adaptation/dummy/basicNN.csv"
	gemm_input = 1
	logpath = "../SS_adaptation/logs"
	global_vars.initialize()
	global text_output
	text_output = ""
	#add_to_text_output("SCALE-Sim will be doing compute type: " + compute_type)

	s = scalesim(save_disk_space=False, verbose=0,
				 config=dummy_config_file,
				 topology=dummy_NN_file,
				 input_type_gemm=gemm_input, hardware_arch_overwrite = hardware_arch, 
				 NN_layers_overwrite = NN_layers, compute_type = compute_type)

	startExecutionTime = time.time()
	s.run_scale(top_path=logpath)
	endExecutionTime = time.time()

	#print("TOTAL SS EXECUTION TIME:", round((endExecutionTime - startExecutionTime), 3))
	SS_results = analyze_outputs(compute_type)
	endPostProcessTime = time.time()
	SS_execution_time = round((endExecutionTime - startExecutionTime) / 60, 5)
	SS_post_process_time = round((endPostProcessTime - endExecutionTime) / 60, 5)
	SS_results.loc[" "] = " "
	SS_results.loc["Simulation Run Time [min]"] = SS_execution_time
	SS_results.loc["Simulation Post Process Time [min]"] = SS_post_process_time
	return(SS_results, text_output)



def setHardware():
	names = ["Systolic Array Rows", "Systolic Array Cols", "SRAM Input Size", "SRAM Filter Size", "SRAM Output Size", "Batch Size"]
	arrayRows = 5
	arrayCols = 5
	SRAMInputSize = 1000
	SRAMFilterSize = 1000
	SRAMOutputSize = 1000
	batchSize = 1

	hardware = pd.DataFrame([arrayRows, arrayCols, SRAMInputSize, SRAMFilterSize, SRAMOutputSize, batchSize], names)
	hardware = hardware.squeeze()
	return(hardware)

def setNN():
	names = ["Input Rows", "Input Columns", "Filter Rows", "Filter Columns", "Channels", "Num Filter", "X Stride", "Y Stride"]
	inputRows = [5]
	inputCols = [5]
	filterRows = [3]
	filterCols = [3]
	channels = [1]
	numFilter = [6]
	xStride = [1]
	yStride = [1]

	NNLayersAll = []

	for i in range(len(inputRows)):
		NNLayer = pd.DataFrame([inputRows[i], inputCols[i], filterRows[i], filterCols[i], channels[i], numFilter[i], xStride[i], yStride[i]], names)
		NNLayersAll.append(NNLayer.squeeze())
	return(NNLayersAll)

def main():
	NNLayers = setNN()
	hardwareArch = setHardware()

	SSResults = run_scale_sim(hardwareArch, NNLayers)
	#SSResults = SSResults.loc[runspecs_names]
	print(SSResults)

if __name__ == "__main__":
    #os.chdir("/Users/d/Desktop/cnn_on_array.nosync/SS_adaptation/")

    main()

