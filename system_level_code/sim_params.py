base_directory = "/Users/D/Desktop/research/onn_arch_system_design/"
SS_inOut_file_path = base_directory + "results/" + "untracked" + "/"
config_file_path  = base_directory + "configs/scale.cfg"


NN_file_name = "test"
NN_file_path_local = "topologies/ONN/"
NN_file_path_local = NN_file_path_local.replace("/", "_") 
NN_file_path_local_name = NN_file_path_local + NN_file_name

SS_results_file_path_name = SS_inOut_file_path + NN_file_path_local_name + "/" + NN_file_path_local_name + "__SS_results.csv"
chip_specs_file_path_name = SS_inOut_file_path + NN_file_path_local_name + "/" + NN_file_path_local_name + "__SS_results_chip_specs.csv"


make_plots = 0
run_system_specs = 1
make_plots = run_system_specs and make_plots
SS_print_verbose = 0
