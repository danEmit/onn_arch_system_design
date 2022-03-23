import pandas as pd
import matplotlib.pyplot as plt
import itertools

a100_throughput = 30000
a100_power_eff = 78
a100_power = 1000 * a100_throughput / a100_power_eff
a100_area = 826

color_options = [["indianred", "brown", "red", "coral", "lightsalmon"], ["forestgreen", "limegreen", "darkgreen", "olivedrab", "mediumseagreen"], ["navy", "royalblue", "dodgerblue", "blue", "cornflowerblue"]]
x_pos_base = []
x_pos_compare = []
x_tick_labels_base = []
x_tick_labels_compare = []
colors_base = ["blue"] * 12
colors_compare = ["blue"] * 12 + ["purple"]
colors_compare_2 = ["red"] * 12 + ["orange"]
array_sizes = []


def prepare_plot_specs(symbol_rate_options, array_size_options):
      
      global x_pos_base, x_pos_compare, x_tick_labels_base, x_tick_labels_compare, array_sizes
      SR_spacing = 1
      array_config_spacing = round(len(symbol_rate_options) *1.5)
      for array_config_idx in range(len(array_size_options)):
            for SR_idx in range(len(symbol_rate_options)):
                  x_pos_base.append(array_config_idx * array_config_spacing + SR_idx * SR_spacing)
        
      x_pos_compare = x_pos_base.copy()
      x_pos_compare.append(max(x_pos_base) + 4)
      x_tick_labels_base = [str(x) + " GHz" for x in symbol_rate_options] * len(array_size_options)
      x_tick_labels_compare = x_tick_labels_base.copy()
      x_tick_labels_compare.append("NVIDIA A100")
      
      array_sizes = array_size_options

def prepare_chip_specs(chip_specs):
      chip_specs.insert(chip_specs.shape[1], "A100", [0] * chip_specs.shape[0])
      
      chip_specs.loc["Total Chip Power", "A100"] = a100_power 
      chip_specs.loc["Total Chip Area", "A100"]  = a100_area
      chip_specs.loc["Inferences Per Second Per Watt", "A100"] = a100_power_eff 
      chip_specs.loc["Inferences Per Second", "A100"] = a100_throughput
      
      chip_specs.loc["x position"] = x_pos_compare
      chip_specs.loc["x tick label"] = x_tick_labels_compare
      chip_specs.columns = x_tick_labels_compare
      

def plot_power(chip_specs):
      #chip_specs.loc["Total Chip Power"].plot(kind= "bar")
      plt.bar(x_pos_compare, chip_specs.loc["Total Chip Power"], color = colors_compare)

      plt.yscale("log")
      plt.xlabel("\n\nArray Configuration")
      plt.ylabel("Total Chip Power [mW, log scale]")
      plt.suptitle("Total Accelerator System Power")
      plt.title("For ResNet50 V1.5")
      plt.xticks(x_pos_compare, x_tick_labels_compare, fontsize = 7, rotation = 45)
      plt.grid(axis='y', color = "black", which='minor', alpha = 0.25)
      plt.grid(axis='y', color = "black", which='major', alpha = 0.6)

      space = "         " 
      array_label = "8 x 8" + space + "16 x 16" + space + "32 x 32" + space + "64 x 64"
      plt.text(0.05, 75, array_label)
      plt.show()
      
def plot_area(chip_specs):
      #chip_specs.loc["Total Chip Area"].plot(kind= "bar")
      plt.bar(x_pos_compare, chip_specs.loc["Total Chip Area"], color = colors_compare)

      plt.yscale("log")
      plt.xlabel("\n\nArray Configuration")
      plt.ylabel("Total Chip Power [mm^2, log scale]")
      plt.suptitle("Total Accelerator System Area")
      #plt.title("For ResNet50 V1.5")
      plt.xticks(x_pos_compare, x_tick_labels_compare, fontsize = 8, rotation = 45)
      plt.grid(axis='y', color = "black", which='minor', alpha = 0.25)
      plt.grid(axis='y', color = "black", which='major', alpha = 0.6)
      
      space = "         " 
      array_label = "8 x 8" + space + "16 x 16" + space + "32 x 32" + space + "64 x 64"
      plt.text(0.05, 0.04, array_label)
      
      plt.show()

