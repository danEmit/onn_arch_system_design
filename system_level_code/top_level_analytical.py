import sim_params_analytical
import pseudo_analytical_sim
import pprint
import pandas as pd
import specs_info

def sweep_hardware_configs(simulator):
     #hardware = pseudo_analytical_sim.hardware_state()

     batch_size_options = sim_params_analytical.batch_size_options
     array_size_options = sim_params_analytical.array_size_options
     SRAM_input_size_options  = sim_params_analytical.SRAM_input_size_options 
     SRAM_filter_size_options = sim_params_analytical.SRAM_filter_size_options 
     SRAM_output_size_options = sim_params_analytical.SRAM_output_size_options 
     accumulator_elements_options = sim_params_analytical.accumulator_elements_options


     for batch_size in batch_size_options:
          for array_size in array_size_options:
               for SRAM_input_size in SRAM_input_size_options:
                    for SRAM_filter_size in SRAM_filter_size_options:
                         for SRAM_output_size in SRAM_output_size_options:
                              for accumulator_elements in accumulator_elements_options:
                                   simulator.set_batch(batch_size)

                                   #hardware_state = {"Array Rows": array_size[0], "Array Cols": array_size[1], "SRAM Input Size": SRAM_input_size,\
                                   #     "SRAM Filter Size": SRAM_filter_size, "SRAM Output Size": SRAM_output_size, "Accumulator Elements":accumulator_elements}
                                   hardware_state = pd.DataFrame([array_size[0], array_size[1], SRAM_input_size,\
                                         SRAM_filter_size, SRAM_output_size, accumulator_elements], specs_info.hardware_specs_names)
                                   
                                   
                                   simulator.set_hardware(hardware_state)
                                   simulator.set_results_vars()
                                   sim_results = simulator.run_all_layers()
                                   x  =1
                                   
     x = 1

def main():
     simulator = pseudo_analytical_sim.hardware_state()
     print("\nSimulating performance of NN model \"", sim_params_analytical.NN_file_name, "\"", "\n", sep='')
     simulator.set_NN(sim_params_analytical.all_layers)
     sweep_hardware_configs(simulator)


if __name__ == "__main__":
    main()
    print("\n")

