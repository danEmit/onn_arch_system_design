import argparse
import sys
import globals
import numpy as np
import time
import os

#content_path = "/Users/D/Desktop/research/scale-sim-v2/"

content_path = os.getcwd()
content_path = content_path[0:content_path.rfind("/")+1]
sys.path.append(content_path)
from scalesim.scale_sim import scalesim

globals.initialize()

logpath = ""

def analyze_memory_writes():
    # here are some magic numbers. they are important!
    SRAM_IFMAP_READS  = 2
    SRAM_FILTER_READS = 5
    SRAM_OFMAP_WRITES = 8
    DRAM_IFMAP_READS  = 11
    DRAM_FILTER_READS = 14
    DRAM_OFMAP_WRITES = 17

    sram_reads  = 0
    sram_writes = 0
    dram_reads  = 0
    dram_writes = 0
    print("\nWill now analyze memory accesses")

    sram_ifmap_reads  = 0
    sram_filter_reads = 0
    sram_ofmap_writes = 0

    dram_ifmap_reads  = 0
    dram_filter_reads = 0
    dram_ofmap_writes = 0

    for row in globals.memoryAccess:
        sram_reads  += row[SRAM_IFMAP_READS] + row[SRAM_FILTER_READS]
        sram_writes += row[SRAM_OFMAP_WRITES]
        dram_reads  += row[DRAM_IFMAP_READS] + row[DRAM_FILTER_READS]
        dram_writes += row[DRAM_OFMAP_WRITES]

        sram_ifmap_reads  += row[SRAM_IFMAP_READS]
        sram_filter_reads += row[SRAM_FILTER_READS]
        sram_ofmap_writes += row[SRAM_OFMAP_WRITES]

        dram_ifmap_reads  += row[DRAM_IFMAP_READS]
        dram_filter_reads += row[DRAM_FILTER_READS]
        dram_ofmap_writes += row[DRAM_OFMAP_WRITES]

    if (0):
        print("SRAM Reads:  ", sram_reads)
        print("SRAM Writes: ", sram_writes)
        print("DRAM Reads:  ", dram_reads)
        print("DRAM Writes: ", dram_writes)

    print()
    if (1):
        print("SRAM IFMAP Reads:   ", sram_ifmap_reads)
        print("SRAM Filter Reads:  ", sram_filter_reads)
        print("SRAM Output Writes: ", sram_ofmap_writes)

        print("DRAM IFMAP Reads:   ", dram_ifmap_reads)
        print("DRAM Filter Reads:  ", dram_filter_reads)
        print("DRAM Output Writes: ", dram_ofmap_writes)
        print()


def analyze_SRAM_trace(SRAM_demand_mat):
    numLayers = len(SRAM_demand_mat)
    #print("num layers", numLayers)
    SRAM_cycles = [0] * numLayers
    for layer in range(numLayers):
        row_idx = 0
        SRAM_cycles[layer] = []
        #print("here is layer: ", layer)
        SRAM_demand_mat_singleLayer = SRAM_demand_mat[layer]
        while (row_idx < SRAM_demand_mat_singleLayer.shape[0]):
            row = SRAM_demand_mat_singleLayer[row_idx, :] 
            program_row_count = 0
            program_col_count = 0 #redundant?
             
            while(sum(row == -1) != row.shape[0]):
                if (program_row_count == 0):
                    program_col_count = sum(row != -1)
                program_row_count += 1
                row_idx += 1
                row = SRAM_demand_mat_singleLayer[row_idx, :]  

            if program_row_count != 0: 
                statsRow = [program_row_count, program_col_count, program_col_count * program_row_count]
                #print("hi here", statsRow)
                SRAM_cycles[layer].append(statsRow)
            
            else:
                row_idx += 1
                
        SRAM_cycles[layer] = np.array(SRAM_cycles[layer])

    return SRAM_cycles


