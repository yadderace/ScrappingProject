import os
from sqlalchemy import create_engine

class DBController():

    
    @staticmethod
    def obtenerCadenaConexion():
        '''
            Devuele la cadena de conexion haciendo uso de variables de entorno.

            Output: String con cadena de conexion
        '''
        strDataBase = os.environ.get('DATABASE_NAME')
        strUserName = os.environ.get('USER_NAME')
        strPortDB = os.environ.get('PORT_DB')
        strHostDB = os.environ.get('HOST_DB')
        strPassword = os.environ.get('PASSWORD_USR')

        strCadenaConexion = 'postgresql://'+ strUserName + ':' + strPassword + '@' + strHostDB + ':' + strPortDB + '/' + strDataBase

        return strCadenaConexion

    # Consulta los datos de scrapping
    @staticmethod
    def obtenerDatosScrapping():
        '''
            Se consulta los datos de encabezado y detalle para datos que fueron
            scrapeados y que no han sido procesados para transformacion.

            Output: Dataframes de encabezado y detalle
        '''
        dfEncabezadoRegistros = None # Registros de encabezado
        dfDetalleRegistros = None # Registros de detalle
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            
            dfEncabezadoRegistros = pd.read_sql_query('select codigoencabezado, idregistro, linkpagina, fecharegistro ' + 
                                                    'from encabezadoregistros where fechalimpieza is null',con=engine)

            dfDetalleRegistros = pd.read_sql_query('select * from detalleregistros ' +
                                                        ' where codigoencabezado in (' + 
                                                            ' select distinct codigoencabezado ' +
                                                            ' from encabezadoregistros' +
                                                            ' where fechalimpieza is null'
                                                        ')',con=engine)

        except Exception as e:
            strError = str(e)

        return dfEncabezadoRegistros, dfDetalleRegistros, strError


    # Registra una accion en base de datos
    @staticmethod
    def registrarLogLimpieza(dfCampos):
        '''
            Crea un nuevo registro en la table idlimpiezalog. Devuelve el id generado

            Output: ID de registro
        '''
        
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion
        idlimpiezalog = None # Id de registro guardado en log de limpieza

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            con = engine.connect()

            # Query para insercion de nuevo registro
            strQuery = "INSERT INTO limpiezalog(CantidadRegistros) VALUES (0) RETURNING idlimpiezalog"

            # Ejecucion de query
            idlimpiezalog = con.execute(strQuery)

            con.close()

        except Exception as e:
            strError = str(e)


        return idlimpiezalog, strError


    # Registra datos de limpieza en la base de datos
    @staticmethod
    def registrarTransformacionDatos(dfCampos, dfLimpiezaData, idlimpiezalog):
        
        '''
            Registra los resultados de limpieza en las tablas de encabezado y detalle.

            Input:
                dfCampos, registros de campos de los datos limpios
                dfLimpiezaData, registros de datos limpios
                idlimpiezalog, ID de log para limpieza

            Output:
                Bandera de ejecucion exitosa
        '''

        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion
        blnEjecucion = False # Bandera de ejecucion
        strError = None
        
        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            
            # Registrando los datos en limpiezadetalle
            dfCampos.to_sql('limpiezadetalle', index = False, if_exists = 'append', con = engine)

            # Registrando los datos en limpiezadata
            dfLimpiezaData.to_sql('limpiezadata', index = False, if_exists = 'append', con = engine)

            # Actualizando la tabla principal de limpieza para registros
            strQuery = "UPDATE limpiezalog SET cantidadregistros = " + str(len(dfTransformacion.index)) + " where idlimpiezalog = " + str(idlimpiezalog)
            
            engine.execute(strQuery)

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion

        
        return blnEjecucion, strError

    # Coloca fecha de limpieza a los registros de scrapping
    @staticmethod
    def actualizarLimpiezaScrapping():
        
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion
        blnEjecucion = False # Bandera de ejecucion
        strError = None

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            
            # Ejecucion de actualizacion
            strQuery = "UPDATE encabezadoregistros SET fechalimpieza = now() where fechalimpieza is null"
            engine.execute(strQuery)

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion

        return blnEjecucion, strError

    # Registra una accion en base de datos
    @staticmethod
    def registrarCamposModelo(dfCampos):
        
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            
            dfCampos.to_sql('modelocampo', index = False, if_exists = 'append', con = engine)

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False


        return blnEjecucion, strError


    # Registra en tabla  modeloencabezado la construccion de un nuevo modelo
    @staticmethod
    def registrarModeloEncabezado(nombreModelo, fileName, mseScore, r2Score):
        
        con = None # Conexion
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        idmodelo = None # Identificador del modelo
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            con = engine.connect()
            
            # Query para insercion de nuevo registro
            strQuery = "INSERT INTO modeloencabezado(tipomodelo, archivomodelo, msescore, r2score) VALUES (%(tipomodelo)s, %(archivomodelo)s, %(msescore)s, %(r2score)s) RETURNING idmodelo"
            idmodelo = con.execute(strQuery, tipomodelo = nombreModelo, archivomodelo = fileName, msescore = mseScore, r2score = r2Score).fetchone()[0]

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False

        finally:
            if(con is not None):
                con.close()

        return blnEjecucion, idmodelo, strError

    # Registra un modelo de datos 
    @staticmethod
    def registrarModeloData(dfData):    
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            
            dfData.to_sql('modelodata', index = False, if_exists = 'append', con = engine)

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False


        return blnEjecucion, strError

    
