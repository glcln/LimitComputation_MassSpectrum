import ROOT
import json
import sys

######### TEMPORARY HACK FOR WRONG XS NUMBERS. SET TO ONE AFTER FIXED.
scale = 1


#inputFolder = "./2DAlpha_CodeV46p3_1Dfrom2DNoExtrapol_ZPrimeTauPrime/"
#inputFolder = "./2DAlpha_CodeV46p2_1Dfrom2DNoExtrapol_ZPrimeTauPrimeWithSSM/"
inputFolder = "./2DAlpha_CodeV46p8_1Dfrom2DNoExtrapol_ZPrimeTauPrimeOfficial"

outputPoints = []

for ZPrimeMass in [3000,4000,5000,6000,7000]:
	# for tauPrimeMass in [200,400,600,800,1000,1200,1400]:
	for tauPrimeMass in [200,400,600,800,1000,1400]:
                if(ZPrimeMass==3000 and tauPrimeMass==800):
                    continue

                tmpName = "tauPrime2e-{}-ZPrimeSSM-{}_2018".format(tauPrimeMass,ZPrimeMass)
		#inputFileName = "{}/Signal_tauPrime2e-{}-ZPrime-{}/higgsCombine.{}.AsymptoticLimits.mH120.root".format(inputFolder,tauPrimeMass,ZPrimeMass,tmpName)
                inputFileName = "{}/higgsCombine.{}.AsymptoticLimits.mH120.root".format(inputFolder,tmpName)
                inputFile = ROOT.TFile(inputFileName)
                inputTree = inputFile.Get("limit")
		tmpDict = {}
		tmpDict["m1"] = ZPrimeMass
		tmpDict["m2"] = tauPrimeMass
		tmpDict["dm"] = tmpDict["m1"]-tmpDict["m2"]

		# inputTree.Print()
		for entry in inputTree:
			# print(entry.)
			# print(entry.limit)
			# print(entry.quantileExpected)

			if entry.quantileExpected==-1:
				tmpDict["upperLimit"] = entry.limit*scale
			if entry.quantileExpected==0.02500000037252903:
				tmpDict["expectedUpperLimitMinus2Sig"] = entry.limit*scale
			elif entry.quantileExpected==0.1599999964237213:
				tmpDict["expectedUpperLimitMinus1Sig"] = entry.limit*scale
			elif entry.quantileExpected==0.5:
				tmpDict["expectedUpperLimit"] = entry.limit*scale
			elif entry.quantileExpected==0.8399999737739563:
				tmpDict["expectedUpperLimitPlus1Sig"] = entry.limit*scale
			elif entry.quantileExpected==0.9750000238418579:
				tmpDict["expectedUpperLimitPlus2Sig"] = entry.limit*scale

		outputPoints.append(tmpDict)


with open("ZPrimeLimits.json", 'w') as f:
    json.dump(outputPoints, f, indent=4)
