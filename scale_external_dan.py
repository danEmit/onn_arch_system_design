import time 
from scalesim.scale_sim import scalesim
import scalesim.global_vars as global_vars
import numpy as np

def analyze_SRAM_trace(SRAM_demand_mat):
	numLayers = len(SRAM_demand_mat)
	SRAM_cycles = [0] * numLayers
	inactive = -1
	for layer in range(numLayers):
		clock_cycle = 0
		SRAM_demand_mat_singleLayer = SRAM_demand_mat[layer]

		num_access_cols = SRAM_demand_mat_singleLayer.shape[1]
		clock_cycle_status = np.sum(SRAM_demand_mat_singleLayer == inactive, axis = 1) != num_access_cols
		num_active_clock_cycle = np.sum(clock_cycle_status)
		num_clock_cycles = SRAM_demand_mat_singleLayer.shape[0]

		active_instances = 0
		active_clock_cycles = np.sum(clock_cycle_status)
		active_ind_words = np.sum(SRAM_demand_mat_singleLayer != inactive)

		if clock_cycle_status[0]:
			active_instances += 1
		for clock_cycle in range(num_clock_cycles - 1):
			if (not clock_cycle_status[clock_cycle] and clock_cycle_status[clock_cycle + 1]):
				active_instances += 1

		SRAM_cycles[layer] = [active_instances, active_clock_cycles, active_ind_words]

	return(SRAM_cycles)

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

def analyze_SRAM_usage():
	input_demand_mat = global_vars.ifmap_demand_mat
	filter_demand_mat = global_vars.filter_demand_mat
	output_demand_mat = global_vars.ofmap_demand_mat
	input_demand_mat_non_skew = global_vars.ifmap_demand_mat_non_skew
	## i know the below makes no sense but it does, it works 
	combined_input_output_demand_mat = [np.logical_and(input_demand_mat[layer] == -1, output_demand_mat[layer] == -1) * -2  + 1  for layer in range(len(input_demand_mat))]

	program_counts = analyze_SRAM_trace(filter_demand_mat)
	analog_compute_counts = analyze_SRAM_trace(input_demand_mat_non_skew)
	digital_compute_counts = analyze_SRAM_trace(combined_input_output_demand_mat)

	memory_accesses = analyze_memory_writes()


def run_scale_sim(hardware_arch, NN_layers):
	print("\nBeginning ScaleSim Execution")
	dummy_config_file = "/Users/d/Desktop/cnn_on_array.nosync/SS_adaptation/dummy/scale.cfg"
	dummy_NN_file = "/Users/d/Desktop/cnn_on_array.nosync/SS_adaptation/dummy/basicNN.csv"
	gemm_input = 0
	logpath = "/Users/d/Desktop/cnn_on_array.nosync/SS_adaptation/logs"
	global_vars.initialize()

	s = scalesim(save_disk_space=True, verbose=1,
				 config=dummy_config_file,
				 topology=dummy_NN_file,
				 input_type_gemm=gemm_input, hardware_arch_overwrite = hardware_arch, NN_layers_overwrite = NN_layers)


	startExecutionTime = time.time()
	s.run_scale(top_path=logpath)
	endExecutionTime = time.time()
	print("TOTAL SS EXECUTION TIME:", round((endExecutionTime - startExecutionTime), 3))
	analyze_SRAM_usage()
	print()



