import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import specs_info
import math

a100_throughput = 30000
a100_power_eff = 78
a100_power = 1000 * a100_throughput / a100_power_eff
a100_area = 826

DPI = 300
title_font_size = 6

NN_name = ""
include_nvidia = 0
plots_folder = ""

#chip_specs   = []
#fixed_values = []
#hardware_settings = []
#hardware_names = []
array_rows_sweep_data = []
array_cols_sweep_data = []
batch_sweep_data = []
SRAM_input_sweeo_data = []

rows_variable_title = ""
cols_variable_title = ""
batch_variable_title = ""
SRAM_input_variable_title = ""

# Helper Functions --------
def regular_to_dB(non_dB_val):
	return (10*math.log10(non_dB_val))

def dB_to_regular(dB_val):
	return (10 ** (dB_val / 10))

def setup_plots(name, nvidia, folder, chip_specs, target_symbol_rate, array_rows_sweep_params, array_cols_sweep_params, batch_sweep_params, SRAM_input_sweep_params):
     global NN_name, include_nvidia, plots_folder, array_rows_sweep_data, array_cols_sweep_data, batch_sweep_data, SRAM_input_sweep_data,\
     rows_variable_title, cols_variable_title, batch_variable_title, SRAM_input_variable_title
     NN_name = name
     include_nvidia = nvidia
     plots_folder = folder

     hardware_names = specs_info.hardware_specs_names.copy()
     hardware_names.append("Symbol Rate (GHz)")
     hardware_settings = chip_specs.loc[hardware_names, :]

     array_rows_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 
     array_cols_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 
     batch_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 
     SRAM_input_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 

     array_rows_sweep_data = pd.DataFrame([], index = chip_specs.index)
     array_cols_sweep_data = pd.DataFrame([], index = chip_specs.index)
     batch_sweep_data = pd.DataFrame([], index = chip_specs.index)
     SRAM_input_sweep_data = pd.DataFrame([], index = chip_specs.index)

     for array_rows in range(array_rows_sweep_params.shape[1]):
          for col in range(chip_specs.shape[1]):
               if array_rows_sweep_params.iloc[:, array_rows].equals(hardware_settings.iloc[:, col]):
                    array_rows_sweep_data.loc[:, array_rows_sweep_data.shape[1]] = chip_specs.iloc[:, col]

     for array_cols in range(array_cols_sweep_params.shape[1]):
          for col in range(chip_specs.shape[1]):
               if array_cols_sweep_params.iloc[:, array_cols].equals(hardware_settings.iloc[:, col]):
                    array_cols_sweep_data.loc[:, array_cols_sweep_data.shape[1]] = chip_specs.iloc[:, col]

     for batch in range(batch_sweep_params.shape[1]):
          for col in range(chip_specs.shape[1]):
               if batch_sweep_params.iloc[:, batch].equals(hardware_settings.iloc[:, col]):
                    batch_sweep_data.loc[:, batch_sweep_data.shape[1]] = chip_specs.iloc[:, col]

     for SRAM_input in range(SRAM_input_sweep_params.shape[1]):
          for col in range(chip_specs.shape[1]):
               if SRAM_input_sweep_params.iloc[:, SRAM_input].equals(hardware_settings.iloc[:, col]):
                    SRAM_input_sweep_data.loc[:, SRAM_input_sweep_data.shape[1]] = chip_specs.iloc[:, col]

     rows_variable_title = "Array Cols: " + str(round(array_rows_sweep_data.loc["Systolic Array Cols", 0])) +\
      ", SRAM Input Size: "  + str(round(array_rows_sweep_data.loc["SRAM Input Size", 0])) + \
      ", SRAM Filter Size: " + str(round(array_rows_sweep_data.loc["SRAM Filter Size", 0])) + \
      ",\nSRAM Output Size: " + str(round(array_rows_sweep_data.loc["SRAM Output Size", 0])) + \
      ", Batch Size: "       + str(round(array_rows_sweep_data.loc["Batch Size", 0])) + \
      ", Accumulator Elements: " + str(round(array_rows_sweep_data.loc["Accumulator Elements", 0])) 

     cols_variable_title = "Array Rows: " + str(round(array_cols_sweep_data.loc["Systolic Array Rows", 0])) +\
      ", SRAM Input Size: "  + str(round(array_cols_sweep_data.loc["SRAM Input Size", 0])) + \
      ", SRAM Filter Size: " + str(round(array_cols_sweep_data.loc["SRAM Filter Size", 0])) + \
      ",\nSRAM Output Size: " + str(round(array_cols_sweep_data.loc["SRAM Output Size", 0])) + \
      ", Batch Size: "       + str(round(array_rows_sweep_data.loc["Batch Size", 0])) + \
      ", Accumulator Elements: " + str(round(array_cols_sweep_data.loc["Accumulator Elements", 0])) 

     batch_variable_title = "Array Rows: " + str(round(batch_sweep_data.loc["Systolic Array Rows", 0])) +\
      ", Array Cols: " + str(round(batch_sweep_data.loc["Systolic Array Cols", 0])) +\
      ", SRAM Input Size: "  + str(round(batch_sweep_data.loc["SRAM Input Size", 0])) + \
      ",\nSRAM Filter Size: " + str(round(batch_sweep_data.loc["SRAM Filter Size", 0])) + \
      ", SRAM Output Size: " + str(round(batch_sweep_data.loc["SRAM Output Size", 0])) + \
      ", Accumulator Elements: " + str(round(batch_sweep_data.loc["Accumulator Elements", 0])) 

     SRAM_input_variable_title = "Array Rows: " + str(round(batch_sweep_data.loc["Systolic Array Rows", 0])) +\
      ", Array Cols: " + str(round(batch_sweep_data.loc["Systolic Array Cols", 0])) +\
      ", SRAM Filter Size: " + str(round(batch_sweep_data.loc["SRAM Filter Size", 0])) + \
      ",\nSRAM Output Size: " + str(round(batch_sweep_data.loc["SRAM Output Size", 0])) + \
      ", Batch Size: "       + str(round(array_rows_sweep_data.loc["Batch Size", 0])) + \
      ", Accumulator Elements: " + str(round(batch_sweep_data.loc["Accumulator Elements", 0])) 

