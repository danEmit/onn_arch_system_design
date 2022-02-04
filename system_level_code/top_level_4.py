from os import listdir
import csv 
import pandas as pd
import os
import matplotlib.pyplot as plt

import numpy as np


## Generic Info
base_directory = "/Users/D/Desktop/research/"
SS_inOut_file_path = base_directory + "onn_arch_system_design/results/"
config_file_path  = base_directory + "onn_arch_system_design/configs/scale.cfg"
SS_file_path      = base_directory + "onn_arch_system_design/"

import sys
sys.path.append(SS_file_path)
print(sys.path)
from scalesim.scale_external_2 import run_scale_sim

import system_specs_6

SS_inputs_start_row = "Systolic Array Rows"
SS_inputs_end_row = "DRAM Bandwidth Mode"
SS_outputs_start_row = "SRAM Input Reads"
SS_outputs_end_row = "Total Vector Segments Processed"

SS_inputs_names = ["Systolic Array Rows", "Systolic Array Cols", "SRAM Input Size", "SRAM Filter Size", "SRAM Output Size", "DRAM Bandwidth Mode"]
SS_outputs_names = ["SRAM Input Reads", "SRAM Filter Reads", "SRAM Output Writes", "DRAM Input Reads", "DRAM Filter Reads", "DRAM Output Writes", \
          "Total Weights Programming Cycles", "Total Vector Segments Processed"]

chip_specs_names = ["Total Chip Area", "Total Chip Power", "Inferences Per Second", "Inferences Per Second Per Watt"]
all_names = SS_inputs_names + SS_outputs_names + chip_specs_names
chip_specs_all = pd.DataFrame(index = chip_specs_names)


def load_saved_SS_results(SS_inOut_file_local):
     print("Loading Existing DF")
     SS_inOut_file_complete = SS_inOut_file_path + SS_inOut_file_local
     #print(SS_inOut_file_complete)
     #print(SS_inOut_file_complete)
     try:
          #SS_inOut_all = pd.read_csv(SS_inOut_file_complete, skiprows = 3, header =None, index_col=0)#.reset_index()
          SS_inOut_all = pd.read_csv(SS_inOut_file_complete, skiprows = 0, index_col=0)
          #print(SS_inOut_all.dtypes)
          #SS_inOut_all = SS_inOut_all.astype(int)
          #print(SS_inOut_all)
          SS_inputs_all  = SS_inOut_all.loc[SS_inputs_start_row:SS_inputs_end_row]
          SS_inputs_all = SS_inputs_all.astype(int)
          #print(SS_inputs_all.dtypes)
          SS_outputs_all = SS_inOut_all.loc[SS_outputs_start_row:SS_outputs_end_row]
          SS_outputs_all = SS_outputs_all.astype(int)
          #print(SS_inputs_all.dtypes)
          #print(SS_outputs_all)
          #print(SS_inputs_all)
          #print("found SS inputs:")
          #print(SS_inputs_all)
          #print("found SS outputs:")
          #print(SS_outputs_all)
     except:
          print("Existing DF empty")
          (SS_inputs_all, SS_outputs_all) = create_SS_inOut()

     SS_inputs_all.index.name = "Parameters"
     SS_outputs_all.index.name = "Parameters"
     return (SS_inputs_all, SS_outputs_all)


def create_SS_inOut():
     print("Creating new empty dataframe")
     SS_inputs_all = pd.DataFrame(index = SS_inputs_names)
     #SS_inputs_all.index.name = "Parameters"
     SS_outputs_all = pd.DataFrame(index = SS_outputs_names)
     #SS_outputs_all.index.name = "Parameters"
     return(SS_inputs_all, SS_outputs_all)  


