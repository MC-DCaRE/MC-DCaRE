import pandas as pd
import numpy
import math
import os
from warnings import simplefilter
simplefilter(action="ignore",category=pd.errors.PerformanceWarning)


directory = os.getcwd()

def count_non_empty_csv_files(folder_path):
    """
    Counts the number of non-empty CSV files in the specified folder.

    Args:
        folder_path (str): Path to the folder containing CSV files.

    Returns:
        int: Number of non-empty CSV files.
    """
    csv_count = 0
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path) and filename.lower().endswith(".csv"):
            # Check if the file size is greater than zero
            if os.path.getsize(full_path) > 0:
                csv_count += 1
    return csv_count

# Leftheadcol12_5p346col34_6p2_angle90p0_bmx5p8_bmy24p4_stb11p7_cch0p40_dfhly1p7_tit0p001_120kvChamberPlug_tle0
scorer = ["tle"]#["dtm","tle"]#,"flu","eflu"]#["tle"] #
coll12opening = ["5.35"]#["5.418"]#["5.35","5.352","5.354","5.346","5.344"]#["5.30"]#["5.418"]#,"5.41","5.412"]#["{:.3f}".format(i) for i in numpy.arange(5.40,5.42,0.002)]#["5.30","5.41"]#]
coll34opening = ["6.23"]#["6.175"]#["{:.3f}".format(i) for i in numpy.arange(6.17,6.191,0.002)]#["6.18"]#
vangle = ["90.0"]#["180.0","270.0","0.0"]#["90.0"]#["180.0","270.0","0.0"]#["270.0","0.0"]#
param_range1 = coll12opening#coll34opening#vseed #lrtrap#srctobladedistance
param_range2 = vangle
protocolnames = ["Top","Left","Bottom","Right","Centre"]#"Top","Bottom","Left"]
bmsprdx_range = ["5.8"]#["{:.1f}".format(i) for i in numpy.arange(3,10,0.2)]#["7.0"]#["{:.1f}".format(i) for i in numpy.arange(3,28,1)]#["22.0"]#["10.7"]#["10.4"]#["5.0"]#["3.0"]#["2.8"]#["2.5","2.6","2.8","2.9"]
bmsprdy_range = ["24.4"]
stb_range = ["11.7"]#["{:.1f}".format(i) for i in numpy.arange(3,7.,0.2)]#["8.5"]#
# stb_range = ["8","8.5","9","9.3","10","10.5","11","11.5","12"]#["0.10","0.105","0.11","0.115","0.12","0.125","0.13","0.135","0.14"]#["0.10","0.11","0.13","0.14"]
cch_thick_range = ["0.40"]#["{:.2f}".format(i) for i in numpy.arange(0.05, 0.5, 0.05)]
dh_fly = ["1.7"]#["{:.2f}".format(i) for i in numpy.arange(2, 8.1, 0.5)] #["0.5"]
# bmx2p8_bmy15_stb0p1_cch0p6_tle
# bmx2p8_bmy15_stb0p1_cch0p6_tle
tithalfthick =  ["0.001"]#,"0.005"]#["{:.3f}".format(i) for i in numpy.arange(0.001, 0.5, 0.1)]#

total = len(coll12opening)*len(coll34opening)*len(vangle)*len(protocolnames)*len(bmsprdx_range)*len(bmsprdy_range)*len(stb_range)*len(cch_thick_range)*len(dh_fly)
print("total jobs = "+str(total))
print("total csv = "+str(total*6))
# print(len(coll12opening))

# Example usage:
folder_to_search = directory #"/path/to/your/folder"
result = count_non_empty_csv_files(folder_to_search)
print(f"Number of non-empty CSV files in '{folder_to_search}': {result}")

