import tkinter as tk
from tkinter import filedialog
import sounddevice as sd
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import matplotlib

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
# source code from https://matplotlib.org/examples/user_interfaces/embedding_in_tk.html
def updateGraph():     #for refresh graph
    """Example function triggered by Tkinter GUI to change matplotlib graphs."""
    plt.clf()
    plt.plot(x,y)
    fig.canvas.draw()
def quit(): #well.... for quiting :)
    root.destroy()
    root.quit()

def recording(): #recording
    global data,samplerate
    samplerate = 44100
    duration = 5  # seconds
    data = sd.rec(duration * samplerate, samplerate=samplerate, channels=2, dtype='float64')
    print("record")
    sd.wait()
    print("finished record")
    data=one_channel(data)
    fftdata = ffttran(data, samplerate)
def LoadWAV():
    global data,samplerate
    try:
        wav=filedialog.askopenfilename(filetypes=(("WAV file", "*.wav*")
                                                  , ("All files", "*.*")))
        data,samplerate=sf.read(wav)
        data, samplerate = sf.read(wav)
        data = one_channel(data)
        fftdata=ffttran(data,samplerate)
    except:pass
def one_channel(data):
    try:
        data = data[:, 0]
    except:
        pass
    return data
def noisecanceiling(data,samplerate):
    fs = samplerate
    duration = int((data.size)/samplerate)
    myrecording = sd.rec(duration * fs, samplerate=fs, channels=2, dtype='float64')
    myrecording=one_channel(myrecording)
    print("getting enviroment sound")
    sd.wait()
    data=data-myrecording
    return data
def timedomaingraph(data,samplerate):
    global x,y
    start_time = 0
    end_time = data.size / samplerate # seconds
    sampling_rate = samplerate
    N = (end_time - start_time) * sampling_rate  # array size
    # Data plotting
    currentGraph="time"
    x = np.linspace(0, end_time, N)
    y = data
    updateGraph()
def ffttran(data,samplerate):
    global fftdata
    fftdata = np.fft.fft(data,data.size)  # "raw" FFT with both + and - frequencies
def freqdomaingrapg(fftdata,samplerate):
    global x,y
    start_time = 0
    end_time = data.size / samplerate  # seconds
    N = (end_time - start_time) * samplerate  # array size
    T=1/samplerate
    x = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))
    y = 2 / N * np.abs(fftdata[0:np.int(N / 2)])
    updateGraph()
def playback(data,samplerate):
    sd.play(data, samplerate)
def stop():
    sd.stop()

def freqchoose(loudfactor, startdata, enddata, datainput, samplerate):
    global data,fftdata
    if startdata==enddata:
        pass
    else:
        if startdata > enddata:
            temp = enddata
            enddata = startdata
            startdata = temp
        if loudfactor<0:
            loudfactor = 1/(loudfactor*-1)
        start_time = 0
        end_time = datainput.size / samplerate  # seconds
        N = (end_time - start_time) * samplerate  # array size
        T = 1 / samplerate
        x = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))
        bitperhert= datainput.size / (samplerate / 2)
        startsize=int(startdata * bitperhert / 2)
        endsize=int(enddata * bitperhert / 2)
        print(loudfactor)
        data1= datainput[0:startsize]
        data2= datainput[startsize:endsize] * loudfactor
        data3= datainput[endsize:int(N)]
        datafinish=np.append(data1,data2)
        datafinish=np.append(datafinish,data3)
        # print(datafinish.size,data3.size,data2.size,data1.size,N)
        fftdata=datafinish
        data=np.fft.ifft(datafinish)
        data=np.real(data)
        print("reach here")
def slider1value(val):
    global startdata
    startdata=int(val)
def slider2value(val):
    global enddata
    enddata = int(val)
def mulvalue(val):
    global loudfactor
    loudfactor = int(val)
if __name__ == "__main__":
    matplotlib.use('TkAgg')
    root = tk.Tk()
    root.title("Frequency Range Booster")
    fig = plt.figure(1)
    canvas = FigureCanvasTkAgg(fig, master=root)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=1, column=3,columnspan=8)
    scale = tk.Scale(orient='vertical',length=400, from_=22050, to=0, command=slider1value)
    scale.grid(row=1,column=1,rowspan=8)
    scale2 = tk.Scale(orient='vertical', length=400, from_=22050, to=0, command=slider2value)
    scale2.grid(row=1, column=2, rowspan=8)
    scale3 = tk.Scale(orient='horizontal', from_=50, to=-50, command=mulvalue)
    scale3.grid(row=0, column=2,sticky="E")
    tk.Label(root, text="Multiplier").grid(row=0,column=1,sticky="W")
    tk.Label(root, text="Select frequency range to multiply").grid(row=1, column=0,columnspan=3,sticky="NE")
    record=tk.Button(root, text="Record")
    record['command']= recording
    record.grid(row=0, column=3,sticky="NESW")
    loadwav=tk.Button(root, text="LoadWAV")
    loadwav['command'] = LoadWAV
    loadwav.grid(row=0, column=4,sticky="NESW")
    tk.Button(root, text="PLAY", command=lambda: playback(data, samplerate)).grid(row=0, column=5, sticky="NESW")
    tk.Button(root, text="STOP", command=stop).grid(row=0, column=6, sticky="NESW")
    tk.Button(root, text="MIX", command=lambda :freqchoose(loudfactor,startdata,enddata,fftdata,samplerate)).grid(row=0, column=7,sticky="NESW")
    tk.Button(root, text="TimeGraph", command=lambda :timedomaingraph(data,samplerate)).grid(row=0, column=8,sticky="NESW")
    tk.Button(root, text="FreqGraph", command=lambda :freqdomaingrapg(fftdata,samplerate)).grid(row=0, column=9,sticky="NESW")
    tk.Button(root, text="Quit", command=quit).grid(row=0, column=10,sticky="NESW")

    root.mainloop()