def return_SS_inOut(NN_file_name, NN_file_path_local):
     SS_inOut_names_all = listdir(SS_inOut_file_path) 
     potential_file_name = NN_file_path_local + NN_file_name + "_SS_results.csv"
     print("searching through all existing files for:", potential_file_name)

     for existing_file_name in SS_inOut_names_all:
          #print(existing_file_name, potential_file_name)
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
     NN_file_name = "basic"
     NN_file_path_local = "topologies:ONN:"
     NN_file_path_local_B = "topologies/ONN/"

     (SS_inputs_all, SS_outputs_all) = return_SS_inOut(NN_file_name, NN_file_path_local)
     print("inputs we have located:", SS_inputs_all.shape)
     #print(SS_inputs_all)
     print("outputs we have located:", SS_outputs_all.shape)
     #print(SS_outputs_all)
     print()

     SRAM_input_size  = 64000
     SRAM_filter_size = 64000
     SRAM_output_size = 64000
     DRAM_mode = 0

     symbol_rate_options = [1 * 10**9, 10 * 10**9]
     symbol_rate = symbol_rate_options[1]
     array_size_options = [[8,8], [8,16], [16, 8]]#, [32,64], [64,64]]
     chip_specs_all_symbol_rates = [0] * len(symbol_rate_options)

     print("will now loop through desired inputs")
     for array_size in array_size_options:
          need_run_SS = 1
          SS_rows = array_size[0]; SS_cols = array_size[1]
          SS_inputs = [SS_rows, SS_cols, SRAM_input_size, SRAM_filter_size, SRAM_output_size, DRAM_mode]
          SS_inputs_wanted = pd.DataFrame(SS_inputs, index = SS_inputs_names, columns = [""])
          SS_inputs_wanted.index.name = "Parameters"
          #print("\nsearching for column of DF with the current desired SS inputs: ", SS_inputs_wanted, "\n")
          print("start of loop. searching for column of DF with the current desired SS inputs, rows:", SS_rows, "cols:", SS_cols)

          results_position = 0
          for column_name in SS_inputs_all:
               if (SS_inputs_wanted.iloc[:, 0].equals(SS_inputs_all[column_name])):
                    print("found matching SS inputs at column", column_name, ",will now load corresponding outputs")
                    # don't run scale sim
                    need_run_SS = 0
                    SS_outputs_single = pd.DataFrame(SS_outputs_all[column_name])
                    results_position = column_name
                    break

          if (need_run_SS):
               print("did not find matching SS inputs. will now run scale sim with current desired inputs")
               SS_inputs_dict = dict({"NN Model Name": NN_file_name, "NN Model Filepath": NN_file_path_local, "Systolic Array Rows": SS_rows, \
                    "Systolic Array Cols": SS_cols, "SRAM Input Size": SRAM_input_size, "SRAM Filter Size": SRAM_filter_size, \
                    "SRAM Output Size": SRAM_output_size, "DRAM Bandwidth Mode": DRAM_mode}) 
               write_config_file(SS_inputs_dict)
               NN_file_path_complete = SS_file_path + NN_file_path_local_B + NN_file_name + ".csv"
               #print(NN_file_path_complete)
               SS_outputs_single = run_scale_sim(config_file_path, NN_file_path_complete, SS_file_path + "logs")
               num_entries = SS_inputs_all.shape[1]
               #print(num_entries)

               SS_outputs_all.insert(0, num_entries, SS_outputs_single, allow_duplicates=True)
               SS_inputs_all.insert(0, num_entries, SS_inputs_wanted, allow_duplicates=True)
               results_position = num_entries
               
               #print(SS_outputs_single)
               #SS_outputs_all.insert(0, "hi", SS_outputs_single, allow_duplicates=True)
               #SS_combined = pd.concat([SS_inputs_wanted, SS_outputs_single], axis = 0)
               #print(SS_combined)
               #SS_outputs_all.insert(0, "hi", SS_combined, allow_duplicates= True)

          
          #print("will now loop through desired symbol rates")
          #for symbol_rate in symbol_rate_options:
          print("will now run power and area model using SS inputs, SS outputs, and symbol rate of:", symbol_rate)
          chip_specs = system_specs_6.run_power_area_model(SS_outputs_single, SS_inputs_wanted, symbol_rate)
          chip_specs_all.insert(0, results_position, chip_specs, allow_duplicates=True)
          #print("results returned from system specs")
          #print(system_specs)
          print()


     filler = pd.DataFrame([[""] * len(SS_inputs_all.columns)], index = [" "])
     '''
     print("here")
     print(SS_inputs_all.shape, filler.shape, SS_outputs_all.shape)
     print(type(SS_inputs_all), type(filler), type(SS_outputs_all))
     print("\nSS_inputs_all:")
     print(SS_inputs_all)
     print("\nfiller:")
     print(filler)
     print("\nSS_outputs_all:")
     print(SS_outputs_all)
     '''
     
     #chip_specs.plot("Total Chip Power")
     #chip_specs_all.loc["Total Chip Power"].plot(kind = 'bar')
     #plt.show()
     #chip_specs_all.loc["Total Chip Area"].plot(kind = 'bar')
     #plt.show()
     
     
     #SS_inOut_all_final = pd.concat([SS_inputs_all, filler, SS_outputs_all])
     SS_inOut_all_final = pd.concat([SS_inputs_all, SS_outputs_all]).astype(float)
     SS_inOut_all_final_rel = SS_inOut_all_final.loc[:, chip_specs_all.columns]
     
     xticks = []
     for col in chip_specs_all:
         label = str(int(SS_inOut_all_final.loc["Systolic Array Rows", col])) + " x " + str(int(SS_inOut_all_final.loc["Systolic Array Cols", col]))
         print(label)
     
     complete_inOut = SS_inOut_all_final
     complete_inOut = pd.concat([SS_inOut_all_final, chip_specs_all])
     chip_specs_all.loc["Total Chip Power"].plot(kind = 'bar')
     #plt.xlabel(["one", "two", "Tree"])
     plt.xticks(np.arange(3), ["one", "two", "Tree"])
     plt.show()
     #print("\nfinal result before saving")
     #print(SS_inOut_all_final)
     complete_inOut_file_complete = SS_inOut_file_path + NN_file_path_local + NN_file_name + "_SS_results.csv"
     try:
          os.remove(complete_inOut_file_complete)
     except:
          x=1
     SS_inOut_all_final.to_csv(complete_inOut_file_complete)
     #print("currently not saving final csv to make sure we run ss every time")
     










if __name__ == "__main__":    
     print("\n\n\n")
     main()
     print("\n\n\n")



