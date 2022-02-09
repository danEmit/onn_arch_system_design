# Imports -----------
import math 
import pandas as pd

# Code Settings ----------
indPrint = 0
decimalPoints = 3
summaryPrint = 0
highestSummaryPrint = 1
mW_adjustment = 1000

# System Info ----------------------------
potential_freqs = [1 * 10**9, 5 * 10**9, 10 * 10**9] 
symbolSize = 6

program_cycle_time = 100 * 10**-9

ADC_Vpp = 1
RxAFE_gain = 5000
PD_responsitivity = 1

crossbar_pitch_x = 0.02 # mm
crossbar_pitch_y = 0.02 # mm
MRM_radius = 5 * 10**-3
	
tx_power_splitter_area_single = 0.00003
grating_coupler_area = 0.0009

PCM_OMA = 0.13
MRM_Tx_OMA = 4

crossbar_junctions_loss_single = 0.05 # dB
waveguide_loss_per_mm = .3
splitting_tree_loss_per_junction = 0.1
grating_coupler_total_loss = 2

laser_wall_efficiency = 0.2
DC_DC_efficiency = 0.9


ADC_power_all = [15, 20, 25] 
PS_energyPerBit = 100 * 10**-15 # joules
ODAC_energyPerSymbol = 168 * 10**-15
PCMHeater_energyPerProgram = 100 * 10**-12
MRMHeater_power_single = 720 * 10**-6 * mW_adjustment
SRAM_energyPerBit = 50 * 10**-15
DRAM_energyPerBit = 3.9 * 10**-12
clock_energyPerCycle = 750 * 10**-15
RxAFE_power_single = 0.00225 * mW_adjustment

ADC_area_all  = [0.03, 0.035, 0.0475]
PS_area_single  = 0; 
ODAC_area_single = 0.0012;
PCMHeater_area_single = 0
MRMHeater_area_single = 0.0276
SRAM_area_single = (.315 * 10**-6) / 0.7 # 0.7 = fill factor
DRAM_area_total = 0;
clock_area_single = 0.021
RxAFE_area_single = 0


'''
# defined by input data 
num_rows = 0
num_cols = 0
symbolRate = 0
freq_index = 0
'''

electronic_area_specs_names = ["ADCs Area", "PS Area", "ODAC Drivers Area", "PCM Heaters Area", "MRM Heaters Area"\
	"SRAM Area", "DRAM Area", "Clock Area", "Rx AFE Area", "Total Electronics Area"]

electronic_power_specs_names = ["ADCs Power", "PS Power", "ODAC Drivers Power", "PCM Heaters Power", "MRM Heaters Power", \
	"SRAM Program Power", "SRAM Compute Power", "DRAM Program Power", "DRAM Compute Power", "Clocks Power", \
	"Total Electronics Program Power", "Total Electronics Compute Power", "Total Combined Electronics Power"]

overall_specs_names = ["Total Chip Area", "Total Chip Power", "Inferences Per Second", "Inferences Per Second Per Watt"]
overall_specs_data = [0] * len(overall_specs_names)
overall_specs = pd.DataFrame(overall_specs_data, index = overall_specs_names, columns = [""])


# Helper Functions --------
def regular_to_dB(non_dB_val):
	return (10*math.log10(non_dB_val))

def dB_to_regular(dB_val):
	return (10 ** (dB_val / 10))


# Functions ------------------------
def identify_freq():
	for i in range(len(potential_freqs)):
		if symbolRate == potential_freqs[i]:
			freq_index = i
			return(i)

	print("Proposed symbol rate not in system, modeling must abort")
	return (-1)

def identify_globals(array_params, symbolRate_input):
	global num_rows, num_cols, freq_index, symbolRate
	num_rows = array_params.loc["Systolic Array Rows"].values[0]
	num_cols = array_params.loc["Systolic Array Cols"].values[0]
	symbolRate = symbolRate_input
	freq_index = identify_freq()


def component_count():
	global num_ADC, num_PS, num_ODAC, num_PCMHeater, num_MRMHeater_driver, num_MRMHeater_control, num_clocks, num_RxAFE, num_MRM
	num_ADC = num_cols
	num_PS = num_rows + num_cols
	num_ODAC = num_rows
	num_PCMHeater = num_rows * num_cols
	num_MRMHeater_driver = num_cols + num_rows
	num_MRMHeater_control = math.ceil(num_MRMHeater_driver / 16)
	num_clocks = math.ceil((num_cols + num_rows) / 4)
	num_RxAFE = num_cols
	num_MRM = num_rows + num_cols