def analyze_SRAM_usage():
    input_demand_mat = globals.ifmap_demand_mat
    filter_demand_mat = globals.filter_demand_mat
    output_demand_mat = globals.ofmap_demand_mat
    input_demand_mat_non_skew = globals.ifmap_demand_mat_non_skew

    np.savetxt(logpath + "/input_SRAM_mat.csv",  input_demand_mat[0], delimiter = ",")
    np.savetxt(logpath + "/filter_SRAM_mat.csv", filter_demand_mat[0], delimiter = ",")
    np.savetxt(logpath + "/output_SRAM_mat.csv", output_demand_mat[0], delimiter = ",")
    np.savetxt(logpath + "/input_unskew_SRAM_mat.csv", input_demand_mat_non_skew[0], delimiter = ",")

    filter_SRAM_cycles = analyze_SRAM_trace(filter_demand_mat)
    num_weight_programming_cycles_total = 0
    num_weight_programming_ind_total = 0
    print("\nWeights programming stats by NN layer:")
    for layerNum in range(len(filter_SRAM_cycles)):
        num_weight_programming_cycles_layer = filter_SRAM_cycles[layerNum].shape[0]
        num_weight_programming_cycles_total += num_weight_programming_cycles_layer
        
        num_weight_programming_ind_layer = sum(filter_SRAM_cycles[layerNum][:, 2])
        num_weight_programming_ind_total += num_weight_programming_ind_layer
        
        print("layer:",layerNum)
        print("# programming cycles:",num_weight_programming_cycles_layer, "------- # ind weights programmed:",num_weight_programming_ind_layer)
        #print("Details on weights programming cycles - rows, columns, total weights:")
        #print(filter_SRAM_cycles[layerNum])
    print("\nTOTAL WEIGHTS PROGRAMMING CYCLES:", num_weight_programming_cycles_total)
    print("TOTAL INDIVIDUAL WEIGHTS PRORGRAMMED:", num_weight_programming_ind_total)
    print()
    
    
    input_SRAM_cycles = analyze_SRAM_trace(input_demand_mat_non_skew)
    num_compute_cycles_total = 0
    num_input_compute_vector_segments_total = 0
    print("\nInput computation vectors stats by NN layer:")
    for layerNum in range(len(input_SRAM_cycles)):
        num_compute_cycles_layer = input_SRAM_cycles[layerNum].shape[0]
        num_compute_cycles_total += num_compute_cycles_layer
        
        num_input_compute_vector_segments_layer = sum(input_SRAM_cycles[layerNum][:, 0])
        num_input_compute_vector_segments_total += num_input_compute_vector_segments_layer
        
        print("layer:", layerNum)
        print("# compute cycles:", num_compute_cycles_layer, "------- # ind input vector SEGMENTS processed:", num_input_compute_vector_segments_layer)
    
    print("\nTOTAL COMPUTE CYCLES:", num_compute_cycles_total)
    print("TOTAL VECTOR SEGMENTS PROCESSED IN ARRAY:", num_input_compute_vector_segments_total)
    print()


def post_process():
    print("\n**** Will now do post-processing ****")
    analyze_memory_writes()
    analyze_SRAM_usage()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', metavar='Topology file', type=str,
                        default="../topologies/conv_nets/test.csv",
                        help="Path to the topology file"
                        )
    parser.add_argument('-c', metavar='Config file', type=str,
                        default="../configs/scale.cfg",
                        help="Path to the config file"
                        )
    parser.add_argument('-p', metavar='log dir', type=str,
                        default="../test_runs",
                        help="Path to log dir"
                        )
    parser.add_argument('-i', metavar='input type', type=str,
                        default="conv",
                        help="Type of input topology, gemm: MNK, conv: conv"
                        )

    batchSize = 10

    args = parser.parse_args()
    topology = args.t
    config = args.c
    logpath = args.p
    inp_type = args.i

    gemm_input = False
    if inp_type == 'gemm':
        gemm_input = True

    s = scalesim(save_disk_space=True, verbose=True,
                 config=config,
                 topology=topology,
                 input_type_gemm=gemm_input
                 )
    startExecutionTime = time.time()
    s.run_scale(top_path=logpath)
    endExecutionTime = time.time()
    print("\nTOTAL EXECUTION TIME:", round((endExecutionTime - startExecutionTime), 3))
    print()

    post_process()
    #analyze_memory_writes()
    #analyze_SRAM_usage()
    endPostProcessTime = time.time()
    print("\nTOTAL POST PROCESS TIME:", round((endPostProcessTime - endExecutionTime), 3))

    print("\n\n")









