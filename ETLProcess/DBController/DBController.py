import os
import pandas as pd
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

    # Registra una accion en base de datos
    @staticmethod
    def registrarAccion(enumAccionSistema, strDescripcionAccion):
        
        con = None # Conexion
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion

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
    
    ###########################################################################################
    # Funciones Transformation.py

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
                                                            ' where fechalimpieza is null' +
                                                        ')',con=engine)

        except Exception as e:
            strError = str(e)

        return dfEncabezadoRegistros, dfDetalleRegistros, strError


    # Registra una accion en base de datos
    @staticmethod
    def registrarLogLimpieza():
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
            idlimpiezalog = con.execute(strQuery).fetchone()[0]

            con.close()

        except Exception as e:
            strError = str(e)


        return idlimpiezalog, strError


    # Registra datos de limpieza en la base de datos
    @staticmethod
    def registrarTransformacionDatos(dfCampos, dfLimpiezaData, idlimpiezalog, intCantidadRegistros):
        
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
            strQuery = "UPDATE limpiezalog SET cantidadregistros = " + str(intCantidadRegistros) + " where idlimpiezalog = " + str(idlimpiezalog)
            
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

    @staticmethod
    def actualizarVistaMaterializada():
        '''
        Se encarga de ejecutar el query para actualizar la vista materializada
        '''

        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion
        blnEjecucion = False # Bandera de ejecucion
        strError = None

        try:
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            
            # Ejecucion de actualizacion
            strQuery = "REFRESH MATERIALIZED VIEW mvwSetLimpio"
            engine.execute(strQuery)

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion

        return blnEjecucion, strError

    ###########################################################################################
    # Funciones ModelConstruction.py

    # Consulta datos en vista de datos limpios
    @staticmethod
    def obtenerDatosLimpios(dateFechaInicial, dateFechaFinal):
        '''
            Se consulta a la vista de datos limpios para obtener aquellos registros
            que se encuentran dentro del rango de fechas establecidos por los parametros

            Input: 
                dateFechaInicial: Fecha Inicial de busqueda
                dateFechaFinal: Fecha Final de busqueda

            Output: Dataframes de registros
        '''
        dfRegistros = None # Registros limpios
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion

        try:
            engine = create_engine(strCadenaConexion)

            # Consulta a vista de datos limpios
            strQuery = 'SELECT * FROM mvwSetLimpio WHERE fecharegistro BETWEEN %(fechaInicial)s AND %(fechaFinal)s'
    
            # Leyendo de base de datos especificando el query y los parametros de fecha.
            dfRegistros = pd.read_sql_query(strQuery, 
                params = {
                    'fechaInicial': dateFechaInicial, 
                    'fechaFinal': dateFechaFinal}, coerce_float = False, con=engine)

        except Exception as e:
            strError = str(e)

        return dfRegistros, strError
    

    # Crea un registro de modelo kmeans creado
    @staticmethod
    def registrarModeloKMeans(strTipoModelo, strFileNameKM):

        con = None # Conexion
        tran = None # Transaction
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion
        idmodelo = None # Id del modelo registrado

        try:

            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            con = engine.connect()
            tran = con.begin()

            # Query para insercion de nuevo registro
            strQuery = "INSERT INTO modeloencabezado(tipomodelo, archivomodelo, msescore, r2score) VALUES (%(tipomodelo)s, %(archivomodelo)s, %(msescore)s, %(r2score)s) RETURNING idmodelo"
            idmodelo = con.execute(strQuery, tipomodelo = strTipoModelo, archivomodelo = strFileNameKM, msescore = 0.0, r2score = 0.0).fetchone()[0]

            # Ejecutamos actualizacion en de modelos
            strQuery = "UPDATE modeloencabezado SET active = false WHERE tipomodelo in ('KM')"
            con.execute(strQuery)

            # Actualizamos el modelo activo
            strQuery = "UPDATE modeloencabezado SET active = true WHERE idmodelo = %(idModelo)s"
            con.execute(strQuery, idModelo = idmodelo)

            tran.commit()

            blnEjecucion = True


        except Exception as e:
            strError = str(e)
            blnEjecucion = False
            tran.rollback()

        finally:
            if(con is not None):
                con.close()

        return idmodelo, strError

    ###########################################################################################
    # Funciones Scrapping.py

    # Obtiene los URL para realizar scrapping si no hay registros en el log
    @staticmethod
    def obtenerUrlScrapping(dateFechaScrapping):
        '''
        Input:
            dateFechaLog: Fecha de log para scrapping para verificar si la URL debe ser scrapeada
        Output:
            DataFrame con los registros de urls
        '''

        dfRegistros = None # Registros limpios
        strError = None # Mensaje de error
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion

        try:
            engine = create_engine(strCadenaConexion)

            # Lectura de registros con url por dia
            strQuery = '''
                    select us.idurlscrapping, us.urlscrapping, us.numeroclics, us.cantidadlimiteregistros, 
                        us.registrosxpagina, us.registrosmin, us.intentosmax,  ls.fechascrapping    
                    from urlscrapping as us   
                    left join logscrapping as ls  
	                    on us.idurlscrapping = ls.idurlscrapping  
	                    and us.idurlscrapping is not null
						and date(ls.fecharegistro) = date(%(fechaScrapping)s) 
                    where us.urlactivo = true 
                    and (ls.cantidadintentos is null or (ls.cantidadintentos < us.intentosmax and ls.cantidadregistros = 0))
                    and (ls.fechascrapping is null or date(ls.fecharegistro) = date( %(fechaScrapping)s )) '''
    
            # Leyendo de base de datos especificando el query y los parametros de fecha.
            dfRegistros = pd.read_sql_query(strQuery, 
                params = {'fechaScrapping': dateFechaScrapping}, coerce_float = False, con=engine)

        except Exception as e:
            strError = str(e)

        return dfRegistros, strError

    # Se encarga de actualizar el registro de logscrapping para una fecha en especifico, de no encontrar registro hace un insert.
    def actualizarLogScrapping(dateFechaScrapping, idUrlScrapping, intRegistros):
        '''
        Input:
            dateFechaScrapping: Fecha en que se realiza el scrapping
            idUrlScrapping: Codigo de registro en tabla urlscrapping
            intRegistros: Registros scrapeados
        Output:
            True/False registro exitoso
            strError Mensaje de error
        '''
        
        strCadenaConexion = DBController.obtenerCadenaConexion() 
        tran = None 
        resultado = False
        strError = None
        
        try:
            
            # Conexion a base de datos
            engine = create_engine(strCadenaConexion)
            con = engine.connect()
            tran = con.begin()

            strQuery = "select count(*) from logscrapping where idurlscrapping = %(idscrapping)s and fechascrapping = date(%(fechascrapp)s)"
            registros = con.execute(strQuery, idscrapping = idUrlScrapping, fechascrapp = dateFechaScrapping).fetchone()[0]
            
            # Si el id de consulta es nulo se procede a realizar una insercion
            if (registros is None or registros == 0):
                strQuery = '''
                    insert into logscrapping(idurlscrapping, fechascrapping, cantidadintentos, cantidadregistros) 
                    values(%(idscrapping)s, %(fechascrapp)s, %(intentos)s, %(registros)s)
                '''
                # Ejecucion de insercion
                con.execute(strQuery, idscrapping = idUrlScrapping, fechascrapp = dateFechaScrapping, intentos = 1, registros = intRegistros)

            # Si existe id entonces se procede 
            else:

                strQuery = '''
                    update logscrapping 
                    set cantidadintentos = (cantidadintentos + 1), 
                        cantidadregistros = cantidadregistros + %(registros)s
                    where idurlscrapping = %(idscrapping)s 
                    and date(fechascrapping) = date(%(fechascrapp)s) 
                '''

                # Ejecucion de actualizacion
                con.execute(strQuery, fechascrapp = dateFechaScrapping, idscrapping = idUrlScrapping, registros = intRegistros)

            tran.commit()
            resultado = True

        except Exception as e:
            strError = e
            tran.rollback()
            resultado = False
            

        finally:
            if(con is not None):
                con.close()

        return resultado, strError

    # Registra los datos de scrapping
    @staticmethod
    def registrarDatosScrapping(listaRegistros):
        
        intRegistrosIngresados = 0 # Cantidad de registros ingresados
        strCadenaConexion = DBController.obtenerCadenaConexion() # Cadena de conexion
        tran = None

        # Recorremos cada registro
        for registro in listaRegistros:

            try:
                # Conexion a base de datos
                engine = create_engine(strCadenaConexion)
                con = engine.connect()
                tran = con.begin()


                # Obtenemos los valores a insertar en encabezado
                intIdRegistro = registro.id
                strLinkPagina = registro.linkPagina
                listaAtributos = registro.atributos
                
                # Query para insercion de nuevo registro
                strQuery = "INSERT INTO encabezadoregistros(idregistro, linkpagina) VALUES (%(idregistro)s, %(linkpagina)s) RETURNING CodigoEncabezado"
                intCodigoEncabezado = con.execute(strQuery, idregistro = intIdRegistro, linkpagina = strLinkPagina).fetchone()[0]

                # Recorremos cada detalle
                for registroDetalle in listaAtributos:
                    strCampo = registroDetalle.campo
                    strValor = registroDetalle.valor
                    strValorJSON = None

                    # Si el campo es JSON lo guardamos en otra columna
                    if(strCampo == "JSON"):
                        strValorJSON = strValor
                        strValor = None

                     # Query para insercion de nuevo registro
                    strQuery = "INSERT INTO public.DetalleRegistros(CodigoEncabezado, NombreCampo, ValorCampo, ValorJSON) VALUES (%(codigoencabezado)s, %(nombrecampo)s, %(valorcampo)s, %(valorjson)s)"
                    con.execute(strQuery, codigoencabezado = intCodigoEncabezado, nombrecampo = strCampo, valorcampo = strValor, valorjson = strValorJSON)
                
                intRegistrosIngresados += 1
                tran.commit()

            except Exception as e:
                strError = e
                tran.rollback()
            

            finally:
                if(con is not None):
                    con.close()

        return (intRegistrosIngresados)
