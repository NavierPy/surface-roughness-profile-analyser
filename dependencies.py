import scipy.io
import pandas as pd
import numpy as np
from functools import reduce
import PySimpleGUI as sg
from scipy import interpolate as interpolator


def cargar_ejemplo(nombre):
    """
    Carga una de las 8 columnas del archivo de ejemplo.
    
    Keyword arguments:
    nombre -- Nombre de la columna a extraer del archivo
    
    Returns:
    X -- Lista de las coordenadas x de los sucesivos puntos del perfil 
    y -- Lista de las coordenadas y de los sucesivos puntos del perfil
    """
    
    mat = scipy.io.loadmat('Ejemplos/vector.mat')
    mat = {k:v for k, v in mat.items() if k[0] != '_'}
    data = pd.DataFrame({k: pd.Series(v[0]) for k, v in mat.items()})
    data.to_csv("Ejemplos/temporal/vector_aux.csv")
    data = pd.read_csv('Ejemplos/temporal/vector_aux.csv')
    data = data.drop('Unnamed: 0', axis=1)
    
    y = list(data[nombre])
    y = [x for x in y if x==x]
    X = list(range(len(y)))
    
    return(X, y)  


def cargar_datos(path):
    """
    Carga un archivo que contenga el perfil de alturas.
    Admite dos formatos:
        Extensión .xml con el formato de https://physics.nist.gov/VSC/jsp/Database.jsp
        Extensión .mat con el formato del archivo proporcionado como ejemplo: vector.mat
    
    Keyword arguments:
    path -- Ruta del archivo
    
    Returns:
    X -- Lista de las coordenadas x de los sucesivos puntos del perfil 
    y -- Lista de las coordenadas y de los sucesivos puntos del perfil
    """
    
    if path.split(".")[-1] == "mat":
        mat = scipy.io.loadmat(path)
        mat = {k:v for k, v in mat.items() if k[0] != '_'}
        data = pd.DataFrame({k: pd.Series(v[0]) for k, v in mat.items()})        
        data.to_csv("Ejemplos/temporal/example_aux.csv")
        data = pd.read_csv('Ejemplos/temporal/example_aux.csv')
        data = data.drop('Unnamed: 0', axis=1)
        
        if data.shape[1] !=1:
            r = sg.popup_get_text('Tu archivo contiene '+ str(data.shape[1]) + " columnas, ¿cuál quieres cargar?", title="Textbox")       

        y = list(data.iloc[:,int(r)-1])
        y = [x for x in y if x==x]
        X = list(range(len(y)))
    
    elif path.split(".")[-1] == "xml":
        from bs4 import BeautifulSoup
        with open(path, 'r') as f:
            data = f.read()
        
        file = BeautifulSoup(data, "xml")
        y = str(file.DATA_POINT_VALUES).split("\n")
        y[0]=y[0].split(">")[-1]
        y = y[0:-1]
        y = [float(x) for x in y]
        X = list(range(len(y)))
        
    else:
        print("Formato inválido")
    
    return(X, y)    


def contar(vector, valor, equal=True):
    """ Devuelve el número de puntos de un vector que son menores o iguales a un valor dado"""
    
    contador = 0
    
    if equal:
        for i in vector:
            if i<=valor:
                contador+=1
                
    else:
        for i in vector:
            if i<valor:
                contador+=1
                
    return(contador)


def CDF(vector):
    """
    Recorre un vector dado y devuelve su función de distribución.
    
    Keyword arguments:
    vector -- Perfil de alturas
    
    Returns:
    X -- Lista de las coordenadas x de la función de distribución 
    y -- Lista de las coordenadas y de la función de distribución 
    """
    
    X = list(np.linspace(min(vector),max(vector),100))
    acumulador = []

    for i in X:
        acumulador.append(contar(vector, i))

    return(X, [x/len(vector) for x in acumulador])


def PDF(X,y):
    """
    Recorre un vector dado y devuelve su función de densidad.
    
    Keyword arguments:
    vector -- Perfil de alturas
    
    Returns:
    X -- Lista de las coordenadas x de la función de densidad 
    y -- Lista de las coordenadas y de la función de densidad 
    """

    param = list(np.linspace(min(y),max(y),100))
    y_CDF = CDF(y)
    Nueva_y = []
    Nueva_y.append(y_CDF[1][0])

    for i in range(len(y_CDF[1])-1):
        Nueva_y.append(y_CDF[1][i+1]-y_CDF[1][i])
    return(param, Nueva_y)
        

def LC(vector):
    """Devuelve la ordenada en el origen de la Línea Central"""

    return((1/len(vector))*reduce(lambda x,y: x+y, vector))

   
def LM(vector):
    """Devuelve la pendiente y la ordenada en el origen de la Línea Media"""
    
    n = len(vector)
    sumx = reduce(lambda x,y: x+y, list(range(len(vector))))
    sumy = reduce(lambda x,y: x+y, vector)
    sumx2 = reduce(lambda x,y: x+y, [x**2 for x in range(len(vector))])
    sumxy = reduce(lambda x,y: x+y, [x[0]*x[1] for x in list(zip(vector, range(len(vector))))])  
    xmedia = sumx/n
    ymedia = sumy/n
    
    a = (sumxy - (sumx*sumy)/n) / (sumx2 - ((sumx**2)/n))
    b = ymedia - a*xmedia
    
    return(a,b)


def Ra(vector):
    """ Devuelve el parámetro Ra de un perfil de alturas dado como un vector"""

    z_ref = LC(vector)
    suma = reduce(lambda x,y: x+y, [abs(z-z_ref) for z in vector])
    Ra = (suma/len(vector))
    
    return(round(Ra,2))


def Rq(vector):
    """ Devuelve el parámetro Rq de un perfil de alturas dado como un vector"""

    z_ref = LC(vector)
    suma = reduce(lambda x,y: x+y, [(z-z_ref)**2 for z in vector])
    Ra = (suma/len(vector))**(1/2)
    return(round(Ra,2))


def aproximar_cdf(valor, array):
    """Devuelve el valor de un vector inmediatamente inferior a uno dado."""
    
    vector = np.sort(array)
    anterior = vector[0]
    
    if valor>vector[-1]:
        return(float(vector[-1]))
    
    elif valor<vector[0]:
        return("Error")
   
    else:
        for i in vector:
            if anterior<=valor and i>valor:
                return(float(anterior))
            anterior = i


def interpolate(h, bins):
    """
    Interpola una curva a partir de un histograma.
    
    Keyword arguments:
    h -- Primer output de la función matplotlib.pyplot.hist()
    bins -- Segundo output de la función matplotlib.pyplot.hist()
    
    
    Returns:
    xnew -- Lista de las coordenadas x de la función interpolada
    ynew -- Lista de las coordenadas y de la función interpolada 
    """
    
    x = []
    y = h
    bl = bins[1]-bins[0]
    
    for i in range(len(bins)-1):
        x.append(bins[i]+bl/2)
    
    f = interpolator.interp1d(x, y, kind="cubic")
    xnew = np.arange(x[0], x[-1], 0.01)
    ynew = f(xnew)
    
    return(xnew,ynew)


def calculatebins(y):
    """ Devuelve el número de bins a usar en un histograma para un vector dado"""
    
    l = len(y)

    return(int(15 + 1.5*round(l/2240, -1)))
    

# License: (CC BY-SA 4.0)
# Author: https://github.com/NavierPy