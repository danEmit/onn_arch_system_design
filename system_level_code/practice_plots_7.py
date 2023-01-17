import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import specs_info
import math
import seaborn as sns; sns.set_theme()

a100_throughput = 30000
a100_power_eff = 78
a100_power = 1000 * a100_throughput / a100_power_eff
a100_area = 826

DPI = 500
title_font_size = 8
xlabel_fontsize = 18
ylabel_fontsize = 18
xticks_fontsize = 15
yticks_fontsize = 15

NN_name = ""
include_nvidia = 0
plots_folder = ""

#chip_specs   = []
#fixed_values = []
#hardware_settings = []
#hardware_names = []
array_rows_sweep_data = []
array_cols_sweep_data = []
batch_size_sweep_data = []
SRAM_input_size_sweep_data = []
array_rows_cols_sweep_data = []
batch_SRAM_input_sweep_data = []

rows_variable_title = ""
cols_variable_title = ""
batch_variable_title = ""
SRAM_input_variable_title = ""
array_rows_cols_variable_title = ""
batch_SRAM_input_variable_title = ""

# Helper Functions --------
def regular_to_dB(non_dB_val):
	return (10*math.log10(non_dB_val))

def dB_to_regular(dB_val):
	return (10 ** (dB_val / 10))

def make_variable_sweep_title(data, sweep_variable_1, sweep_variable_2= ""):
     title = ""
     if sweep_variable_1 != "Systolic Array Rows" and sweep_variable_2 != "Systolic Array Rows":
          title += "Array Rows: " + str(round(data.loc["Systolic Array Rows"].iloc[0])) + ", "
     if sweep_variable_1 != "Systolic Array Cols" and sweep_variable_2 != "Systolic Array Cols":
          title += "Array Cols: " + str(round(data.loc["Systolic Array Cols"].iloc[0])) + ", "
     if sweep_variable_1 != "Batch Size" and sweep_variable_2 != "Batch Size":
          title += "Batch Size: " + str(round(data.loc["Batch Size"].iloc[0])) + ", "
     if sweep_variable_1 != "Accumulator Elements" and sweep_variable_2 != "Accumulator Elements" :
          value = data.loc["Accumulator Elements"].iloc[0]
          value = value / 1000000
          if value % 1 != 0:
               value = round(value, 1)
          else:
               value = int(value)
          title += "Accumulator Elements: " + str(value) + "M,\n"
     if sweep_variable_1 != "SRAM Input Size" and sweep_variable_2 != "SRAM Input Size":
          value = data.loc["SRAM Input Size"].iloc[0]
          value = value / 1000000
          if value % 1 != 0:
               value = round(value, 1)
          else:
               value = int(value)
          title += "SRAM Input Size: " + str(value) + "M, "
     if sweep_variable_1 != "SRAM Filter Size" and sweep_variable_2 != "SRAM Filter Size":
          value = data.loc["SRAM Input Size"].iloc[0]
          value = value / 1000000
          if value % 1 != 0:
               value = round(value, 1)
          else:
               value = int(value)
          title += "SRAM Filter Size: " + str(value) + "M, "
     if sweep_variable_1 != "SRAM Output Size" and sweep_variable_2 != "SRAM Output Size":
          value = data.loc["SRAM Output Size"].iloc[0]
          value = value / 1000000
          if value % 1 != 0:
               value = round(value, 1)
          else:
               value = int(value)
          title += "SRAM Output Size: " + str(value)  + "M"
     return(title)


