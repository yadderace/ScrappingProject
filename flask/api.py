import os
import pickle
import json
import numpy as np
import pandas as pd
import requests
import re
import datetime

from sqlalchemy import create_engine
from flask import Flask, request, jsonify, Response
from bs4 import BeautifulSoup
from json import JSONEncoder
from enum import Enum

app = Flask(__name__)

#########################################################################

class DBOperations():

    
    @staticmethod
    def obtenerCadenaConexion():
        '''
            Devuele la cadena de conexion haciendo uso de variables de entorno.

            Output: String con cadena de conexion
        '''
        strDataBase = os.environ.get('DATABASE_NAME')

        if(strDataBase is None):
            raise Exception("No se encontro variable de entorno DATABASE_NAME")

        strUserName = os.environ.get('USER_NAME')

        if(strUserName is None):
            raise Exception("No se encontro variable de entorno USER_NAME")

        strPortDB = os.environ.get('PORT_DB')

        if(strPortDB is None):
            raise Exception("No se encontro variable de entorno PORT_DB")

        strHostDB = os.environ.get('HOST_DB')

        if(strHostDB is None):
            raise Exception("No se encontro variable de entorno HOST_DB")

        strPassword = os.environ.get('PASSWORD_USR')

        if(strPassword is None):
            raise Exception("No se encontro variable de entorno PASSWORD_USR")

        strCadenaConexion = 'postgresql://'+ strUserName + ':' + strPassword + '@' + strHostDB + ':' + strPortDB + '/' + strDataBase

        return strCadenaConexion

    # Registra una accion en base de datos
    @staticmethod
    def registrarAccion(enumAccionSistema, strDescripcionAccion):
        
        con = None # Conexion
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strCadenaConexion = DBOperations.obtenerCadenaConexion()

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            con = engine.connect()
        
            strQuery = "INSERT INTO logaccionessistema(nombreaccion, descripcionaccion) VALUES (%(nombreaccion)s, %(descripcionaccion)s)"
            con.execute(strQuery, nombreaccion = enumAccionSistema, descripcionaccion = strDescripcionAccion)

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False

        finally:
            if(con is not None):
                con.close()

        return blnEjecucion, strError
    
    # Busca el modelo activo en base de datos y devuelve el nombre del archivo.
    @staticmethod
    def obtenerModeloRegresionActivo():
        
        con = None # Conexion
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strArchivoModelo = None # Nombre del archivo del modelo
        strCadenaConexion = DBOperations.obtenerCadenaConexion()

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            con = engine.connect()
        
            strQuery = "SELECT archivomodelo FROM modeloencabezado WHERE active = true AND tipomodelo in ('LR', 'RF')"
            strArchivoModelo = con.execute(strQuery).fetchone()[0]

            strQuery = "SELECT nombrecampo, tipodatacampo, ordencampo FROM modelocampo WHERE idmodelo = (SELECT idmodelo FROM modeloencabezado WHERE active = true AND tipomodelo in ('LR', 'RF')) ORDER BY ordencampo ASC"
            dfCamposModelo = pd.read_sql_query(strQuery, con = engine)
            
            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False

        finally:
            if(con is not None):
                con.close()

        return blnEjecucion, strArchivoModelo, dfCamposModelo, strError

    # Busca el modelo activo en base de datos y devuelve el nombre del archivo.
    @staticmethod
    def obtenerModeloKMeansActivo():
        
        con = None # Conexion
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strArchivoModelo = None # Nombre del archivo del modelo
        strCadenaConexion = DBOperations.obtenerCadenaConexion()

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            con = engine.connect()
        
            strQuery = "SELECT archivomodelo FROM modeloencabezado WHERE active = true AND tipomodelo in ('KM')"
            strArchivoModelo = con.execute(strQuery).fetchone()[0]

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False

        finally:
            if(con is not None):
                con.close()

        return blnEjecucion, strArchivoModelo, strError

    @staticmethod
    def obtenerDatosApartamentos(dateFechaInicial, dateFechaFinal):
        '''
            Se consulta los datos de la vista materializada con un rango de fechas establecida.
            Solo consulta datos de apartamentos

            Output: Dataframes de registros
        '''
        dfRegistros = None # Registros de encabezado
        strError = None # Mensaje de error
        strCadenaConexion = DBOperations.obtenerCadenaConexion() # Cadena de conexion

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)

            # Consulta a vista de datos limpios
            strQuery = '''
                SELECT DISTINCT idregistro, fechacreacion, fecharegistro, validohasta, 
	                latitud, longitud, espacio_m2, precio, amueblado, parqueo, 
	                estudio, banos, habitaciones, moneda, tipovendedor from mvwsetlimpio WHERE fecharegistro BETWEEN %(fechaInicial)s AND %(fechaFinal)s and tipoinmueble = 0'''
    
            # Leyendo de base de datos especificando el query y los parametros de fecha.
            dfRegistros = pd.read_sql_query(strQuery, 
                params = {
                    'fechaInicial': dateFechaInicial, 
                    'fechaFinal': dateFechaFinal}, coerce_float = False, con=engine)

        except Exception as e:
            strError = str(e)

        return dfRegistros, strError