def plot_inf_specs(chip_specs):
      delta = 0.8
      x_pos_compare_mod_L = [x * 2 for x in x_pos_compare]
      x_pos_compare_mod_R = [x + delta for x in x_pos_compare_mod_L]
      x_pos_compare_mod_avg = [(x + delta / 2) for x in x_pos_compare_mod_L]

      
      fig, axL = plt.subplots()
      axR = axL.twinx() 
      axR.bar(x_pos_compare_mod_L, chip_specs.loc["Inferences Per Second Per Watt"], color = colors_compare)
      axL.bar(x_pos_compare_mod_R, chip_specs.loc["Inferences Per Second"], color = colors_compare_2)
      axL.set_yscale("log")
      #axR.set_yscale("log")
      axL.set_ylabel("Inferences Per Second")
      axR.set_ylabel("Inferences Per Second Per Watt")
      axR.grid(axis='y', color = "black", which='major', alpha = 0.5)
      axL.grid(axis='y', color = "black", which='major', alpha = 0.5)
      #axL.set_xticks(x_pos_compare_mod_avg, labels = x_tick_labels_compare)
      #axR.set_xticks([])

      plt.suptitle("Overall Performance of NN Accelerator for ResNet50 v1.5")
      #axL.set_xticks(x_pos_compare_mod_avg)#, x_tick_labels_compare)# fontsize = 1, rotation = 45)
      #axL.set_xticklabels(x_tick_labels_compare)
      plt.show()

def power_breakdown(chip_specs, params_interest, params_total_quantities, params_other_names):
      final_params_plot = []
      for params_other_name, params_total_quantity in itertools.zip_longest(params_other_names, params_total_quantities):
            if (params_other_name == None):
                  final_params_plot.append(params_total_quantity)
                  break
            chip_specs.loc[params_other_name] = chip_specs.loc[params_total_quantity]
      
      for params_other_name, params_group in zip(params_other_names, params_interest):
            final_params_plot.append(params_other_name)
            for param in params_group:
                  final_params_plot.append(param)
                  chip_specs.loc[params_other_name] = chip_specs.loc[params_other_name] - chip_specs.loc[param]
                  
                  
      col_idx = 4
      plt.pie(chip_specs.iloc[:, 0].loc[final_params_plot], autopct='%1.1f%%')
      plt.legend(final_params_plot)
      array = array_sizes[col_idx % len(array_sizes)]
      plt.suptitle("Power Breakdown for Array Size " + str(array[0]) + "x" + str(array[1]) + ", " + x_tick_labels_compare[col_idx])
      plt.title("Total Power " + str(round(chip_specs.iloc[chip_specs.index.get_loc("Total Chip Power"), col_idx], 2)) + " mW, ResNet50 V1.5")
      plt.show()
      



def make_stacked_bar_plot(chip_specs, params_interest, params_total_quantities, params_other_names, symbol_rate_options, array_configs, ylabel):
      final_params_plot = []
      for params_other_name, params_total_quantity in itertools.zip_longest(params_other_names, params_total_quantities):
            if (params_other_name == None):
                  final_params_plot.append(params_total_quantity)
                  break
            chip_specs.loc[params_other_name] = chip_specs.loc[params_total_quantity]
      
      for params_other_name, params_group in zip(params_other_names, params_interest):
            final_params_plot.append(params_other_name)
            for param in params_group:
                  final_params_plot.append(param)
                  chip_specs.loc[params_other_name] = chip_specs.loc[params_other_name] - chip_specs.loc[param]
                  
      
      tick_labels = [str(x) + " GHz" for x in symbol_rate_options] * len(array_configs)
      
      
      x_pos = []
      SR_spacing = 1
      array_config_spacing = round(len(symbol_rate_options) *1.5)
      for array_config_idx in range(len(array_configs)):
            for SR_idx in range(len(symbol_rate_options)):
                  x_pos.append(array_config_idx * array_config_spacing + SR_idx * SR_spacing)
                  
      #chip_specs.loc[final_params_plot].T.plot.bar(stacked = True)
      running_sum = [0] * chip_specs.shape[1]
      for (param_idx, param) in enumerate(final_params_plot):
            plt.bar(x_pos, chip_specs.loc[param], bottom = running_sum)
            running_sum += chip_specs.loc[param]
            
      xtick_labels = [str(x) + " GHz" for x in symbol_rate_options] * len(array_configs)
      plt.xticks(x_pos, xtick_labels, fontsize = 8, rotation = 45)
      plt.legend(final_params_plot)
      plt.suptitle("Overall System Performance for Evaluating ResNet50 V1.5")
      #plt.grid(color='black')
      plt.ylim([1, 1000])
      plt.yscale("log")
      plt.show()
      
      

      
      
   