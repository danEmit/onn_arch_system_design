import csv
import math
#from pyexpat import model

#from pyparsing import col
import specs_info
import pandas as pd
import sim_params_analytical_standalone

dec_points = 2

def make_analytical_model(input_rows, input_cols, filter_rows, filter_cols, channels, num_filter, strides, SA_rows, SA_cols, SRAM_input, SRAM_filter, SRAM_output, batch_size, accumulator_elements_col)
     outputs_names = specs_info.SS_outputs_names.copy()
     outputs_data = [0] * len(outputs_names)
     model_outputs = pd.DataFrame(index = outputs_names)
     



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
     SA_rows = 8
     SA_cols = 8
     SRAM_input  = 64000
     SRAM_filter = 64000
     SRAM_output = 64000
     accumulator_elements_col = 5000

     analytical_model_file_path_name = "/Users/d/Desktop/onn_arch_system_design/AM.csv"

     accumulator_elements_col = 5000


     analytical_model = make_analytical_model(input_rows, input_cols, filter_rows, filter_cols, channels, num_filter, strides, SA_rows, SA_cols, SRAM_input, SRAM_filter, SRAM_output, batch_size, accumulator_elements_col)
     analytical_model.to_csv(analytical_model_file_path_name)


if __name__ == "__main__":
    main()

