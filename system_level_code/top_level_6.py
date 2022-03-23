from os import listdir
import csv 
import pandas as pd
import os
import matplotlib.pyplot as plt

import numpy as np

import system_specs_9
import sys
import practice_plots_6


## Generic Info
results_type = "untracked"
if results_type not in ["official", "untracked"]:
     print("WRONG RESULTS DESTINATION")

base_directory = "/Users/D/Desktop/research/onn_arch_system_design/"
#base_directory = "/homes/dansturm/Desktop/onn_arch_system_design/"
SS_inOut_file_path = base_directory + "results/" + results_type + "/"
config_file_path  = base_directory + "configs/scale.cfg"
sys.path.append(base_directory)
from scalesim.scale_external_2 import run_scale_sim


ghz = 10**9
make_plots = 1
run_system_specs = 1
make_plots = run_system_specs and make_plots
save_SS_imm = 1
SS_print_verbose = 0

#print(sys.path)


SS_inputs_start_row = "Systolic Array Rows"
SS_inputs_end_row = "DRAM Bandwidth Mode"
SS_outputs_start_row = "SRAM Input Reads"
SS_outputs_end_row = "Total Vector Segments Processed"

SS_inputs_names = ["Systolic Array Rows", "Systolic Array Cols", "SRAM Input Size", "SRAM Filter Size", "SRAM Output Size", "DRAM Bandwidth Mode"]
SS_outputs_names = ["SRAM Input Reads", "SRAM Filter Reads", "SRAM Output Writes", "DRAM Input Reads", "DRAM Filter Reads", "DRAM Output Writes", \
          "Total Weights Programming Cycles", "Total Vector Segments Processed"]
SS_in_out_names = SS_inputs_names + SS_outputs_names

#chip_specs_names = ["Total Chip Area", "Total Chip Power", "Inferences Per Second", "Inferences Per Second Per Watt"]

electronic_area_specs_names = ["ADCs Area", "PS Area", "ODAC Drivers Area", "PCM Heaters Area", "MRM Heaters Area",\
     "SRAM Area", "DRAM Area", "Clock Area", "Rx AFE Area"]

electronic_power_specs_names = ["ADCs Power", "PS Power", "ODAC Drivers Power", "PCM Heaters Power", "MRM Heaters Power", \
     "SRAM Program Power", "SRAM Compute Power", "DRAM Program Power", "DRAM Compute Power", "Clocks Power", "Rx AFE Power"]

photonic_area_specs_names = ["MRMs Area", "Crossbar Array Area", "Tx Power Splitters Area", "Grating Coupler Area"]

photonic_power_specs_names = ["Photonic Power Single PD", "PCM OMA", "MRM Tx OMA", "Power Loss Crossbar Junctions", "Power Loss Crossbar Waveguides", "Power Loss Splitting Tree",\
     "Power Loss Tx Waveguides", "Power Loss Grating Coupler", "Power Loss Waveguide Power Combining"]

photonic_power_actual_loss_names = ["PCM OMA Actual Loss", "MRM Tx OMA Actual Loss", "Crossbar Junctions Actual Loss", "Crossbar Waveguides Actual Loss", "Splitting Tree Actual Loss",\
     "Tx Waveguides Actual Loss", "Grating Coupler Actual Loss", "Waveguide Power Combining Actual Loss"]

time_specs_names = ["Compute Portion", "Program Portion", "Total Time"]

semi_high_results_names = ["Total Electronics Area", "Total Photonics Area", "Total Electronics Program Power", \
     "Total Electronics Compute Power", "Total Combined Electronics Power", "Total Electronics Power dBm", "Total Photonic Losses and OMA", "Total Photonic Power mW",\
          "Total Laser Power from Wall mW", "Total Laser Power from Wall dBm"]

overall_specs_names = ["Total Chip Area", "Total Chip Power", "Total Chip Power dBm", "Inferences Per Second", "Inferences Per Second Per Watt"]


