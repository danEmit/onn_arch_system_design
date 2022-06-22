from sqlalchemy import column
import sim_params_analytical
import pseudo_analytical_sim
import pprint
import pandas as pd
import specs_info
import os
import numpy as np
import system_specs_9
import practice_plots_7

hardware_names = specs_info.hardware_specs_names
runspecs_names = specs_info.runspecs_names
hardware_runspecs_names = hardware_names + runspecs_names
chip_specs_names = specs_info.all_specs_names

all_names = hardware_names + runspecs_names + chip_specs_names

simulator = 0
hardware_runspecs_existing = 0
hardware_runspecs_wanted = 0

array_rows_sweep_params = 0
array_cols_sweep_params = 0
batch_size_sweep_params = 0
SRAM_input_size_sweep_params = 0
array_rows_cols_sweep_params = 0
batch_SRAM_input_sweep_params = 0

def load_saved_hardware_runspecs_results(results_file_path_name):
     print("Loading existing results file")
     try:
          hardware_runspecs_info = pd.read_csv(results_file_path_name, skiprows = 0, index_col=0)
          hardware_runspecs_info = hardware_runspecs_info.loc[hardware_runspecs_names].astype(int)
     except:
          print("Existing results file empty")
          hardware_runspecs_info = create_hardware_runspecs_info()
     return (hardware_runspecs_info)

def create_hardware_runspecs_info():
     print("Cannot find useful results file, creating new empty dataframe")
     hardware_runspecs_info = pd.DataFrame(index = hardware_runspecs_names)
     return(hardware_runspecs_info)  

def manage_saved_data(hardware_runspecs_results_folder, hardware_runspecs_path_name):
     if not os.path.isdir(hardware_runspecs_results_folder):
          os.mkdir(hardware_runspecs_results_folder)
          os.mkdir(hardware_runspecs_results_folder + sim_params_analytical.detailed_results_folder)
          os.mkdir(hardware_runspecs_results_folder + sim_params_analytical.plots_folder)

     if os.path.isfile(hardware_runspecs_path_name):
          hardware_runspecs_info = load_saved_hardware_runspecs_results(hardware_runspecs_path_name)
     else:
          hardware_runspecs_info = create_hardware_runspecs_info() 
     return hardware_runspecs_info

def search_solutions_run_sim(hardware_wanted_single, column_name):     
     print("\n---------------------------------")
     print("Searching for results with desired hardware state:")
     print("     Array Size:       ", hardware_wanted_single.loc["Systolic Array Rows"].item(), "x", hardware_wanted_single.loc["Systolic Array Cols"].item())
     print("     SRAM Input Size:  ", hardware_wanted_single.loc["SRAM Input Size"].item())
     print("     SRAM Filter Size: ", hardware_wanted_single.loc["SRAM Filter Size"].item())
     print("     SRAM Output Size: ", hardware_wanted_single.loc["SRAM Output Size"].item())
     print("     Accumulator Elements per Col: ", hardware_wanted_single.loc["Accumulator Elements"].item())
     print("     Batch Size: ", hardware_wanted_single.loc["Batch Size"].item())
     #print("---------------------------------")

     need_run_sim = 1
     for existing_result in range(hardware_runspecs_existing.shape[1]):
          if (hardware_wanted_single.equals(hardware_runspecs_existing.loc[hardware_names].iloc[:, existing_result])):
               need_run_sim = 0
               hardware_runspecs_wanted.insert(hardware_runspecs_wanted.shape[1], column_name, \
                    hardware_runspecs_existing.loc[hardware_runspecs_names].iloc[:, existing_result], allow_duplicates=True)
               print("Found existing results for this hardware state")
               break

     need_run_sim = 1
     if (need_run_sim):       
          print("\nDid not find existing results for this hardware state, will now run simulation")    
          simulator.set_hardware(hardware_wanted_single)   
          midlevel_specs_single = simulator.run_all_layers()
          hardware_runspecs_wanted.insert(hardware_runspecs_wanted.shape[1], \
               column_name, pd.concat([hardware_wanted_single, midlevel_specs_single]), allow_duplicates=True)
          hardware_runspecs_existing.insert(hardware_runspecs_existing.shape[1], \
               "filler name", pd.concat([hardware_wanted_single, midlevel_specs_single]), allow_duplicates=True)                                             
          hardware_runspecs_existing.to_csv(sim_params_analytical.sim_results_file_path_name)
     print("---------------------------------")

