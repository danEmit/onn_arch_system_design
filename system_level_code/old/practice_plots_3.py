import pandas as pd
import matplotlib.pyplot as plt

color_options = [["indianred", "brown", "red", "coral", "lightsalmon"], ["forestgreen", "limegreen", "darkgreen", "olivedrab", "mediumseagreen"], ["navy", "royalblue", "dodgerblue", "blue", "cornflowerblue"]]


def make_stacked_bar_plot(all_df, params_interest, params_total_quantities, params_other_names, repeat_tick_labels, array_configs, ylabel):
      mega_df = pd.concat(all_df, axis = 1)
      num_SR  = len(all_df)
      num_array_config = all_df[0].shape[1]
      overall_col_idxs = []
      #print("num_SR", num_SR, "num_array_config", num_array_config)
      for array_config_idx in range(num_array_config):
            for SR_idx in range(num_SR):
                  overall_col_idxs.append(array_config_idx + num_array_config * SR_idx)

      mega_df = mega_df.iloc[:, overall_col_idxs]

      params_actual = []
      colors_actual = []

      for params_group_idx, params_group in enumerate(params_interest):
            helper_df = pd.DataFrame(columns = mega_df.columns, index = ["helper"])
            helper_df.loc["helper"] = [0] * helper_df.shape[0]
            for param_idx, param in enumerate(params_group):
                  helper_df = helper_df + mega_df.loc[param]
                  params_actual.append(param)
                  colors_actual.append(color_options[params_group_idx][param_idx])
            helper_df = mega_df.loc[params_total_quantities[params_group_idx]] - helper_df
            mega_df.loc[params_other_names[params_group_idx]] = helper_df.loc["helper"]
            params_actual.append(params_other_names[params_group_idx])
            colors_actual.append(color_options[params_group_idx][param_idx + 1])

      xtick_labels = repeat_tick_labels * num_array_config


      x_pos = []
      SR_spacing = 1
      array_config_spacing = num_SR *1.5
      for array_config_idx in range(num_array_config):
            for SR_idx in range(num_SR):
                  x_pos.append(array_config_idx * array_config_spacing + SR_idx * SR_spacing)

      #print(x_pos)


      # maybe make these constants and just change the font size on x axis
      figWidth = 5#0.5 * num_SR * num_array_config
      figHeight  = 8#figHeight

      fig = plt.figure(figsize=(figHeight, figWidth))
      #ax = fig.add_subplot(111)
      sum_holder = pd.DataFrame(columns = mega_df.columns, index = ["sum_holder"])
      sum_holder.loc["sum_holder"] = [0] * sum_holder.shape[0]
      for param_idx, param in enumerate(params_actual):
            #print(mega_df.loc[param])
            #ax.bar(x_pos, mega_df.loc[param], width = 0.35, bottom = sum_holder.loc["sum_holder"], label = param, color = colors_actual[param_idx])
            plt.bar(x_pos, mega_df.loc[param], width = 0.35, bottom = sum_holder.loc["sum_holder"], label = param, color = colors_actual[param_idx])

            sum_holder += mega_df.loc[param]
            #print(sum_holder)
      #print(x_pos, xtick_labels)
      plt.xticks(x_pos, xtick_labels, fontsize = 8, rotation = 45)

      xlabel = array_configs[0]
      for config in array_configs[1:]:
            #print(xlabel)
            #print(config)
            #print()
            xlabel = xlabel + " " * num_SR * 20 + config

      plt.xlabel(xlabel, fontsize = 10)
      plt.ylabel(ylabel)
      plt.gcf().subplots_adjust(bottom=0.15)
      #ax.legend()
      plt.legend()
      plt.yscale("log")
      return(fig)
      #plt.show()




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