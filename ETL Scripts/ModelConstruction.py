import pandas as pd
import numpy as np
from datetime import date, timedelta
from sqlalchemy import create_engine


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


dateFechaActual = date.today()
dateFechaAnterior = dateFechaActual - timedelta(days= 45)

dfSetLimpio = lecturaDataLimpia(dateFechaAnterior, dateFechaActual)

print(len(dfSetLimpio.index))

dfSetLimpio = obtenerRegistrosUnicos(dfSetLimpio)

print(len(dfSetLimpio.index))

dfSetLimpio = obtenerPrecioReal(dfSetLimpio)

print(dfSetLimpio)
