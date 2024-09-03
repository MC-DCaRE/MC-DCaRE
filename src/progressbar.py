
import PySimpleGUI as sg
import os 
import sys
import time

path = sys.argv[1]
num_of_csvresult = sys.argv[2]

def count_filled_csv ():
	num_filled_csv = 0
	for filename in os.listdir(path+"/runfolder/datafolder"):
		if filename.lower().endswith('.csv'):
			file_path = os.path.join(path+"/runfolder/datafolder", filename)
			if os.path.getsize(file_path) > 0:
				num_filled_csv += 1
	return num_filled_csv

layout = [
    [sg.Text('Running...')],
    [sg.ProgressBar(num_of_csvresult, orientation='h', size=(20, 20), key='-PROGRESS_BAR-')],
    [sg.Text(f"{count_filled_csv()} / {num_of_csvresult} done"), sg.Text('Current Time: ',key='-TIME-')],
]

window = sg.Window('Progress', layout)

start_time = time.time()

while True:
    event, values = window.read(timeout=1000)

    if event == sg.WINDOW_CLOSED:
        break

    i=count_filled_csv()
    window['-PROGRESS_BAR-'].update(i)
    elapsed_seconds = int(time.time() - start_time)
    elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))
    window['-TIME-'].update(f'Elapsed Time: {elapsed_time_str}')

window.close()

#doesn't work not sure why
#while True:
	#sg.one_line_progress_meter('Progress',count_filled_csv(),num_of_csvresult)