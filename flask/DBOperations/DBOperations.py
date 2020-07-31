from sqlalchemy import create_engine

class DBOperations():

    # Registra una accion en base de datos
    @staticmethod
    def registrarAccion(enumAccionSistema, strDescripcionAccion):
        
        con = None # Conexion
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error

        try:
            # Conexion a base de datos
            engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
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

        try:
            # Conexion a base de datos
            engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
            con = engine.connect()
        
            strQuery = "SELECT archivomodelo FROM modeloencabezado WHERE active = true AND tipomodelo in ('LR', 'RF')"
            strArchivoModelo = con.execute(strQuery).fetchone()[0]

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False

        finally:
            if(con is not None):
                con.close()

        return blnEjecucion, strArchivoModelo, strError

    # Busca el modelo activo en base de datos y devuelve el nombre del archivo.
    @staticmethod
    def obtenerModeloKMeansActivo():
        
        con = None # Conexion
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error
        strArchivoModelo = None # Nombre del archivo del modelo

        try:
            # Conexion a base de datos
            engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
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