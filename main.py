import sys
import os
from pathlib import Path
import cv2
import tkinter as tk
from recorder.experiment_recorder import DummyRecorder, ExperimentRecorder
from viewer.draw import PreviewRenderer
from viewer.gaze import EyeTracker, MouseTrackerDriver, TobiiTrackerDriver
from viewer.screen import ScreenCapturer, StaticImageCapturer

# Define o caminho do diretório de experimentos (Videos)
if getattr(sys, 'frozen', False):  # Verifica se estamos executando a partir de um arquivo compilado
    app_path = Path(sys._MEIPASS)  # Diretório temporário onde os arquivos estão extraídos
else:
    app_path = Path(__file__).parent  # Diretório de execução normal no código-fonte

# path for saving the videos
DEFAULT_EXP_DIR = Path(os.path.expanduser('~/Movies/gaze_viewer'))

# Garantir que o diretório de experimentos existe
if not DEFAULT_EXP_DIR.exists():
    DEFAULT_EXP_DIR.mkdir(parents=True)

# Inicializa os valores de id e projeto
id = 'default'
projeto = 'default'

def salvar(entry1, entry2, root):
    """Função chamada para salvar os dados do projeto e id"""
    global projeto
    global id
    projeto = str(entry1.get())  
    id = str(entry2.get())       
    
    print(f"Valor 1: {projeto}, Valor 2: {id}")
    
    root.destroy()  # Fecha a GUI após salvar
    run_viewer(id, projeto, mouse=False)  # Chama a função para iniciar o experimento

def on_focus_in(entry, placeholder):
    """Remove o texto de placeholder quando o campo recebe o foco"""
    if entry.get() == placeholder:
        entry.delete(0, tk.END)

def on_focus_out(entry, placeholder):
    """Adiciona o texto de placeholder se o campo estiver vazio"""
    if entry.get() == "":
        entry.insert(0, placeholder)

def gui():
    """Função para a interface gráfica"""
    root = tk.Tk()
    root.title("Gaze")

    # Criando os campos de entrada
    entry1 = tk.Entry(root)
    placeholder1 = "Nome do Projeto"
    entry1.insert(0, placeholder1)  # Texto de placeholder
    entry1.bind("<FocusIn>", lambda event: on_focus_in(entry1, placeholder1))
    entry1.bind("<FocusOut>", lambda event: on_focus_out(entry1, placeholder1))
    entry1.pack(padx=20, pady=5)

    entry2 = tk.Entry(root)
    placeholder2 = "Nome do Participante"
    entry2.insert(0, placeholder2)  # Texto de placeholder
    entry2.bind("<FocusIn>", lambda event: on_focus_in(entry2, placeholder2))
    entry2.bind("<FocusOut>", lambda event: on_focus_out(entry2, placeholder2))
    entry2.pack(padx=20, pady=5)

    # Botão Salvar que chama a função salvar
    button_salvar = tk.Button(root, text="Salvar", command=lambda: salvar(entry1, entry2, root))
    button_salvar.pack(pady=10)

    root.mainloop()  # Inicia a interface gráfica

def run_viewer(id, projeto, experiment_dir=DEFAULT_EXP_DIR, mouse=True, record=True, preview_width=1024, gaze_radius=30, window_name='Clique em Q para finalizar', target=None):
    """Função principal do experimento"""
    print(f"Executando experimentos com ID: {id} e Projeto: {projeto}")

    # Se tiver um target, usa a imagem estática, senão captura a tela
    if target:
        capturer = StaticImageCapturer(target)
    else:
        capturer = ScreenCapturer()

    # Usar mouse ou rastreador de olhos
    if mouse:
        driver = MouseTrackerDriver()
    else:
        driver = TobiiTrackerDriver()  # Usando o rastreador de olhos

    # Inicializa o rastreador de olhos
    eye_tracker = EyeTracker(driver)

    # Inicializa o gravador
    if record:
        recorder = ExperimentRecorder(id, projeto, experiment_dir, capturer, eye_tracker)
    else:
        recorder = DummyRecorder()

    with capturer, eye_tracker, recorder:
        renderer = PreviewRenderer(capturer, eye_tracker, preview_width, gaze_radius)
        print('Para sair, mude o foco para a janela de visualização e pressione "q"')
        while cv2.waitKey(1) != ord('q'):
            if capturer.screen is None:
                continue

            preview = renderer.draw_preview()  # Desenha a pré-visualização
            recorder.on_mouse(capturer.mouse_position())  # Captura a posição do mouse

            cv2.imshow(window_name, preview)  # Exibe a imagem com o preview

if __name__ == '__main__':
    gui()  # Inicia a GUI