def plot_photonic_losses():
     for rows_constant in [0, 1]:
          if rows_constant:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = rows_variable_title
          else:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = cols_variable_title

          array_param = filtered_data.loc[variable]
          combining_loss = filtered_data.loc["Power Loss Waveguide Power Combining"]
          crossbar_loss = filtered_data.loc["Power Loss Crossbar Junctions"]
          spliting_tree_loss = filtered_data.loc["Power Loss Splitting Tree"]
          total_photonic_loss_OMA = filtered_data.loc["Total Photonic Losses and OMA dBm"]

          plt.plot(array_param, combining_loss, "-o")
          plt.plot(array_param, crossbar_loss,"o-")
          plt.plot(array_param, spliting_tree_loss, "o-")
          plt.plot(array_param, total_photonic_loss_OMA, "o-" )
          plt.legend(["Power Loss Waveguide Power Combining", "Power Loss Crossbar Junctions", "Power Loss Splitting Tree", "Total Photonic Losses and OMA"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Loss [dB]")
          #plt.xscale("log")
          plt.yscale("linear")
          plt.suptitle("Effect of " + variable + " on Different Photonic Losses")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "photonics_losses_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()

def plot_times():
     for rows_constant in [0, 1, 2]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = rows_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = cols_variable_title
          else:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_sweep_data
               title = batch_variable_title

          array_param = filtered_data.loc[variable]
          compute_portion = filtered_data.loc["Compute Portion"]
          program_portion = filtered_data.loc["Program Portion"]
          total_time = filtered_data.loc["Total Time"]
          #IPS = filtered_data.loc["Inferences Per Second"]
          #total_time = 1/IPS
          compute_time = compute_portion * total_time 
          program_time = program_portion * total_time

          if (rows_constant == 2):
               total_time = total_time/array_param
               compute_time = compute_time / array_param
               program_time = program_time / array_param

          plt.plot(array_param, total_time, "-o")
          plt.plot(array_param, compute_time,"o-")
          plt.plot(array_param, program_time, "o-")
          #plt.legend(["Inferences per total time", "Inferences per compute time", "Inferences per program time"])
          plt.legend(["Total Time", "Compute Time", "Program Time"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Time [us]")
          #plt.xscale("log")
          #plt.yscale("log")
          plt.suptitle("Effect of " + variable + " on Inference Time")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "time_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()

          plt.plot(array_param, compute_portion, "-o")
          plt.plot(array_param, program_portion, "-o")
          plt.legend(["Compute Portion", "Program Portion"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("(Unitless)")
          plt.suptitle("Effect of " + variable + " on Inference Time")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "time_portions_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()

def plot_power():
     for rows_constant in [0, 1]:
          if rows_constant:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = rows_variable_title
          else:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = cols_variable_title
     
          array_param = filtered_data.loc[variable]

          electronics_program_power = filtered_data.loc["Electronics Program Power Time Adjusted"]
          electronics_compute_power = filtered_data.loc["Electronics Compute Power Time Adjusted"]
          total_photonic_loss_OMA = filtered_data.loc["Total Laser Power from Wall Time Adjusted"]
          total_power = filtered_data.loc["Total Chip Power"]
          
          plt.plot(array_param, electronics_program_power, "-o")
          plt.plot(array_param, electronics_compute_power,"o-")
          plt.plot(array_param, total_photonic_loss_OMA, "o-")
          plt.plot(array_param, total_power, "-o")
          #plt.legend(["Inferences per total time", "Inferences per compute time", "Inferences per program time"])
          plt.legend(["Programming Electronic Power", "Compute Electronic Power", "Compute Laser Power", "Total Chip Power"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Power [mW]")
          #plt.xscale("log")
          plt.yscale("log")
          plt.suptitle("Effect of " + variable + " on Chip Power")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "power_breakdown_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()

def plot_electronic_power_breakdown():
     for rows_constant in [0, 1, 2, 3]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = rows_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = cols_variable_title
          elif rows_constant == 2:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_sweep_data
               title = batch_variable_title
          elif rows_constant == 3:
               variable = "SRAM Input Size"
               file_term = "variable_SRAM_input_size"
               filtered_data = SRAM_input_sweep_data
               title = SRAM_input_variable_title

          array_param = filtered_data.loc[variable]

          ADC_power = filtered_data.loc["ADCs Power"]
          DRAM_power = filtered_data.loc["DRAM Compute Power"]
          PS_power = filtered_data.loc["PS Power"]
          MRM_heater_power = filtered_data.loc["MRM Heaters Power"]
          ODAC_power = filtered_data.loc["ODAC Drivers Power"]
          total_electronic_power = filtered_data.loc["Electronics Compute Power"]

          plt.plot(array_param, ADC_power, "-o")
          plt.plot(array_param, DRAM_power,"o-")
          plt.plot(array_param, PS_power, "o-")
          plt.plot(array_param, MRM_heater_power, "o-" )
          plt.plot(array_param, ODAC_power, "o-")
          plt.plot(array_param, total_electronic_power, "o-" )
          plt.legend(["ADCs", "DRAM", "Ser/Des", "MRM Heater", "ODAC Driver", "total"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Power [mW]")
          #plt.xscale("log")
          plt.yscale("log")
          plt.suptitle("Effect of " + variable + " on Different Electronic Compute Power Consumption")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "electronic_power_power_breakdown_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()

def IPSW():
     for rows_constant in [0, 1, 2]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = rows_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = cols_variable_title
          else:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_sweep_data
               title = batch_variable_title

          array_param = filtered_data.loc[variable]
          IPSW = filtered_data.loc["Inferences Per Second Per Watt"]
          plt.plot(array_param, IPSW, "-o")
          #plt.legend("IPSW")
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("IPSW")
          plt.yscale("linear")
          plt.suptitle("Effect of " + variable + " on Inferences per Second per Watt")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "IPSW_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()





