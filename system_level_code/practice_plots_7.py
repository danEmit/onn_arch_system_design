import pandas as pd
import matplotlib.pyplot as plt
import itertools
import numpy as np

a100_throughput = 30000
a100_power_eff = 78
a100_power = 1000 * a100_throughput / a100_power_eff
a100_area = 826

NN_name = ""
include_nvidia = 0
plots_folder = ""

def setup_plots(name, nvidia, folder):
     global NN_name, include_nvidia, plots_folder
     NN_name = name
     include_nvidia = nvidia
     plots_folder = folder
      
def variable_batch(complete_specs, symbol_rate_options, array_size_options, batch_size_options):
     fixed_specs = ["SRAM Input Size", "SRAM Output Size", "SRAM Filter Size",\
          "Systolic Array Rows", "Systolic Array Cols", "Accumulator Elements"]
     fixed_values = complete_specs.loc[fixed_specs].iloc[:, 15]
     fixed_values["Systolic Array Rows"] = 128
     fixed_values["Systolic Array Cols"] = 128

     accepted_col = []
     for col in range(complete_specs.shape[1]):
          if complete_specs.loc[fixed_specs].iloc[:, col].equals(fixed_values):
               accepted_col.append(col)

     filtered_data = complete_specs.iloc[:, accepted_col]
     power = filtered_data.loc["Total Chip Power", :].to_list()
     area  = filtered_data.loc["Total Chip Area",  :].to_list()
     IPS   = filtered_data.loc["Inferences Per Second",  :].to_list()
     IPSW  = filtered_data.loc["Inferences Per Second Per Watt",  :].to_list()

     SR_spacing = 1
     batch_config_spacing = round(len(symbol_rate_options) *2)
     bar_pos = []
     batch_label_pos = []
     for batch_config_idx in range(len(batch_size_options)):
          batch_label_pos.append(batch_config_idx * batch_config_spacing + SR_spacing)
          for SR_idx in range(len(symbol_rate_options)):
               bar_pos.append(batch_config_idx * batch_config_spacing + SR_idx * SR_spacing)

     batch_label = ["Batch Size\n" + str(x) for x in batch_size_options]

     if include_nvidia:
          bar_pos.append(max(bar_pos) + 4)
          batch_label_pos.append(max(batch_label_pos) + 5)
          IPS.append(a100_throughput)
          IPSW.append(a100_power_eff)
          power.append(a100_power)
          area.append(a100_area)
          batch_label.append("NVIDIA A100")

     power_W = [x/1000 for x in power]
     p1 = plt.bar(bar_pos, power_W)
     plt.xticks(batch_label_pos, batch_label, fontsize = 7, rotation = 0)
     plt.ylabel("Power [W]")
     plt.yscale("log")
     plt.suptitle("Power vs Batch Size for " + str(NN_name), fontsize = 10)
     plt.title("Systolic Array, Accumulutor, and SRAM Sizes Held Constant", fontsize = 8)
     plt.savefig(plots_folder + "power_with_variable_batch", dpi = 300, bbox_inches = "tight")
     plt.close()

     p1 = plt.bar(bar_pos, area)
     plt.xticks(batch_label_pos, batch_label, fontsize = 7, rotation = 0)
     plt.ylabel("Area [mm ^ 2]")
     plt.yscale("log")
     plt.suptitle("Area vs Batch Size for " + str(NN_name), fontsize = 10)
     plt.title("Systolic Array, Accumulutor, and SRAM Sizes Held Constant", fontsize = 8)
     plt.savefig(plots_folder + "area_with_variable_batch", dpi = 300, bbox_inches = "tight")
     plt.close()

     delta = 0.8
     bar_pos_mod_L = [x * 2 for x in bar_pos]
     bar_pos_mod_R = [x + delta for x in bar_pos_mod_L]
     bar_pos_mod_avg = [(x + delta / 2) for x in bar_pos_mod_L]

     fig, axL = plt.subplots()
     axR = axL.twinx() 
     ln1 = axR.bar(bar_pos_mod_L, IPS,  color = "red", label = "IPS")
     ln2 = axL.bar(bar_pos_mod_R, IPSW, color = "blue", label = "IPS/W")
     #axL.set_yscale("log")
     #axR.set_yscale("log")
     axL.set_ylabel("Inferences Per Second")
     axR.set_ylabel("Inferences Per Second Per Watt")
     axL.set_yscale("log")
     axR.set_yscale("log")
     axR.grid(axis='y', color = "black", which='major', alpha = 0.5)
     axL.grid(axis='y', color = "black", which='major', alpha = 0.5)
     batch_label_pos_expanded = [2 * x + 0.5 for x in batch_label_pos]
     plt.xticks(batch_label_pos_expanded, batch_label, fontsize = 7, rotation = 0)
     #axL.set_xticks(x_pos_compare_mod_avg, labels = x_tick_labels_compare)
     #axR.set_xticks([])
     axR.legend()
     axL.legend()
     #lns = ln1+ln2
     #labs = [l.get_label() for l in lns]
     #axL.legend(lns, labs, loc=0)
     plt.suptitle("Overall Performance of NN Accelerator for ResNet50 v1.5")
     plt.title("Systolic Array, Accumulutor, and SRAM Sizes Held Constant", fontsize = 8)
     plt.savefig(plots_folder + "IPS_IPSW_with_variable_batch", dpi = 300, bbox_inches = "tight")
     plt.close()