#########################################################################

class AccionSistema(Enum):

    # Errores
    ERROR = 1
    WARNING = 2

    # Acciones para el sistema interno
    SCRAPPING = 3
    DATA_CLEANING = 4
    MODEL_CONSTRUCTION = 5
    MODEL_SELECTION = 6
    MV_REFRESH = 7


    # Acciones para aplicativo web
    PRICE_PREDICTION = 101
    FEATURE_COMPARATION = 102
    CONFIGURATION = 103

#########################################################################

# Clase para el detalle de apartamento
class DetalleApartamento(JSONEncoder):
    def __init__(self, campo, valor):
        self.campo = campo
        self.valor = valor


    def default(self, o):
            return o.__dict__  


# Clase para ejecutar el proceso de scrapping
class Scrapping():

    # Obtiene el html donde se encuentran los detalles de un apartamento y devuelve la
    # lista de detalles para ese apartamento.
    @staticmethod
    def obtenerDetalleRegistro(htmlRegistro):
        
        # Objeto soup para obtener cada uno de los atributos registrados en el detalle.
        soup = BeautifulSoup(htmlRegistro)

        registrosDetalles = soup.find_all('div', {'class': '_3_knn'})

        # Validamos que se pudo obtener informacion de detalle del registro.
        if(registrosDetalles is None):
            print("No se pudo obtener informacion de detalle para el registro")
            return None
        
        listaDetalle = []

        for idx in range(0, len(registrosDetalles)):
            
            # Se obtiene el registro de detalle
            registro = registrosDetalles[idx]
            #print(registro)

            # Obtenemos el nombre del detalle
            campo = registro.find('span', {'class': '_25oXN'}).string.strip()
            # Obtenemos el valor del detalle
            valor = registro.find('span', {'class': '_2vNpt'}).string.strip()
            
            # Creamos objeto de detalle y lo agregamos a la lista de detalle
            objDetalleApartamento = DetalleApartamento(campo, valor)
            listaDetalle.append(objDetalleApartamento)
        
        # Devolvemos la lista de todos los detalles
        return listaDetalle

    # Devuelve un listado de objetos de detalle (latitud y longitud)
    @staticmethod
    def obtenerUbicacion(registrosJS):

        for registro in  registrosJS:
            strContenido = str(registro.prettify())
            match = re.search("window.__APP", strContenido)

            if(match):
                
                # Limpiamos el contenido de la etiqueta script que posee un JSON con la informacion del apartamento
                strContenido = strContenido.replace('<script type="text/javascript">', '').replace('</script>', '').replace('window.__APP =','').replace('props:', '\"props\":').replace('};', '}')
                idxInicial = strContenido.index('"elements":')
                idxFinal = strContenido.index('"collections":')
                strContenido = "{" + strContenido[idxInicial:(idxFinal-1)] + "}"
                jsonContenido = json.loads(strContenido)
                jsonLocations = jsonContenido['elements'][list(jsonContenido['elements'].keys())[0]]['locations']

                listaDetalle = list()

                if(len(jsonLocations) > 0):
                    # Guardamos la latitud
                    objDetalleApartamento = DetalleApartamento('Latitude', jsonLocations[0]['lat'])
                    listaDetalle.append(objDetalleApartamento)

                    # Guardamos la longitud
                    objDetalleApartamento = DetalleApartamento('Longitude', jsonLocations[0]['lon'])
                    listaDetalle.append(objDetalleApartamento)

                # Guardamos el objeto JSON
                objDetalleApartamento = DetalleApartamento('JSON', json.dumps(jsonContenido))
                listaDetalle.append(objDetalleApartamento)

                return listaDetalle
        
        return None

    @staticmethod
    def obtenerAtributosPagina(strUrl):
            
        # Haciendo consulta GET para el link
        s = requests.Session()
        s.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    
        # Se intenta realizar peticion por Get
        r = None
        try:
            r = s.get(strUrl)
            
        except requests.exceptions.ConnectionError as e:
            #TODO Registrar error
            return None, str(e)
        

        if(r.status_code != 200):
            #TODO Registrar error de status
            return None, "Status Code != 200"

        
        htmlCode = r.text
        soup = BeautifulSoup(htmlCode)

        detalleRegistro = soup.find('div', {'class': '_3JPEe'})

        if(detalleRegistro is None):
            #TODO Registrar error
            return None, "div class != _3JPEe"

        # Se obtiene la lista de detalles.
        listaDetalle = Scrapping.obtenerDetalleRegistro(detalleRegistro.prettify())

        # Se obtiene el precio de la casa.
        precioRegistro = soup.find('span', {'class': '_2xKfz'}).string.strip()

        # Se agrega el precio como detalle a la lista.
        objDetalleApartamento = DetalleApartamento('Precio', precioRegistro)
        listaDetalle.append(objDetalleApartamento)

        # Se obtiene la ubicacion.
        registrosJS = soup.find_all('script', {'type': 'text/javascript'})
        
        if(registrosJS is None or len(registrosJS) == 0):
            #TODO Registrar error
            return None, "script type text/javascript"
        
        # Obtener informacion de la ubicacion
        listaUbicacion = Scrapping.obtenerUbicacion(registrosJS)

        if(listaUbicacion is not None):
            listaDetalle = listaDetalle + listaUbicacion

        strID = str(re.search("[0-9]+",re.search("iid-[0-9]+$", strUrl).group()).group())

        listaDetalle.append(DetalleApartamento('ID', strID))

        return listaDetalle, None

