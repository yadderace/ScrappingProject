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

    