def time_analysis(program_cycles, vector_input_cycles):
	global total_time, total_time_us, compute_portion, program_portion, program_time_total, compute_time_total 
	program_time_total = program_cycles * program_cycle_time
	compute_time_total = vector_input_cycles / symbolRate

	total_time = program_time_total + compute_time_total
	total_time_us = total_time * 10**6

	compute_portion = compute_time_total / total_time
	program_portion = program_time_total / total_time

	if (summaryPrint):
		print("Time Summary")
		print("compute portion: ", round(compute_portion, decimalPoints))
		print("program_portion: ", round(program_portion, decimalPoints))
		print("total time: ", round(total_time_us, decimalPoints), "microseconds")
		print()

	#return(total_time_us, compute_portion, program_portion)

def signal_power_analysis():
	PD_power_single = (ADC_Vpp / RxAFE_gain) / PD_responsitivity
	PD_power_single = PD_power_single * mW_adjustment
	num_ADC = num_cols
	PD_power_total = PD_power_single * num_ADC 
	PD_power_total_dBm = regular_to_dB(PD_power_total)

	if (indPrint):
		print("Photonic power needed at single PD:", round(PD_power_single, decimalPoints), "mW")
		print()

	return(PD_power_total_dBm)

def photonic_loss_analysis():
	num_crossbar_junctions = (num_cols + num_rows) / 2
	crossbar_junctions_loss_total = crossbar_junctions_loss_single * num_crossbar_junctions

	photonic_ray_avg_dist_crossbar = (num_rows * crossbar_pitch_y / 2) + (num_cols * crossbar_pitch_x / 2)
	crossbar_waveguide_loss_total = waveguide_loss_per_mm * photonic_ray_avg_dist_crossbar

	length_of_MRM_waveguide = 2 * math.pi * MRM_radius
	tx_waveguide_loss_total = length_of_MRM_waveguide * num_MRM * waveguide_loss_per_mm

	splitting_tree_num_junction = num_rows 
	splitting_tree_loss_total = splitting_tree_num_junction * splitting_tree_loss_per_junction

	photonic_combining_loss = 1 / num_rows
	photonic_combining_loss_dB = -1 * regular_to_dB(photonic_combining_loss)

	if (indPrint):
		print("Total power lost in crossbar junctions:  ", round(crossbar_junctions_loss_total, decimalPoints), "dB")
		print("Total power lost in crossbar waveguides: ", round(crossbar_waveguide_loss_total, decimalPoints), "dB")
		print("Total power lost in splitting tree junctions: ", round(splitting_tree_loss_total, decimalPoints), "dB")
		print("Total power lost in tx waveguides: ", round(tx_waveguide_loss_total, decimalPoints), "dB")
		print("Total power lost in grating coupler: ", round(grating_coupler_total_loss, decimalPoints), "dB")
		print("Total power lost in waveguide power combining:", round(photonic_combining_loss_dB, decimalPoints), "dB,", photonic_combining_loss, "[non-dB]")
		print()

	total_photonic_loss = crossbar_junctions_loss_total + crossbar_waveguide_loss_total + splitting_tree_loss_total + grating_coupler_total_loss + tx_waveguide_loss_total + photonic_combining_loss_dB
	return (total_photonic_loss)

def photonics_power_analysis():
	### Signal Power Analysis ------------------------
	PD_power_total_dBm = signal_power_analysis()

	### Photonics Power and OMA -----------------------
	# note all defined in globals
	if (indPrint):
		print("PCM OMA: ", PCM_OMA, "dB")
		print("MRM Transmitter OMA: ", MRM_Tx_OMA, "dB")
		print()

	total_photonic_loss_OMA = photonic_loss_analysis() + PCM_OMA + MRM_Tx_OMA 
	laser_output_power_dBm = PD_power_total_dBm + total_photonic_loss_OMA
	laser_output_power = dB_to_regular(laser_output_power_dBm) # mW
	laser_wall_power = laser_output_power / laser_wall_efficiency

	if (summaryPrint):
		print("Photonics Power Summary")
		print("Total photonic losses/OMA: ", round(total_photonic_loss_OMA, decimalPoints), "dB")
		print("Total photonic power: ", round(laser_output_power, decimalPoints), "mW,", round(laser_output_power_dBm, decimalPoints), "dBm")
		print("Total laser power from wall: ", round(laser_wall_power, decimalPoints), "mW")
		print()

	return (laser_output_power, laser_wall_power)

