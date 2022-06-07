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

def sweep_hardware_configs(simulator):
     hardware_runspecs_existing = manage_saved_data(\
          sim_params_analytical.results_file_base_folder, \
               sim_params_analytical.sim_results_file_path_name)
     hardware_runspecs_wanted = pd.DataFrame(index = hardware_runspecs_names)

     num_hardware = 0
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
                                   hardware_wanted_single = pd.DataFrame(hardware_wanted_single, index = hardware_names)
                                   
                                   print("\n---------------------------------")
                                   print("Searching for results with desired hardware state:")
                                   print("     Array Size:       ", array_size[0], "x", array_size[1])
                                   print("     SRAM Input Size:  ", SRAM_input_size)
                                   print("     SRAM Filter Size: ", SRAM_filter_size)
                                   print("     SRAM Output Size: ", SRAM_output_size)
                                   print("     Accumulator Elements per Col: ", accumulator_elements)
                                   print("     Batch Size: ", batch_size)
                                   #print("---------------------------------")

                                   need_run_sim = 1
                                   for existing_result in hardware_runspecs_existing:
                                        if (hardware_wanted_single.iloc[:, 0].equals(hardware_runspecs_existing.loc[hardware_names, existing_result])):
                                             need_run_sim = 0
                                             hardware_runspecs_wanted.insert(hardware_runspecs_wanted.shape[1], "filler name", \
                                                  hardware_runspecs_existing.loc[hardware_runspecs_names, existing_result], allow_duplicates=True)
                                             print("Found existing results for this hardware state")
                                             break

                                   if (need_run_sim):       
                                        print("\nDid not find existing results for this hardware state, will now run simulation")    
                                        simulator.set_hardware(hardware_wanted_single)   
                                        midlevel_specs_single = simulator.run_all_layers()
                                        hardware_runspecs_wanted.insert(hardware_runspecs_wanted.shape[1], \
                                             "filler name", pd.concat([hardware_wanted_single, midlevel_specs_single]), allow_duplicates=True)
                                        hardware_runspecs_existing.insert(hardware_runspecs_existing.shape[1], \
                                             "filler name", pd.concat([hardware_wanted_single, midlevel_specs_single]), allow_duplicates=True)                                             
                                        hardware_runspecs_existing.to_csv(sim_params_analytical.sim_results_file_path_name)
                                   print("---------------------------------")

     hardware_runspecs_existing.to_csv(sim_params_analytical.sim_results_file_path_name)
     print("\nDone running simulator on for all hardware states")
     if (sim_params_analytical.run_system_specs):
          (chip_specs, complete_final_specs) = run_system_specs(num_hardware, hardware_runspecs_wanted)
     if (sim_params_analytical.make_plots):
          make_plots(chip_specs, hardware_runspecs_wanted, complete_final_specs)
          #practice_plots_6.make_plot_1(complete_final_specs)  

def make_plots(chip_specs, hardware_runspecs_wanted, complete_final_specs):
     '''
     practice_plots_6.prepare_plot_specs(sim_params_analytical.symbol_rate_options, sim_params_analytical.array_size_options, sim_params_analytical.batch_size_options)
     practice_plots_6.prepare_chip_specs(chip_specs)
     practice_plots_6.plot_power(chip_specs)
     practice_plots_6.plot_area(chip_specs)
     practice_plots_6.plot_inf_specs(chip_specs)

     params_interest = [["ADCs Power", "DRAM Program Power", "DRAM Compute Power", "PCM Heaters Power"], []]
     params_total_quantities = ["Total Combined Electronics Power", "Total Laser Power from Wall mW"]
     params_other_names = ["Other Electrical Power"]
     practice_plots_6.power_breakdown(chip_specs, params_interest, params_total_quantities, params_other_names)
     '''
     '''
     practice_plots_7.setup_plots(sim_params_analytical.NN_file_name, 1, sim_params_analytical.plots_folder_complete)
     practice_plots_7.variable_batch(complete_final_specs, sim_params_analytical.symbol_rate_options, \
          sim_params_analytical.array_size_options, sim_params_analytical.batch_size_options)  
     practice_plots_7.variable_array(complete_final_specs, sim_params_analytical.symbol_rate_options, \
          sim_params_analytical.array_size_options, sim_params_analytical.batch_size_options)  
     '''
     practice_plots_7.setup_plots(sim_params_analytical.NN_file_name, 1, sim_params_analytical.plots_folder_complete)
     practice_plots_7.row_col_trends(complete_final_specs)


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
     simulator = pseudo_analytical_sim.hardware_state()
     print("\nSimulating performance of NN model \"", sim_params_analytical.NN_file_name, "\"", "\n", sep='')
     simulator.set_NN(sim_params_analytical.all_layers)
     sweep_hardware_configs(simulator)


if __name__ == "__main__":
    main()
    print("\n")

