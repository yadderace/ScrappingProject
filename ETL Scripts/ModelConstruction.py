import pandas as pd
from datetime import date, timedelta
from sqlalchemy import create_engine


# Lectura de los datos limpios en BD
def lecturaDataLimpia(dateFechaInicial, dateFechaFinal):
    
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')

    strQuery = 'select * from mvwSetLimpio where  fecharegistro between %(fechaInicial)s and %(fechaFinal)s'
    
    dfRegistros = pd.read_sql_query(strQuery, 
        params = {
            'fechaInicial': dateFechaInicial, 
            'fechaFinal': dateFechaFinal}, con=engine)

    return dfRegistros



dateFechaActual = date.today()
dateFechaAnterior = dateFechaActual - timedelta(days= 45)

dfSetLimpio = lecturaDataLimpia(dateFechaAnterior, dateFechaActual)

print(dfSetLimpio)