def photonics_area_analysis():
	num_crossbar_cell = num_rows * num_cols
	crossbar_area_single = crossbar_pitch_x * crossbar_pitch_y
	crossbar_area_total = crossbar_area_single * num_crossbar_cell

	MRM_area_single = (MRM_radius * 2) * (MRM_radius * 2)
	MRM_area_total = MRM_area_single * num_MRM

	num_tx_power_splitter = num_rows - 1
	tx_power_splitter_area_total = tx_power_splitter_area_single * num_tx_power_splitter

	photonics_area_total = MRM_area_total + crossbar_area_total + tx_power_splitter_area_total + grating_coupler_area

	if (indPrint):
		print("MRM total area (for Tx and Rx): ", round(MRM_area_total, decimalPoints), "mm^2")
		print("Crossbar total area: ", round(crossbar_area_total, decimalPoints), "mm^2")
		print("Tx power splitters total area: ", round(tx_power_splitter_area_total, decimalPoints), "mm^2")
		print("Grating coupler area: ", round(grating_coupler_area, decimalPoints), "mm^2")
		print()

	if (summaryPrint):
		print("Photonics Area Summary")
		print("Total Photonics Area: ", round(photonics_area_total, decimalPoints), "mm^2")
		print()

	return(summaryPrint)

'''
def electronics_component_count():
	elc_comp_count = dict({"num_ADC": num_cols, "num_PS": num_rows + num_cols, "num_ODAC": num_rows, "num_PCMHeater": num_rows * num_cols, \
		"num_MRMHeater_driver": num_cols + num_rows, "num_clocks": math.ceil((num_cols + num_rows) / 4), "num_RxAFE": num_cols})
'''

def electronics_power_analysis(SS_results):
	#ADC
	ADC_power_single = ADC_power_all[freq_index]
	ADC_power_total = ADC_power_single * num_ADC 

	#Serializer/deserializer
	PS_power_single = PS_energyPerBit * symbolSize * symbolRate * mW_adjustment
	PS_power_total = PS_power_single * num_PS 

	#ODACs
	ODAC_power_single = ODAC_energyPerSymbol * symbolRate * mW_adjustment
	ODAC_power_total = ODAC_power_single * num_ODAC 

	# PCM Heater
	PCMHeater_power_single = (PCMHeater_energyPerProgram / program_cycle_time) * mW_adjustment
	PCMHeater_power_total = PCMHeater_power_single * num_PCMHeater 

	# MRM Heaters
	MRMHeater_power_total  = MRMHeater_power_single * num_MRMHeater_driver
	
	# SRAM 
	SRAM_energyPerSymbol = SRAM_energyPerBit * symbolSize 
	SRAM_energy_total_program = SS_results.loc["SRAM Filter Reads"].values[0] * SRAM_energyPerSymbol
	SRAM_power_total_program  = (SRAM_energy_total_program / program_time_total) * mW_adjustment

	SRAM_energy_total_compute = (SS_results.loc["SRAM Input Reads"].values[0] + SS_results.loc["SRAM Output Writes"].values[0]) * SRAM_energyPerSymbol
	SRAM_power_total_compute = (SRAM_energy_total_compute / compute_time_total) * mW_adjustment
	
	# DRAM
	DRAM_energyPerSymbol = DRAM_energyPerBit * symbolSize 
	DRAM_energy_total_program = SS_results.loc["DRAM Filter Reads"].values[0] * DRAM_energyPerSymbol
	DRAM_power_total_program  = (DRAM_energy_total_program / program_time_total) * mW_adjustment

	DRAM_energy_total_compute = (SS_results.loc["DRAM Input Reads"].values[0] + SS_results.loc["DRAM Output Writes"].values[0]) * DRAM_energyPerSymbol
	DRAM_power_total_compute = (DRAM_energy_total_compute / compute_time_total) * mW_adjustment

	# clock
	clock_power_single = clock_energyPerCycle * symbolRate * mW_adjustment
	clock_power_total = clock_power_single * num_clocks

	# rx AFE
	RxAFE_power_total = RxAFE_power_single * num_RxAFE

	electrical_power_compute_total = ADC_power_total + PS_power_total + ODAC_power_total + SRAM_power_total_compute + \
	clock_power_total + RxAFE_power_total + MRMHeater_power_total + DRAM_power_total_compute 
	electrical_power_program_total = PCMHeater_power_total + SRAM_power_total_program
	electrical_power_combined_total = electrical_power_program_total * program_portion + electrical_power_compute_total * compute_portion
	#electrical_power_wall = electrical_power_combined_total / DC_DC_efficiency

	if (indPrint):
		print("ADCs total power: ", round(ADC_power_total, decimalPoints))
		print("Serializers total power: ", round(PS_power_total, decimalPoints), "mW")
		print("ODAC drivers total power: ", round(ODAC_power_total, decimalPoints), "mW")
		print("PCM heaters total power: ", round(PCMHeater_power_total, decimalPoints), "mW")
		print("MRM heaters total power: ", round(MRMHeater_power_total, decimalPoints), "mW")
		print("SRAM power total program: ", round(SRAM_power_total_program, decimalPoints), "mW")
		print("SRAM power total compute: ", round(SRAM_power_total_compute, decimalPoints), "mW")

		print("DRAM power total program: ", round(DRAM_power_total_program, decimalPoints), "mW")
		print("DRAM power total compute: ", round(DRAM_power_total_compute, decimalPoints), "mW")

		print("Total effective number of clocks: ", num_clocks)
		print("Clock total power: ", round(clock_power_total, decimalPoints), "mW")
		print()

	if (summaryPrint):
		print("Electronics power summary")
		print("Total electrical power compute: ", round(electrical_power_compute_total, decimalPoints), "mW")
		print("Total electrical power program: ", round(electrical_power_program_total, decimalPoints), "mW")
		print("Total electrical power combined: ", round(electrical_power_combined_total, decimalPoints), "mW")
		#print("Total electrical power from wall: ", round(electrical_power_wall), "mW")
		print()

	return electrical_power_combined_total

