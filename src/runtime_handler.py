# This script is used to handle all of the initialisation and running of simulations. It will set up a date and timestamped folder in /runfolder and copy all of the relevant files from /tmp and /src over into it
# The duplication of files are intended, this will allow for users to rerun the script as it was in case of downstream changes in the future or for reevaluation.
# Future improvements would be to add in a logging function that logs console output at runtime. This would allow for easier debugging and integrate a progress bar that watches the number of histories left to completion.
import os
from datetime import datetime
import shutil
import subprocess
import multiprocessing as mp


def run_topas(command, rundatadir):
    # This function runs TOPAS simulation with the given command and directory
    result = subprocess.run(
        command, cwd=rundatadir, shell=True
    )  # for instant console output
    print("ran")


def plugsgenerator(phantomsize: str, rundatadir: str, topas_application_path: str):
    """
    This function is only used for CTDI to generate 5 files to simulate the placement of a detector on 5 possible plug positions.
    Returns a list of (command, rundatadir) tuples to be processed.
    """
    path = os.getcwd()
    plugs_position = [
        "ChamberPlugCentre",
        "ChamberPlugTop",
        "ChamberPlugBottom",
        "ChamberPlugLeft",
        "ChamberPlugRight",
    ]
    commands = []
    for position in plugs_position:
        with open(path + "/tmp/headsourcecode.txt", "r") as f:
            content1 = f.read()
        if phantomsize == "ctdi16":
            phantom_path = path + "/tmp/CTDIphantom_16.txt"
        elif phantomsize == "ctdi32":
            phantom_path = path + "/tmp/CTDIphantom_32.txt"
        else:
            phantom_path = path + "/tmp/CTDIphantom_16.txt"
        with open(phantom_path, "r") as f:
            content2 = f.read()

        combined = content1 + content2
        # Replace placeholders before writing the final file
        combined = combined.replace("@@PLACEHOLDER@@", position)
        combined = combined.replace(
            "s:Ge/" + position + '/Material="PMMA"',
            "s:Ge/" + position + '/Material="Air"',
        )

        positionfile = rundatadir + "/" + position + ".txt"
        with open(positionfile, "w") as f:
            f.write(combined)

        commands.append(
            (
                topas_application_path + " " + rundatadir + "/" + position + ".txt",
                rundatadir,
            )
        )
    return commands


def log_output(input_file_path, tag, topas_application_path, fan_tag):
    rundatadir = os.path.join(
        os.getcwd() + "/runfolder", datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    )
    os.makedirs(rundatadir)  # creates a folder marked by date and time
    shutil.copy(input_file_path, rundatadir)
    path = os.getcwd()

    if tag == "dicom":
        shutil.copy(
            path + "/src/boilerplates/TOPAS_includeFiles/HUtoMaterialSchneider.txt",
            rundatadir,
        )
        shutil.copy(path + "/src/boilerplates/TOPAS_includeFiles/Muen.dat", rundatadir)
        shutil.copy(
            path + "/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt",
            rundatadir,
        )
        if fan_tag == "Full Fan":
            shutil.copy(
                path + "/src/boilerplates/TOPAS_includeFiles/fullfan.txt", rundatadir
            )
        elif fan_tag == "Half Fan":
            shutil.copy(
                path + "/src/boilerplates/TOPAS_includeFiles/halffan.txt", rundatadir
            )
        shutil.copy(path + "/tmp/ConvertedTopasFile.txt", rundatadir)
        shutil.copy(path + "/tmp/head_calibration_factor.txt", rundatadir)
        shutil.copy(path + "/tmp/headsourcecode.txt", rundatadir)
        shutil.copy(path + "/tmp/patientDICOM.txt", rundatadir)

        command = topas_application_path + " " + rundatadir + "/headsourcecode.txt"
        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(run_topas, [(command, rundatadir)])
        run_status = "DICOM simulation completed"

    elif tag == "ctdi16":
        shutil.copy(path + "/src/boilerplates/TOPAS_includeFiles/Muen.dat", rundatadir)
        shutil.copy(
            path + "/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt",
            rundatadir,
        )
        shutil.copy(path + "/tmp/ConvertedTopasFile.txt", rundatadir)
        shutil.copy(path + "/tmp/head_calibration_factor.txt", rundatadir)
        if fan_tag == "Full Fan":
            shutil.copy(
                path + "/src/boilerplates/TOPAS_includeFiles/fullfan.txt", rundatadir
            )
        elif fan_tag == "Half Fan":
            shutil.copy(
                path + "/src/boilerplates/TOPAS_includeFiles/halffan.txt", rundatadir
            )
        commands = plugsgenerator("ctdi16", rundatadir, topas_application_path)

        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(run_topas, commands)
        run_status = "CTDI simulation completed"

    elif tag == "ctdi32":
        shutil.copy(path + "/src/boilerplates/TOPAS_includeFiles/Muen.dat", rundatadir)
        shutil.copy(
            path + "/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt",
            rundatadir,
        )
        shutil.copy(path + "/tmp/ConvertedTopasFile.txt", rundatadir)
        shutil.copy(path + "/tmp/head_calibration_factor.txt", rundatadir)

        if fan_tag == "Full Fan":
            shutil.copy(
                path + "/src/boilerplates/TOPAS_includeFiles/fullfan.txt", rundatadir
            )
        elif fan_tag == "Half Fan":
            shutil.copy(
                path + "/src/boilerplates/TOPAS_includeFiles/halffan.txt", rundatadir
            )
        commands = plugsgenerator("ctdi32", rundatadir, topas_application_path)

        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(run_topas, commands)
        run_status = "CTDI simulation completed"

    else:
        run_status = "Error encountered"

    return run_status


if __name__ == "__main__":
    pass
