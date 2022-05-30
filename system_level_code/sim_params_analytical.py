make_plots = 0
run_system_specs = 1
make_plots = run_system_specs and make_plots

base_directory = "/Users/d/Desktop/onn_arch_system_design/"
results_file_path = base_directory + "results/" + "analytical_standalone" + "/"
NN_file_name = "test"
results_file_base_folder = results_file_path + NN_file_name
sim_results_file_path_name = results_file_base_folder + "/" + NN_file_name + "__model_results.csv"
chip_specs_file_path_name = results_file_base_folder + "/" + NN_file_name + "__model_results_chip_specs.csv"


SRAM_input_size_options  = [64000]
SRAM_filter_size_options = [64000]
SRAM_output_size_options = [64000]

batch_size_options_overall = [1, 8, 128, 16, 32]
array_size_options_overall = [[8, 8], [16, 16], [32, 32], [64, 64], [128, 128]]
accumulator_elements_options = [5000]

batch_size_options_index = [0]
array_size_options_index = [0]

batch_size_options = [batch_size_options_overall[x] for x in batch_size_options_index]
array_size_options = [array_size_options_overall[x] for x in array_size_options_index]

symbol_rate_options = [1, 5, 10]


input_height  = [10]#, 50]
input_width   = [10]#, 50] 
filter_height = [3]#, 7]
filter_width  = [3]#, 7]
channels = [2]#, 10]
num_filter = [10]#, 5]
strides = [1]#, 1]

if (1):
     input_height  = [10, 5]
     input_width   = [10, 5] 
     filter_height = [3, 4]
     filter_width  = [3, 4]
     channels = [2, 1]
     num_filter = [10, 3]
     strides = [1, 1]


num_layers = len(input_height) 
all_layers = []
for layer in range(num_layers):
     layer_dict = {"Input Height" : input_height[layer], "Input Width" : input_width[layer], "Filter Height" : filter_height[layer], "Filter Width": filter_width[layer], \
          "Channels" : channels[layer], "Num Filter" : num_filter[layer], "Strides" : strides[layer]}
     all_layers.append(layer_dict)


x = 1


for ind in range(len(channels) - 1):
     if (num_filter[ind] != channels[ind + 1]):
          print("\nNote that this is not a valid NN, the number of filters in layer ", str(ind), " is different from the number of channels in layer ", str(ind + 1), sep = "")






x = 1


