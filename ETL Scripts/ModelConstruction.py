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

print(len(dfSetLimpio))
