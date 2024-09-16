import os
from datetime import datetime
import shutil
import subprocess
import multiprocessing as mp

def run_topas(x1):
        print("command")
        command = x1[0][0]
        rundatadir = x1[1][0]
        subprocess.run("cd " + rundatadir, shell=True)
        subprocess.run(command, cwd= rundatadir, shell =True)
        print('ran')

def log_output(input_file_path, filename, topas_application_path):
        rundatadir = os.path.join(
                os.getcwd() +"/runfolder",
                datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(rundatadir) #creates a folder marked by date and time 
        shutil.copy(input_file_path, rundatadir)
        
        if filename == 'dicom.bat':
                shutil.copy('/root/nccs/Topas_wrapper/src/boilerplates/runfiles/dicomfiles/HUtoMaterialSchneider.txt', rundatadir)
                shutil.copy('/root/nccs/Topas_wrapper/src/boilerplates/runfiles/dicomfiles/ConvertedTopasFile_head.txt', rundatadir)
                shutil.copy('/root/nccs/Topas_wrapper/src/boilerplates/runfiles/dicomfiles/Muen.dat', rundatadir)
                shutil.copy('/root/nccs/Topas_wrapper/src/boilerplates/runfiles/dicomfiles/NbParticlesInTime.txt', rundatadir)
                command = [topas_application_path + ' ' + rundatadir + '/dicom.bat']
                pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
                pool.map_async(run_topas, [(command, [rundatadir])])
                pool.close()
                pool.join()
                pass

        elif filename == 'generate_allproc.py':
        #       edit the file to add timestamp corrections
                shutil.copy('/root/nccs/Topas_wrapper/tmp/headsourcecode.bat', rundatadir)
                shutil.copy('/root/nccs/Topas_wrapper/src/boilerplates/runfiles/CTDI/ConvertedTopasFile.txt', rundatadir)
                shutil.copy('/root/nccs/Topas_wrapper/src/boilerplates/runfiles/CTDI/Muen.dat', rundatadir)
                command_topas = "python3 " + rundatadir + "/generate_allproc.py"
                subprocess.run(command_topas, cwd= rundatadir , shell =True)
              
                batch_files = ['Bottomhead_default.bat', 'Centrehead_default.bat', 'Lefthead_default.bat', 'Righthead_default.bat', 'Tophead_default.bat']
                command = []
                for filename in batch_files:
                        command.append(topas_application_path+ rundatadir + "/" + str(filename))

                print(command)
                pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
                pool.map_async(run_topas, [(command, [rundatadir])])
                pool.close()
                pool.join()

        else:
              pass


        # Not implemented yet
        # logger = logging.getLogger(__name__)
        # logname = rundatadir + '/example.log'
        # logging.basicConfig(filename= logname , encoding='utf-8', level=logging.DEBUG)

        # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # # Create a file handler to write logs to a file
        # file_handler = logging.FileHandler(logname)
        # file_handler.setLevel(logging.DEBUG)
        # file_handler.setFormatter(formatter)

        # # Create a stream handler to print logs to the console
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.DEBUG)  # You can set the desired log level for console output
        # console_handler.setFormatter(formatter)

        # # Add the handlers to the logger
        # logger.addHandler(file_handler)
        # logger.addHandler(console_handler)
        # logger.debug
        # logging.basicConfig(...)
        # multiprocessing_logging.install_mp_handler()
        # # pool = Pool(...)
        return rundatadir

if __name__ == "__main__":
    log_output()
    
    
# Now you can log messages with different levels
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')