chip_specs_names = electronic_area_specs_names + electronic_power_specs_names + photonic_area_specs_names + photonic_power_specs_names \
+ photonic_power_actual_loss_names + time_specs_names + semi_high_results_names + overall_specs_names

all_names = SS_inputs_names + SS_outputs_names + chip_specs_names

def load_saved_SS_results(SS_inOut_file_local):
     print("Loading Existing DF")
     SS_inOut_file_complete = SS_inOut_file_path + SS_inOut_file_local

     try:
          SS_in_out_info = pd.read_csv(SS_inOut_file_complete, skiprows = 0, index_col=0)
          SS_in_out_info = SS_in_out_info.loc[SS_in_out_names].astype(int)
          #SS_inputs_all  = SS_inOut_all.loc[SS_inputs_start_row:SS_inputs_end_row]
          #SS_inputs_all = SS_inputs_all.astype(int)
          #SS_outputs_all = SS_inOut_all.loc[SS_outputs_start_row:SS_outputs_end_row]
          #SS_outputs_all = SS_outputs_all.astype(int)
     except:
          print("Existing DF empty")
          SS_in_out_info = create_SS_inOut()

     #SS_inputs_all.index.name = "Parameters"
     #SS_outputs_all.index.name = "Parameters"
     return (SS_in_out_info)