#########################################################################

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

@app.route('/')
def hello_world():
    return 'Hello world!\n'

@app.route('/predict', methods = ['POST'])
def predict():
    
    # Obtiene directorio de las variables del sistema
    directorioModelo = os.environ.get('MODEL_DIRECTORY')
    
    # Obtiene el nombre del archivo para modelo de regresion y lo carga
    blnEjecucion, strArchivoModelo, dfCamposModelo, strError = DBOperations.obtenerModeloRegresionActivo()
    if(not blnEjecucion):
        print(strError)
    
    modeloRegresion = pickle.load(open(directorioModelo + strArchivoModelo, 'rb'))

    # Obtiene el nombre del archivo para el modelo kmeans y lo carga
    blnEjecucion, strArchivoModelo, strError = DBOperations.obtenerModeloKMeansActivo()
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
    DBOperations.registrarAccion(AccionSistema.PRICE_PREDICTION.name, "Prediccion con los valores("+ str(dfParams.loc[0]) +")")

    return str(output)

@app.route('/scrapping', methods = ['POST'])
def scrapping():
    
    # Lectura de variables del request
    dfParams = pd.DataFrame(request.get_json())
    strUrl = dfParams.iloc[0]['url']

    # Ejecucion de scrapping a pagina enviada
    listaAtributos, strError = Scrapping.obtenerAtributosPagina(strUrl)
    
    
    # Verificacion de errores
    if(strError is not None):
        DBOperations.registrarAccion(AccionSistema.ERROR.name, strError)
        return strError

    if(listaAtributos is None or len(listaAtributos) == 0):
        strError = "No se obtuvo listado de atributos."
        DBOperations.registrarAccion(AccionSistema.WARNING.name, strError)
        return strError
    
    # Conversion a JSON de los atributos
    jsonAtributos = json.dumps(listaAtributos, default = lambda x: x.__dict__)
    

    DBOperations.registrarAccion(AccionSistema.SCRAPPING.name, jsonAtributos)
    return app.response_class(
        response = jsonAtributos,
        status=200,
        mimetype='application/json'
    )

@app.route('/data', methods = ['POST'])
def data():
    
    # Lectura de variables del request
    dfParams = pd.DataFrame(request.get_json())
    dateFechaInicial = dfParams.iloc[0]['fechaInicial']
    dateFechaFinal = dfParams.iloc[0]['fechaFinal']

    # Conversion a tipo fecha
    dateFechaInicial = datetime.datetime.strptime(dateFechaInicial, '%Y-%m-%d')
    dateFechaFinal = datetime.datetime.strptime(dateFechaFinal, '%Y-%m-%d')

    # Consulta de datos
    dfRegistros, strError = DBOperations.obtenerDatosApartamentos(dateFechaInicial, dateFechaFinal)

    if(dfRegistros is None):
        DBOperations.registrarAccion(AccionSistema.WARNING.name, "No se pudieron obtener registros de vista materializada. [api.py ! data()] " + str(strErr))
        return "No se pudieron obtener registros", 500

        
    return Response(dfRegistros.to_json(orient="records"), mimetype='application/json')

if __name__ == "__main__":
    app.run()

