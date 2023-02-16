import time 
from scalesim.scale_sim import scalesim
import scalesim.global_vars as global_vars


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
	memory_accesses = analyze_memory_writes()
	print()

def main():
	# no plan to ever really run this (?)
	dummy_config_file = "/Users/d/Desktop/SS_adaptation.nosync/dummy/scale.cfg"
	dummy_NN_file = "/Users/d/Desktop/SS_adaptation.nosync/dummy/basicNN.csv"
	gemm_input = 0
	logpath = "/Users/d/Desktop/SS_adaptation.nosync/logs"
	hardware_arch_overwrite = "hasdfas"

	s = scalesim(save_disk_space=True, verbose=1,
				 config=dummy_config_file,
				 topology=dummy_NN_file,
				 input_type_gemm=gemm_input, hardware_arch_overwrite = hardware_arch_overwrite)
	startExecutionTime = time.time()
	#logpath = "../test_runs"
	s.run_scale(top_path=logpath)
	endExecutionTime = time.time()
	print("\nTOTAL SS EXECUTION TIME:", round((endExecutionTime - startExecutionTime), 3))
	print()
	

if __name__ == "__main__":
	main()




