import os
import re
import pickle
import datetime
import pandas as pd
import numpy as np
from datetime import date, timedelta
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score


# Lectura de los datos limpios en BD
def lecturaDataLimpia(dateFechaInicial, dateFechaFinal):
    
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')

    strQuery = 'select * from mvwSetLimpio where  fecharegistro between %(fechaInicial)s and %(fechaFinal)s'
    
    # Leyendo de base de datos especificando el query y los parametros de fecha.
    dfRegistros = pd.read_sql_query(strQuery, 
        params = {
            'fechaInicial': dateFechaInicial, 
            'fechaFinal': dateFechaFinal}, coerce_float = False, con=engine)

    return dfRegistros

# Funcion encargada de obtener solo los ultimos registros para cada idregistro
def obtenerRegistrosUnicos(dfSetDatos):
    # Conversion a string del campo idregistro
    dfAnalisisSet = dfSetDatos.astype({'idregistro': 'str'})

    # Conversion a fecha del campo fecharegsitro
    dfAnalisisSet['fecharegistro'] = pd.to_datetime(dfAnalisisSet['fecharegistro'], format = "%Y-%m-%d")

    # Obtencion de fecha maxima por cada idregistro y filtro de esos registros.
    dfAnalisisSet = dfAnalisisSet.loc[dfAnalisisSet.reset_index().groupby(['idregistro'])['fecharegistro'].idxmax()]

    return(dfAnalisisSet)

# Calcula el precio real en quetzales para cada registro del set de datos
def obtenerPrecioReal(dfSetDatos):
    # Factor de conversion
    cambio_moneda = 7.69

    # Creacion de nueva columna
    dfSetDatos['precioreal'] = np.where(dfSetDatos['moneda'] == 'US$', dfSetDatos['precio'] * cambio_moneda, 
                                            dfSetDatos['precio'])
    return (dfSetDatos)

# Calcula la columna oferta para determinar si es un alquiler o una venta
def obtenerOferta(dfSetDatos):
    # Asignacion de valor pivote
    intValorPivote = 50000

    # Creacion de nueva columna oferta.
    dfSetDatos['oferta'] = ['Venta' if precio > intValorPivote else 'Alquiler' for precio in dfSetDatos['precioreal']]

    return(dfSetDatos)

# Filtra los registros que so los de interes para construir el modelo
def filtrarRegistros(dfSetDatos):
    # Especificamos los filtros para registros
    dfSetDatos = dfSetDatos[(dfSetDatos['oferta'] == 'Venta') & 
                (dfSetDatos['tipoinmueble'] == 0) & # 0 = Apartamento
                ((dfSetDatos['amueblado'] == False) | (dfSetDatos['amueblado'].isnull()))]

    # Especificamos los filtros para columnas
    dfSetDatos = dfSetDatos[['codigoencabezado', 'idregistro', 'banos', 'habitaciones', 
                               'espacio_m2', 'latitud', 'longitud', 'moneda',
                               'parqueo', 'tipovendedor', 'precioreal', 'userid']]

    return(dfSetDatos)

# Se genera un modelo kmeans para la ubicacion de latitud y longitud
def generarModeloUbicacion(dfSetDatos):
    intKClusters = 13

    # Se obtienen los valores que se utilizaran para la construccion de modelo KMeans
    npUbicaciones = np.array(list(zip(dfSetDatos['longitud'], 
                                    dfSetDatos['latitud']))).reshape(len(dfSetDatos['longitud']), 2)

    # Construccion del modelo
    kmeanModel = KMeans(n_clusters = intKClusters, max_iter = 2000).fit(npUbicaciones)

    # Asignacion de clusters a registros
    dfSetDatos['ubicacion'] = ["U" + str(ubicacion) for ubicacion in kmeanModel.labels_]

    # Calculo de frecuencia para ubicacion
    srFreqUbicacion = pd.Series(dfSetDatos['ubicacion']).value_counts()

    # Eliminando elementos que tienen baja frecuencia para ubicacion
    intNumeroPivote = 10
    idxEliminar = srFreqUbicacion[srFreqUbicacion <= intNumeroPivote].index
    dfSetDatos = dfSetDatos[~dfSetDatos.ubicacion.isin(idxEliminar)]

    # Creamos el dataframe con el cual vamos a mapear los valores
    dfMapeo = pd.DataFrame({'ubicacion': dfSetDatos.ubicacion.unique()})
    dfMapeo['nuevaubicacion'] = ["U" + str(ubicacion) for ubicacion in range(1, len(dfMapeo) + 1)]

    # Colocamos los nuevos valores de ubicacion
    dfSetDatos['ubicacion'] = dfSetDatos.join(dfMapeo.set_index('ubicacion'), on = 'ubicacion')['nuevaubicacion']

    return(dfSetDatos, kmeanModel, len(dfMapeo))

