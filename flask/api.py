import os
import pickle 
import numpy as np
import pandas as pd
import DBOperations.DBOperations as localdb
import DBOperations.Scrapping as localscp

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

@app.route('/scrapping', methods = ['POST'])
def scrapping():
    
    # Ejecucion de scrapping a pagina enviada
    listaAtributos, strError = localscp.Scrapping.obtenerAtributosPagina('https://www.olx.com.gt/item/alquilo-apartamento-zona-16-a-2-minutos-de-cayala-iid-1100443094')
    
    # Verificacion de errores
    if(strError is not None):
        localdb.DBOperations.registrarAccion(AccionSistema.ERROR.name, strError)
        return strError

    if(listaAtributos is None or len(listaAtributos)):
        strError = "No se obtuvo listado de atributos."
        localdb.DBOperations.registrarAccion(AccionSistema.WARNING.name, strError)
        return strError
    
    # Conversion a JSON de los atributos
    jsonAtributos = json.dumps(listaAtributos)

    localdb.DBOperations.registrarAccion(AccionSistema.SCRAPPING.name, jsonAtributos)
    return jsonAtributos



if __name__ == "__main__":
    app.run()