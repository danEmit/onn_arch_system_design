import platform

distributed_computing = 0

make_plots = 0
run_system_specs = 1
make_plots = run_system_specs and make_plots
SS_print_verbose = 0


base_directory = "/Users/d/Desktop/onn_arch_system_design/"
SS_inOut_file_path = base_directory + "results/" + "untracked" + "/"
config_file_path  = base_directory + "configs/scale.cfg"

NN_file_name = "test"
NN_file_path_local = "topologies/ONN/"
NN_file_path_name = base_directory + NN_file_path_local + NN_file_name + ".csv"
NN_file_path_local = NN_file_path_local.replace("/", "_") 


NN_file_path_local_name = NN_file_path_local + NN_file_name
SS_results_file_base_folder = SS_inOut_file_path + NN_file_path_local_name



SS_results_file_path_name = SS_inOut_file_path + NN_file_path_local_name + "/" + NN_file_path_local_name + "__SS_results.csv"
chip_specs_file_path_name = SS_inOut_file_path + NN_file_path_local_name + "/" + NN_file_path_local_name + "__SS_results_chip_specs.csv"


SRAM_input_size  = 64000
SRAM_filter_size = 64000
SRAM_output_size = 64000
DRAM_mode = 0

batch_size_options_overall = [1, 8, 128, 16, 32]
array_size_options_overall = [[8, 8], [16, 16], [32, 32], [64, 64], [128, 128]]


symbol_rate_options = [1, 5, 10]

batch_size_options_index = []
array_size_options_index = []

if distributed_computing:
    computer_name = platform.node()
    computer_name = computer_name[0:5]
    SS_results_file_path_name_write = SS_inOut_file_path + NN_file_path_local_name + "/" + NN_file_path_local_name + "__" + computer_name + "__SS_results.csv"
    run_system_specs = 0
    make_plots = 0

    batch_size_options_index = [0, 3]
    array_size_options_index = [0, 3, 2]

else:
    batch_size_options_index = [x for x in range(len(batch_size_options_overall))]
    array_size_options_index = [x for x in range(len(array_size_options_overall))]


batch_size_options = [batch_size_options_overall[x] for x in batch_size_options_index]
array_size_options = [array_size_options_overall[x] for x in array_size_options_index]


x = 1


