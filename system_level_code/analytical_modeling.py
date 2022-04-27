import csv
import math
import specs_info
import pandas as pd

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
    
     outputs_names = specs_info.SS_outputs_names
     outputs_data = [0] * len(outputs_names)
     model_outputs = pd.DataFrame(index = outputs_names)
     
     (input_rows, input_cols, filter_rows, filter_cols, channels, num_filter, strides, SA_rows, SA_cols, SRAM_input, SRAM_filter, SRAM_output) = acquire_NN_SS_info(SS_inputs_dict, NN_file_path_name)
     num_layers = len(input_rows)

     for index, layer in enumerate(range(num_layers)):
         filter_size = filter_rows[layer] * filter_cols[layer] * channels[layer]
         row_fold = math.ceil(filter_size / SA_rows)
         col_fold = math.ceil(num_filter[layer] / SA_cols)

         num_programs = row_fold * col_fold
         conv_rows = math.ceil((input_rows[layer] - filter_rows[layer] + 1) / strides[layer]) 
         conv_cols = math.ceil((input_cols[layer] - filter_cols[layer] + 1) / strides[layer]) 
         
         convRows = math.ceil(input_rows[layer] / strides[layer])
         convCols = math.ceil(input_cols[layer] / strides[layer])

         compute_cycles = num_programs * conv_rows * conv_cols * batch_size

         avg_rows_used = filter_size / (filter_rows[layer] * row_fold)
         SRAM_input_reads = compute_cycles * avg_rows_used
         avg_cols_used = num_filter[layer] / (filter_cols[layer] * col_fold)
         SRAM_output_writes = compute_cycles * avg_cols_used
         SRAM_filter_reads = filter_size * num_filter[layer]

         DRAM_filter_reads = -1
         DRAM_input_reads = -1
         DRAM_output_writes = SRAM_output_writes


         model_outputs.at[:, "AM " + str(index)] = [SRAM_input_reads, SRAM_filter_reads, SRAM_output_writes, \
              DRAM_input_reads, DRAM_filter_reads, DRAM_output_writes, num_programs, compute_cycles]
     
     totals = model_outputs.sum(axis = 1)
     model_outputs.at[:, "AM total"] = totals
     return(model_outputs)

     x = 1

