import time 
from scalesim.scale_sim import scalesim


def run_scale_sim(hardware_arch, NN_layers):
	print("\nBeginning ScaleSim Execution")
	dummy_config_file = "/Users/d/Desktop/SS_adaptation.nosync/dummy/scale.cfg"
	dummy_NN_file = "/Users/d/Desktop/SS_adaptation.nosync/dummy/basicNN.csv"
	gemm_input = 0
	logpath = "/Users/d/Desktop/SS_adaptation.nosync/logs"

	s = scalesim(save_disk_space=True, verbose=1,
				 config=dummy_config_file,
				 topology=dummy_NN_file,
				 input_type_gemm=gemm_input, hardware_arch_overwrite = hardware_arch, NN_layers_overwrite = NN_layers)


	startExecutionTime = time.time()
	s.run_scale(top_path=logpath)
	endExecutionTime = time.time()
	print("TOTAL SS EXECUTION TIME:", round((endExecutionTime - startExecutionTime), 3))
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




