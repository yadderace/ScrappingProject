import os
import pickle 
import numpy as np
import pandas as pd
import DBOperations.DBOperations as localdb

from DBOperations.AccionSistema import AccionSistema
from sqlalchemy import create_engine
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods = ['POST'])
def predict():
    
    # Obtiene directorio de las variables del sistema
    directorioModelo = os.environ.get('MODEL_DIRECTORY')
    
    # Obtiene el nombre del archivo para modelo de regresion y lo carga
    blnEjecucion, strArchivoModelo, strError = localdb.DBOperations.obtenerModeloRegresionActivo()
    if(not blnEjecucion):
        print(strError)
    
    modeloRegresion = pickle.load(open(directorioModelo + strArchivoModelo, 'rb'))

    # Obtiene el nombre del archivo para el modelo kmeans y lo carga
    blnEjecucion, strArchivoModelo, strError = localdb.DBOperations.obtenerModeloKMeansActivo()
    if(not blnEjecucion):
        print(strError)
    
    modeloKMeans = pickle.load(open(directorioModelo + strArchivoModelo, 'rb'))

    # Lectura de variables del request
    dfParams = pd.DataFrame(request.get_json())
    
    # Utiizamos el modelo kmeans para obtener la categoria
    categoria = modeloKMeans.predict(dfParams[['longitud', 'latitud']])
    
    # Creamos dataframe de ubicaciones
    dfUbicaciones = pd.DataFrame(np.zeros((len(np.unique(modeloKMeans.labels_)),), dtype=int).reshape(1,-1), 
                columns = ["U" + str(cat) for cat in np.unique(modeloKMeans.labels_)])
    dfUbicaciones["U" + str(categoria[0])] = 1
    dfUbicaciones = dfUbicaciones.astype(np.uint8)

    # Unimos los demas parametros
    dfParams = pd.concat([dfParams, dfUbicaciones], axis = 1)

    # Eliminamos latitud y longitud
    dfParams = dfParams.drop(['longitud','latitud'], axis=1, errors='ignore')
    
    dfParams.astype({'parqueo': 'int'})

    dfParams['espacio_m2'] = dfParams['espacio_m2'].astype(float)
    dfParams['banos'] = dfParams['banos'].astype(float)
    dfParams['habitaciones'] = dfParams['habitaciones'].astype(float)
    dfParams[['monedaq', 'monedad', 'tipodueno', 'tipoinmobiliaria']] = dfParams[['monedaq', 'monedad', 'tipodueno', 'tipoinmobiliaria']].astype(np.uint8)
    
    listaEncabezados = ['banos',	
                        'espacio_m2',	
                        'habitaciones',	
                        'parqueo',	
                        'monedaq',
                        'monedad',	
                        'tipodueno',	
                        'tipoinmobiliaria',	
                        'U0',
                        'U1',	
                        'U2',	
                        'U3',	
                        'U4',	
                        'U5',	
                        'U6',	
                        'U7',	
                        'U8',	
                        'U9']
    dfParams = dfParams[listaEncabezados]
    
    prediction = modeloRegresion.predict(dfParams)
    
    output = prediction[0]
    
    localdb.DBOperations.registrarAccion(AccionSistema.PRICE_PREDICTION.name, "Prediccion con los valores("+ str(dfParams.loc[0]) +")")

    return str(output)
    

if __name__ == "__main__":
    app.run()