def create_SS_inOut():
     print("Creating new empty dataframe")
     SS_in_out_info = pd.DataFrame(index = SS_in_out_names)
     #SS_outputs_all = pd.DataFrame(index = SS_outputs_names)
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
     NN_file_name = "Resnet50"
     NN_file_path_local = "topologies:ONN:"
     NN_file_path_local_B = "topologies/ONN/"

     SS_in_out_saved = return_SS_inOut(NN_file_name, NN_file_path_local)

     #print("inputs we have located:", SS_inputs_saved.shape)
     #print("outputs we have located:", SS_outputs_saved.shape)
     #print()

     SRAM_input_size  = 64000
     SRAM_filter_size = 64000
     SRAM_output_size = 64000
     DRAM_mode = 0

     #symbol_rate_options = [1 * ghz, 5 * ghz, 10 * ghz]
     symbol_rate_options = [1, 5, 10]
     base_SR = symbol_rate_options[0]
     #symbol_rate = symbol_rate_options[1]
     #array_size_options = [[8,8], [64,64]]
     array_size_options = [[8,8], [16, 16], [32, 32], [64,64]]
     #array_size_options = [[8,8], [16, 16]]
     #array_size_options = [[8, 8]]
      
     #array_size_options = [[9,9], [15, 15], [17, 17]]
     screwup_array = [15, 15]
     
     # note that for whatever reason if i execute the line below, i get this issue where when i try to 
     # alter one of the PDs, the rest get altered as well... not sure why...
     # chip_specs_all_symbol_rates = [pd.DataFrame(index = chip_specs_names)] * len(symbol_rate_options)
     
     '''
     chip_specs_all_symbol_rates = []
     for symbol_rate in symbol_rate_options:
         chip_specs_all_symbol_rates.append(pd.DataFrame(index = chip_specs_names))
     '''
     #SS_inputs_wanted = [pd.DataFrame(index = SS_inputs_names)] * len(array_size_options)
     #SS_output_wanted = [pd.DataFrame(index = SS_inputs_names)] * len(array_size_options)
     
     #SS_in_out_wanted  = [0] * len(array_size_options)
     #chip_specs        = [0] * len(array_size_options)
     SS_in_out_wanted = pd.DataFrame(index = SS_in_out_names)
     chip_specs = pd.DataFrame(index = chip_specs_names)
     
     print("will now loop through desired inputs")
     for (array_size_idx, array_size) in enumerate(array_size_options):
          SS_rows = array_size[0]; SS_cols = array_size[1]
          SS_inputs = [SS_rows, SS_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, DRAM_mode]
          #SS_outputs = [0] * len(SS_outputs_names)
          SS_inputs_wanted_single = pd.DataFrame(SS_inputs, index = SS_inputs_names, columns = ["0"])
          print("start of loop. searching for column of DF with the current desired SS inputs, rows:", SS_rows, "cols:", SS_cols)

          need_run_SS = 1
          for column_name in SS_in_out_saved:
               if (SS_inputs_wanted_single.iloc[:, 0].equals(SS_in_out_saved.loc[SS_inputs_names, column_name])):
                    print("found matching SS inputs at column", column_name, ",will now load corresponding outputs")
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

               SS_outputs_single = run_scale_sim(config_file_path, NN_file_path_complete, base_directory + "logs", SS_print_verbose)
               SS_in_out_wanted.insert(SS_in_out_wanted.shape[1], "filler name", pd.concat([SS_inputs_wanted_single, SS_outputs_single]), allow_duplicates=True)
               SS_in_out_saved.insert(SS_in_out_saved.shape[1], "filler name", pd.concat([SS_inputs_wanted_single, SS_outputs_single]), allow_duplicates=True)
              # SS_in_out_wanted[array_size_idx].at[SS_outputs_names] = SS_outputs_single
               #SS_in_out_saved.insert(SS_in_out_saved.shape[1], SS_in_out_saved.shape[1], SS_in_out_wanted[array_size_idx]) 
     
     saved_specs_file_path = SS_inOut_file_path + NN_file_path_local + NN_file_name + "_SS_results.csv"
     SS_in_out_saved.to_csv(saved_specs_file_path)

     col_repeat_idxs = np.repeat(range(len(array_size_options)), len(symbol_rate_options))
     SS_in_out_wanted = SS_in_out_wanted.iloc[:, col_repeat_idxs]
     symbol_rate_df = pd.DataFrame(symbol_rate_options * len(array_size_options), ["filler name"] * len(array_size_options) * len(symbol_rate_options), ["Symbol Rate (GHz)"]).T
     SS_in_out_wanted = pd.concat([symbol_rate_df, SS_in_out_wanted])
     
     chip_specs = pd.DataFrame(index = chip_specs_names)
     for  (columnName, SS_in_out_single) in SS_in_out_wanted.iteritems():
           chip_specs_single = system_specs_9.run_power_area_model(SS_in_out_single[SS_outputs_names], SS_in_out_single[SS_inputs_names], SS_in_out_single["Symbol Rate (GHz)"] * ghz)
           chip_specs.insert(chip_specs.shape[1], "filler name", chip_specs_single, allow_duplicates = True)     

     saved_specs_file_path = SS_inOut_file_path + NN_file_path_local + NN_file_name + "_SS_results_and_chip_specs.csv"
     complete_final_specs = pd.concat([SS_in_out_wanted, chip_specs])
     complete_final_specs.to_csv(saved_specs_file_path)
     #practice_plots_4.make_stacked_bar_plot() 

     ''' 
     params_interest = [["ADCs Power"], ["MRM Tx OMA Actual Loss", "Crossbar Junctions Actual Loss"]]
     params_interest = [["ADCs Power", "DRAM Program Power", "DRAM Compute Power"], []]
     params_total_quantities = ["Total Combined Electronics Power", "Total Laser Power from Wall mW"]
     params_other_names = ["Other Electrical Power", "Other Photonic Power"]
     params_other_names = ["Other Electrical Power"]
     #repeat_tick_labels = [str(x) + " GHz" for x in symbol_rate_options]
     array_configs = [str(x[0]) + " x " + str(x[1]) for x in array_size_options]
     fig = practice_plots_5.make_stacked_bar_plot(chip_specs, params_interest, params_total_quantities, params_other_names, symbol_rate_options, array_configs, "mW")
     '''
     
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



