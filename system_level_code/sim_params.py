base_directory = "/Users/d/Desktop/onn_arch_system_design/"
SS_inOut_file_path = base_directory + "results/" + "untracked" + "/"
config_file_path  = base_directory + "configs/scale.cfg"
base_directory_system_code = base_directory + "system_level_code/"

NN_file_name = "test"
NN_file_path_local = "topologies/ONN/"
NN_file_path_name = base_directory + NN_file_path_local + NN_file_name + ".csv"
NN_file_path_local = NN_file_path_local.replace("/", "_") 


NN_file_path_local_name = NN_file_path_local + NN_file_name
SS_results_file_base_folder = SS_inOut_file_path + NN_file_path_local_name

SS_results_file_path_name = SS_inOut_file_path + NN_file_path_local_name + "/" + NN_file_path_local_name + "__SS_results.csv"
chip_specs_file_path_name = SS_inOut_file_path + NN_file_path_local_name + "/" + NN_file_path_local_name + "__SS_results_chip_specs.csv"


make_plots = 0
run_system_specs = 1
make_plots = run_system_specs and make_plots
SS_print_verbose = 0




batch_size_options = [8, 32, 128]