def variable_array(complete_specs, symbol_rate_options, array_size_options, batch_size_options):
     fixed_specs = ["SRAM Input Size", "SRAM Output Size", "SRAM Filter Size",\
          "Batch Size", "Accumulator Elements"]
     fixed_values = complete_specs.loc[fixed_specs].iloc[:, 15]
     fixed_values["Batch Size"] = 16

     accepted_col = []
     for col in range(complete_specs.shape[1]):
          if complete_specs.loc[fixed_specs].iloc[:, col].equals(fixed_values):
               accepted_col.append(col)

     filtered_data = complete_specs.iloc[:, accepted_col]
     power = filtered_data.loc["Total Chip Power", :].to_list()
     area  = filtered_data.loc["Total Chip Area",  :].to_list()
     IPS   = filtered_data.loc["Inferences Per Second",  :].to_list()
     IPSW  = filtered_data.loc["Inferences Per Second Per Watt",  :].to_list()

     SR_spacing = 1
     array_config_spacing = round(len(symbol_rate_options) *2)
     bar_pos = []
     array_label_pos = []
     for array_config_idx in range(len(array_size_options)):
          array_label_pos.append(array_config_idx * array_config_spacing + SR_spacing)
          for SR_idx in range(len(symbol_rate_options)):
               bar_pos.append(array_config_idx * array_config_spacing + SR_idx * SR_spacing)

     array_label = ["Array Size\n" + str(x) for x in array_size_options]

     if include_nvidia:
          bar_pos.append(max(bar_pos) + 4)
          array_label_pos.append(max(array_label_pos) + 5)
          IPS.append(a100_throughput)
          IPSW.append(a100_power_eff)
          power.append(a100_power)
          area.append(a100_area)
          array_label.append("NVIDIA A100")

     power_W = [x/1000 for x in power]
     p1 = plt.bar(bar_pos, power_W)
     plt.xticks(array_label_pos, array_label, fontsize = 7, rotation = 0)
     plt.ylabel("Power [W]")
     plt.yscale("log")
     plt.suptitle("Power vs Array Size for " + str(NN_name), fontsize = 10)
     plt.title("Batch, Accumulutor, and SRAM Sizes Held Constant", fontsize = 8)
     plt.savefig(plots_folder + "power_with_variable_array", dpi = 300, bbox_inches = "tight")
     plt.close()

     p1 = plt.bar(bar_pos, area)
     plt.xticks(array_label_pos, array_label, fontsize = 7, rotation = 0)
     plt.ylabel("Area [mm ^ 2]")
     plt.yscale("log")
     plt.suptitle("Area vs Array Size for " + str(NN_name), fontsize = 10)
     plt.title("Batch, Accumulutor, and SRAM Sizes Held Constant", fontsize = 8)
     plt.savefig(plots_folder + "area_with_variable_array", dpi = 300, bbox_inches = "tight")
     plt.close()

     delta = 0.8
     bar_pos_mod_L = [x * 2 for x in bar_pos]
     bar_pos_mod_R = [x + delta for x in bar_pos_mod_L]
     bar_pos_mod_avg = [(x + delta / 2) for x in bar_pos_mod_L]

     fig, axL = plt.subplots()
     axR = axL.twinx() 
     ln1 = axR.bar(bar_pos_mod_L, IPS,  color = "red", label = "IPS")
     ln2 = axL.bar(bar_pos_mod_R, IPSW, color = "blue", label = "IPS/W")
     #axL.set_yscale("log")
     #axR.set_yscale("log")
     axL.set_ylabel("Inferences Per Second")
     axR.set_ylabel("Inferences Per Second Per Watt")
     axL.set_yscale("log")
     axR.set_yscale("log")
     axR.grid(axis='y', color = "black", which='major', alpha = 0.5)
     axL.grid(axis='y', color = "black", which='major', alpha = 0.5)
     array_label_pos_expanded = [2 * x + 0.5 for x in array_label_pos]
     plt.xticks(array_label_pos_expanded, array_label, fontsize = 7, rotation = 0)
     #axL.set_xticks(x_pos_compare_mod_avg, labels = x_tick_labels_compare)
     #axR.set_xticks([])
     axR.legend()
     axL.legend()
     #lns = ln1+ln2
     #labs = [l.get_label() for l in lns]
     #axL.legend(lns, labs, loc=0)
     plt.suptitle("Overall Performance of NN Accelerator for ResNet50 v1.5")
     plt.title("Batch, Accumulutor, and SRAM Sizes Held Constant", fontsize = 8)
     plt.savefig(plots_folder + "IPS_IPSW_with_variable_array", dpi = 300, bbox_inches = "tight")
     plt.close()
