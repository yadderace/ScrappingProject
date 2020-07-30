from sqlalchemy import create_engine

class DBController():

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