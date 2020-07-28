
from sqlalchemy import create_engine

class DBRegistroAcciones():

    # Registra una accion en base de datos
    @staticmethod
    def registrarAccion(enumAccionSistema, strDescripcionAccion):
        # Conexion a base de datos
        engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
        con = engine.connect()
    
        # Query para insercion de nuevo registro
        strQuery = "INSERT INTO logaccionessistema(nombreaccion, descripcionaccion) VALUES (%(nombreaccion)s, %(descripcionaccion)s)"
        con.execute(strQuery, nombreaccion = enumAccionSistema, descripcionaccion = strDescripcionAccion)

        con.close()
