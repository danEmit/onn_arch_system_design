import time 

#import sys
#print(sys.path)

#import scale_sim
from scalesim.scale_sim import scalesim




def main():
    dummy_config_file = "/Users/d/Desktop/SS_adaptation.nosync/dummy/scale.cfg"
    dummy_NN_file = "/Users/d/Desktop/SS_adaptation.nosync/dummy/basicNN.csv"
    gemm_input = 0
    logpath = "/Users/d/Desktop/SS_adaptation.nosync/logs"

    s = scalesim(save_disk_space=True, verbose=1,
                 config=dummy_config_file,
                 topology=dummy_NN_file,
                 input_type_gemm=gemm_input,
                 )
    startExecutionTime = time.time()
    #logpath = "../test_runs"
    s.run_scale(top_path=logpath)
    endExecutionTime = time.time()
    print("\nTOTAL SS EXECUTION TIME:", round((endExecutionTime - startExecutionTime), 3))
    print()
    

if __name__ == "__main__":
    main()




