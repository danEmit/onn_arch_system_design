import csv
import math
#from pyexpat import model

#from pyparsing import col
import specs_info
import pandas as pd
import sim_params

dec_points = 2

def acquire_NN_SS_info(SS_inputs_dict, NN_file_path_name):
     input_rows = [] 
     input_cols  = []
     filter_rows = [] 
     filter_cols = []
     channels = []
     num_filter = []
     strides = []

     SA_rows     = SS_inputs_dict["Systolic Array Rows"]
     SA_cols     = SS_inputs_dict["Systolic Array Cols"]
     SRAM_input  = SS_inputs_dict["SRAM Input Size"]
     SRAM_filter = SS_inputs_dict["SRAM Filter Size"]
     SRAM_output = SS_inputs_dict["SRAM Output Size"]

     with open(NN_file_path_name, newline='') as csvfile:
          spamreader = csv.reader(csvfile, delimiter=',')
          firstRow = 1
          for row in spamreader:
               if firstRow:
                    firstRow = 0
                    continue
               try:
                    input_rows.append(int(row[1]))
                    input_cols.append(int(row[2]))
                    filter_rows.append(int(row[3]))
                    filter_cols.append(int(row[4]))
                    channels.append(int(row[5]))
                    num_filter.append(int(row[6]))
                    strides.append(int(row[7]))
               except:
                    print("can't convert all the data in NN file to ints")

     return (input_rows, input_cols, filter_rows, filter_cols, channels, num_filter, strides, SA_rows, SA_cols, SRAM_input, SRAM_filter, SRAM_output)

def make_analytical_model(SS_inputs_dict, batch_size, NN_file_path_name):
     outputs_names = specs_info.SS_outputs_names.copy()
     outputs_data = [0] * len(outputs_names)
     model_outputs = pd.DataFrame(index = outputs_names)
     
     (input_rows, input_cols, filter_rows, filter_cols, channels, num_filter, strides, SA_rows, SA_cols, SRAM_input, SRAM_filter, SRAM_output) = acquire_NN_SS_info(SS_inputs_dict, NN_file_path_name)
     num_layers = len(input_rows)

     for index, layer in enumerate(range(num_layers)):
          filter_size = filter_rows[layer] * filter_cols[layer] * channels[layer]
          row_fold = math.ceil(filter_size / SA_rows)
          col_fold = math.ceil(num_filter[layer] / SA_cols)

          num_programs = row_fold * col_fold
          conv_rows = math.ceil((input_rows[layer] - filter_rows[layer]) / strides[layer]) + 1
          conv_cols = math.ceil((input_cols[layer] - filter_cols[layer]) / strides[layer]) + 1
          
          conv_rows = math.ceil(input_rows[layer] / strides[layer])
          conv_cols = math.ceil(input_cols[layer] / strides[layer])

          num_conv_in_input = conv_rows * conv_cols 
          num_conv_in_input_batch = num_conv_in_input * batch_size
          compute_cycles = num_programs * num_conv_in_input_batch

          SRAM_input_reads = num_conv_in_input_batch * filter_size * col_fold
          SRAM_output_writes = num_conv_in_input_batch * row_fold * num_filter[layer]
          SRAM_filter_reads = filter_size * num_filter[layer]

          DRAM_filter_reads = -1
          DRAM_input_reads = -1
          DRAM_output_writes = SRAM_output_writes
          
          col_name = "AM " + str(index)
          model_outputs.at[specs_info.SS_outputs_names, col_name] = [SRAM_input_reads, SRAM_filter_reads, \
               SRAM_output_writes, DRAM_input_reads, DRAM_filter_reads, DRAM_output_writes,\
                     num_programs, compute_cycles]
     
     totals = model_outputs.sum(axis = 1)
     model_outputs.at[:, "AM total"] = totals
     return(model_outputs)

     x = 1

