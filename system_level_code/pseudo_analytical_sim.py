import math
import SRAM_model

num_conv_in_input_delete = 0


class hardware_state():
     def __init__(self):
          x = 1

     def set_hardware(self, hardware_state_info):
          self.array_rows = hardware_state_info["Array Rows"]
          self.array_cols = hardware_state_info["Array Cols"]
          self.SRAM_input_size = hardware_state_info["SRAM Input Size"]
          self.SRAM_filter_size = hardware_state_info["SRAM Filter Size"]
          self.SRAM_output_size = hardware_state_info["SRAM Output Size"]
          self.accumulator_elements = hardware_state_info["Accumulator Elements"]

          print("---------------------------------")
          print("Hardware state set to:")
          print("Array Size:       ", self.array_rows, "x", self.array_cols)
          print("SRAM Input Size:  ", self.SRAM_input_size)
          print("SRAM Filter Size: ", self.SRAM_filter_size)
          print("SRAM Output Size: ", self.SRAM_output_size)
          print("Accumulator Elements per Col: ", self.accumulator_elements)
          print("---------------------------------")
          print()

          self.input_SRAM  = SRAM_model.SRAM_model(self.SRAM_input_size)
          self.filter_SRAM = SRAM_model.SRAM_model(self.SRAM_filter_size)


     def set_batch(self, batch_size):
          self.batch_size = batch_size
          print("Batch set to: ", batch_size, "\n")
     
     def set_NN(self, NN_layers_all):
          self.NN_layers_all = NN_layers_all
          self.num_NN_layers = len(NN_layers_all)

     def set_results_vars(self):
          self.num_programming_practice = [0] * self.num_NN_layers
          self.num_programming_theory   = [0] * self.num_NN_layers
          self.num_compute_cycles_practice = [0] * self.num_NN_layers
          self.num_compute_cycles_theory = [0] * self.num_NN_layers

          self.SRAM_input_reads = [0] * self.num_NN_layers
          self.SRAM_filter_reads = [0] * self.num_NN_layers
          self.SRAM_output_writes = [0] * self.num_NN_layers
          self.DRAM_input_reads = [0] * self.num_NN_layers
          self.DRAM_filter_reads = [0] * self.num_NN_layers
          self.DRAM_output_writes = [0] * self.num_NN_layers
          self.accumulator_dumps = [0] * self.num_NN_layers
 
     # this function probably useless
     def set_NN_layer(self, NN_layer):
          self.input_rows  = NN_layer["Input Height"]
          self.input_cols  = NN_layer["Input Width"]
          self.filter_rows = NN_layer["Filter Height"]
          self.filter_cols = NN_layer["Filter Width"]
          self.channels    = NN_layer["Channels"]
          self.num_filter  = NN_layer["Num Filter"]
          self.stride      = NN_layer["Strides"]

          print("Input Rows:   ", self.input_rows)
          print("Input Height: ", self.input_cols)
          print("Filter Rows:  ", self.filter_rows)
          print("Filter Cols:  ", self.filter_cols)
          print("Channels:     ", self.channels)
          print("Num Filter:   ", self.num_filter)
          print("Stride:       ", self.stride)
          print()


     def run_all_layers(self):
          for index, layer in enumerate(self.NN_layers_all):
               #self.set_NN_layer(self, layer)
               print("\n********* Now simulating layer", index, "***********")
               self.current_layer = index
               self.single_layer_set_params(layer)
               self.print_results()

     def single_layer_set_params(self, NN_layer):
          input_rows  = NN_layer["Input Height"]
          input_cols  = NN_layer["Input Width"]
          filter_rows = NN_layer["Filter Height"]
          filter_cols = NN_layer["Filter Width"]
          channels    = NN_layer["Channels"]
          num_filter  = NN_layer["Num Filter"]
          stride      = NN_layer["Strides"]

          filter_size = filter_rows * filter_cols * channels
          single_input_size = input_cols * input_rows * channels

          overall_col_fold = math.ceil(num_filter / self.array_cols)  
          overall_row_fold = math.ceil(filter_size / self.array_rows)
          overall_batch_fold = self.batch_size

          conv_rows = math.ceil((input_rows - filter_rows) / stride) + 1
          conv_cols = math.ceil((input_cols - filter_cols) / stride) + 1
          conv_rows = math.ceil(input_rows / stride)
          conv_cols = math.ceil(input_cols / stride)

          num_conv_in_input = conv_rows * conv_cols 
          global num_conv_in_input_delete 
          num_conv_in_input_delete = num_conv_in_input
          batch_col_fold_product_allowed = self.accumulator_elements / num_conv_in_input # what can fit onto accumulator
          batch_col_fold_product_theory  = overall_batch_fold * overall_col_fold
          if batch_col_fold_product_allowed > batch_col_fold_product_theory:
               #batch_col_fold_product_allowed = batch_col_fold_product_theory
               minor_col_fold = overall_col_fold
               minor_batch_fold = overall_batch_fold
          else:
               minor_col_fold = 1
               minor_batch_fold = math.floor(batch_col_fold_product_allowed / minor_col_fold)
          
          minor_row_fold = 1

          major_col_fold = math.ceil(overall_col_fold / minor_col_fold)
          major_row_fold = math.ceil(overall_row_fold / minor_row_fold)
          major_batch_fold = math.ceil(overall_batch_fold / minor_batch_fold)

          self.accumulator_dumps[self.current_layer] = major_batch_fold * major_col_fold
          self.num_compute_cycles_theory[self.current_layer] = self.batch_size * overall_col_fold * overall_row_fold * num_conv_in_input
          self.SRAM_input_reads[self.current_layer] = num_conv_in_input * self.batch_size * filter_size * overall_col_fold
          self.SRAM_filter_reads[self.current_layer] = filter_size * num_filter * major_batch_fold
          self.SRAM_output_writes[self.current_layer] = num_conv_in_input * self.batch_size * num_filter
          self.DRAM_output_writes[self.current_layer] = max(self.SRAM_output_writes[self.current_layer] - self.SRAM_output_size, 0)

          if self.current_layer == 0:
               SRAM_input_output_crossover_data = 0
          else:
               SRAM_input_output_crossover_data = min(self.SRAM_output_size, self.SRAM_output_writes[self.current_layer - 1])

          self.input_SRAM.new_layer(single_input_size, self.batch_size, SRAM_input_output_crossover_data)
          self.filter_SRAM.new_layer(self.array_cols * self.array_rows, overall_row_fold * overall_col_fold, 0)
          self.run_single_layer(major_col_fold, minor_col_fold, major_batch_fold, minor_batch_fold, major_row_fold, minor_row_fold)
          self.input_SRAM.conclude_layer()
          self.filter_SRAM.conclude_layer()



     def run_single_layer(self, major_col_fold, minor_col_fold, major_batch_fold, minor_batch_fold, major_row_fold, minor_row_fold):     
          self.num_programming_practice[self.current_layer] = 0
          self.num_programming_theory[self.current_layer] = major_col_fold * minor_col_fold * major_row_fold * minor_row_fold * major_batch_fold

          old_col_group = -1
          old_row_group = -1
          current_col_group = -1
          current_row_group = -1
          for major_col_group in range(major_col_fold):
               for major_batch_group in range(major_batch_fold):
                    for minor_col_group in range(minor_col_fold):
                         for major_row_group in range(major_row_fold):
                              for minor_row_group in range(minor_row_fold):
                                   for minor_batch_group in range(minor_batch_fold):
                                        old_col_group = current_col_group
                                        old_row_group = current_row_group

                                        current_col_group = major_col_group * minor_col_fold + minor_col_group
                                        current_row_group = major_row_group * minor_row_fold + minor_row_group
                                        current_batch = major_batch_group * minor_batch_fold + minor_batch_group

                                        if (old_col_group != current_col_group) or (old_row_group != current_row_group):
                                             self.num_programming_practice[self.current_layer] += 1
                                        self.num_compute_cycles_practice[self.current_layer] += num_conv_in_input_delete 

                                        if (0):
                                             print("")
                                             print("Current Col Group:", current_col_group)
                                             print("Current Row Group:", current_row_group)
                                             print("Current Batch Group:", current_batch)

                                        filter_index = current_col_group * major_row_fold * minor_row_fold + current_row_group
                                        self.manage_SRAM_DRAM_access(current_batch, filter_index)

          #self.SRAM_filter_reads[self.current_layer] = self.num_programming_practice[self.current_layer] * self.
          

     def manage_SRAM_DRAM_access(self, current_batch, filter_index):
          self.input_SRAM.access_component(current_batch)
          self.filter_SRAM.access_component(filter_index)

     def access_SRAM_data(self):
          self.DRAM_input_reads  = self.input_SRAM.DRAM_reads
          self.DRAM_filter_reads = self.filter_SRAM.DRAM_reads

     def print_results(self):
          print("\n-----------Results-----------")
          for layer_num in range(self.current_layer, self.current_layer + 1):
          #for layer_num in range(self.num_NN_layers):
               print("Layer Number: ", layer_num)
               print("Num Programming Practice: ", self.num_programming_practice[self.current_layer])
               print("Num Programming Theory:  ", self.num_programming_theory[self.current_layer])  
               print("Num Compute Cycles Practice: ", self.num_compute_cycles_practice[self.current_layer])
               print("Num Compute Cycles Theory: ", self.num_compute_cycles_theory[self.current_layer])

               print("SRAM Input Reads: ", self.SRAM_input_reads[self.current_layer])
               print("SRAM Filter Reads: ", self.SRAM_filter_reads[self.current_layer])
               print("SRAM Output Writes: ", self.SRAM_output_writes[self.current_layer])
               print("DRAM Input Reads: ", self.DRAM_input_reads[self.current_layer])
               print("DRAM Filter Reads: ", self.DRAM_filter_reads[self.current_layer])
               print("DRAM Output Writes: ", self.DRAM_output_writes[self.current_layer])
               print("Accumulator Dumps: ", self.accumulator_dumps[self.current_layer])