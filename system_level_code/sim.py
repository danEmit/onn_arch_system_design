import math


printOut = 1
arrayRows = 3
arrayCols = 2

batch = 10

inputRows = [7]
inputCols = [7]

filterRows = [3]
filterCols = [3]
channels = [1]
filters = [1]
strideRow = [1]
strideCol = [1]

layers = len(inputRows)

computeCycles_res = []
programs_res = [] 

SRAMInputReads_res = []
SRAMOutputWrites_res = []

for layer in range(layers):
	filterSize = filterRows[layer] * filterCols[layer] * channels[layer]

	rowFold = math.ceil(filterSize / arrayRows)
	colFold = math.ceil(filters[layer] / arrayCols)

	programs = rowFold * colFold
	convRows = math.ceil((inputRows[layer] - filterRows[layer] + 1) / strideRow[layer]) 
	convCols = math.ceil((inputCols[layer] - filterCols[layer] + 1) / strideCol[layer]) 
	#convRows = math.ceil(inputRows[layer] / strideRow[layer])
	#convCols = math.ceil(inputCols[layer] / strideCol[layer])
	computeCycles = programs * convRows * convCols * batch

	avgRowsUsed = filterSize / (filterRows[layer] * rowFold)
	SRAMInputReads = computeCycles * avgRowsUsed

	avgColsUsed = filters[layer] / (filterCols[layer] * colFold)
	SRAMOutputWrites = computeCycles * avgColsUsed



	programs_res.append(programs)
	computeCycles_res.append(computeCycles)
	SRAMInputReads_res.append(SRAMInputReads)
	SRAMOutputWrites_res.append(SRAMOutputWrites)

	if (printOut):
		print()
		print("filter size", filterSize)
		print("row fold", rowFold)
		print("col fold", colFold)
		print("programs", programs)
		print("conv rows", convRows)
		print("conv cols", convCols)
		print("compute cycles", computeCycles)
		print("avg rows used", avgRowsUsed)
		print("SRAM input reads", SRAMInputReads)
		print("avg cols used", avgColsUsed)
		print("SRAM output writes", SRAMOutputWrites)
		print()


'''


print("programs", programs_res)
print("compute cycles", computeCycles_res)
print("SRAM input reads", SRAMInputReads_res)
print("SRAM output writes", SRAMOutputWrites_res)
'''