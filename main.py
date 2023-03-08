import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dependencies import *


menu = ["iso1661029_a",
        "iso1661029_b", 
        "iso1661029_a4096", 
        "iso1661029_a4096sc", 
        "iso1661029_asc", 
        "iso1661029_b4096", 
        "iso1661029_b4096sc", 
        "iso1661029_bsc"]

_VARS = {'window': False}


def draw_figure(canvas, figure):
    """ Función para dibujar gráficos dentro de la interfaz de usuario """
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg



# \\  -------- PYSIMPLEGUI -------- //

AppFont = 'Any 16'
sg.theme('LightGrey')

# Estructura de la interfaz de usuario:
    
first_column = [  [sg.Text("Cargar vector de ejemplo")],
            [sg.Combo(menu, key='example'), sg.Button('Cargar', key='loadfromexample')],
            [sg.Text("Cargar vector desde archivo")],
            [sg.FileBrowse(key="-IN-"), sg.Button('Cargar', key='loadfromfile')],
            [sg.Text("______________")],
            [sg.Text("¿Qué quieres calcular?")],
            [sg.Button('Mostrar perfil')],
            [sg.Button('Mostrar LM'), sg.Button('Mostrar LC')],
            [sg.Button('Calcular PDF'), sg.Button('Calcular CDF')],
            [sg.Button('Calcular Ra'),sg.Text("Ra= "+str("..."), key='ra')],
            [sg.Button('Calcular Rq'),sg.Text("Rq= "+str("..."), key='rq')] ]

second_column = [[sg.Canvas(key='figCanvas')],
          [sg.Text("Calcular valores:     P ("),
           sg.InputText(size=(5, 2), key='x1'), sg.Text("<z<="), 
           sg.InputText(size=(5, 2), key='x2'),sg.Text(") ="),sg.Text("", key='resultado'),
           sg.Text("    "), sg.Button('Calcular', key="imagen")]]

layout = [
    [sg.Column(first_column),
     sg.VSeperator(),
     sg.Column(second_column),]
]


_VARS['window'] = sg.Window('Profile Roughness Analyzer',
                            layout,
                            finalize=True,
                            resizable=True,
                            element_justification="right")

# //  -------- PYSIMPLEGUI -------- \\

    

# \\  -------- EMPTY PLOT FOR DISPLAY -------- //

fig = plt.figure()
lienzo = draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)

# //  -------- EMPTY PLOT FOR DISPLAY -------- \\

    

# \\  -------- MAIN LOOP -------- //

while True:
    
    event, values = _VARS['window'].read(timeout=200)
    
    if event == sg.WIN_CLOSED or event == 'Salir':
        break
    
    elif event == 'loadfromfile':
        X, y = cargar_datos(values["-IN-"])
        
    elif event == 'loadfromexample':
        X, y = cargar_ejemplo(values['example'])
        
    elif event == 'Mostrar perfil':
        y_plot = y
        x_plot = list(range(len(y_plot)))
        fig = plt.figure()
        plt.plot(x_plot, y_plot, '-k')
        
        lienzo.get_tk_widget().forget()
        lienzo = draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)
        plt.close('all')
        
    elif event == 'Mostrar LC':
        y_plot = y
        x_plot = list(range(len(y_plot)))
        fig = plt.figure()
        plt.plot(x_plot, y_plot, '-k')
        b = LC(y)
        plt.plot(x_plot, [b for x in x_plot], '-b')
        
        lienzo.get_tk_widget().forget()
        lienzo = draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)
        plt.close('all')
        
    elif event == 'Mostrar LM':
        y_plot = y
        x_plot = list(range(len(y_plot)))
        fig = plt.figure()
        plt.plot(x_plot, y_plot, '-k')
        a, b = LM(y)
        plt.plot(x_plot, [a*x+b for x in x_plot], '-b')
        
        lienzo.get_tk_widget().forget()
        lienzo = draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)
        plt.close('all')
        
    elif event == 'Calcular PDF':
        
        #Deprecated:
        # x_pdf, y_pdf = PDF(X,y)
        # plt.plot(x_pdf, y_pdf, '-k')
        
        #Histograma:
        fig = plt.figure()
        h, bins, patches = plt.hist(y, bins=calculatebins(y), density=True)
        
        #Línea media interpolada:
        xpol, ypol = interpolate(h, bins)
        plt.plot(xpol, ypol, '-k')
        
        #Común
        lienzo.get_tk_widget().forget()
        lienzo = draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)
        plt.close('all')


    elif event == 'Calcular CDF':
        
        #Deprecated:
        # x_cdf, y_cdf = CDF(y)
        # fig = plt.figure()
        # plt.plot(x_cdf, y_cdf, '-k')
        
        #Histograma:
        fig = plt.figure()
        h, bins, patches = plt.hist(y, calculatebins(y), density=True, cumulative=True)
        
        #Línea media interpolada:
        xpol, ypol = interpolate(h, bins)
        plt.plot(xpol, ypol, '-k')
        
        #Común        
        lienzo.get_tk_widget().forget()
        lienzo = draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)
        plt.close('all')
        
    elif event == 'Calcular Ra':
        value = "Ra= "+str(Ra(y))
        _VARS['window']['ra'].update(value)
        
    elif event == 'Calcular Rq':
        value = "Rq= "+str(Rq(y))
        _VARS['window']['rq'].update(value)
    
    elif event == "imagen":
        x_cdf, y_cdf = CDF(y)
        
        aprox1 = aproximar_cdf(float(values["x1"]), x_cdf)
        aprox2 = aproximar_cdf(float(values["x2"]), x_cdf)
        
        if type(aprox1)!=float:
            aprox1 = min(x_cdf)
            
        if type(aprox2)!=float:
            aprox2 = max(x_cdf)
            
        bajox1= contar(y, aprox1, equal=False)/len(y)
        bajox2= contar(y, aprox2)/len(y)
        diferencia=round(bajox2-bajox1,3)
        
        _VARS['window']["resultado"].update(diferencia)

# //  -------- MAIN LOOP -------- \\


    
_VARS['window'].close()


# License: (CC BY-SA 4.0)
# Author: https://github.com/NavierPy