def sweep_hardware_full():
     num_hardware = 0
     print("\nAll params to be swept:")
     print("batch size options: ", sim_params_analytical.batch_size_options)
     print("array size options: ", sim_params_analytical.array_size_options)
     print("input SRAM  size options: ", sim_params_analytical.SRAM_input_size_options)
     print("filter SRAM size options: ", sim_params_analytical.SRAM_filter_size_options)
     print("output SRAM size options: ", sim_params_analytical.SRAM_output_size_options)
     print("accumulator size options: ", sim_params_analytical.accumulator_elements_options)
     for batch_size in sim_params_analytical.batch_size_options:
          for array_size in sim_params_analytical.array_size_options:
               for SRAM_input_size in sim_params_analytical.SRAM_input_size_options:
                    for SRAM_filter_size in sim_params_analytical.SRAM_filter_size_options:
                         for SRAM_output_size in sim_params_analytical.SRAM_output_size_options:
                              for accumulator_elements in sim_params_analytical.accumulator_elements_options:
                                   num_hardware += 1
                                   hardware_wanted_single = [array_size[0], array_size[1], SRAM_input_size, SRAM_filter_size, SRAM_output_size, accumulator_elements, batch_size]
                                   hardware_wanted_single = pd.DataFrame(hardware_wanted_single, index = hardware_names).iloc[:, 0]
                                   search_solutions_run_sim(hardware_wanted_single)
     return(num_hardware)
                      
def make_sweep_params_array(sweep_data, variable_options, variable_name):
     num_options = len(variable_options)
     sweep_params = pd.DataFrame(sweep_data, index = hardware_names)
     sweep_index = [0] * num_options
     sweep_params = sweep_params.iloc[:, [0] * num_options]
     sweep_params.loc[variable_name, :] = variable_options
     sweep_params.columns = [variable_name + " " + str(x) for x in range(num_options)]
     return(sweep_params)

def make_sweep_params_double_array(sweep_data, variable_options_1, variable_options_2, variable_name_1, variable_name_2):
     num_options = len(variable_options_1) * len(variable_options_2)
     sweep_params = pd.DataFrame(sweep_data, index = hardware_names)
     sweep_index = [0] * num_options
     sweep_params = sweep_params.iloc[:, [0] * num_options]
     sweep_params.loc[variable_name_1, :] = variable_options_1 * len(variable_options_2)
     sweep_params.loc[variable_name_2, :] = np.repeat(variable_options_2, len(variable_options_1))
     sweep_params.columns = [variable_name_1 + " x " + variable_name_2 + " " + str(x) for x in range(num_options)]
     return(sweep_params)

def sweep_hardware_partial():
     global array_rows_sweep_params, array_cols_sweep_params, batch_size_sweep_params, SRAM_input_size_sweep_params, \
     array_rows_cols_sweep_params, batch_SRAM_input_sweep_params
     all_params  = pd.DataFrame([], index = hardware_names)

     array_rows_sweep_params = make_sweep_params_array(sim_params_analytical.array_rows_sweep_data, \
          sim_params_analytical.array_rows_options, "Systolic Array Rows")
     array_cols_sweep_params = make_sweep_params_array(sim_params_analytical.array_cols_sweep_data, \
          sim_params_analytical.array_cols_options, "Systolic Array Cols")
     batch_size_sweep_params = make_sweep_params_array(sim_params_analytical.batch_size_sweep_data, \
          sim_params_analytical.batch_size_options, "Batch Size")
     SRAM_input_size_sweep_params = make_sweep_params_array(sim_params_analytical.SRAM_input_size_sweep_data, \
          sim_params_analytical.SRAM_input_size_options, "SRAM Input Size")
     array_rows_cols_sweep_params = make_sweep_params_double_array(sim_params_analytical.array_rows_cols_sweep_data, \
          sim_params_analytical.array_rows_options, sim_params_analytical.array_cols_options, "Systolic Array Rows", "Systolic Array Cols")
     batch_SRAM_input_sweep_params = make_sweep_params_double_array(sim_params_analytical.batch_SRAM_input_sweep_data, \
          sim_params_analytical.SRAM_input_size_options, sim_params_analytical.batch_size_options, "SRAM Input Size", "Batch Size")

     all_params = pd.concat([array_rows_sweep_params, array_cols_sweep_params, batch_size_sweep_params, \
          SRAM_input_size_sweep_params, array_rows_cols_sweep_params, batch_SRAM_input_sweep_params], axis = 1)

     all_params = pd.DataFrame(sim_params_analytical.single_setting, index = hardware_names)
     num_hardware = all_params.shape[1]
     for col in all_params:
          hardware_wanted_single = all_params.loc[:, col]
          search_solutions_run_sim(hardware_wanted_single, col)

     #print(hardware_runspecs_wanted[:, array_rows_sweep_params.columns])
     return(num_hardware)

