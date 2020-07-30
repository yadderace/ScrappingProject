from sqlalchemy import create_engine

class DBController():

    # Registra una accion en base de datos
    @staticmethod
    def registrarCamposModelo(dfCampos):
        
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error

        try:
            # Conexion a base de datos
            engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
            
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

        try:
            # Conexion a base de datos
            engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
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

    @staticmethod
    def registrarModeloData(dfData):    
        blnEjecucion = False # Bandera de ejecucion de SQL
        strError = None # Mensaje de error

        try:
            # Conexion a base de datos
            engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
            
            dfData.to_sql('modelodata', index = False, if_exists = 'append', con = engine)

            blnEjecucion = True

        except Exception as e:
            strError = str(e)
            blnEjecucion = False


        return blnEjecucion, strError