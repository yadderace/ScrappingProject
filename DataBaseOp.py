import psycopg2

class DataBaseOp:

    
    
    # Metodo para registras los datos en base de datos
    @staticmethod
    def RegistrarDatos(listaRegistros):

        intRegistrosIngresados = 0

        strQueryEncabezado = "INSERT INTO public.EncabezadoRegistros(IdRegistro, LinkPagina) VALUES (%s, %s) RETURNING CodigoEncabezado"

        strQueryDetalle = "INSERT INTO public.DetalleRegistros(CodigoEncabezado, NombreCampo, ValorCampo) VALUES (%s, %s, %s)"

        # Recorremos cada registro
        for(registro in listaRegistros):

            # Obtenemos la conexion a BD
            conn = None
            try:
                conn = psycopg2.connect(user = "postgres",
                                  password = "150592",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "DBApartamentos")
            except(Exception, psycopg2.DatabaseError) as error:
                print(error)
                return(intRegistrosIngresados)

            # Obtenemos los valores a insertar en encabezado
            intIdRegistro = registro.id
            strLinkPagina = registro.linkPagina
            listaAtributos = registro.atributos

            # Ejecutamos el query de insercion encabezado y obtenemos el valor de codigo asignado
            cur = conn.cursor()
            cur.execute(strQueryEncabezado, (intIdRegistro, strLinkPagina))
            intCodigoEncabezado = cur.fetchone()[0]

            # Recorremos cada detalle
            for registroDetalle in listaAtributos:
                
                strCampo = registroDetalle.campo
                strValor = registroDetalle.valor

                # Ejecutamos la insercion de registro detalle
                cur.execute(strQueryDetalle, (intCodigoEncabezado, strCampo, strValor))
            
            # Confirmamos la insercion
            conn.commit()
            
            # Cerramos la conexion
            if(conn):
                cur.close()
                conn.close()

            intRegistrosIngresados += 1
            # ==================    Fin de ciclo For para encabezado
        
        return (intRegistrosIngresados)
        # ======================    Fin del metodo Registrar Datos









