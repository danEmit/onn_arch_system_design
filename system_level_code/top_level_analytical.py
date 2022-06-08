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


def search_solutions_run_sim(hardware_wanted_single):     
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
               hardware_runspecs_wanted.insert(hardware_runspecs_wanted.shape[1], "filler name", \
                    hardware_runspecs_existing.loc[hardware_runspecs_names].iloc[:, existing_result], allow_duplicates=True)
               print("Found existing results for this hardware state")
               break

     if (need_run_sim):       
          print("\nDid not find existing results for this hardware state, will now run simulation")    
          simulator.set_hardware(hardware_wanted_single)   
          midlevel_specs_single = simulator.run_all_layers()
          print("insert")
          hardware_runspecs_wanted.insert(hardware_runspecs_wanted.shape[1], \
               "filler name", pd.concat([hardware_wanted_single, midlevel_specs_single]), allow_duplicates=True)
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
                      

def sweep_hardware_partial():


     base_params =  [sim_params_analytical.array_rows, sim_params_analytical.array_cols, sim_params_analytical.SRAM_input_size, sim_params_analytical.SRAM_filter_size, \
     sim_params_analytical.SRAM_output_size, sim_params_analytical.accumulator_elements, sim_params_analytical.batch_size]

     base_params = pd.DataFrame(base_params, index = hardware_names)
     all_params  = pd.DataFrame([], index = hardware_names)
     #print(base_params)

     batch_sweep_index = [0] * len(sim_params_analytical.batch_size_options)
     batch_sweep = base_params.loc[:, batch_sweep_index]
     batch_sweep.loc["Batch Size", :] = sim_params_analytical.batch_size_options
     all_params = pd.concat([all_params, batch_sweep], axis =1 )

     array_cols_sweep_index = [0] * len(sim_params_analytical.array_cols_options)
     all_cols_sweep = base_params.loc[:, array_cols_sweep_index]
     all_cols_sweep.loc["Systolic Array Cols", :] = sim_params_analytical.array_cols_options
     all_params = pd.concat([all_params, all_cols_sweep], axis = 1)

     array_rows_sweep_index = [0] * len(sim_params_analytical.array_rows_options)
     all_rows_sweep = base_params.loc[:, array_rows_sweep_index]
     all_rows_sweep.loc["Systolic Array Rows", :] = sim_params_analytical.array_rows_options
     all_params = pd.concat([all_params, all_rows_sweep], axis = 1)

     SRAM_input_size_sweep_index = [0] * len(sim_params_analytical.SRAM_input_size_options)
     SRAM_input_size_sweep = base_params.loc[:, SRAM_input_size_sweep_index]
     SRAM_input_size_sweep.loc["SRAM Input Size", :] = sim_params_analytical.SRAM_input_size_options
     all_params = pd.concat([all_params, SRAM_input_size_sweep], axis = 1)

     SRAM_filter_size_sweep_index = [0] * len(sim_params_analytical.SRAM_filter_size_options)
     SRAM_filter_size_sweep = base_params.loc[:, SRAM_filter_size_sweep_index]
     SRAM_filter_size_sweep.loc["SRAM Filter Size", :] = sim_params_analytical.SRAM_filter_size_options
     all_params = pd.concat([all_params, SRAM_filter_size_sweep], axis = 1)

     SRAM_output_size_sweep_index = [0] * len(sim_params_analytical.SRAM_output_size_options)
     SRAM_output_size_sweep = base_params.loc[:, SRAM_output_size_sweep_index]
     SRAM_output_size_sweep.loc["SRAM Output Size", :] = sim_params_analytical.SRAM_output_size_options
     all_params = pd.concat([all_params, SRAM_output_size_sweep], axis = 1)

     accumulator_elements_sweep_index = [0] * len(sim_params_analytical.accumulator_elements_options)
     accumulator_elements_sweep = base_params.loc[:, accumulator_elements_sweep_index]
     accumulator_elements_sweep.loc["SRAM Output Size", :] = sim_params_analytical.accumulator_elements_options
     all_params = pd.concat([all_params, accumulator_elements_sweep], axis = 1)


     print("\n\nALL PARAMS:")
     print(all_params, "\n\n")
     for col in range(all_params.shape[1]):
          hardware_wanted_single = all_params.iloc[:, col]
          search_solutions_run_sim(hardware_wanted_single)
     
     return(len(all_params))


def organize_hardware():
     global hardware_runspecs_existing, hardware_runspecs_wanted
     hardware_runspecs_existing = manage_saved_data(\
          sim_params_analytical.results_file_base_folder, \
               sim_params_analytical.sim_results_file_path_name)
     hardware_runspecs_wanted = pd.DataFrame(index = hardware_runspecs_names)


     #num_hardware = sweep_hardware_full()
     num_hardware = sweep_hardware_partial()

     hardware_runspecs_existing.to_csv(sim_params_analytical.sim_results_file_path_name)
     print("\nDone running simulator for all hardware states")
     if (sim_params_analytical.run_system_specs):
          #print(hardware_runspecs_wanted)
          (chip_specs, complete_final_specs) = run_system_specs(num_hardware, hardware_runspecs_wanted)
     if (sim_params_analytical.make_plots):
          make_plots(chip_specs, hardware_runspecs_wanted, complete_final_specs)
          #practice_plots_6.make_plot_1(complete_final_specs)  

def make_plots(chip_specs, hardware_runspecs_wanted, complete_final_specs):
     practice_plots_7.setup_plots(sim_params_analytical.NN_file_name, 1, sim_params_analytical.plots_folder_complete, complete_final_specs)
     practice_plots_7.plot_photonic_losses()
     practice_plots_7.plot_times()
     practice_plots_7.plot_power()
     #practice_plots_7.row_col_trends(complete_final_specs)


def run_system_specs(num_hardware, hardware_runspecs_wanted):
     col_repeat_idxs = np.repeat(range(num_hardware), len(sim_params_analytical.symbol_rate_options))
     hardware_runspecs_wanted_expanded = hardware_runspecs_wanted.iloc[:, col_repeat_idxs]
     symbol_rate_df = pd.DataFrame(sim_params_analytical.symbol_rate_options * num_hardware, \
          ["filler name"] * len(sim_params_analytical.symbol_rate_options) * num_hardware, ["Symbol Rate (GHz)"]).T
     hardware_runspecs_wanted_expanded = pd.concat([symbol_rate_df, hardware_runspecs_wanted_expanded])

     chip_specs = pd.DataFrame(index = chip_specs_names)

     for (columnName, hardware_runspecs_single) in hardware_runspecs_wanted_expanded.iteritems():
               chip_specs_single = system_specs_9.run_power_area_model(hardware_runspecs_single[runspecs_names],\
                     hardware_runspecs_single[hardware_names], hardware_runspecs_single["Symbol Rate (GHz)"] * 10**9)
               chip_specs.insert(chip_specs.shape[1], "filler name", chip_specs_single, allow_duplicates = True)    
     
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

