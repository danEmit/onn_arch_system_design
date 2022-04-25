SS_inputs_names = ["Systolic Array Rows", "Systolic Array Cols", "SRAM Input Size", "SRAM Filter Size", "SRAM Output Size", "DRAM Bandwidth Mode", "Batch Size"]
SS_outputs_names = ["SRAM Input Reads", "SRAM Filter Reads", "SRAM Output Writes", "DRAM Input Reads", "DRAM Filter Reads", "DRAM Output Writes", \
          "Total Weights Programming Cycles", "Total Vector Segments Processed"]


electronic_area_specs_names = ["ADCs Area", "PS Area", "ODAC Drivers Area", "PCM Heaters Area", "MRM Heaters Area",\
	"SRAM Area", "DRAM Area", "Clock Area", "Rx AFE Area"]

electronic_power_specs_names = ["ADCs Power", "PS Power", "ODAC Drivers Power", "PCM Heaters Power", "MRM Heaters Power", \
	"SRAM Program Power", "SRAM Compute Power", "DRAM Program Power", "DRAM Compute Power", "Clocks Power", "Rx AFE Power"]

photonic_area_specs_names = ["MRMs Area", "Crossbar Array Area", "Tx Power Splitters Area", "Grating Coupler Area"]

photonic_power_specs_names = ["Photonic Power Single PD", "PCM OMA", "MRM Tx OMA", "Power Loss Crossbar Junctions", "Power Loss Crossbar Waveguides", "Power Loss Splitting Tree",\
	"Power Loss Tx Waveguides", "Power Loss Grating Coupler", "Power Loss Waveguide Power Combining"]

photonic_power_actual_loss_names = ["PCM OMA Actual Loss", "MRM Tx OMA Actual Loss", "Crossbar Junctions Actual Loss", "Crossbar Waveguides Actual Loss", "Splitting Tree Actual Loss",\
	"Tx Waveguides Actual Loss", "Grating Coupler Actual Loss", "Waveguide Power Combining Actual Loss"]

time_specs_names = ["Compute Portion", "Program Portion", "Total Time"]

semi_high_results_names = ["Total Electronics Area", "Total Photonics Area", "Total Electronics Program Power", \
	"Total Electronics Compute Power", "Total Combined Electronics Power", "Total Electronics Power dBm", "Total Photonic Losses and OMA", "Total Photonic Power mW",\
		"Total Laser Power from Wall mW", "Total Laser Power from Wall dBm"]

overall_specs_names = ["Total Chip Area", "Total Chip Power", "Total Chip Power dBm", "Inferences Per Second", "Inferences Per Second Per Watt"]

all_specs_names = electronic_area_specs_names + electronic_power_specs_names + photonic_area_specs_names + photonic_power_specs_names \
+ photonic_power_actual_loss_names + time_specs_names + semi_high_results_names + overall_specs_names



def access_specs_names():
    return all_specs_names