def organize_hardware():
     global hardware_runspecs_existing, hardware_runspecs_wanted
     hardware_runspecs_existing = manage_saved_data(\
          sim_params_analytical.results_file_base_folder, \
               sim_params_analytical.sim_results_file_path_name)
     hardware_runspecs_wanted = pd.DataFrame(index = hardware_runspecs_names)

     num_hardware = sweep_hardware_partial()

     hardware_runspecs_existing.to_csv(sim_params_analytical.sim_results_file_path_name)
     #hardware_runspecs_wanted.to_csv(sim_params_analytical.sim_results_file_path_name_current)
     print("\nDone running simulator for all hardware states\n")
     if (sim_params_analytical.run_system_specs):
          (chip_specs, complete_final_specs) = run_system_specs(num_hardware, hardware_runspecs_wanted)
     if (sim_params_analytical.make_plots):
          (array_rows_sweep_results, array_cols_sweep_results, batch_size_sweep_results, SRAM_input_size_sweep_results, \
               array_rows_cols_sweep_results, batch_SRAM_input_sweep_results) = isolate_results(complete_final_specs)
          make_plots(array_rows_sweep_results, array_cols_sweep_results, batch_size_sweep_results, SRAM_input_size_sweep_results, \
               array_rows_cols_sweep_results, batch_SRAM_input_sweep_results)

def isolate_results(complete_final_specs):
     array_rows_sweep_results = complete_final_specs.loc[:, array_rows_sweep_params.columns]
     array_cols_sweep_results = complete_final_specs.loc[:, array_cols_sweep_params.columns]
     batch_size_sweep_results = complete_final_specs.loc[:, batch_size_sweep_params.columns]
     SRAM_input_size_sweep_results = complete_final_specs.loc[:, SRAM_input_size_sweep_params.columns]
     array_rows_cols_sweep_results = complete_final_specs.loc[:, array_rows_cols_sweep_params.columns]
     batch_SRAM_input_sweep_results = complete_final_specs.loc[:, batch_SRAM_input_sweep_params.columns]

     return(array_rows_sweep_results, array_cols_sweep_results, batch_size_sweep_results, \
          SRAM_input_size_sweep_results, array_rows_cols_sweep_results, batch_SRAM_input_sweep_results)


def make_plots(array_rows_sweep_results, array_cols_sweep_results, batch_size_sweep_results, SRAM_input_size_sweep_results, array_rows_cols_sweep_results, batch_SRAM_input_sweep_results):
     practice_plots_7.setup_plots(sim_params_analytical.NN_file_name, 1, \
          sim_params_analytical.plots_folder_complete, 10,\
          array_rows_sweep_results, array_cols_sweep_results, batch_size_sweep_results, SRAM_input_size_sweep_results, array_rows_cols_sweep_results, batch_SRAM_input_sweep_results)
     practice_plots_7.plot_photonic_losses()
     practice_plots_7.plot_times()
     practice_plots_7.plot_power()
     practice_plots_7.plot_electronic_power_breakdown()
     practice_plots_7.IPSW()
     practice_plots_7.array_rows_cols_sweep_plots()
     practice_plots_7.batch_SRAM_input_sweep_plots()
     practice_plots_7.comps_of_IPSW()


def run_system_specs(num_hardware, hardware_runspecs_wanted):
     col_repeat_idxs = np.repeat(range(num_hardware), len(sim_params_analytical.symbol_rate_options))
     hardware_runspecs_wanted_expanded = hardware_runspecs_wanted.iloc[:, col_repeat_idxs]
     symbol_rate_df = pd.DataFrame(sim_params_analytical.symbol_rate_options * num_hardware, \
          ["filler name"] * len(sim_params_analytical.symbol_rate_options) * num_hardware, ["Symbol Rate (GHz)"]).T
     symbol_rate_df.columns = hardware_runspecs_wanted_expanded.columns
     hardware_runspecs_wanted_expanded = pd.concat([symbol_rate_df, hardware_runspecs_wanted_expanded])
     chip_specs = pd.DataFrame(index = chip_specs_names)


     for (columnName, hardware_runspecs_single) in hardware_runspecs_wanted_expanded.iteritems():
               chip_specs_single = system_specs_9.run_power_area_model(hardware_runspecs_single[runspecs_names],\
                     hardware_runspecs_single[hardware_names], hardware_runspecs_single["Symbol Rate (GHz)"] * 10**9)
               chip_specs.insert(chip_specs.shape[1], columnName, chip_specs_single, allow_duplicates = True)    
     
     complete_final_specs = pd.concat([hardware_runspecs_wanted_expanded, chip_specs])
     complete_final_specs.to_csv(sim_params_analytical.chip_specs_file_path_name)
     return(chip_specs, complete_final_specs)

def main():
     global simulator
     simulator = pseudo_analytical_sim.hardware_state()
     print("\nSimulating performance of NN model \"", sim_params_analytical.NN_file_name, "\"", "\n", sep='')
     simulator.set_NN(sim_params_analytical.all_layers)
     organize_hardware()
     #sweep_hardware_configs(simulator)


if __name__ == "__main__":
    print("\n"*5) 
    main()
    print("\n"*5) 

