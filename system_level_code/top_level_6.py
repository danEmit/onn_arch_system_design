from os import listdir
import csv 
import pandas as pd
import os
import matplotlib.pyplot as plt

import numpy as np

import system_specs_9
import sys
import practice_plots_6
import specs_info


## Generic Info
results_type = "untracked"
if results_type not in ["official", "untracked"]:
     print("WRONG RESULTS DESTINATION")

base_directory = "/Users/D/Desktop/research/onn_arch_system_design/"
base_directory = "/Users/d/Desktop/onn_arch_system_design/"
SS_inOut_file_path = base_directory + "results/" + results_type + "/"
config_file_path  = base_directory + "configs/scale.cfg"
sys.path.append(base_directory)
from scalesim.scale_external_2 import run_scale_sim


ghz = 10**9
make_plots = 0
run_system_specs = 0
make_plots = run_system_specs and make_plots
save_SS_imm = 1
SS_print_verbose = 0


SS_inputs_names = specs_info.SS_inputs_names
SS_outputs_names = specs_info.SS_outputs_names
SS_in_out_names = SS_inputs_names + SS_outputs_names
chip_specs_names = specs_info.all_specs_names

all_names = SS_inputs_names + SS_outputs_names + chip_specs_names

def load_saved_SS_results(SS_inOut_file_local):
     print("Loading Existing DF")
     SS_inOut_file_complete = SS_inOut_file_path + SS_inOut_file_local

     try:
          SS_in_out_info = pd.read_csv(SS_inOut_file_complete, skiprows = 0, index_col=0)
          SS_in_out_info = SS_in_out_info.loc[SS_in_out_names].astype(int)

     except:
          print("Existing DF empty")
          SS_in_out_info = create_SS_inOut()

     return (SS_in_out_info)


def create_SS_inOut():
     print("Creating new empty dataframe")
     SS_in_out_info = pd.DataFrame(index = SS_in_out_names)
     return(SS_in_out_info)  


def return_SS_inOut(NN_file_name, NN_file_path_local):
     SS_inOut_names_all = listdir(SS_inOut_file_path) 
     potential_file_name = NN_file_path_local + NN_file_name + "_SS_results.csv"
     print("searching through all existing files for:", potential_file_name)

     for existing_file_name in SS_inOut_names_all:
          if (existing_file_name == potential_file_name):
               return load_saved_SS_results(potential_file_name) 
          else:
               continue
     print("could not find file for current NN")
     return create_SS_inOut()


def write_config_file(config_info):
     generic_info_top = "[general]\nrun_name = ONN_sim\n\n[architecture_presets]"
     generic_info_bottom = "\nIfmapOffset:    0\nFilterOffset:   1\nOfmapOffset:    1\nBandwidth : 10\nDataflow : ws\nMemoryBanks:   1\n\n[run_presets]\nInterfaceBandwidth: CALC"
     generic_info_middle = "\nArrayHeight: " + str(config_info["Systolic Array Rows"]) + "\nArrayWidth: " + str(config_info["Systolic Array Cols"]) + \
     "\nIfmapSramSzkB: " + str(config_info["SRAM Input Size"]) + "\nFilterSramSzkB: " + str(config_info["SRAM Filter Size"]) + "\nOfmapSramSzkB: " + str(config_info["SRAM Output Size"])
     total_text = generic_info_top + generic_info_middle + generic_info_bottom

     file = open(config_file_path, 'w')
     file.write(total_text)
     file.close()

     
