from os import listdir
import csv 
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import sys

import analytical_modeling_SS_integrated
import system_specs_9
import practice_plots_6
import specs_info
import sim_params
#import analytical_modeling


sys.path.append(sim_params.base_directory)
from scalesim.scale_external_2 import run_scale_sim

SS_inputs_names = specs_info.SS_inputs_names
SS_outputs_names = specs_info.SS_outputs_names
SS_in_out_names = SS_inputs_names + SS_outputs_names
chip_specs_names = specs_info.all_specs_names

all_names = SS_inputs_names + SS_outputs_names + chip_specs_names

def load_saved_SS_results(SS_results_file_path_name):
     print("Loading Existing DF")
     try:
          SS_in_out_info = pd.read_csv(SS_results_file_path_name, skiprows = 0, index_col=0)
          SS_in_out_info = SS_in_out_info.loc[SS_in_out_names].astype(int)
     except:
          print("Existing DF empty")
          SS_in_out_info = create_SS_inOut()
     return (SS_in_out_info)


def create_SS_inOut():
     print("Creating new empty dataframe")
     SS_in_out_info = pd.DataFrame(index = SS_in_out_names)
     return(SS_in_out_info)  

def write_config_file(config_info):
     generic_info_top = "[general]\nrun_name = ONN_sim\n\n[architecture_presets]"
     generic_info_bottom = "\nIfmapOffset:    0\nFilterOffset:   1\nOfmapOffset:    1\nBandwidth : 10\nDataflow : ws\nMemoryBanks:   1\n\n[run_presets]\nInterfaceBandwidth: CALC"
     generic_info_middle = "\nArrayHeight: " + str(config_info["Systolic Array Rows"]) + "\nArrayWidth: " + str(config_info["Systolic Array Cols"]) + \
     "\nIfmapSramSzkB: " + str(config_info["SRAM Input Size"]) + "\nFilterSramSzkB: " + str(config_info["SRAM Filter Size"]) + "\nOfmapSramSzkB: " + str(config_info["SRAM Output Size"])
     total_text = generic_info_top + generic_info_middle + generic_info_bottom

     file = open(sim_params.config_file_path, 'w')
     file.write(total_text)
     file.close()

def manage_saved_data(SS_results_file_base_folder, SS_results_file_path_name):
     if not os.path.isdir(SS_results_file_base_folder):
          os.mkdir(SS_results_file_base_folder)

     if os.path.isfile(SS_results_file_path_name):
          SS_in_out_saved = load_saved_SS_results(SS_results_file_path_name)
     else:
          SS_in_out_saved = create_SS_inOut() 
     return SS_in_out_saved
     
def mix_model_results(analytical_model, SS_outputs_by_layer, SS_results_file_path_name_write_layers):
     combined_models = pd.DataFrame(index = SS_outputs_names)
     num_layers = analytical_model.shape[1]
     if (num_layers != SS_outputs_by_layer.shape[1]):
          print("two models have different shapes, problem")
     for layer in range(num_layers):
          combined_models.insert(combined_models.shape[1], SS_outputs_by_layer.columns[layer], SS_outputs_by_layer.iloc[:, layer])
          combined_models.insert(combined_models.shape[1], analytical_model.columns[layer],    analytical_model.iloc[:, layer])
     x = 1
     combined_models.to_csv(SS_results_file_path_name_write_layers)

