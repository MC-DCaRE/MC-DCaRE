# This script is used to handle all the initialisation and running of the simulations. It will set up a date and timestamped folder in /runfolder and copy all the relevant files from /tmp and /src over into it
# The duplication of the files are intended, this will allow for users to rerun the script as it was in case of downstream changes in the future. 
# Future improvments would be to add in and logging function that logs the console output at runtime. This would allow for easier debugging  
import os
from datetime import datetime
import shutil
import subprocess
import multiprocessing as mp

def run_topas(x1):
        command = x1[0][0]
        rundatadir = x1[1][0]
        subprocess.run("cd " + rundatadir, shell=True)
        result = subprocess.run(command, cwd= rundatadir, shell =True, capture_output=True, text=True)
        print(result.stdout) #Gives console output
        print('ran')

def log_output(input_file_path, tag, topas_application_path, fan_tag):
        rundatadir = os.path.join(
                os.getcwd() +"/runfolder",
                datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(rundatadir) #creates a folder marked by date and time 
        shutil.copy(input_file_path, rundatadir)
        path = os.getcwd()
        
        if tag == 'dicom':
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/HUtoMaterialSchneider.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/ConvertedTopasFile_head.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Muen.dat', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Graphics.txt', rundatadir)
                if fan_tag == 'Full Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/fullfan.txt', rundatadir)
                elif fan_tag == 'Half Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/halffan.txt', rundatadir)
                shutil.copy(path + '/tmp/headsourcecode.txt', rundatadir)
                shutil.copy(path + '/tmp/patientDICOM.txt', rundatadir)

                command = [topas_application_path + ' ' + rundatadir + '/headsourcecode.txt']
                pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
                pool.map_async(run_topas, [(command, [rundatadir])])
                pool.close()
                pool.join()
                run_status= "DICOM simulation completed"

        elif tag == 'ctdi16':
                # Needs plus position generator 
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/ConvertedTopasFile_head.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Muen.dat', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Graphics.txt', rundatadir)
                ### ADD 5 plugs generation
                if fan_tag == 'Full Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/fullfan.txt', rundatadir)
                elif fan_tag == 'Half Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/halffan.txt', rundatadir)
                shutil.copy(path + '/tmp/headsourcecode.txt', rundatadir)
                shutil.copy(path + '/tmp/CTDIphantom_16.txt', rundatadir)

                command = [topas_application_path + ' ' + rundatadir + '/headsourcecode.txt']
                pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
                pool.map_async(run_topas, [(command, [rundatadir])])
                pool.close()
                pool.join()
                run_status= "CTDI simulation completed" 

        elif tag == 'ctdi32':
                # Needs plus position generator 
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/ConvertedTopasFile_head.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Muen.dat', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Graphics.txt', rundatadir)
                ### ADD 5 plugs generation
                if fan_tag == 'Full Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/fullfan.txt', rundatadir)
                elif fan_tag == 'Half Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/halffan.txt', rundatadir)
                shutil.copy(path + '/tmp/headsourcecode.txt', rundatadir)
                shutil.copy(path + '/tmp/CTDIphantom_32.txt', rundatadir)

                command = [topas_application_path + ' ' + rundatadir + '/headsourcecode.txt']
                pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
                pool.map_async(run_topas, [(command, [rundatadir])])
                pool.close()
                pool.join()
                run_status= "CTDI simulation completed" 

        else:
              run_status = 'Error encountered' 


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
        return run_status

if __name__ == "__main__":
    log_output()
    
    
# Now you can log messages with different levels
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')