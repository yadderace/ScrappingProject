import os
import pickle 
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, request, jsonify

app = Flask(__name__)

# Busca el modelo activo en base de datos y devuelve el nombre del archivo.
def obtenerModeloActivo():
    
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
    
    strQuery = "SELECT archivomodelo FROM modeloencabezado WHERE active = true AND tipomodelo in ('LR', 'RF')" 
    archivoModelo = engine.execute(strQuery).fetchone()[0]

    return archivoModelo

# Busca el modelo kmeans activo en base de datos y devuelve el nombre del archivo.
def obtenerModeloKMeansActivo():
    
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
    
    strQuery = "SELECT archivomodelo FROM modeloencabezado WHERE active = true AND tipomodelo in ('KM')"
    archivoModelo = engine.execute(strQuery).fetchone()[0]

    return archivoModelo


@app.route('/predict', methods = ['POST'])
def predict():
    
    # Obtiene directorio de las variables del sistema
    directorioModelo = os.environ.get('MODEL_DIRECTORY')
    
    # Obtiene el nombre del archivo para modelo de regresion y lo carga
    strArchivoModelo = obtenerModeloActivo()
    modeloRegresion = pickle.load(open(directorioModelo + strArchivoModelo, 'rb'))

    # Obtiene el nombre del archivo para el modelo kmeans y lo carga
    strArchivoModelo = obtenerModeloKMeansActivo()
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

    print(dfParams)

    # Unimos los demas parametros
    dfParams = pd.concat([dfParams, dfUbicaciones], axis = 1)

    # Eliminamos latitud y longitud
    dfParams = dfParams.drop(['longitud','latitud'], axis=1, errors='ignore')
    
    dfParams.astype({'parqueo': 'int'})

    dfParams['espacio_m2'] = dfParams['espacio_m2'].astype(float)
    dfParams['banos'] = dfParams['banos'].astype(float)
    dfParams['habitaciones'] = dfParams['habitaciones'].astype(float)
    dfParams[['monedaq', 'monedad', 'tipodueno', 'tipoinmobiliaria']] = dfParams[['monedaq', 'monedad', 'tipodueno', 'tipoinmobiliaria']].astype(np.uint8)
    
    dfParams = dfParams[['banos',	
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
                        'U9']]

    print(dfParams)

    print(dfParams.dtypes)

    prediction = modeloRegresion.predict(dfParams)
    print(prediction)

    output = prediction[0]
    print(output)

    return str(output)
    

if __name__ == "__main__":
    app.run()