def main():
     print("\n\n\n\n\n\n\n\n\n\n")

     SS_results_file_path_name = sim_params.SS_results_file_path_name
     SS_results_file_path_name_write = sim_params.SS_results_file_path_name_write
     SS_in_out_saved = manage_saved_data(sim_params.SS_results_file_base_folder, SS_results_file_path_name)

     SS_in_out_wanted = pd.DataFrame(index = SS_in_out_names)
     chip_specs = pd.DataFrame(index = chip_specs_names)

     

     
     print("will now loop through desired inputs")
     for batch_size in sim_params.batch_size_options:
          for (array_size_idx, array_size) in enumerate(sim_params.array_size_options):
               SS_rows = array_size[0]; SS_cols = array_size[1]
               SS_inputs = [SS_rows, SS_cols, sim_params.SRAM_input_size, sim_params.SRAM_filter_size, sim_params.SRAM_output_size, sim_params.DRAM_mode, batch_size]
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
                    SS_inputs_dict = dict({"Systolic Array Rows": SS_rows, \
                         "Systolic Array Cols": SS_cols, "SRAM Input Size": sim_params.SRAM_input_size, "SRAM Filter Size": sim_params.SRAM_filter_size, \
                         "SRAM Output Size": sim_params.SRAM_output_size, "DRAM Bandwidth Mode": sim_params.DRAM_mode}) 
                    write_config_file(SS_inputs_dict)

                    (SS_outputs_single, SS_outputs_by_layer) = run_scale_sim(sim_params.config_file_path, sim_params.NN_file_path_name, sim_params.base_directory + "logs", sim_params.SS_print_verbose, batch_size)
                    layer_filename_addition = "_BS_" + str(batch_size) + "_AS_" + str(SS_rows) + "_" + str(SS_cols) + "_SRAM_" + str(sim_params.SRAM_input_size) + "_" + str(sim_params.SRAM_filter_size) + "_" + str(sim_params.SRAM_output_size)
                    
                    SS_results_file_path_name_write_layers = SS_results_file_path_name_write[0: -4] + layer_filename_addition + ".csv"
                    analytical_model = analytical_modeling_SS_integrated.make_analytical_model(SS_inputs_dict, batch_size, sim_params.NN_file_path_name)
                    mix_model_results(analytical_model, SS_outputs_by_layer, SS_results_file_path_name_write_layers)

                    SS_in_out_wanted.insert(SS_in_out_wanted.shape[1], "filler name", pd.concat([SS_inputs_wanted_single, SS_outputs_single]), allow_duplicates=True)
                    SS_in_out_saved.insert(SS_in_out_saved.shape[1], "filler name", pd.concat([SS_inputs_wanted_single, SS_outputs_single]), allow_duplicates=True)
          
                    SS_in_out_saved.to_csv(SS_results_file_path_name_write)


     SS_in_out_saved.to_csv(SS_results_file_path_name_write)

     if (sim_params.run_system_specs):
          num_batch_array = len(sim_params.array_size_options) * len(sim_params.batch_size_options)
          col_repeat_idxs = np.repeat(range(num_batch_array), len(sim_params.symbol_rate_options))
          SS_in_out_wanted = SS_in_out_wanted.iloc[:, col_repeat_idxs]
          symbol_rate_df = pd.DataFrame(sim_params.symbol_rate_options * num_batch_array, ["filler name"] * len(sim_params.symbol_rate_options) * num_batch_array, ["Symbol Rate (GHz)"]).T
          SS_in_out_wanted = pd.concat([symbol_rate_df, SS_in_out_wanted])
          
          chip_specs = pd.DataFrame(index = chip_specs_names)
          for  (columnName, SS_in_out_single) in SS_in_out_wanted.iteritems():
               chip_specs_single = system_specs_9.run_power_area_model(SS_in_out_single[SS_outputs_names], SS_in_out_single[SS_inputs_names], SS_in_out_single["Symbol Rate (GHz)"] * 10**9)
               chip_specs.insert(chip_specs.shape[1], "filler name", chip_specs_single, allow_duplicates = True)     

          complete_final_specs = pd.concat([SS_in_out_wanted, chip_specs])
          complete_final_specs.to_csv(sim_params.chip_specs_file_path_name)

     if (sim_params.make_plots):
          practice_plots_6.prepare_plot_specs(sim_params.symbol_rate_options, sim_params.array_size_options)
          practice_plots_6.prepare_chip_specs(chip_specs)
          practice_plots_6.plot_power(chip_specs)
          practice_plots_6.plot_area(chip_specs)
          practice_plots_6.plot_inf_specs(chip_specs)
          
          params_interest = [["ADCs Power", "DRAM Program Power", "DRAM Compute Power", "PCM Heaters Power"], []]
          params_total_quantities = ["Total Combined Electronics Power", "Total Laser Power from Wall mW"]
          params_other_names = ["Other Electrical Power"]
          practice_plots_6.power_breakdown(chip_specs, params_interest, params_total_quantities, params_other_names)


if __name__ == "__main__":    
     print("\n\n\n")
     main()
     print("\n\n\n")



