import os
import pickle 
import numpy as np
import pandas as pd
import DBOperations.DBOperations as localdb

from DBOperations.AccionSistema import AccionSistema
from sqlalchemy import create_engine
from flask import Flask, request, jsonify

app = Flask(__name__)

# Obtiene los datos acorde al dataframe de campos
def ordenarDatos(dfCampos, dfData):
    
    # Obteniendo los nombres de campo como lista
    listaCampos = dfCampos.nombrecampo.to_list()

    # Diccionario de campos
    dictCast = pd.Series(dfCampos.tipodatacampo.values, index = dfCampos.nombrecampo).to_dict()
    
    
    # Eliminar elementos en caso de que existan
    if 'precioreal' in listaCampos:
        listaCampos.remove('precioreal')
        dictCast.pop('precioreal')
    
    if 'idregistro' in listaCampos:
        listaCampos.remove('idregistro')
        dictCast.pop('idregistro')
    
    # Seleccion y conversion de campos
    dfData = dfData[listaCampos]
    dfData = dfData.astype(dictCast)

    
    return dfData


@app.route('/predict', methods = ['POST'])
def predict():
    
    # Obtiene directorio de las variables del sistema
    directorioModelo = os.environ.get('MODEL_DIRECTORY')
    
    # Obtiene el nombre del archivo para modelo de regresion y lo carga
    blnEjecucion, strArchivoModelo, dfCamposModelo, strError = localdb.DBOperations.obtenerModeloRegresionActivo()
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
    
    # Unimos los demas parametros
    dfParams = pd.concat([dfParams, dfUbicaciones], axis = 1)

    # Eliminamos latitud y longitud
    dfParams = dfParams.drop(['longitud','latitud'], axis=1, errors='ignore')
    
    # Seleccion y casteo de datos
    dfParams = ordenarDatos(dfCamposModelo, dfParams)

    # Calculo de prediccion
    prediction = modeloRegresion.predict(dfParams)
    output = prediction[0]
    
    # Registro de accion
    localdb.DBOperations.registrarAccion(AccionSistema.PRICE_PREDICTION.name, "Prediccion con los valores("+ str(dfParams.loc[0]) +")")

    return str(output)
    

if __name__ == "__main__":
    app.run()