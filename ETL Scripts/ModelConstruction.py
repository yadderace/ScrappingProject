import pandas as pd
import numpy as np
from datetime import date, timedelta
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
#from sklearn.model_selection import train_test_split
#from sklearn.linear_model import LinearRegression
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.metrics import mean_squared_error, r2_score


# Lectura de los datos limpios en BD
def lecturaDataLimpia(dateFechaInicial, dateFechaFinal):
    
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')

    strQuery = 'select * from mvwSetLimpio where  fecharegistro between %(fechaInicial)s and %(fechaFinal)s'
    
    # Leyendo de base de datos especificando el query y los parametros de fecha.
    dfRegistros = pd.read_sql_query(strQuery, 
        params = {
            'fechaInicial': dateFechaInicial, 
            'fechaFinal': dateFechaFinal}, con=engine)

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

    return(dfSetDatos, kmeanModel)

dateFechaActual = date.today()
dateFechaAnterior = dateFechaActual - timedelta(days= 45)

# Lectura en base de datos de los registros candidatos para la construccion del modelo
dfSetLimpio = lecturaDataLimpia(dateFechaAnterior, dateFechaActual)

# Se obtienen los registros unicos (eliminar duplicados)
dfSetLimpio = obtenerRegistrosUnicos(dfSetLimpio)

# Se calcula una columna de precio real (quetzales)
dfSetLimpio = obtenerPrecioReal(dfSetLimpio)

# Se calcula una columna para ver si la oferta es de Venta o Alquiler
dfSetLimpio = obtenerOferta(dfSetLimpio)

# Se filtran solo los registros necesarios para la construccion del modelo
# Tambien se filtran las columnas a ser consideradas para la construccion.
dfSetLimpio = filtrarRegistros(dfSetLimpio)

# Se crea una columna ubicacion acorde a los valores de latitud y longitud.
# Tambien se obtiene el modelo kmeans que fue generado.
dfSetLimpio, kmeanModel = generarModeloUbicacion(dfSetLimpio)


print(dfSetLimpio)
