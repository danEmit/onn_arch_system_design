import csv
import numpy as np

mega = 10 ** 6

make_plots = 1
run_system_specs = 1
make_plots = run_system_specs and make_plots

base_directory = "/Users/d/Desktop/onn_arch_system_design/"
results_file_path = base_directory + "results/" + "analytical_standalone" + "/"
NN_file_name = "Resnet50"
NN_file_folder = "topologies/ONN/"
NN_file_folder_mod = NN_file_folder.replace("/", "_") 
results_file_base_folder = results_file_path + NN_file_folder_mod + NN_file_name + "/"
sim_results_file_path_name = results_file_base_folder + NN_file_name + "__hardware_runspecs_info.csv"
chip_specs_file_path_name = results_file_base_folder + NN_file_name + "__chip_specs.csv"
detailed_results_folder = "layer_detail/"
detailed_results_folder_complete = results_file_base_folder + detailed_results_folder
plots_folder = "plots/"
plots_folder_complete = results_file_base_folder + plots_folder

all_layers = []
if (0):
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
          
     for ind in range(len(channels) - 1):
          if (num_filter[ind] != channels[ind + 1]):
               print("\nNote that this is not a valid NN, the number of filters in layer ", str(ind), " is different from the number of channels in layer ", str(ind + 1), sep = "")

else:
     input_rows = [] 
     input_cols  = []
     filter_rows = [] 
     filter_cols = []
     channels = []
     num_filter = []
     strides = []
     max_single_input_size = 0
     max_all_filters_size = 0
     max_output_size = 0

     NN_directory = base_directory + NN_file_folder + NN_file_name + ".csv"

     with open(NN_directory, newline='') as csvfile:
          spamreader = csv.reader(csvfile, delimiter=',')
          firstRow = 1
          for row in spamreader:
               if firstRow:
                    firstRow = 0
                    continue
               try:
                    layer_dict = {"Input Height" : int(row[1]), "Input Width" : int(row[2]), "Filter Height" : int(row[3]), "Filter Width": int(row[4]), \
                    "Channels" : int(row[5]), "Num Filter" : int(row[6]), "Strides" : int(row[7])}
                    all_layers.append(layer_dict)
                    
                    single_input_size = layer_dict["Input Height"] * layer_dict["Input Width"] * layer_dict["Channels"]
                    if single_input_size > max_single_input_size:
                         max_single_input_size = single_input_size
                    
                    all_filters_size = layer_dict["Filter Height"] * layer_dict["Filter Width"] * layer_dict["Channels"] * layer_dict["Num Filter"]
                    if all_filters_size > max_all_filters_size:
                         max_all_filters_size = all_filters_size



               except:
                    print("can't convert all the data in NN file to ints")



SRAM_input_size_options  = [1000000]#, 2000000]#, 5000000, 10000000]
SRAM_filter_size_options = [ 500000]#, 1000000]#, 2000000,  5000000]
SRAM_output_size_options = [ 300000]#, 1000000]#, 2000000,  5000000]

array_rows = 16
array_cols = 16
array_rows_options = [8, 16, 32, 64, 128, 256]
array_cols_options = [8, 16, 32, 64, 128, 256]
array_size_options = []
for array_rows_slider in array_rows_options:
     for array_rows_slider in array_cols_options:
          array_size_options.append([array_rows_slider, array_rows_slider])

min_SRAM_filter_size = max(array_rows_options) * max(array_cols_options)
SRAM_filter_size = int(max_all_filters_size)
SRAM_filter_size_options = np.linspace(min_SRAM_filter_size, max_all_filters_size, 4).astype(int)


SRAM_input_size_options = [int(x * max_single_input_size) for x in [1.1, 3.1, 5.1, 10.1]]
SRAM_input_size = int(max_single_input_size * 1.1)

SRAM_output_size_options = SRAM_input_size_options
SRAM_output_size = SRAM_input_size

batch_size_options = [1, 8, 16, 32, 64, 128]
batch_size = 1

accumulator_elements_options = [20000, 100000, 1000000]
accumulator_elements = 20000

SRAM_input_size_options  = [1000000]
SRAM_filter_size_options = [1000000]
SRAM_output_size_options = [1000000]

symbol_rate_options = [10]

## array rows
array_rows_options = [8, 16, 32, 64, 128, 256]
#array_rows_options = [8, 17]
array_rows = 0
array_cols = 64
batch_size = 32
SRAM_input_size = mega * 100
SRAM_filter_size = int(0.5 * mega)
SRAM_output_size = int(0.5 * mega)
accumulator_elements = 20000
array_rows_sweep_data = [array_rows, array_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, accumulator_elements, batch_size]

array_rows = 64
array_cols_options = [8, 16, 32, 64, 128, 256]
#array_cols_options = [8, 18]
array_cols = 0
batch_size = 32
SRAM_input_size = mega * 100
SRAM_filter_size = int(0.5 * mega)
SRAM_output_size = int(0.5 * mega)
accumulator_elements = 20000
array_cols_sweep_data = [array_rows, array_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, accumulator_elements, batch_size]

array_rows = 64
array_cols = 64
batch_size_options = [1, 8, 16, 32, 64, 128]
#batch_size_options = [32]
batch_size = 0
SRAM_input_size = mega * 10
SRAM_filter_size = int(0.5 * mega)
SRAM_output_size = int(0.5 * mega) 
accumulator_elements = 20000
batch_size_sweep_data = [array_rows, array_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, accumulator_elements, batch_size]

array_rows = 64
array_cols = 64
batch_size = 32
SRAM_input_size = 0
SRAM_input_size_options = list(np.linspace(mega, 100 * mega, 5).astype(int))
SRAM_filter_size = int(0.5 * mega)
SRAM_output_size = int(0.5 * mega) * 100
accumulator_elements = 20000
SRAM_input_size_sweep_data = [array_rows, array_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, accumulator_elements, batch_size]


array_rows = 0
array_cols = 0
batch_size = 128
SRAM_input_size = 10 * mega
SRAM_filter_size = int(0.5 * mega)
SRAM_output_size = int(0.5 * mega)
accumulator_elements = 20000
array_rows_cols_sweep_data = [array_rows, array_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, accumulator_elements, batch_size]


array_rows = 64
array_cols = 64
batch_size = 0
SRAM_input_size = 0 
SRAM_filter_size = int(0.5 * mega)
SRAM_output_size = int(0.5 * mega)
accumulator_elements = 20000
batch_SRAM_input_sweep_data = [array_rows, array_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, accumulator_elements, batch_size]

