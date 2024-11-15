from pathlib import Path
import csv
import click
import cv2
from tqdm import tqdm
from recorder.experiment_recorder import GAZE_FILENAME, MOUSE_FILENAME, OVERLAYED_FILENAME, SCREEN_FILENAME, SCREEN_TSTAMPS_FILENAME, VideoWriter
from viewer.draw import BLUE, draw_circle
from viewer.gaze import GazeData
from viewer.heatmap import HeatmapPlotter


# for tkinter
import tkinter as tk
import tkinter.filedialog as tkFileDialog
from tkinter.ttk import Label
from tkinter import ttk
from time import sleep

SCREEN_TYPE = 'screen'
GAZE_TYPE = 'gaze'
MOUSE_TYPE = 'mouse'

# tkinter
root=tk.Tk()    
root.title("Post Process Overlayed")
ent1=tk.Entry(root,font=40)
ent1.grid(row=2,column=1)
label = Label(root, text='Give the directory for processing')
label.grid(row=1, column=1)



progressbar = ttk.Progressbar(orient=tk.HORIZONTAL, length=160)
progressbar.grid(row=4, column=1)


# ask for directory for compiling the overlayed movie
def browsefunc():
    # [] label asking the directory
    # [] directory selection
    # [] start button
    # [] progress bar
    
    filename =tkFileDialog.askdirectory()
    ent1.insert(tk.END, filename) 
    print(ent1.get())
    postprocess(ent1.get())
    ## end
    sleep(5)
    
    sleep(5)
    print("finalizado")
    root.destroy()


b1=tk.Button(root,text="Select the PATH",font=40,command=browsefunc)
b1.grid(row=3,column=1)

# post processing code
def fix_types(data_row):
    types = {
        'tstamp': float,
        'x': float,
        'y': float,
    }
    out = {}
    for k, v in data_row.items():
        convert = types.get(k, lambda d: d)
        out[k] = convert(v)
    return out


def load_data(filename, dtype):
    with open(filename) as f:
        reader = csv.DictReader(f)
        return [dict(**fix_types(row), dtype=dtype, frame_idx=i) for i, row in enumerate(reader)]


def process(screen_filename, overlayed_filename, data):
    video = cv2.VideoCapture(str(screen_filename))

    writer = None
    plotter = None
    frame = None
    last_gaze = None
    mouse = None

    # Get total number of iterations
    total_frames = len(data)

    # Function to write each frame
    def write_frame(frame):
        if frame is None:
            return

        curr_frame = frame.copy()
        curr_frame = plotter.plot(curr_frame)
        if mouse:
            draw_circle(curr_frame, mouse, BLUE, 10, radius_delta=5)
        if last_gaze:
            draw_circle(curr_frame, last_gaze, (0, 0, 255), 30, radius_delta=15)
        writer.add_frame(curr_frame)

    gaze_cache = []
    for i, d in enumerate(data):  # Removido o tqdm para não exibir no terminal
        # Update progress bar incrementally
        progress = (i + 1) / total_frames * 100
        progressbar['value'] = progress
        root.update_idletasks()  # This forces tkinter to update the progress bar
        root.update()  # This allows the tkinter window to update, ensuring the progress bar updates in real time
        
        dtype = d['dtype']
        if dtype == SCREEN_TYPE:
            write_frame(frame)
            _, frame = video.read()
            if writer is None:
                height, width = frame.shape[:2]
                writer = VideoWriter(overlayed_filename, width, height, 10.0)
                plotter = HeatmapPlotter(100, (width, height))
                for gaze in gaze_cache:
                    plotter.add_sample(gaze)
        if dtype == GAZE_TYPE:
            gaze = GazeData(d['x'], d['y'], d['tstamp'])
            last_gaze = gaze[:2]
            if plotter:
                plotter.add_sample(gaze)
            else:
                gaze_cache.append(gaze)
        if dtype == MOUSE_TYPE:
            mouse = d['x'], d['y']
    
    write_frame(frame)  # Write last frame
    label_end = Label(root, text='Its done!')
    label_end.grid(row=4, column=4)





# @click.command()
# @click.argument('recording')
def postprocess(recording):
    """Processa gravação na pasta RECORDING"""

    recording = Path(recording)
    gaze_filename = recording / GAZE_FILENAME
    mouse_filename = recording / MOUSE_FILENAME
    screen_tstamps_filename = recording / SCREEN_TSTAMPS_FILENAME
    screen_filename = recording / SCREEN_FILENAME
    overlayed_filename = recording / OVERLAYED_FILENAME

    print('Carregando dados da tela...')
    screen_data = load_data(screen_tstamps_filename, SCREEN_TYPE)
    if not screen_data:
        print('Não foi encontrado nenhum dado da tela. Encerrando.')
        return

    print('Carregando dados do olhar...')
    gaze_data = load_data(gaze_filename, GAZE_TYPE)
    print('Carregando dados do mouse...')
    mouse_data = load_data(mouse_filename, MOUSE_TYPE)
    data = (
        gaze_data +
        mouse_data +
        screen_data
    )
    print('Ordenando dados...')
    data.sort(key=lambda d: d['tstamp'])

    print('Gerando vídeo')
    # stepping post processing

    process(screen_filename, overlayed_filename, data)


if __name__ == '__main__':
    # postprocess()
    root.mainloop()