# Elimina valores nulos para ciertos campos ya establecidos
def eliminarValoresNulos(dfSetDatos, dfSetInicial):

    # ------------------------------------------ [Parqueo]

    # Obtenemos la info de los registros que tienen parqueo como nulo.
    dfSinParqueo = dfSetDatos.loc[pd.isnull(dfSetDatos['parqueo']), ['idregistro', 'parqueo']]
    
    # Obtenemos la info de los regsitros del catalogo inicial solo para los registros de interes.
    dfCatalogo = dfSetInicial.loc[dfSetInicial.idregistro.isin(dfSinParqueo['idregistro']), ['idregistro', 'descripcion']]

    # Verificamos si existe palabra parqueo dentro de columna descripcion
    dfCatalogo['parqueo'] = [True if (re.search('parqueo',str(descripcion).lower())) else False \
                            for descripcion in dfCatalogo['descripcion']]

    # Asignacion de los valores calculados para parqueo
    dfSetDatos = dfSetDatos.set_index(['idregistro'])\
        .combine_first(dfCatalogo[['idregistro', 'parqueo']].set_index(['idregistro']))\
        .reset_index()


    # Verificamos si existe palabra parqueo dentro de columna descripcion
    dfSetDatos['parqueo'] = [1 if (parqueo == True) else 0 for parqueo in dfSetDatos['parqueo']]

    # ---------------------------------------- [Tipo Vendedor]

    # Obtenemos los codigos de vendedor donde el tipo_vendedor es nulo.
    dfSinVendedor = dfSetDatos.loc[pd.isnull(dfSetDatos['tipovendedor']), ['idregistro', 'tipovendedor', 'userid']]

    # Calculamos la frecuencia de registros para cada user_id
    srFreqVendedores = pd.Series(dfSinVendedor['userid']).value_counts(dropna = False)

    # Para aquellos user_id que solo poseen un registro se les asigna el valor de "Dueno Directo"
    intNumeroPivote = 1
    idxDuenos = srFreqVendedores[srFreqVendedores == intNumeroPivote].index
    dfSinVendedor['tipovendedor'] = [0 if x else 1 for x in dfSinVendedor.userid.isin(idxDuenos)] # 0 = Dueno Directo, 1 = Inmobiliaria

    # Asignacion de los valores calculados para tipo de vendedor
    dfSetDatos = dfSetDatos.set_index(['idregistro']).combine_first(dfSinVendedor[['idregistro', 'tipovendedor']].set_index(['idregistro'])).reset_index()

    # Convertimos a entero
    dfSetDatos = dfSetDatos.astype({'tipovendedor': 'int'})

    return(dfSetDatos)

# Creacion de variables dummies por Hot Encodign para moneda, tipo vendedor y ubicacion
def crearVariablesDummy(dfSetDatos):
    
    # Eliminamos variables dummy si ya existen
    dfSetDatos = dfSetDatos.drop(['monedaq','monedad', 'tipoinmobiliaria', 'tipodueno'], axis=1, errors='ignore')

    # Convertimos aquellas variables categoricas a variables dummy.
    dfSetDatos = pd.concat([dfSetDatos, pd.get_dummies(dfSetDatos['moneda'])\
                                .rename(columns={'Q': 'monedaq', 'US$': 'monedad'})], axis = 1)

    dfSetDatos = pd.concat([dfSetDatos, pd.get_dummies(dfSetDatos['tipovendedor'])\
                                .rename(columns={1: 'tipoinmobiliaria', 
                                                0: 'tipodueno'})], axis = 1)
    
    dfSetDatos = pd.concat([dfSetDatos, pd.get_dummies(dfSetDatos['ubicacion'])], axis = 1)

    return(dfSetDatos)

# Selecionamos las variables (columnas necesarias) para la construccion del modelo.
def seleccionVariablesModelo(dfSetDatos, intCantidadUbicacion):

    # Seleccion de todas las variables de ubicacion
    variables_ubicacion =["U" + str(ubicacion) for ubicacion in [*range(1, intCantidadUbicacion + 1)]]

    # Seleccion de las demas variables
    variables_set = ['codigoencabezado','idregistro', 'banos', 'espacio_m2', 
                    'habitaciones', 'monedaq', 'monedad',
                    'parqueo', 'tipodueno', 'tipoinmobiliaria', 
                    'precioreal']
                    
    # Seleccion de las variables
    dfModeloSet = dfSetDatos[dfSetDatos.columns.intersection(variables_ubicacion + variables_set)]

    return dfModeloSet

