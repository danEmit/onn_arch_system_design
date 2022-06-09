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

NN_name = ""
include_nvidia = 0
plots_folder = ""

chip_specs   = []
fixed_values = []
hardware_settings = []
hardware_names = []
# Helper Functions --------
def regular_to_dB(non_dB_val):
	return (10*math.log10(non_dB_val))

def dB_to_regular(dB_val):
	return (10 ** (dB_val / 10))

def setup_plots(name, nvidia, folder, chip_specs_insert, base_params):
     global NN_name, include_nvidia, plots_folder, chip_specs, fixed_values, hardware_settings, hardware_names
     NN_name = name
     include_nvidia = nvidia
     plots_folder = folder
     chip_specs = chip_specs_insert
     hardware_names = specs_info.hardware_specs_names.copy()
     hardware_names.append("Symbol Rate (GHz)")
     hardware_settings = chip_specs.loc[hardware_names, :]
     fixed_values = hardware_settings.iloc[:, 0]
     fixed_values = base_params
     fixed_values.loc["Symbol Rate (GHz)"] = 1



def filter_data(variable, fixed_value_input = 0):
     if fixed_value_input == 0:
          fixed_value_input = fixed_values.copy()
     fixed_specs = hardware_names.copy()
     fixed_specs.remove(variable)
     compare_vals = fixed_value_input.loc[fixed_specs].astype(float)
     accepted_col = []
     for col in range(chip_specs.shape[1]):
          if chip_specs.loc[fixed_specs].iloc[:, col].equals(compare_vals):
               accepted_col.append(col)

     filtered_data = chip_specs.iloc[:, accepted_col]
     return(filtered_data)

