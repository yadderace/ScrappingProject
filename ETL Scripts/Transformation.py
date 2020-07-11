import re
import json
import ast
import pandas as pd
import numpy as np

from sqlalchemy import create_engine

# Lectura de datos sin limpieza en base de datos
def lecturaDataScrapping():
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')

    dfEncabezadoRegistros = pd.read_sql_query('select * from encabezadoregistros ezadoregistros',con=engine)
    dfDetalleRegistros = pd.read_sql_query('select * from detalleregistros',con=engine)

    return (dfEncabezadoRegistros, dfDetalleRegistros)

# Realiza modificaciones a los registros con campo administracion
def limpiarCampoAdmnistracion(dfDetalleRegistros):
    dfDetalleAdmin = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Administración",
                                        ["codigoencabezado", "nombrecampo", "valorcampo"]]
    # Reseteamos valores de indices.
    dfDetalleAdmin.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleAdmin.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Administracion
    dfDetalleAdmin.rename(columns={'valorcampo': 'administracion'}, inplace = True)

    # Cambiamos el tipo de dato
    dfDetalleAdmin = dfDetalleAdmin.astype({'administracion': float})

    return (dfDetalleAdmin)

# Realiza modificaciones a los registros con campo amueblado
def limpiarCampoAmueblado(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Amueblado"
    dfDetalleAmueblado = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Amueblado",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleAmueblado.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleAmueblado.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Amueblado
    dfDetalleAmueblado.rename(columns={'valorcampo': 'amueblado'}, inplace = True)

    # Reemplazamos los valores de amueblado por valores numericos
    dfDetalleAmueblado['amueblado'] = dfDetalleAmueblado.amueblado.map({'No': 0, 'Sí': 1})

    return(dfDetalleAmueblado)

# Realiza las modificaciones  los registros con campo antiguedad
def limpiarCampoAntiguedad(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Antigüedad"
    dfDetalleAntiguedad = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Antigüedad",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleAntiguedad.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleAntiguedad.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Antiguedad
    dfDetalleAntiguedad.rename(columns={'valorcampo': 'antiguedad'}, inplace = True)

    # Reemplazamos los valores de antiguedad
    dfDetalleAntiguedad['antiguedad'] = dfDetalleAntiguedad.antiguedad.map({'En construcción': 0,
                                                'A estrenar': 1,
                                                'Hasta 5 años': 2,
                                                'Entre 5 y 10 años': 3,
                                                'Entre 10 y 20 años': 4,
                                                'Entre 20 y 50 años': 5,
                                                'Más de 50 años': 6
                                                })
    
    return (dfDetalleAntiguedad)

# Realiza las modificaciones a los registros con campo banos
def limpiarCampoBanos(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Baños"
    dfDetalleBanos = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Baños",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleBanos.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleBanos.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Baños
    dfDetalleBanos.rename(columns={'valorcampo': 'banos'}, inplace = True)

    # Cambiamos el tipo de dato
    dfDetalleBanos = dfDetalleBanos.astype({'banos': int})

    return (dfDetalleBanos)

# Realiza las modificaciones a los registros con campo habitaciones
def limpiarCampoHabitaciones(dfDetalleRegistros):
    
    # Obtenemos solo registros con NombreCampo == "Habitaciones"
    dfDetalleHabitaciones = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Habitaciones",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleHabitaciones.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleHabitaciones.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Habitaciones
    dfDetalleHabitaciones.rename(columns={'valorcampo': 'habitaciones'}, inplace = True)

    # Como existe un valor llamado estudio, se creara una variable que inidique si es estudio.
    dfDetalleHabitaciones['estudio'] = np.where(dfDetalleHabitaciones['habitaciones'] == 'Estudio', 1, 0)
            
    # Para aquellos que son estudio definiremos el valor de habitaciones como 1
    dfDetalleHabitaciones['habitaciones'] = np.where(dfDetalleHabitaciones['habitaciones'] == 'Estudio', '1', 
                                                    dfDetalleHabitaciones['habitaciones'])

    # Cambiamos el tipo de dato
    dfDetalleHabitaciones = dfDetalleHabitaciones.astype({'habitaciones': int})

    return (dfDetalleHabitaciones)

# Realiza las modificaciones a los registros con campo latitud
def limpiarCampoLatitud(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Latitude"
    dfDetalleLatitude = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Latitude",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleLatitude.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleLatitude.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Latitud
    dfDetalleLatitude.rename(columns={'valorcampo': 'latitud'}, inplace = True)

    # Cambiamos el tipo de dato
    dfDetalleLatitude = dfDetalleLatitude.astype({'latitud': float})

    return(dfDetalleLatitude)

# Realiza las modificaciones a los registros con campo longitud
def limpiarCampoLongitud(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Longitud"
    dfDetalleLongitude = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Longitude",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleLongitude.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleLongitude.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Longitud
    dfDetalleLongitude.rename(columns={'valorcampo': 'longitud'}, inplace = True)

    # Cambiamos el tipo de dato
    dfDetalleLongitude = dfDetalleLongitude.astype({'longitud': float})

    return(dfDetalleLongitude)

# Realiza las modificaciones a los registros con campo espacio total
def limpiarCampoEspacioTotal(dfDetalleRegistros):
    
    # Obtenemos solo registros con NombreCampo == "Metros Cuadrados Totales"
    dfDetalleEspacio = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Metros Cuadrados Totales",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleEspacio.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleEspacio.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con espacio_m2
    dfDetalleEspacio.rename(columns={'valorcampo': 'espacio_m2'}, inplace = True)

    # Obtenemos solo los valores numericos
    dfDetalleEspacio['espacio_m2'] =  [re.sub('m2','', str(espacio)).strip() for espacio in dfDetalleEspacio['espacio_m2']]
        

    # Cambiamos el tipo de dato
    dfDetalleEspacio = dfDetalleEspacio.astype({'espacio_m2': float})

    return(dfDetalleEspacio)

# Realiza las modificaciones a los registros con campo parqueadero
def limpiarCampoParqueo(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Parqueadero"
    dfDetalleParqueo = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Parqueadero",
                                        ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleParqueo.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleParqueo.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Parqueo
    dfDetalleParqueo.rename(columns={'valorcampo': 'parqueo'}, inplace = True)

    # Reemplazamos los valores de parqueo por valores numericos
    dfDetalleParqueo['parqueo'] = dfDetalleParqueo.parqueo.map({'No': 0, 'Si': 1})

    return(dfDetalleParqueo)

# Realiza las modificaciones a los registros con campo piso
def limpiarCampoPiso(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Piso"
    dfDetallePiso = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Piso",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetallePiso.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetallePiso.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con piso
    dfDetallePiso.rename(columns={'valorcampo': 'piso'}, inplace = True)

    # Cambiamos el tipo de dato
    dfDetallePiso = dfDetallePiso.astype({'piso': int})

    return(dfDetallePiso)

# Realiza las modificaciones a los registros con campo precio
def limpiarCampoPrecio(dfDetalleRegistros):
    
    # Obtenemos solo registros con NombreCampo == "Precio"
    dfDetallePrecio = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Precio",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetallePrecio.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetallePrecio.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con precio
    dfDetallePrecio.rename(columns={'valorcampo': 'precio'}, inplace = True)

    # Separamos por espacio para poder tener una lista con el tipo de moneda y el precio en cada registro
    dfDetallePrecio['precio'] = [strPrecio.split() for strPrecio in dfDetallePrecio['precio']]

    # Creamos un campo de moneda
    dfDetallePrecio['moneda'] = [precio[0] for precio in dfDetallePrecio['precio']]

    # Eliminamos las comas del precio
    dfDetallePrecio['precio'] = [re.sub(',', '', str(precio[1])) for precio in dfDetallePrecio['precio']]

    # Cambiamos el tipo de dato
    dfDetallePrecio = dfDetallePrecio.astype({'precio': float})

    return(dfDetallePrecio)

# Realiza las modificaciones a los registros con campo tipo
def limpiarCampoTipo(dfDetalleRegistros):
    
    # Obtenemos solo registros con NombreCampo == "Tipo"
    dfDetalleTipo = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Tipo",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleTipo.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleTipo.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con Tipo
    dfDetalleTipo.rename(columns={'valorcampo': 'tipo'}, inplace = True)

    # Reemplazamos los valores de parqueo por valores numericos
    dfDetalleTipo['tipo'] = dfDetalleTipo.tipo.map({'Apartamento': 0, 'Casa': 1})

    return (dfDetalleTipo)

# Realiza las modificaciones a los registros con campo tipo vendedor
def limpiarCampoTipoVendedor(dfDetalleRegistros):
    # Obtenemos solo registros con NombreCampo == "Tipo de vendedor"
    dfDetalleVendedor = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "Tipo de vendedor",
                                            ["codigoencabezado", "nombrecampo", "valorcampo"]]

    # Reseteamos valores de indices.
    dfDetalleVendedor.reset_index(drop = True, inplace = True)

    # Eliminamos la columna NombreCampo
    dfDetalleVendedor.drop(columns = ['nombrecampo'], inplace = True)

    # Renombramos la columna ValorCampo con tipo_vendedor
    dfDetalleVendedor.rename(columns={'valorcampo': 'tipo_vendedor'}, inplace = True)

    # Reemplazamos los valores de tipo_vendedor por valores numericos
    dfDetalleVendedor['tipo_vendedor'] = dfDetalleVendedor.tipo_vendedor.map({'Dueño Directo': 0, 'Inmobiliaria': 1})

    return(dfDetalleVendedor)

# Realiza las modificaciones a los registros con campo tipo JSON
def limpiarCampoJSON(dfDetalleRegistros):
    # Obtenemos los registros con campo JSON
    dfDetalleJson = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "JSON",
                                        ["codigoencabezado", "nombrecampo", "valorjson"]]

    # Obtenemos solo registros con NombreCampo == "JSON"
    dfDetalleJson = dfDetalleRegistros.loc[dfDetalleRegistros["nombrecampo"] == "JSON",
                                            ["codigoencabezado", "nombrecampo", "valorjson"]]

    # Reseteamos valores de indices.
    dfDetalleJson.reset_index(drop = True, inplace = True)

    # Obtenemos los elementos que interesan
    dfDetalleJson['favoritos'] = [list(json.loads(json.dumps(elemento))['elements'].values())[0]['favorites']['count']
                                for elemento in dfDetalleJson['valorjson']]

    dfDetalleJson['titulo'] = [list(json.loads(json.dumps(elemento))['elements'].values())[0]['title']
                                for elemento in dfDetalleJson['valorjson']]

    dfDetalleJson['fecha_creacion'] = [list(json.loads(json.dumps(elemento))['elements'].values())[0]['created_at']
                                for elemento in dfDetalleJson['valorjson']]
                                                    
    dfDetalleJson['valido_hasta'] = [list(json.loads(json.dumps(elemento))['elements'].values())[0]['valid_to']
                                for elemento in dfDetalleJson['valorjson']]

    dfDetalleJson['descripcion'] = [list(json.loads(json.dumps(elemento))['elements'].values())[0]['description']
                                for elemento in dfDetalleJson['valorjson']]

    dfDetalleJson['partner_code'] = [list(json.loads(json.dumps(elemento))['elements'].values())[0]['partner_code']
                                for elemento in dfDetalleJson['valorjson']]

    dfDetalleJson['user_id'] = [list(json.loads(json.dumps(elemento))['elements'].values())[0]['user_id']
                                for elemento in dfDetalleJson['valorjson']]

    # Eliminamos la columna NombreCampo y ValorJSON
    dfDetalleJson.drop(columns = ['valorjson'], inplace = True)
    dfDetalleJson.drop(columns = ['nombrecampo'], inplace = True)

    return(dfDetalleJson)

# Haciendo merge de datasets
def mergeDataSets(dfEnc, dfDet, strCampo, strHow):
    dfFinal = dfEnc.merge(dfDet, on = strCampo, how = strHow)
    return (dfFinal)


# Obteniendo encabezado y detalle
dfEnc, dfDet = lecturaDataScrapping()

# Obtenemos registros que tienen atributo administracion
dfDetAdmin = limpiarCampoAdmnistracion(dfDet)
dfFinal = mergeDataSets(dfEnc, dfDetAdmin, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo administracion
dfDetAmueb = limpiarCampoAmueblado(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetAmueb, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo antiguedad
dfDetAnt = limpiarCampoAntiguedad(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetAnt, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo antiguedad
dfDetBanos = limpiarCampoBanos(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetBanos, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo habitaciones
dfDetHabit = limpiarCampoHabitaciones(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetHabit, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo latitud
dfDetLat = limpiarCampoLatitud(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetLat, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo longitud
dfDetLon = limpiarCampoLongitud(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetLon, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo espacio
dfDetEspacio = limpiarCampoEspacioTotal(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetEspacio, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo parqueadero
dfDetParq = limpiarCampoParqueo(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetParq, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo piso
dfDetPiso = limpiarCampoPiso(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetPiso, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo precio
dfDetPrecio = limpiarCampoPrecio(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetPrecio, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo tipo (casa, apto)
dfDetTipo = limpiarCampoTipo(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetTipo, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo tipo vendedor
dfDetTipoVen = limpiarCampoTipoVendedor(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetTipoVen, 'codigoencabezado', 'left')

# Obtenemos registros que tienen atributo tipo vendedor
dfDetJSON = limpiarCampoJSON(dfDet)
dfFinal = mergeDataSets(dfFinal, dfDetJSON, 'codigoencabezado', 'left')

print(dfFinal)