# Transforma los datos y devuelve un set que sera utilizado para la creacion del modelo.
def transformarDatosModelo(dfSetLimpio):
    # Se obtienen los registros unicos (eliminar duplicados)
    dfSetLimpio = obtenerRegistrosUnicos(dfSetLimpio)

    # Se calcula una columna de precio real (quetzales)
    dfSetLimpio = obtenerPrecioReal(dfSetLimpio)

    # Se calcula una columna para ver si la oferta es de Venta o Alquiler
    dfSetLimpio = obtenerOferta(dfSetLimpio)

    # Se filtran solo los registros necesarios para la construccion del modelo
    # Tambien se filtran las columnas a ser consideradas para la construccion.
    dfSetFiltrado = filtrarRegistros(dfSetLimpio)

    # Se crea una columna ubicacion acorde a los valores de latitud y longitud.
    # Tambien se obtiene el modelo kmeans que fue generado.
    dfSetFiltrado, kmeanModel, intCantidadUbicacion = generarModeloUbicacion(dfSetFiltrado)

    # Eliminamos valores nulos
    dfSetFiltrado = eliminarValoresNulos(dfSetFiltrado, dfSetLimpio)

    # Creamos variables dummy por Hot Encoding
    dfSetFiltrado = crearVariablesDummy(dfSetFiltrado)

    # Obtener el set que se va a utilizar para el modelo.
    dfSetModelo = seleccionVariablesModelo(dfSetFiltrado, intCantidadUbicacion)

    return (dfSetModelo)

# Construye el modelo de entrenamiento y devuelve los score para el test
def construirModeloLinearRegression(xTrain, xTest, yTrain, yTest):
    
    # Construccion del modelo
    linearRegModel = LinearRegression()
    linearRegModel.fit(xTrain, yTrain)

    # Prediccion para los test
    yHat = linearRegModel.predict(xTest)

    # Calculo de metricas
    mseLinearRegModel = mean_squared_error(yTest, yHat)
    r2LinearRegModel = r2_score(yTest, yHat)

    return (linearRegModel, yHat, mseLinearRegModel, r2LinearRegModel)

# Construye el modelo de entrenamiento y devuelve los score para el test
def construirModeloRandomForestRegressor(xTrain, xTest, yTrain, yTest):
    
    # Construccion del modelo
    randomForestModel = RandomForestRegressor(n_estimators = 200, max_depth = 20, random_state = 1505)
    randomForestModel.fit(xTrain, yTrain)

    # Obtenemos las predicciones del modelo para los datos test
    yHat = randomForestModel.predict(xTest)

    # Calculo de metricas
    mseRandomForestModel = mean_squared_error(yTest, yHat)
    r2RandomForestModel = r2_score(yTest, yHat)

    return (randomForestModel, yHat, mseRandomForestModel, r2RandomForestModel)

# Se obtiene un dataframe que especifica los campos y su tipo de datos para el dataframe
def transformarCampos(dfData):
    
    dfCampos = dfData.drop(columns = ['codigoencabezado'], errors ='ignore' , axis = 1)

    # Se crea nuevo dataframe con nombres de columnas y sus respectivos tipos de datos
    dfCampos = pd.DataFrame(dfCampos[dfCampos.columns].dtypes).reset_index()

    # Se establecen los nombres de columnas para el dataframe
    dfCampos.columns = ['nombrecampo', 'tipodatacampo']

    # Cambiamos el tipo de datos
    dfCampos = dfCampos.astype({'nombrecampo': 'str', 'tipodatacampo': 'str'})

    return (dfCampos)

# Transforma los datos para pivotear por codigoencabezad
def transformarCamposData(dfData):
    
    # Trasladando columnas a registros
    dfTransformacion = pd.DataFrame(dfData.melt(id_vars = 'codigoencabezado', var_name = 'nombrecampo', value_name = 'valordata'))
    dfTransformacion = dfTransformacion.astype({'nombrecampo':'str', 'valordata':'str'})

    return(dfTransformacion)