def setup_plots(name, nvidia, folder, target_symbol_rate, array_rows_sweep_results, array_cols_sweep_results,\
 batch_size_sweep_results, SRAM_input_size_sweep_results, array_rows_cols_sweep_results, batch_SRAM_input_sweep_results):
     global NN_name, include_nvidia, plots_folder, \
     array_rows_sweep_data, array_cols_sweep_data, batch_size_sweep_data, SRAM_input_size_sweep_data, \
     array_rows_cols_sweep_data, batch_SRAM_input_sweep_data,\
     rows_variable_title, cols_variable_title, batch_variable_title, SRAM_input_variable_title, \
     array_rows_cols_variable_title, batch_SRAM_input_variable_title

     NN_name = name
     include_nvidia = nvidia
     plots_folder = folder

     #hardware_names = specs_info.hardware_specs_names.copy()
     #hardware_names.append("Symbol Rate (GHz)")
     #hardware_settings = chip_specs.loc[hardware_names, :]

     array_rows_sweep_data = array_rows_sweep_results
     array_cols_sweep_data = array_cols_sweep_results
     batch_size_sweep_data = batch_size_sweep_results
     SRAM_input_size_sweep_data = SRAM_input_size_sweep_results
     array_rows_cols_sweep_data = array_rows_cols_sweep_results
     batch_SRAM_input_sweep_data = batch_SRAM_input_sweep_results

     #array_rows_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 
     #array_cols_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 
     #batch_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 
     #SRAM_input_sweep_params.loc["Symbol Rate (GHz)", :] = target_symbol_rate 


     rows_variable_title = make_variable_sweep_title(array_rows_sweep_data, "Systolic Array Rows")
     cols_variable_title = make_variable_sweep_title(array_cols_sweep_data, "Systolic Array Cols")
     batch_variable_title = make_variable_sweep_title(batch_size_sweep_data, "Batch Size")
     SRAM_input_variable_title = make_variable_sweep_title(SRAM_input_size_sweep_data, "SRAM Input Size")
     array_rows_cols_variable_title =  make_variable_sweep_title(array_rows_cols_sweep_data, "Systolic Array Rows", "Systolic Array Cols")
     batch_SRAM_input_variable_title = make_variable_sweep_title(batch_SRAM_input_sweep_data, "Batch Size", "SRAM Input Size")