def electronics_area_analysis(array_params):
	#ADC
	ADC_area_single  = ADC_area_all[freq_index]
	ADC_area_total  = ADC_area_single * num_ADC

	#PS
	PS_area_total  = PS_area_single  * num_PS

	#ODAC
	ODAC_area_total  = ODAC_area_single * num_ODAC

	#PCM Heaters
	PCMHeater_area_total  = PCMHeater_area_single * num_PCMHeater

	#MRM Heater
	MRMHeater_area_total  = MRMHeater_area_single * num_MRMHeater_control

	#SRAM
	SRAM_area_total  = SRAM_area_single * (array_params.loc["SRAM Input Size"].values[0] + array_params.loc["SRAM Filter Size"].values[0] + array_params.loc["SRAM Output Size"].values[0])

	#Clock
	clock_area_total = clock_area_single * num_clocks

	#DRAM 
	DRAM_area_total = 0;

	#RX AFE
	RxAFE_area_total  = RxAFE_area_single * num_RxAFE

	if (indPrint):
		print("ADCs total area:  ",  round(ADC_area_total, decimalPoints), "mm^2")
		print("Serializers total area:  ", round(PS_area_total, decimalPoints), "mm^2")
		print("ODAC drivers total area:  ", round(ODAC_area_total, decimalPoints), "mm^2")
		print("PCM heaters total area:  ", round(PCMHeater_area_total, decimalPoints), "mm^2")
		print("MRM heaters total area:  ", round(MRMHeater_area_total, decimalPoints), "mm^2")
		print("SRAM area total: ", round(SRAM_area_total, decimalPoints), "mm^2")
		print("DRAM area total:  ", round(DRAM_area_total, decimalPoints), "mm^2")
		print("Clock total area:  ", round(clock_area_total, decimalPoints),  "mm^2")
		print("Rx AFE total area:  ", round(RxAFE_area_total, decimalPoints), "mm^2")
		print()

	electronics_area = ADC_area_total + ODAC_area_total + SRAM_area_total + PCMHeater_area_total + clock_area_total \
	+ RxAFE_area_total + MRMHeater_area_total + DRAM_area_total

	if (summaryPrint):
		print("Electronics Area Summary")
		print("Total electrical area: ", round(electronics_area, decimalPoints + 1), "mm^2")
		print()
	return(electronics_area)


def run_power_area_model(SS_results, array_params, symbolRate):
	identify_globals(array_params, symbolRate)
	component_count()

	time_analysis(SS_results.loc["Total Weights Programming Cycles"].values[0], SS_results.loc["Total Vector Segments Processed"].values[0])
	(laser_output_power, laser_wall_power) = photonics_power_analysis()
	photonics_area_total = photonics_area_analysis()
	(electronics_power_circuit) = electronics_power_analysis(SS_results)
	electronics_area = electronics_area_analysis(array_params)
	total_power = electronics_power_circuit + laser_wall_power
	total_area  = electronics_area  + photonics_area_total

	inferences_per_second = 1/total_time
	inferences_per_second_per_watt = inferences_per_second / total_power

	overall_specs.at["Total Chip Area":"Inferences Per Second Per Watt", ""] = [total_area, \
	total_power, inferences_per_second, inferences_per_second_per_watt] 

	if (summaryPrint): 
		print("Overall Summary")
		print("Total Power:", round(total_power, decimalPoints), "mW")
		print("Inferences Per Second:", round(inferences_per_second, decimalPoints))
		print("Inferences Per Seconds Per Watt:", round(inferences_per_second_per_watt, decimalPoints))
		print()
	if (highestSummaryPrint):
         x = 1
		#print("	inf per sec:", round(inferences_per_second, decimalPoints), \
		#	", power:", round(total_power, decimalPoints), "mW", \
		#	", inf per sec per watt", round(inferences_per_second_per_watt, decimalPoints))

	return overall_specs