# Registra el modelo creado y los datos con los que fue generado y probado
def registrarModelo(dfSetModelo, xTrain, fileName, nombreModelo, mseScore, r2Score):
    
    # Conexion a base de datos
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
    con = engine.connect()
    
    # Query para insercion de nuevo registro
    strQuery = "INSERT INTO modeloencabezado(tipomodelo, archivomodelo, msescore, r2score) VALUES (%(tipomodelo)s, %(archivomodelo)s, %(msescore)s, %(r2score)s) RETURNING idmodelo"
    idmodelo = con.execute(strQuery, tipomodelo = nombreModelo, archivomodelo = fileName, msescore = mseScore, r2score = r2Score).fetchone()[0]
    con.close()

    # Obtenemos los set de train y test
    dfTrain = dfSetModelo.loc[dfSetModelo.index.isin(xTrain.index)]
    dfTest = dfSetModelo.loc[~dfSetModelo.index.isin(xTrain.index)]

    # Obtenemos el dataframe de campos
    dfCampos = transformarCampos(dfTrain)

    dfCampos['idmodelo'] = idmodelo

    dfCampos.to_sql('modelocampo', index = False, if_exists = 'append', con = engine)

    # Registro de los datos de entrenamiento
    dfTransformadosTR = transformarCamposData(dfTrain)
    dfTransformadosTR['idmodelo'] = idmodelo
    dfTransformadosTR['tipodata'] = 'TR'
    dfTransformadosTR.to_sql('modelodata', index = False, if_exists = 'append', con = engine)


    # Registro de los datos de prueba
    dfTransformadosTS = transformarCamposData(dfTest)
    dfTransformadosTS['idmodelo'] = idmodelo
    dfTransformadosTS['tipodata'] = 'TS'
    dfTransformadosTS.to_sql('modelodata', index = False, if_exists = 'append', con = engine)

    return(idmodelo)    

# Actualizamos los registros para dejar el modelo que estara activo.
def actualizarModeloActivo(idModeloActivo):
    
    # Conexion a base de datos
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
    con = engine.connect()
    
    # Ejecutamos actualizacion en de modelos
    strQuery = "UPDATE modeloencabezado SET active = false"
    con.execute(strQuery)

    # Actualizamos el modelo activo
    strQuery = "UPDATE modeloencabezado SET active = true WHERE idmodelo = %(idModelo)s"
    con.execute(strQuery, idModelo = idModeloActivo)
    con.close()

# Construye los modelos sobre el set de datos y guarda los archivos.
def construirModelos(dfSetModelo):
    
    # Seleccionamos las variables predictoras
    dfPredictors = dfSetModelo.loc[:, ~dfSetModelo.columns.isin(['precioreal', 'idregistro', 'codigoencabezado'])]
    
    # Seleccionamos la variable dependiente
    Y = dfSetModelo['precioreal']
    
    # Separamos los datos para test y training
    xTrain, xTest, yTrain, yTest = train_test_split(dfPredictors, Y, test_size = 0.3, random_state=1505)
    
    # Ejecutamos los modelos y obtenemos los scores
    lrModel, lrHat, lrMSE, lrR2 = construirModeloLinearRegression(xTrain, xTest, yTrain, yTest)
    rfModel, rfHat, rfMSE, rfR2 = construirModeloRandomForestRegressor(xTrain, xTest, yTrain, yTest)

    # Guarda modelos en MODEL DIRECTORY
    directorioModelo = os.environ.get('MODEL_DIRECTORY')
    strFileNameLR = 'lr' + str(datetime.datetime.now().timestamp()) + '.mdl'
    strFileNameRF = 'rf' + str(datetime.datetime.now().timestamp()) + '.mdl'


    # Escribir modelos
    pickle.dump(lrModel, open(directorioModelo + strFileNameLR, 'wb'))
    pickle.dump(lrModel, open(directorioModelo + strFileNameRF, 'wb'))

    # Registramos el modelo en base de datos
    idmodeloLR = registrarModelo(dfSetModelo, xTrain, strFileNameLR, 'LR', lrMSE, lrR2)
    idmodeloRF = registrarModelo(dfSetModelo, xTrain, strFileNameRF, 'RF', rfMSE, rfR2)

    # Validamos cual de los dos tiene un mejor
    if(lrR2 >= rfR2):
        actualizarModeloActivo(idmodeloLR)
    else:
        actualizarModeloActivo(idmodeloRF)

dateFechaActual = date.today()
dateFechaAnterior = dateFechaActual - timedelta(days= 60)

# Lectura en base de datos de los registros candidatos para la construccion del modelo
dfSetLimpio = lecturaDataLimpia(dateFechaAnterior, dateFechaActual)

# Tranformacion de los datos a utilizar para el modelo
dfSetModelo = transformarDatosModelo(dfSetLimpio)

# Construimos los modelos y guardamos sus datos
construirModelos(dfSetModelo)