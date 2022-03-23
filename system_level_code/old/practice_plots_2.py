import pandas as pd
import matplotlib.pyplot as plt

color_options = [["indianred", "brown", "red", "coral", "lightsalmon"], ["forestgreen", "limegreen", "darkgreen", "olivedrab", "mediumseagreen"], ["navy", "royalblue", "dodgerblue", "blue", "cornflowerblue"]]


def make_stacked_bar_plot(all_df, params_interest, params_total_quantities, params_other_names):
	mega_df = pd.concat(all_df, axis = 1)
	num_SR = len(all_df)
	num_array_config = all_df[0].shape[1]
	overall_col_idxs = []
	for SR_idx in range(num_SR):
		for col_idx in range(num_array_config):
			overall_col_idxs.append(num_SR * col_idx + SR_idx)
	#mega_df = mega_df.iloc[overall_col_idxs]

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


	#print(mega_df)


	df_plot = mega_df.loc[params_actual].T
	#print(df_plot)
	x_pos = [0,1,4,6,7,9]
	kwargs={'x':x_pos}
	ax = df_plot.plot.bar(stacked = True, color = colors_actual, **kwargs)
	plt.xlabel(["32", "16", "8"])
	plt.show()




def main():
    # set up data to plot
    row_names = ["power A 1", "power A 2", "power A total", "power B 1", "power B 2", "power B 3", "power B total"]
    data1 = [5, 4, 21, 1, 9, 9, 22]
    data2 = [2, 2, 22, 2, 5, 8, 21]
    #data3 = [8, 1, 27, 3, 3, 7, 22]
    data3 = [x * 1.2 for x in data1]
    data4 = [x * 1.2 for x in data2]
    data5 = [x * 1.5 for x in data1]
    data6 = [x * 1.5 for x in data2]


    #data4 = data2 * 2
    #data5 = data1 * 3
    #data6 = data1 * 3
    df1 = pd.DataFrame(data1, index = row_names, columns = ["16"])
    df1.insert(0, "32", data2)
    df2 = pd.DataFrame(data3, index = row_names, columns = ["16"])
    df2.insert(0, "32", data4)
    df3 = pd.DataFrame(data5, index = row_names, columns = ["16"])
    df3.insert(0, "32", data6)

    all_df = [df1, df2, df3] # to show different symbol rates

    params_interest = [["power A 1"], ["power B 1", "power B 3"]]
    params_total_quantities = ["power A total", "power B total"]
    params_other_names = ["power electrical other", "power photonic other"]
    make_stacked_bar_plot(all_df, params_interest, params_total_quantities, params_other_names)


if __name__ == "__main__":
    main()