# Names for the specs categories in dataframe

SS_inputs_names = ["Systolic Array Rows", "Systolic Array Cols", "SRAM Input Size", "SRAM Filter Size", "SRAM Output Size", "DRAM Bandwidth Mode", "Batch Size"]
SS_outputs_names = ["SRAM Input Reads", "SRAM Filter Reads", "SRAM Output Writes", "DRAM Input Reads", "DRAM Filter Reads", "DRAM Output Writes", \
          "Total Weights Programming Cycles", "Total Vector Segments Processed"]

runspecs_names = ["SRAM Input Reads", "SRAM Filter Reads", "SRAM Output Writes", "DRAM Input Reads", "DRAM Filter Reads", "DRAM Output Writes", \
          "Total Weights Programming Cycles", "Total Vector Segments Processed", "Accumulator Dumps"]
hardware_specs_names = ["Systolic Array Rows", "Systolic Array Cols", "SRAM Input Size", "SRAM Filter Size", "SRAM Output Size", "Accumulator Elements", "Batch Size"]

electronic_area_specs_names = ["ADCs Area", "PS Area", "ODAC Drivers Area", "PCM Heaters Area", "MRM Heaters Area",\
	"SRAM Area", "DRAM Area", "Clock Area", "Rx AFE Area"]

electronic_power_specs_names = ["ADCs Power", "PS Power", "ODAC Drivers Power", "PCM Heaters Power", "MRM Heaters Power", \
	"SRAM Program Power", "SRAM Final Sum Compute Power", "SRAM Accumulator Power", "Accumulator Adder Power", "DRAM Program Power", "DRAM Compute Power", "Clocks Power", "Rx AFE Power"]

photonic_area_specs_names = ["MRMs Area", "Crossbar Array Area", "Tx Power Splitters Area", "Grating Coupler Area"]

photonic_power_specs_names = ["Photonic Power Single PD", "PCM OMA", "MRM Tx OMA", "Power Loss Crossbar Junctions", "Power Loss Crossbar Waveguides", "Power Loss Splitting Tree",\
	"Power Loss Tx Waveguides", "Power Loss Grating Coupler", "Power Loss Waveguide Power Combining"]

time_specs_names = ["Compute Portion", "Program Portion", "Total Time"]

semi_high_results_names = ["Total Electronics Area", "Total Photonics Area", "Electronics Program Power", \
	"Electronics Compute Power", "Electronics Program Power Time Adjusted", "Electronics Compute Power Time Adjusted", \
	"Total Electronics Power Time Adjusted", "Total Electronics Power Time Adjusted dBm", "Total Photonic Losses and OMA dBm", \
	"Total Photonic Power", "Total Laser Power from Wall", \
	"Total Laser Power from Wall Time Adjusted", "Total Laser Power from Wall Time Adjusted dBm"]

overall_specs_names = ["Total Chip Area", "Total Chip Power", "Inferences Per Second", "Inferences Per Second Per Watt"]

all_specs_names = electronic_area_specs_names + electronic_power_specs_names + photonic_area_specs_names + photonic_power_specs_names \
 + time_specs_names + semi_high_results_names + overall_specs_names


# Code Settings ----------
indPrint = 0
summaryPrint = 0
decimalPoints = 3
highestSummaryPrint = 0
mW_adjustment = 1000

# System Info ----------------------------
potential_freqs = [1 * 10**9, 5 * 10**9, 10 * 10**9] 
symbolSize = 6

program_cycle_time = 100 * 10**-9

electronics_clock = 10 ** 9

ADC_Vpp = 1
RxAFE_gain = 5000
PD_responsitivity = 1

crossbar_pitch_x = 0.02 # mm
crossbar_pitch_y = 0.02 # mm
MRM_radius = 5 * 10**-3
	
tx_power_splitter_area_single = 0.00003
grating_coupler_area = 0.0009

PCM_OMA = -0.13
MRM_Tx_OMA = -4

crossbar_junctions_loss_single = -0.05 # dB
waveguide_loss_per_mm = -.3
splitting_tree_loss_per_junction = -0.1
grating_coupler_total_loss = -2

laser_wall_efficiency = 0.2

ADC_power_all = [15, 20, 25] 
PS_energyPerBit = 100 * 10**-15 # joules
ODAC_energyPerSymbol = 168 * 10**-15
PCMHeater_energyPerProgram = 100 * 10**-12
MRMHeater_power_single = 720 * 10**-6 * mW_adjustment
SRAM_energyPerBit = 50 * 10**-15
DRAM_energyPerBit = 3.9 * 10**-12
clock_energyPerCycle = 750 * 10**-15
RxAFE_power_single = 0.00225 * mW_adjustment
single_addition_energy = (0.1 * 6 / 32) * 10 ** -12 # joule

ADC_area_all  = [0.03, 0.035, 0.0475]
PS_area_single  = 0; 
ODAC_area_single = 0.0012;
PCMHeater_area_single = 0
MRMHeater_area_single = 0.0276
SRAM_area_single = (.315 * 10**-6) / 0.7 # 0.7 = fill factor
DRAM_area_total = 0;
clock_area_single = 0.021
RxAFE_area_single = 0


def access_specs_names():
    return all_specs_names



