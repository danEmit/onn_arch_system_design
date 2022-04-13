def initialize(batch_size_input):
	#print("\nInitializing Globals\n")
	global memoryAccess 
	#global SRAM_demand_mat
	global ifmap_demand_mat
	global filter_demand_mat
	global ofmap_demand_mat
	global ifmap_demand_mat_non_skew

	global batch_size 
	global num_program
	global compute_clock_cycles

	ifmap_demand_mat = []
	filter_demand_mat = []
	ofmap_demand_mat = []
	ifmap_demand_mat_non_skew = []

	memoryAccess = []
	#SRAM_demand_mat = []
	batch_size = batch_size_input
	num_program = []
	compute_clock_cycles = []
	


	'''
	global ifmap_h 
    global ifmap_w
    global filt_h 
    global filt_w 
    global num_ch   
    global num_filt 
    global stride_h
    global stride_w
    ''' 