def plot_photonic_losses():
     for rows_constant in [0, 1]:
          if rows_constant:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
          else:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"

          filtered_data = filter_data(variable)

          array_param = filtered_data.loc[variable]
          combining_loss = filtered_data.loc["Power Loss Waveguide Power Combining"]
          crossbar_loss = filtered_data.loc["Power Loss Crossbar Junctions"]
          spliting_tree_loss = filtered_data.loc["Power Loss Splitting Tree"]
          total_photonic_loss_OMA = filtered_data.loc["Total Photonic Losses and OMA"]

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
          plt.title("All Other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + "photonics_losses_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()

def plot_times():
     for rows_constant in [0, 1, 2]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
          elif rows_constant == 2:
               variable = "Batch Size"
               file_term = "variable_batch"

          filtered_data = filter_data(variable)
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
          plt.title("All other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + "time_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()

          plt.plot(array_param, compute_portion, "-o")
          plt.plot(array_param, program_portion, "-o")
          plt.legend(["Compute Portion", "Program Portion"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("(Unitless)")
          plt.suptitle("Effect of " + variable + " on Inference Time")
          plt.title("All other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + "time_portions_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()

def plot_power():
     for rows_constant in [0, 1]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
     
          filtered_data = filter_data(variable)
          array_param = filtered_data.loc[variable]

          electronics_program_power = filtered_data.loc["Total Electronics Program Power"]
          electronics_compute_power = filtered_data.loc["Total Electronics Compute Power"]
          total_photonic_loss_OMA = filtered_data.loc["Total Laser Power from Wall mW Compute Adjusted"]
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
          #plt.yscale("log")
          plt.suptitle("Effect of " + variable + " on Chip Power")
          plt.title("All other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + "power_breakdown_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()

def plot_electronic_power_breakdown():
     for rows_constant in [0, 1]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"

          filtered_data = filter_data(variable)
          array_param = filtered_data.loc[variable]

          ADC_power = filtered_data.loc["ADCs Power"]
          DRAM_power = filtered_data.loc["DRAM Compute Power"]
          PS_power = filtered_data.loc["PS Power"]
          MRM_heater_power = filtered_data.loc["MRM Heaters Power"]
          ODAC_power = filtered_data.loc["ODAC Drivers Power"]
          total_electronic_power = filtered_data.loc["Total Electronics Compute Power"]

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
          plt.yscale("linear")
          plt.suptitle("Effect of " + variable + " on Different Electronic Compute Power Consumption")
          plt.title("Other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + "electronic_power_power_breakdown_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()


'''
# note assuming only one batch and symbol rate size
# also just one memory size, accumulator, etc
def row_col_trends(chip_specs):
     for rows_constant in [0, 1]:
          if rows_constant:
               selector = "Systolic Array Rows"
               variable = "Systolic Array Cols"
               file_term = "constant_rows"
          else:
               selector = "Systolic Array Cols"
               variable = "Systolic Array Rows"
               file_term = "constant_cols"
          fixed_spec = 8

          chip_specs_cols = chip_specs.loc[selector] == fixed_spec
          select_specs = chip_specs.iloc[:,[x for x in chip_specs_cols]]

          array_param = select_specs.loc[variable]
          combining_loss = select_specs.loc["Power Loss Waveguide Power Combining"]
          crossbar_loss = select_specs.loc["Power Loss Crossbar Junctions"]
          spliting_tree_loss = select_specs.loc["Power Loss Splitting Tree"]
          total_photonic_loss_OMA = select_specs.loc["Total Photonic Losses and OMA"]


          plt.plot(array_param, combining_loss, "-o")
          plt.plot(array_param, crossbar_loss,"o-")
          plt.plot(array_param, spliting_tree_loss, "o-")
          plt.plot(array_param, total_photonic_loss_OMA, "o-" )
          plt.legend(["Power Loss Waveguide Power Combining", "Power Loss Crossbar Junctions", "Power Loss Splitting Tree", "Total Photonic Losses and OMA"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Loss [dB]")
          plt.xscale("log")
          plt.yscale("linear")
          plt.suptitle("Effect of " + variable + " on Different Photonic Losses")
          plt.title(selector + " and other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + file_term + "_photonic_losses", dpi = DPI, bbox_inches = "tight")   
          plt.close()


          total_time = select_specs.loc["Total Time"]
          compute_time = select_specs.loc["Compute Portion"] * total_time 
          program_time = select_specs.loc["Program Portion"] * total_time
          IPS = select_specs.loc["Inferences Per Second"]
          IP_compute_time = 1 / compute_time
          IP_program_time = 1 / program_time


          plt.plot(array_param, total_time, "-o")
          plt.plot(array_param, compute_time,"o-")
          plt.plot(array_param, program_time, "o-")
          #plt.legend(["Inferences per total time", "Inferences per compute time", "Inferences per program time"])
          plt.legend(["Total Time", "Compute Time", "Program Time"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Rate [1/us]")
          plt.ylabel("Time [us]")
          #plt.xscale("log")
          #plt.yscale("log")
          plt.suptitle("Effect of " + variable + " on Inference Time")
          plt.title(selector + " and other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + file_term + "_time", dpi = DPI, bbox_inches = "tight")  
          plt.close()


          total_laser_power_dbm = select_specs.loc["Total Laser Power from Wall dBm"]
          total_laser_power     = select_specs.loc["Total Laser Power from Wall mW"]
          PD_power_total_dBm = total_laser_power_dbm + total_photonic_loss_OMA
          total_laser_power_waveguide_combining_dbm = PD_power_total_dBm - combining_loss
          total_laser_power_waveguide_combining = dB_to_regular(total_laser_power_waveguide_combining_dbm)     
          IPSW_laser_combining = IPS / total_laser_power_waveguide_combining
          IPSW_laser = IPS / total_laser_power

          plt.plot(array_param, IPSW_laser, "o-")
          plt.plot(array_param, IPSW_laser_combining, "o-")
          plt.legend(["IPS per watt of laser power", "IPS per watt of laser power\n if the only loss comes from \n1/n waveguide combining"], fontsize = 10)
          plt.xlabel(variable)
          plt.yscale("log")
          plt.ylabel("Inferences per second per watt")
          plt.grid("minor")
          plt.title("Effect of " + variable + " on IPSW")     
          plt.savefig(plots_folder + file_term + "_IPSW_photonics", dpi = DPI, bbox_inches = "tight")   
          plt.close()



          electronics_program_power = select_specs.loc["Total Electronics Program Power"]
          electronics_compute_power = select_specs.loc["Total Electronics Compute Power"]

          plt.plot(array_param, electronics_program_power, "-o")
          plt.plot(array_param, electronics_compute_power,"o-")
          plt.legend(["Total Electronics Program Power", "Total Electronics Compute Power"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Power [mW]")
          plt.xscale("linear")
          plt.yscale("linear")
          plt.suptitle("Effect of " + variable + " on Electronic Power Consumption")
          plt.title(selector + " and other Features Held Constant", fontsize = 8)
          plt.savefig(plots_folder + file_term + "_electronic_losses", dpi = DPI, bbox_inches = "tight")   
          plt.close()


          IPSW_electronics_program = IPS / electronics_program_power
          IPSW_electronic_compute = IPS / electronics_compute_power
          plt.plot(array_param, IPSW_laser, "o-")
          plt.plot(array_param, IPSW_laser_combining, "o-")
          plt.legend(["IPS per watt of electronics programming", "IPS per watt of electronic compute"], fontsize = 10)
          plt.xlabel(variable)
          plt.yscale("log")
          plt.ylabel("Inferences per second per watt")
          plt.grid("minor")
          plt.title("Effect of " + variable + " on IPSW")     
          plt.savefig(plots_folder + file_term + "_IPSW_electronics", dpi = DPI, bbox_inches = "tight")   
          plt.close()

'''