def main():
     print("\n\n\n\n\n\n\n\n\n\n")
     NN_file_name = "test"
     NN_file_path_local = "topologies:ONN:"
     NN_file_path_local_B = "topologies/ONN/"

     SS_in_out_saved = return_SS_inOut(NN_file_name, NN_file_path_local)

     SRAM_input_size  = 64000
     SRAM_filter_size = 64000
     SRAM_output_size = 64000
     DRAM_mode = 0
     batch_size_options = [8, 32, 128]

     symbol_rate_options = [1, 5, 10]
     base_SR = symbol_rate_options[0]
     array_size_options = [[8,8], [16, 16], [32, 32], [64,64], [128, 128]]
     #array_size_options = [[8,8], [16, 16]]
     #array_size_options = [[8, 8]]


     SS_in_out_wanted = pd.DataFrame(index = SS_in_out_names)
     chip_specs = pd.DataFrame(index = chip_specs_names)

     if (1):
          batch_size_options_options = [[1], [32]]
          BSO_index = int(sys.argv[1])
          batch_size_options = batch_size_options_options[BSO_index]     
          array_size_options_options = [[[8,8]], [[16, 16]], [[32, 32]], [[64,64]], [[128, 128]]]
          ASO_index = int(sys.argv[2])
          print("Batch Size Index:", BSO_index, "Array Size Index:", ASO_index)
          array_size_options = array_size_options_options[ASO_index]

          saved_specs_file_path = SS_inOut_file_path + NN_file_path_local + NN_file_name 
          saved_specs_file_path += "_BSO_" + str(BSO_index) + "_ASO_" + str(ASO_index)
          saved_specs_file_path += "_SS_results.csv"
     else:
          saved_specs_file_path = SS_inOut_file_path + NN_file_path_local + NN_file_name + "_SS_results.csv"
     
     print("will now loop through desired inputs")
     for batch_size in batch_size_options:
          for (array_size_idx, array_size) in enumerate(array_size_options):
               SS_rows = array_size[0]; SS_cols = array_size[1]
               SS_inputs = [SS_rows, SS_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, DRAM_mode, batch_size]
               SS_inputs_wanted_single = pd.DataFrame(SS_inputs, index = SS_inputs_names, columns = ["0"])
               print("start of loop. searching for column of DF with the current desired SS inputs, rows:", SS_rows, "cols:", SS_cols, "batch size:", batch_size)

               need_run_SS = 1
               for column_name in SS_in_out_saved:
                    if (SS_inputs_wanted_single.iloc[:, 0].equals(SS_in_out_saved.loc[SS_inputs_names, column_name])):
                         print("found matching SS inputs at column \"", column_name, "\", will now load corresponding outputs")
                         need_run_SS = 0
                         SS_in_out_wanted.insert(SS_in_out_wanted.shape[1], "filler name", SS_in_out_saved.loc[SS_in_out_names, column_name], allow_duplicates=True)
                         break
               
               if need_run_SS:
                    print("did not find matching SS inputs. will now run scale sim with current desired inputs")
                    SS_inputs_dict = dict({"NN Model Name": NN_file_name, "NN Model Filepath": NN_file_path_local, "Systolic Array Rows": SS_rows, \
                         "Systolic Array Cols": SS_cols, "SRAM Input Size": SRAM_input_size, "SRAM Filter Size": SRAM_filter_size, \
                         "SRAM Output Size": SRAM_output_size, "DRAM Bandwidth Mode": DRAM_mode}) 
                    write_config_file(SS_inputs_dict)
                    NN_file_path_complete = base_directory + NN_file_path_local_B + NN_file_name + ".csv"

                    SS_outputs_single = run_scale_sim(config_file_path, NN_file_path_complete, base_directory + "logs", SS_print_verbose, batch_size)
                    SS_in_out_wanted.insert(SS_in_out_wanted.shape[1], "filler name", pd.concat([SS_inputs_wanted_single, SS_outputs_single]), allow_duplicates=True)
                    SS_in_out_saved.insert(SS_in_out_saved.shape[1], "filler name", pd.concat([SS_inputs_wanted_single, SS_outputs_single]), allow_duplicates=True)
          
                    SS_in_out_saved.to_csv(saved_specs_file_path)


     #saved_specs_file_path = SS_inOut_file_path + NN_file_path_local + NN_file_name + "_SS_results.csv"
     SS_in_out_saved.to_csv(saved_specs_file_path)

     if (run_system_specs):
          num_batch_array = len(array_size_options) * len(batch_size_options)
          col_repeat_idxs = np.repeat(range(num_batch_array), len(symbol_rate_options))
          SS_in_out_wanted = SS_in_out_wanted.iloc[:, col_repeat_idxs]
          symbol_rate_df = pd.DataFrame(symbol_rate_options * num_batch_array, ["filler name"] * len(symbol_rate_options) * num_batch_array, ["Symbol Rate (GHz)"]).T
          SS_in_out_wanted = pd.concat([symbol_rate_df, SS_in_out_wanted])
          
          chip_specs = pd.DataFrame(index = chip_specs_names)
          for  (columnName, SS_in_out_single) in SS_in_out_wanted.iteritems():
               chip_specs_single = system_specs_9.run_power_area_model(SS_in_out_single[SS_outputs_names], SS_in_out_single[SS_inputs_names], SS_in_out_single["Symbol Rate (GHz)"] * ghz)
               chip_specs.insert(chip_specs.shape[1], "filler name", chip_specs_single, allow_duplicates = True)     

          saved_specs_file_path = SS_inOut_file_path + NN_file_path_local + NN_file_name + "_SS_results_and_chip_specs.csv"
          complete_final_specs = pd.concat([SS_in_out_wanted, chip_specs])
          complete_final_specs.to_csv(saved_specs_file_path)

     if (make_plots):
          practice_plots_6.prepare_plot_specs(symbol_rate_options, array_size_options)
          practice_plots_6.prepare_chip_specs(chip_specs)
          practice_plots_6.plot_power(chip_specs)
          practice_plots_6.plot_area(chip_specs)
          practice_plots_6.plot_inf_specs(chip_specs)
          
          params_interest = [["ADCs Power", "DRAM Program Power", "DRAM Compute Power", "PCM Heaters Power"], []]
          params_total_quantities = ["Total Combined Electronics Power", "Total Laser Power from Wall mW"]
          params_other_names = ["Other Electrical Power"]
          practice_plots_6.power_breakdown(chip_specs, params_interest, params_total_quantities, params_other_names)
     

           
           

     
     
     x = 1
          
          
          
          
          
     

     
               


if __name__ == "__main__":    
     print("\n\n\n")
     main()
     print("\n\n\n")



