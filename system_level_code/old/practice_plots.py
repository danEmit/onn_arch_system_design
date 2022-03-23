import pandas as pd
import matplotlib.pyplot as plt

row_names = ["power A 1", "power A 2", "power A total", "power B 1", "power B 2", "power B 3", "power B total"]
data1 = [5, 4, 21, 1, 9, 9, 22]
data2 = [2, 2, 22, 2, 5, 8, 21]
data3 = [8, 1, 27, 3, 3, 7, 22]
data4 = [6, 7, 27, 4, 3, 2, 24]
data5 = [3, 2, 28, 2, 1, 9, 24]
data6 = [5, 6, 25, 2, 4, 1, 29]

df1 = pd.DataFrame(data1, index = row_names, columns = ["16"])
df1.insert(0, "32", data2)
df2 = pd.DataFrame(data3, index = row_names, columns = ["16"])
df2.insert(0, "32", data4)
df3 = pd.DataFrame(data5, index = row_names, columns = ["16"])
df3.insert(0, "32", data6)

all_df = [df1, df2, df3] # to show different symbol rates

params_interest = [["power A 1"], ["power B 1", "power B 3"]]
params_totals = [["power A total"], ["power B total"]]
#params_plot = params_interest
#params_plot[0].append("power electrical other")
#params_plot[1].append("power photonic other")
params_plot = ["power electrical other", "power photonic other"]

color_options = [["indianred", "brown", "red", "coral", "lightsalmon"], ["forestgreen", "limegreen", "darkgreen", "olivedrab", "mediumseagreen"], ["navy", "royalblue", "dodgerblue", "blue", "cornflowerblue"]]
actual_colors = []


fig, ax = plt.subplots()


df_plot = pd.DataFrame()
helper_df = pd.DataFrame()

num_SR = len(all_df)

for SR_index, SR_df in enumerate(all_df):
	for column_idx, column_name in enumerate(SR_df):
		overall_col_index = num_SR * column_idx + SR_index
		print("overall col index", overall_col_index)
		helper_df = pd.DataFrame()
		for param_group_idx, param_group in enumerate(params_interest):
			for param in param_group:

				print(SR_df.loc[param, column_name])




		print(overall_col_index)
		print(column_idx, SR_index)
		#for index, param in enumerate(params_interest):
		#	df_plot.insert(SR_df.loc[param])
		#	print(helper_df)

