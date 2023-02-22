import time 
from scalesim.scale_sim import scalesim
import scalesim.global_vars as global_vars
import numpy as np
import pandas as pd

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
		SRAM_cycles[layer] = [program_instance_count, program_clock_cycle_count, compute_instance_count, compute_clock_cycle_count]

	
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

def analyze_outputs():
	input_demand_mat = global_vars.ifmap_demand_mat
	filter_demand_mat = global_vars.filter_demand_mat
	output_demand_mat = global_vars.ofmap_demand_mat
	input_demand_mat_non_skew = global_vars.ifmap_demand_mat_non_skew

	memory_accesses = analyze_memory_writes()
	totals = memory_accesses
	runspecs_names = ["SRAM Input Reads", "SRAM Filter Reads", "SRAM Output Writes", \
		"DRAM Input Reads", "DRAM Filter Reads", "DRAM Output Writes",\
				"Total Programming Instances", "Total Programming Clock Cycles", \
				"Total Compute Instances", "Total Compute Clock Cycles Analog", "Total Compute Clock Cycles Digital"]

	SRAM_accesses_layer = analyze_all_SRAM_traces_together(filter_demand_mat, input_demand_mat, output_demand_mat)
	SRAM_accesses_total = np.sum(SRAM_accesses_layer, axis = 0)
	analog_compute_counts_layer = count_SRAM_trace_clock_cycles(input_demand_mat_non_skew)
	analog_compute_counts_total = sum(analog_compute_counts_layer)
	totals.extend([SRAM_accesses_total[0], SRAM_accesses_total[1], SRAM_accesses_total[2], analog_compute_counts_total, SRAM_accesses_total[3]])

	return(pd.DataFrame(totals, runspecs_names))



def run_scale_sim(hardware_arch, NN_layers):
	print("\nBeginning ScaleSim Execution")
	dummy_config_file = "/Users/d/Desktop/cnn_on_array.nosync/SS_adaptation/dummy/scale.cfg"
	dummy_NN_file = "/Users/d/Desktop/cnn_on_array.nosync/SS_adaptation/dummy/basicNN.csv"
	gemm_input = 0
	logpath = "/Users/d/Desktop/cnn_on_array.nosync/SS_adaptation/logs"
	global_vars.initialize()

	s = scalesim(save_disk_space=False, verbose=1,
				 config=dummy_config_file,
				 topology=dummy_NN_file,
				 input_type_gemm=gemm_input, hardware_arch_overwrite = hardware_arch, NN_layers_overwrite = NN_layers)


	startExecutionTime = time.time()
	s.run_scale(top_path=logpath)
	endExecutionTime = time.time()

	#print("TOTAL SS EXECUTION TIME:", round((endExecutionTime - startExecutionTime), 3))
	SS_results = analyze_outputs()
	endPostProcessTime = time.time()
	SS_execution_time = round((endExecutionTime - startExecutionTime) / 60, 3)
	SS_post_process_time = round((endPostProcessTime - endExecutionTime) / 60, 3)
	SS_results.loc[" "] = " "
	SS_results.loc["Simulation Run Time [min]"] = SS_execution_time
	SS_results.loc["Simulation Post Process Time [min]"] = SS_post_process_time
	return(SS_results)

	