# protocolnames = ["Top","Left","Bottom"]#,"Centre", "Bottom", "Left", "Right"]
# Topheadcoll12_5p353_angle_0p0_DF_HLY_4p4ChamberPlug_tle0
databs = pd.DataFrame()
#centre
for names in protocolnames:

	for para2 in param_range2:
		for para1 in param_range1:
			for col34 in coll34opening:
				for bmx in bmsprdx_range:
					for bmy in bmsprdy_range:
						for stb in stb_range:
							for cch in cch_thick_range:
								for me in scorer:
									for DF_HLY in dh_fly:
										for ii in tithalfthick:
										# for ii in [0]:#numpy.arange(1,5,0.5):numpy.arange(1,5,0.5):
											
											# includeFile = 'ConvertedTopasFile_'+"{:.2f}".format(ii)+'.txt'
											
										# centrecsvname = names+"head"+"seed"+str(para1)
											# centrecsvname = names+"head"+"coll12_"+str(para1)+"_angle"+str(para2)+"_bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_90kv"+"ChamberPlug_"+str(me)+"0"
											# centrecsvname = centrecsvname.replace(".","p")
											# tablename = "bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_"+str(me)
											# tablename = tablename.replace(".","p")
											# print(centrecsvname)
											# df = pd.read_csv(centrecsvname+ ".csv",skiprows = 5, names = ['Dose (Gy)'])     
											# # totaldose = df['Dose (Gy)'].sum()
											# # df = pd.read_csv(centrecsvname+ ".csv",skiprows = 8, names = ['X', 'Y', 'Z', 'Dose (Gy)'])
											# totaldose = df['Dose (Gy)'].sum()

											# rowname = names+"_"+para2+"_"+para1
											# databs.loc[rowname,tablename] = totaldose
			                                # Topheadcoll12_5p509_angle180p0_bmx11_bmy9p5_stb12_cch1p4_dfhly6p5_120kvChamberPlug_tle0
											centrecsvname = names+"head"+"col12_"+str(para1)+"col34_"+str(col34)+"_angle"+str(para2)+"_bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_dfhly"+str(DF_HLY)+"_tit"+ii+"_120kv"+"ChamberPlug_"+str(me)+"0"
											# centrecsvname = names+"head"+"col12_"+str(para1)+"col34_"+str(col34)+"_angle"+str(para2)+"_bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_dfhly"+str(DF_HLY)+"_cvt"+"{:.2f}".format(ii)+"_120kv"+"ChamberPlug_"+str(me)+"0"
											centrecsvname = centrecsvname.replace(".","p")
											# tablename = "coll12_"+str(para1)
											# tablename = "col12"+str(para1)+"col34"+str(col34)+"tit"+ii+"_bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_dfhly"+str(DF_HLY)
											# tablename = "bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_dfhly"+str(DF_HLY)+"_tit"+ii#+"_"+str(me)#+"_coll34_"+para1
											tablename = "col34"+str(col34)+"bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_dfhly"+str(DF_HLY)+"_"+str(me)+"_Al"+ii
											# tablename = "col12"+str(para1)+"bmx"+str(bmx)+"_bmy"+str(bmy)+"_stb"+str(stb)+"_cch"+str(cch)+"_dfhly"+str(DF_HLY)+"_"+str(me)+"_tit"+ii

											tablename = tablename.replace(".","p")
											# print(centrecsvname)
											# filename = centrecsvname+".csv"
											filename = "oldfiles/"+centrecsvname+".csv"
											# filename = "csvfiles/"+centrecsvname+".csv"
											if os.path.isfile(filename):
												# print("isfile")
												df = pd.read_csv(filename,skiprows = 5, names = ['Dose (Gy)'])     
											# totaldose = df['Dose (Gy)'].sum()
											# df = pd.read_csv(centrecsvname+ ".csv",skiprows = 8, names = ['X', 'Y', 'Z', 'Dose (Gy)'])
												totaldose = df['Dose (Gy)'].sum()

												# rowname = names+"_"+para2
												rowname = names+"_"+para2+"_"+para1
												databs.loc[rowname,tablename] = totaldose
												# databs.loc[tablename,rowname] = totaldose
databs.to_csv("stb11p7_coll12_5p35_6p23_bmcut90_ig.csv", index=True)
print(databs)
# Topheadcoll12_5p509_angle270p0_bmx2p7_bmy20_stb0p10_cch0p9_100kvChamberPlug_tle0

