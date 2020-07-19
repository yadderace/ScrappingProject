import os
import pickle 
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, request, jsonify

app = Flask(__name__)

# Busca el modelo activo en base de datos y devuelve el nombre del archivo.
def obtenerModeloActivo():
    
    engine = create_engine('postgresql://postgres:150592@localhost:5432/DBApartamentos')
    
    strQuery = "SELECT archivomodelo FROM modeloencabezado WHERE active = true"
    idmodelo = engine.execute(strQuery).fetchone()[0]

    return idmodelo


@app.route('/predict', methods = ['POST'])
def predict():
    
    # Obtiene directorio de las variables del sistema
    directorioModelo = os.environ.get('MODEL_DIRECTORY')
    
    # Obtiene el nombre del archivo
    strArchivoModelo = obtenerModeloActivo()
    
    # Carga del modelo
    model = pickle.load(open(directorioModelo + strArchivoModelo, 'rb'))
    
    # Lectura de variables del request
    dfParams = pd.DataFrame(request.get_json())
    
    dfParams['U1'] = 0
    dfParams['U2'] = 0
    dfParams['U3'] = 0
    dfParams['U4'] = 0
    dfParams['U5'] = 0
    dfParams['U6'] = 0
    dfParams['U7'] = 0
    dfParams['U8'] = 0
    dfParams['U9'] = 1
    dfParams['U10'] = 0
    
    print(dfParams)

    prediction = model.predict(dfParams)
    print(prediction)

    output = prediction[0]
    print(output)

    return str(output)
    

if __name__ == "__main__":
    app.run()