def make_analytical_model_acc(SS_inputs_dict, NN_file_path_name, accumulator_elements_col, batch_size):
     outputs_names = specs_info.acc_related_specs.copy()
     outputs_data = [0] * len(outputs_names)
     model_outputs = pd.DataFrame(index = outputs_names)
     
     (input_rows, input_cols, filter_rows, filter_cols, channels, num_filter, strides, SA_rows, SA_cols, SRAM_input, SRAM_filter, SRAM_output) = acquire_NN_SS_info(SS_inputs_dict, NN_file_path_name)
     num_layers = len(input_rows)

     for index, layer in enumerate(range(num_layers)):
          filter_size = filter_rows[layer] * filter_cols[layer] * channels[layer]
          row_fold_theor = math.ceil(filter_size / SA_rows)
          col_fold_theor = math.ceil(num_filter[layer] / SA_cols)

          conv_rows = math.ceil((input_rows[layer] - filter_rows[layer]) / strides[layer]) + 1
          conv_cols = math.ceil((input_cols[layer] - filter_cols[layer]) / strides[layer]) + 1
          #convRows = math.ceil(input_rows[layer] / strides[layer])
          #convCols = math.ceil(input_cols[layer] / strides[layer])
          num_conv_in_input = conv_rows * conv_cols 

          ## need to compute specs for full col fold and col fold of one 
          ## note that it's now more about what batch size is allowed than what batch size we pick, right? 
          
          batch_col_fold_product = accumulator_elements_col / num_conv_in_input
          if (batch_col_fold_product < 1):
               print("accumulator not big enough, try other value")
               # then write -1 to all fields
               # return

          # if col fold = 1
          col_fold_mini = 1
          batch_size_mini = batch_col_fold_product

          


          

          num_programs = row_fold * col_fold

          num_conv_in_input_batch = num_conv_in_input * batch_size
          compute_cycles = num_programs * num_conv_in_input_batch

          #avg_rows_used = filter_size / (SA_rows * row_fold)
          SRAM_input_reads = num_conv_in_input_batch * filter_size * col_fold
          SRAM_output_writes = num_conv_in_input_batch * row_fold * num_filter[layer]
          #avg_cols_used = num_filter[layer] / (filter_cols[layer] * col_fold)
          #SRAM_output_writes = compute_cycles * avg_cols_used
          SRAM_filter_reads = filter_size * num_filter[layer]

          DRAM_filter_reads = -1
          DRAM_input_reads = -1
          DRAM_output_writes = SRAM_output_writes
          


          needed_acc_depth_batch_1_no_col_fold = num_conv_in_input
          needed_acc_depth_batch_1_max_col_fold = needed_acc_depth_batch_1_no_col_fold * col_fold
          batch_col_fold_product_given_acc = accumulator_elements_col / num_conv_in_input
          needed_input_SRAM_size_given_acc_size_no_cold_fold = input_rows[layer] * input_cols[layer] * batch_col_fold_product_given_acc     # so this will be a function of batch 
          needed_input_SRAM_size_given_acc_size_full_cold_fold = needed_input_SRAM_size_given_acc_size_no_cold_fold / col_fold


          model_outputs.at[extra_specs_adv, col_name] = [round(needed_acc_depth_batch_1_no_col_fold, dec_points), \
               round(needed_acc_depth_batch_1_max_col_fold, dec_points), round(batch_col_fold_product_given_acc, dec_points), \
                    round(needed_input_SRAM_size_given_acc_size_no_cold_fold, dec_points), \
                         round(needed_input_SRAM_size_given_acc_size_full_cold_fold, dec_points)]
               
     
          
        #model_outputs.at["", "AM " + str(index)]
     
     totals = model_outputs.sum(axis = 1)
     model_outputs.at[:, "AM total"] = totals
     return(model_outputs)

     x = 1

def pseudo_analytical_model(SS_inputs_dict, batch_size, NN_file_path_name, accumulator_elements_col):
     outputs_names = specs_info.SS_outputs_names.copy()
     outputs_data = [0] * len(outputs_names)
     model_outputs = pd.DataFrame(index = outputs_names)
     
     (input_rows_, input_cols_, filter_rows_, filter_cols_, channels_, num_filter_, strides_, SA_rows, SA_cols, SRAM_input, SRAM_filter, SRAM_output) = acquire_NN_SS_info(SS_inputs_dict, NN_file_path_name)
     num_layers = len(input_rows)

     for layer_num in range(num_layers):     
          if (1):
               input_rows = input_rows_[layer_num]
               input_cols = input_cols_[layer_num]
               filter_rows = filter_rows_[layer_num]
               filter_cols = filter_cols_[layer_num]
               channels = channels_[layer_num]
               num_filter = num_filter_[layer_num]
               strides = strides_[layer_num]
               filter_size = filter_rows * filter_cols * channels
     
          overall_col_fold = math.ceil(num_filter / SA_cols)  
          overall_row_fold = math.ceil(filter_size / SA_rows)
          overall_batch_fold = batch_size

          conv_rows = math.ceil((input_rows - filter_rows) / strides) + 1
          conv_cols = math.ceil((input_cols - filter_cols) / strides) + 1
          num_conv_in_input = conv_rows * conv_cols 
          batch_col_fold_product = accumulator_elements_col / num_conv_in_input # what can fit onto accumulator

          minor_col_fold = 1
          minor_batch_fold = batch_col_fold_product / minor_col_fold
          minor_row_fold = 1

          major_col_fold = overall_col_fold / minor_col_fold
          major_row_fold = overall_row_fold / minor_row_fold
          major_batch_fold = overall_batch_fold / minor_batch_fold

          # one alternative would be to switch major batch group and major col group
          # but probably wouldn't have much effect
          for major_col_group in range(major_col_fold):
               for major_batch_group in range(major_batch_fold):
                    for minor_col_group in range(minor_col_fold):
                         for major_row_group in range(major_row_fold):
                              for minor_row_group in range(minor_row_fold):
                                   for minor_batch_group in range(minor_batch_fold):
                                        current_col_group = major_col_group * minor_col_fold + minor_col_group
                                        current_row_group = major_row_group * minor_row_fold + minor_row_group
                                        current_batch = major_batch_group * minor_batch_fold + minor_batch_group




def main():
     SS_rows = 8
     SS_cols = 8
     batch_size = 8
     SRAM_input_size = 64000
     SRAM_filter_size = 64000
     SRAM_output_size = 64000
     DRAM_mode = 0

     


     NN_file_path_name = "/Users/d/Desktop/onn_arch_system_design/topologies/ONN/Resnet50.csv"
     analytical_model_file_path_name = "/Users/d/Desktop/onn_arch_system_design/AM.csv"

     accumulator_elements_col = 5000

     SS_inputs_dict = dict({"Systolic Array Rows": SS_rows, \
                         "Systolic Array Cols": SS_cols, \
                         "SRAM Input Size": sim_params.SRAM_input_size, \
                         "SRAM Filter Size": sim_params.SRAM_filter_size, \
                         "SRAM Output Size": sim_params.SRAM_output_size, \
                         "DRAM Bandwidth Mode": sim_params.DRAM_mode}) 


     analytical_model = make_analytical_model(SS_inputs_dict, NN_file_path_name, accumulator_elements_col)
     analytical_model.to_csv(analytical_model_file_path_name)


if __name__ == "__main__":
    main()