def plot_photonic_losses():
     print("Plotting photonic losses as a function of systolic array rows and cols")
     for rows_constant in [0, 1]:
          if rows_constant:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = cols_variable_title
          else:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = rows_variable_title

          array_param = filtered_data.loc[variable]
          combining_loss = filtered_data.loc["Power Loss Waveguide Power Combining"]
          crossbar_loss = filtered_data.loc["Power Loss Crossbar Junctions"]
          spliting_tree_loss = filtered_data.loc["Power Loss Splitting Tree"]
          total_photonic_loss_OMA = filtered_data.loc["Total Photonic Losses and OMA dBm"]
          crossbar_waveguides_loss = filtered_data.loc["Power Loss Crossbar Waveguides"]
          tx_waveguide_loss = filtered_data.loc["Power Loss Tx Waveguides"]


          plt.plot(array_param, combining_loss, "-o")
          plt.plot(array_param, crossbar_loss,"o-")
          plt.plot(array_param, spliting_tree_loss, "o-")
          plt.plot(array_param, total_photonic_loss_OMA, "o-" )
          plt.plot(array_param, crossbar_waveguides_loss, "o-" )
          plt.plot(array_param, tx_waveguide_loss, "o-" )
          plt.legend(["Power Loss Waveguide Power Combining", "Power Loss Crossbar Junctions", "Power Loss Splitting Tree",\
           "Total Photonic Losses and OMA", "Power Loss Crossbar Waveguides", "Power Loss Tx Waveguides"])
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
     print("Plotting effect of SA rows and columns and also batch size on inference time and ratio of compute to program time")
     for rows_constant in [0, 1, 2]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = cols_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = rows_variable_title
          else:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_size_sweep_data
               title = batch_variable_title

          array_param = filtered_data.loc[variable]
          compute_portion = filtered_data.loc["Compute Portion"]
          program_portion = filtered_data.loc["Program Portion"]
          total_time = filtered_data.loc["Total Time"]
          #IPS = filtered_data.loc["Inferences Per Second"]
          #total_time = 1/IPS
          compute_time = compute_portion * total_time 
          program_time = program_portion * total_time

          '''
          if (rows_constant == 2):
               total_time = total_time/array_param
               compute_time = compute_time / array_param
               program_time = program_time / array_param
          '''

          plt.plot(array_param, total_time, "-o")
          plt.plot(array_param, compute_time,"o-")
          plt.plot(array_param, program_time, "o-")
          #plt.legend(["Inferences per total time", "Inferences per compute time", "Inferences per program time"])
          plt.legend(["Total Time", "Compute Time", "Program Time"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Time [sec]")
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
          plt.suptitle("Effect of " + variable + " on Compute vs Program Time")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "time_portions_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()


def plot_power():
     print("Plotting high-level breakdown of system power as a function of systolic array rows and cols")
     for rows_constant in [0, 1, 2]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = cols_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = rows_variable_title
          else:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_size_sweep_data
               title = batch_variable_title
     
          array_param = filtered_data.loc[variable]

          electronics_program_power = filtered_data.loc["Electronics Program Power Time Adjusted"]
          electronics_compute_power = filtered_data.loc["Electronics Compute Power Time Adjusted"]
          laser_compute_power = filtered_data.loc["Total Laser Power from Wall Time Adjusted"]
          total_power = filtered_data.loc["Total Chip Power"]
          
          plt.plot(array_param, electronics_program_power, "-o")
          plt.plot(array_param, electronics_compute_power,"o-")
          plt.plot(array_param, laser_compute_power, "o-")
          plt.plot(array_param, total_power, "-o")
          #plt.legend(["Inferences per total time", "Inferences per compute time", "Inferences per program time"])
          plt.legend(["Programming Electronic Power", "Compute Electronic Power", "Compute Laser Power", "Total Chip Power"])
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("Power [mW]")
          #plt.xscale("log")
          #plt.yscale("log")
          plt.suptitle("Effect of " + variable + " on Chip Power (Time Adjusted)")
          plt.title(title, fontsize = int(1.5 *title_font_size))
          plt.savefig(plots_folder + "power_breakdown_" + file_term, dpi = DPI, bbox_inches = "tight")  
          plt.close()

def plot_electronic_power_breakdown():
     print("Plotting a breakdown of electronic power as a function of SA rows, SA cols, batch size, and SRAM input size")
     for rows_constant in [2]: # usually [0, 1, 2, 3]
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = cols_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = rows_variable_title
          elif rows_constant == 2:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_size_sweep_data
               title = batch_variable_title
          elif rows_constant == 3:
               variable = "SRAM Input Size"
               file_term = "variable_SRAM_input_size"
               filtered_data = SRAM_input_size_sweep_data
               title = SRAM_input_variable_title

          array_param = filtered_data.loc[variable]

          ADC_power = filtered_data.loc["ADCs Power"]
          DRAM_power = filtered_data.loc["DRAM Compute Power"]
          PS_power = filtered_data.loc["PS Power"]
          MRM_heater_power = filtered_data.loc["MRM Heaters Power"]
          ODAC_power = filtered_data.loc["ODAC Drivers Power"]
          total_electronic_power = filtered_data.loc["Electronics Compute Power"]
          accumulator_SRAM_power = filtered_data.loc["SRAM Accumulator Power"]

          plt.plot(array_param, ADC_power, "-o")
          plt.plot(array_param, DRAM_power,"o-")
          plt.plot(array_param, PS_power, "o-")
          plt.plot(array_param, MRM_heater_power, "o-" )
          plt.plot(array_param, ODAC_power, "o-")
          plt.plot(array_param, accumulator_SRAM_power, "o-")
          plt.plot(array_param, total_electronic_power, "o-" )
          plt.xticks(fontsize=xticks_fontsize)
          plt.yticks(fontsize=yticks_fontsize)
          plt.legend(["ADCs", "DRAM", "Ser/Des", "MRM Heater", "ODAC Driver", "Accumulator\nSRAM Power", "total"], fontsize = 12, bbox_to_anchor=(0.53, 0.38))
          plt.grid("minor")
          plt.xlabel(variable, fontsize = xlabel_fontsize)
          plt.ylabel("Power [mW]", fontsize = ylabel_fontsize)
          #plt.xscale("log")
          plt.yscale("log")
          #plt.suptitle("Effect of " + variable + " on Different Electronic Compute Power Consumption")
          #plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "electronic_power_breakdown_" + file_term, dpi = DPI, bbox_inches = "tight")   




          plt.close()

def IPSW():
     print("plotting IPSW and IPS as a function of SA rows, SA cols, and batch size")
     for rows_constant in [0, 1, 2]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = cols_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = rows_variable_title
          else:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_size_sweep_data
               title = batch_variable_title

          array_param = filtered_data.loc[variable]
          IPSW = filtered_data.loc["Inferences Per Second Per Watt"]
          IPS = filtered_data.loc["Inferences Per Second"]

          plt.plot(array_param, IPSW, "-o")
          #plt.legend("IPSW")
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("IPS/W")
          plt.yscale("linear")
          plt.suptitle("Effect of " + variable + " on Inferences per Second per Watt")
          plt.title(title, fontsize = int(1.5 * title_font_size))
          plt.savefig(plots_folder + "IPSW_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()

          plt.plot(array_param, IPS, "-o")
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("IPS")
          plt.yscale("linear")
          plt.suptitle("Effect of " + variable + " on Inferences per Second")
          plt.title(title, fontsize = title_font_size)
          plt.savefig(plots_folder + "IPS_notWatt_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()

def array_rows_cols_sweep_plots():
     print("Plotting IPS/W as function of SA rows AND cols")
     filtered_data = array_rows_cols_sweep_data
     row_vals = np.unique(filtered_data.loc["Systolic Array Rows"])
     col_vals = np.unique(filtered_data.loc["Systolic Array Cols"])
     IPSW = np.zeros((len(row_vals), len(col_vals)))
     for col in filtered_data:
          row_index = np.where(row_vals == filtered_data.loc["Systolic Array Rows", col])[0][0]
          col_index = np.where(col_vals == filtered_data.loc["Systolic Array Cols", col])[0][0]
          IPSW[row_index, col_index] = filtered_data.loc["Inferences Per Second Per Watt", col]

     ax = sns.heatmap(IPSW, cbar_kws={'label': 'IPS/W'})
     #plt.suptitle("Effect of Systolic Array Rows and Cols on IPS/W")
     plt.ylabel("Crossbar Array Rows", fontsize = ylabel_fontsize)
     plt.xlabel("Crossbar Array Cols", fontsize = xlabel_fontsize)

     plt.xticks(fontsize=xticks_fontsize)
     plt.yticks(fontsize=yticks_fontsize)

     ax.figure.axes[-1].yaxis.label.set_size(20)
     cbar = ax.collections[0].colorbar
     # here set the labelsize by 20
     cbar.ax.tick_params(labelsize=15)

     ax.set_xticklabels([str(int(x)) for x in col_vals])
     ax.set_yticklabels([str(int(x)) for x in row_vals])
     #plt.title("\n\n\n" + array_rows_cols_variable_title, fontsize = int(title_font_size))
     plt.savefig(plots_folder + "IPSW_rows_cols_2D", dpi = DPI, bbox_inches = "tight")
     plt.close()


def batch_SRAM_input_sweep_plots():
     print("Plotting IPS/W as function of batch and SRAM input")
     filtered_data = batch_SRAM_input_sweep_data
     row_vals = np.unique(filtered_data.loc["Batch Size"])
     col_vals = np.unique(filtered_data.loc["SRAM Input Size"])
     IPSW = np.zeros((len(row_vals), len(col_vals)))
     for col in filtered_data:
          row_index = np.where(row_vals == filtered_data.loc["Batch Size", col])[0][0]
          col_index = np.where(col_vals == filtered_data.loc["SRAM Input Size", col])[0][0]
          IPSW[row_index, col_index] = filtered_data.loc["Inferences Per Second Per Watt", col]

     ax = sns.heatmap(IPSW, cbar_kws={'label': 'IPS/W'})
     ax.figure.axes[-1].yaxis.label.set_size(20)
     cbar = ax.collections[0].colorbar
     # here set the labelsize by 20
     cbar.ax.tick_params(labelsize=15)


     #plt.suptitle("Effect of Batch Size and SRAM Input Size on IPS/W")
     plt.ylabel("Batch Size", fontsize = ylabel_fontsize)
     plt.xlabel("SRAM Input Size [MegaBytes]", fontsize = xlabel_fontsize)

     col_vals = col_vals * 6 / (8 * 1000000)
     col_vals = np.round(col_vals, 1)


     ax.set_yticklabels([str(int(x)) for x in row_vals])
     ax.set_xticklabels([str(int(x)) for x in col_vals])
     plt.xticks(fontsize=xticks_fontsize)
     plt.yticks(fontsize=yticks_fontsize)

     #plt.title(batch_SRAM_input_variable_title, fontsize = title_font_size)
     plt.savefig(plots_folder + "IPSW_batch_SRAM_input_2D", dpi = DPI, bbox_inches = "tight")
     plt.close()


def comps_of_IPSW():
     print("plotting the contributions of different power sources to 1/IPS/W")
     for rows_constant in [0, 1, 2]:
          if rows_constant == 0:
               variable = "Systolic Array Cols"
               file_term = "variable_cols"
               filtered_data = array_cols_sweep_data
               title = cols_variable_title
          elif rows_constant == 1:
               variable = "Systolic Array Rows"
               file_term = "variable_rows"
               filtered_data = array_rows_sweep_data
               title = rows_variable_title
          else:
               variable = "Batch Size"
               file_term = "variable_batch"
               filtered_data = batch_size_sweep_data
               title = batch_variable_title

          IPSW = filtered_data.loc["Inferences Per Second Per Watt"]
          IPS = filtered_data.loc["Inferences Per Second"]
          electronic_power_compute = filtered_data.loc["Electronics Compute Power Time Adjusted"]
          photonics_power_compute  = filtered_data.loc["Total Laser Power from Wall Time Adjusted"]
          ADC_power_compute = filtered_data.loc["ADCs Power"] * filtered_data.loc["Compute Portion"]

          inverse_IPSW = 1 / IPSW
          IPS_electronic_compute = (1 / 1000) * electronic_power_compute / IPS
          IPS_photonics_compute = (1 / 1000) * photonics_power_compute / IPS
          IPS_ADC_compute = (1 / 1000) * ADC_power_compute / IPS

          array_param = filtered_data.loc[variable]
          plt.plot(array_param, inverse_IPSW, "-o")
          plt.plot(array_param, IPS_electronic_compute, "-o")
          plt.plot(array_param, IPS_photonics_compute,  "-o")
          plt.plot(array_param, IPS_ADC_compute,  "-o")
          plt.grid("minor")
          plt.xlabel(variable)
          plt.ylabel("W * sec / inference")
          plt.yscale("log")
          plt.suptitle("Effect of " + variable + " on various powers vs IPS")
          plt.title(title, fontsize = int(title_font_size))
          plt.legend(["1 / IPS/W", "Electronics Compute Power / IPS", "Photonics Compute Power / IPS", "ADC Compute Power / IPS"])
          plt.savefig(plots_folder + "comps_of_IPWS_inverse_" + file_term, dpi = DPI, bbox_inches = "tight")   
          plt.close()


def IPS_dual_core_manual_data():
     print("plotting the effect of dual vs single core on IPS vs batch size")

     IPS_single_core = [400.737357, 2934.389401, 2934.389401, 2934.389401, 2934.389401, 2934.389401]
     IPS_dual_core   = [352.586135, 1532.070682, 2013.089511, 2387.959051, 2633.124002, 2775.545584]

     array_param = batch_size_sweep_data.loc["Batch Size"]
     title = batch_variable_title

     plt.figure(figsize=(10 * 1.15, 2.3 * 1.15))
     plt.plot(array_param, IPS_single_core, "-o")
     plt.plot(array_param, IPS_dual_core, "-o")
     plt.grid("minor")
     plt.xlabel("Batch Size", fontsize = xlabel_fontsize)
     plt.ylabel("IPS", fontsize = ylabel_fontsize)
     plt.yscale("linear")
     #plt.suptitle("Effect of Batch Size on IPS in Single- and Dual-Core Crossbar Acccelerators")
     #plt.subplots_adjust(top=0.78)
     #plt.title(title, fontsize = title_font_size)
     plt.legend(['Dual Core', 'Single Core'])
     #plt.tight_layout()
     


     plt.xticks(fontsize=xticks_fontsize)
     plt.yticks(fontsize=yticks_fontsize)

     #plt.show()
     #set_size_inches(30, 10.5)
     plt.savefig(plots_folder + "IPS_variable_batch_dual_single_core", dpi = DPI, bbox_inches = "tight")   
     plt.close()



def single_config_breakdown():
     print("taking a certain optimal config and making breakdown of power and area")

     ADCsPower = 3200.0
     PCMHeaterPower = 16384 * 0.179186040588822
     DRAMComputePower = 15026.2439258661
     PSPower = 1536

     totalElectronicsPowerTimeAdjusted = 25100
     electronicPowerRemainder = totalElectronicsPowerTimeAdjusted - ADCsPower - PCMHeaterPower  - DRAMComputePower - PSPower
     laserWallPower = 5313.15043252708

     powers = [ADCsPower, PCMHeaterPower, DRAMComputePower, laserWallPower, electronicPowerRemainder, PSPower]
     total = sum(powers)
     labels = ['ADCs', 'PCM Heater', 'DRAM (Compute)', "Laser Power\nFrom Wall", "Other Electronic\n Power",  'Ser/Des']

     print(labels)
     print(powers)
     print([100 * i / total for i in powers] )


     ADCsArea = 6.08
     SRAMArea = 99.9
     CrossbarArea = 6.5536 * 2
     totalPhotonicsArea = 13.13751
     remainingPhotonicsArea = totalPhotonicsArea - CrossbarArea
     totalElectronicsArea = 107.9192
     remainingElectronicsArea = totalElectronicsArea - ADCsArea - SRAMArea

     areas = [ADCsArea, SRAMArea, CrossbarArea, remainingElectronicsArea, remainingPhotonicsArea]
     totalArea = sum(areas)
     labels = ["ADCs Area", "SRAM Area", "Crossbar Area", "Other Electronics Area", "Other Photonics Area"]

     print(labels)
     print(areas)
     print([100 * i / totalArea for i in areas])



     '''
     fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
     def func(pct, allvals):
         absolute = int(np.round(pct/100.*np.sum(allvals)))
         return "{:.1f}%\n({:d} g)".format(pct, absolute)


     wedges, texts, autotexts = ax.pie(powers, autopct=lambda pct: func(pct, powers),
                                       textprops=dict(color="w"))

     ax.legend(wedges, labels,
               title="Ingredients",
               loc="center left",
               bbox_to_anchor=(1, 0, 0.5, 1))

     plt.setp(autotexts, size=8, weight="bold")

     ax.set_title("Matplotlib bakery: A pie")



     fig1, ax1 = plt.subplots()
     wedges, texts, autotexts = ax1.pie(powers, labels=labels, autopct=lambda p: '{:.1f} W'.format(p * total / (100 * 1000)),
        shadow=False, startangle=0)

     #ax1.legend(wedges, labels,
     #     title="Ingredients",
     #     loc="center left",
     #     bbox_to_anchor=(1, 0, 0.5, 1))
     #plt.setp(autotexts, size=8, weight="bold")

     ax1.axis('equal') 

     plt.savefig(plots_folder + "power_breakdown", dpi = 500, bbox_inches = "tight")   



     '''
















