import subprocess
import os
import multiprocessing as mp

batch_files = []
command = []
directory = os.getcwd()
topas_directory = "/root/topas/bin/topas "

for root, dirs, files in os.walk(directory):
    #dirs.clear()
    for filename in files:
#    	print('filename:',filename)
        if ('bat' in filename) and ('sourcecode' not in filename):
            batch_files.append(str(filename))
            command.append(topas_directory+ directory +"/runfolder"+"/"+str(filename))
    
# print(batch_files)
# print(command)

def run_topas(command):
	subprocess.run(["cd runfolder"], shell=True)
	subprocess.run(command, cwd= directory +"/runfolder", shell =True)
	
if __name__ ==  '__main__':
    pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
    pool.map_async(run_topas, command)
    pool.close()
    pool.join()

# pool = mp.Pool(15)
# pool.map_async(run_topas, command)
# pool.close()
# pool.join()

print("Done")

