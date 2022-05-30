import math


class hardware_state():
     def __init__(self, hardware_state_info):
          self.array_rows = hardware_state_info["Array Rows"]
          self.array_cols = hardware_state_info["Array Cols"]
          self.SRAM_input_size = hardware_state_info["SRAM Input Size"]
          self.SRAM_filter_size = hardware_state_info["SRAM Filter Size"]
          self.SRAM_output_size = hardware_state_info["SRAM Output Size"]
          self.accumulator_elements = hardware_state_info["Accumulator Elements"]


     def single_layer_set_params(hardware_state, NN_layer, batch_size):
          input_rows  = NN_layer["Input Height"]
          input_cols  = NN_layer["Input Width"]
          filter_rows = NN_layer["Filter Height"]
          filter_cols = NN_layer["Filter Width"]
          channels    = NN_layer["Channels"]
          num_filter  = NN_layer["Num Filter"]
          stride      = NN_layer["Strides"]

          array_rows = hardware_state["Array Rows"]
          array_cols = hardware_state["Array Cols"]
          SRAM_input_size = hardware_state["SRAM Input Size"]
          SRAM_filter_size = hardware_state["SRAM Filter Size"]
          SRAM_output_size = hardware_state["SRAM Output Size"]
          accumulator_elements = hardware_state["Accumulator Elements"]

          print("Input Rows:   ", input_rows)
          print("Input Height: ", input_cols)
          print("Filter Rows:  ", filter_rows)
          print("Filter Cols:  ", filter_cols)
          print("Channels:     ", channels)
          print("Num Filter:   ", num_filter)
          print("Stride:       ", stride)
          print()

          filter_size = filter_rows * filter_cols * channels

          overall_col_fold = math.ceil(num_filter / array_cols)  
          overall_row_fold = math.ceil(filter_size / array_rows)
          overall_batch_fold = batch_size

          conv_rows = math.ceil((input_rows - filter_rows) / stride) + 1
          conv_cols = math.ceil((input_cols - filter_cols) / stride) + 1
          conv_rows = math.ceil(input_rows / stride)
          conv_cols = math.ceil(input_cols / stride)

          num_conv_in_input = conv_rows * conv_cols 
          batch_col_fold_product_allowed = accumulator_elements / num_conv_in_input # what can fit onto accumulator
          batch_col_fold_product_theory  = overall_batch_fold * overall_col_fold
          if batch_col_fold_product_allowed > batch_col_fold_product_theory:
               batch_col_fold_product_allowed = batch_col_fold_product_theory

          minor_col_fold = 1
          minor_batch_fold = math.floor(batch_col_fold_product_allowed / minor_col_fold)
          minor_row_fold = 1

          major_col_fold = math.ceil(overall_col_fold / minor_col_fold)
          major_row_fold = math.ceil(overall_row_fold / minor_row_fold)
          major_batch_fold = math.ceil(overall_batch_fold / minor_batch_fold)

          run_sim(major_col_fold, minor_col_fold, major_batch_fold, minor_batch_fold, major_row_fold, minor_row_fold)




     def run_sim(major_col_fold, minor_col_fold, major_batch_fold, minor_batch_fold, major_row_fold, minor_row_fold):     
          for major_col_group in range(major_col_fold):
                         for major_batch_group in range(major_batch_fold):
                              for minor_col_group in range(minor_col_fold):
                                   for major_row_group in range(major_row_fold):
                                        for minor_row_group in range(minor_row_fold):
                                             for minor_batch_group in range(minor_batch_fold):
                                                  current_col_group = major_col_group * minor_col_fold + minor_col_group
                                                  current_row_group = major_row_group * minor_row_fold + minor_row_group
                                                  current_batch = major_batch_group * minor_batch_fold + minor_batch_group

                                                  print("")
                                                  print("Current Col Group:", current_col_group)
                                                  print("Current Row Group:", current_row_group)
                                                  print("Current Batch Group:", current_batch)
