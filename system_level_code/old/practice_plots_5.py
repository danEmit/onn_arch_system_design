import pandas as pd
import matplotlib.pyplot as plt
import itertools

a100_throughput = 30000
a100_power_eff = 78 / 1000
a100_power = a100_throughput / a100_power_eff
a100_area = 826

color_options = [["indianred", "brown", "red", "coral", "lightsalmon"], ["forestgreen", "limegreen", "darkgreen", "olivedrab", "mediumseagreen"], ["navy", "royalblue", "dodgerblue", "blue", "cornflowerblue"]]
x_pos_base = []
x_pos_compare = []
x_tick_labels_base = []
x_tick_labels_compare = []
colors_base = ["blue"] * 12
colors_compare = ["blue"] * 12 + ["red"]

def prepare_plot_specs(symbol_rate_options, array_size_options):
      
      global x_pos_base, x_pos_compare, x_tick_labels_base, x_tick_labels_compare
      SR_spacing = 1
      array_config_spacing = round(len(symbol_rate_options) *1.5)
      for array_config_idx in range(len(array_size_options)):
            for SR_idx in range(len(symbol_rate_options)):
                  x_pos_base.append(array_config_idx * array_config_spacing + SR_idx * SR_spacing)
        
      x_pos_compare = x_pos_base.copy()
      x_pos_compare.append(max(x_pos_base) + 2)
      x_tick_labels_base = [str(x) + " GHz" for x in symbol_rate_options] * len(array_size_options)
      x_tick_labels_compare = x_tick_labels_base.copy()
      x_tick_labels_compare.append("NVIDIA A100")

def prepare_chip_specs(chip_specs):
      chip_specs.insert(chip_specs.shape[1], "nvidia", [0] * chip_specs.shape[0])
      

def plot_power(chip_specs, compare_a100):
      plt_data = chip_specs.loc["Total Chip Power"].values.tolist()
      '''
      x_pos_mod = x_pos.copy()
      x_tick_mod = x_tick_labels.copy()
      color_mod = colors.copy()
      if compare_a100:
            x_pos_mod.append(max(x_pos) + 2)
            x_tick_mod.append("NVIDIA A100")
            plt_data.append(a100_power)
            color_mod.append("red")
      
      plt.bar(x_pos_mod, plt_data, color = color_mod)
      plt.xticks(x_pos_mod, x_tick_mod, fontsize = 8, rotation = 45)
      '''
      
      if compare_a100:
            plt_data.append(a100_power)
            plt.bar(x_pos_compare, plt_data, color = colors_compare)
            plt.xticks(x_pos_compare, x_tick_labels_compare, fontsize = 8, rotation = 45)
      else: 
            plt.bar(x_pos_base, plt_data, color = colors_base)
            plt.xticks(x_pos_base, x_tick_labels_base, fontsize = 8, rotation = 45)

      plt.yscale("log")
      plt.xlabel("\n\nArray Configuration")
      plt.ylabel("Total Chip Power [mW, log scale]")
      plt.title("Total Accelerator System Power")
      plt.grid(axis='y', color = "black", which='minor', alpha = 0.25)
      plt.grid(axis='y', color = "black", which='major', alpha = 0.6)

      
      plt.show()
      
def plot_area(chip_specs, compare_a100):
      plt_data = chip_specs.loc["Total Chip Area"].values.tolist()
      
      if compare_a100:
            plt_data.append(a100_area)
            plt.bar(x_pos_compare, plt_data, color = colors_compare)
            plt.xticks(x_pos_compare, x_tick_labels_compare, fontsize = 8, rotation = 45)
      else: 
            plt.bar(x_pos_base, plt_data, color = colors_base)
            plt.xticks(x_pos_base, x_tick_labels_base, fontsize = 8, rotation = 45)
            
      #plt.xticks(x_pos_base, x_tick_labels_base, fontsize = 8, rotation = 45)
      plt.yscale("log")
      plt.xlabel("\n\nArray Configuration")
      plt.ylabel("Total Chip Power [mm^2, log scale]")
      plt.title("Total Accelerator System Area")
      plt.grid(axis='y', color = "black", which='minor', alpha = 0.25)
      plt.grid(axis='y', color = "black", which='major', alpha = 0.6)
      plt.show()

def plot_inf_specs(chip_specs, compare_100):
      plt_data_inf = chip_specs.loc["Inferences Per Second"].values.tolist()
      plt_data_inf_watt = chip_specs.loc["Inferences Per Second Per Watt"].values.tolist()
      
      fig, axL = plt.subplots()
      axR = axL.twinx() 
      axR.bar(x_pos_base, plt_data_inf, position = 0)
      axL.bar(x_pos_base, plt_data_inf_watt, position = 1)
      plt.show()

      '''
      if compare_a100:
            plt_data_inf.append(a100_throughput)
            plt_data_inf_watt_append(a100_power_eff)
            axL.bar

      '''
      
      



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
      #plt.grid(color='black')
      plt.ylim([1, 1000])
      plt.yscale("log")
      plt.show()
      
      

      
      
      x = 1




def main():
    # set up data to plot
    row_names = ["power A 1", "power A 2", "power A total", "power B 1", "power B 2", "power B 3", "power B total"]
    data1 = [5, 4, 9, 1, 9, 9, 19]
    data2 = [2, 2, 4, 2, 8, 5, 15]
    #data3 = [8, 1, 27, 3, 3, 7, 22]
    data3 = [x * 1.2 for x in data1]
    data4 = [x * 1.2 for x in data2]
    data5 = [x * 1.5 for x in data1]
    data6 = [x * 1.5 for x in data2]

    data7 = [x * 2 for x in data1]
    data8 = [x * 2 for x in data2]


    #data4 = data2 * 2
    #data5 = data1 * 3
    #data6 = data1 * 3
    df1 = pd.DataFrame(data1, index = row_names, columns = ["16"])
    df1.insert(0, "32", data2)
    df2 = pd.DataFrame(data3, index = row_names, columns = ["16"])
    df2.insert(0, "32", data4)
    df3 = pd.DataFrame(data5, index = row_names, columns = ["16"])
    df3.insert(0, "32", data6)
    df4 = pd.DataFrame(data7, index = row_names, columns = ["16"])
    df4.insert(0, "32", data8)

    all_df = [df1, df2, df3] # to show different symbol rates
    all_df = [df1, df2, df3, df4]

    params_interest = [["power A 1"], ["power B 1", "power B 3"]]
    params_total_quantities = ["power A total", "power B total"]
    params_other_names = ["power electrical other", "power photonic other"]
    repeat_tick_labels = ['1 GHz', '10 GHz', '5 GHz', '2 GHz']
    array_configs = ["16 x 16", "32 x 32"]
    fig = make_stacked_bar_plot(all_df, params_interest, params_total_quantities, params_other_names, repeat_tick_labels, array_configs, "mW")
    plt.show()


if __name__ == "__main__":
    main()