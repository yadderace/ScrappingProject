import requests
import re
import json

from bs4 import BeautifulSoup
from json import JSONEncoder

##################################################################################
# CLASES


# Clase para el detalle de apartamento
class DetalleApartamento(JSONEncoder):
    def __init__(self, campo, valor):
        self.campo = campo
        self.valor = valor


    def default(self, o):
            return o.__dict__  


# Clase para ejecutar el proceso de scrapping
class Scrapping():

    # Obtiene el html donde se encuentran los detalles de un apartamento y devuelve la
    # lista de detalles para ese apartamento.
    @staticmethod
    def obtenerDetalleRegistro(htmlRegistro):
        
        # Objeto soup para obtener cada uno de los atributos registrados en el detalle.
        soup = BeautifulSoup(htmlRegistro)

        registrosDetalles = soup.find_all('div', {'class': '_3_knn'})

        # Validamos que se pudo obtener informacion de detalle del registro.
        if(registrosDetalles is None):
            print("No se pudo obtener informacion de detalle para el registro")
            return None
        
        listaDetalle = []

        for idx in range(0, len(registrosDetalles)):
            
            # Se obtiene el registro de detalle
            registro = registrosDetalles[idx]
            #print(registro)

            # Obtenemos el nombre del detalle
            campo = registro.find('span', {'class': '_25oXN'}).string.strip()
            # Obtenemos el valor del detalle
            valor = registro.find('span', {'class': '_2vNpt'}).string.strip()
            
            # Creamos objeto de detalle y lo agregamos a la lista de detalle
            objDetalleApartamento = DetalleApartamento(campo, valor)
            listaDetalle.append(objDetalleApartamento)
        
        # Devolvemos la lista de todos los detalles
        return listaDetalle

# ------------------------------------------------------------------------------------------------------------------

    # Devuelve un listado de objetos de detalle (latitud y longitud)
    @staticmethod
    def obtenerUbicacion(registrosJS):

        for registro in  registrosJS:
            strContenido = str(registro.prettify())
            match = re.search("window.__APP", strContenido)

            if(match):
                
                # Limpiamos el contenido de la etiqueta script que posee un JSON con la informacion del apartamento
                strContenido = strContenido.replace('<script type="text/javascript">', '').replace('</script>', '').replace('window.__APP =','').replace('props:', '\"props\":').replace('};', '}')
                idxInicial = strContenido.index('"elements":')
                idxFinal = strContenido.index('"collections":')
                strContenido = "{" + strContenido[idxInicial:(idxFinal-1)] + "}"
                jsonContenido = json.loads(strContenido)
                jsonLocations = jsonContenido['elements'][list(jsonContenido['elements'].keys())[0]]['locations']

                listaDetalle = list()

                if(len(jsonLocations) > 0):
                    # Guardamos la latitud
                    objDetalleApartamento = DetalleApartamento('Latitude', jsonLocations[0]['lat'])
                    listaDetalle.append(objDetalleApartamento)

                    # Guardamos la longitud
                    objDetalleApartamento = DetalleApartamento('Longitude', jsonLocations[0]['lon'])
                    listaDetalle.append(objDetalleApartamento)

                # Guardamos el objeto JSON
                objDetalleApartamento = DetalleApartamento('JSON', json.dumps(jsonContenido))
                listaDetalle.append(objDetalleApartamento)

                return listaDetalle
        
        return None

# ------------------------------------------------------------------------------------------------------------------


    @staticmethod
    def obtenerAtributosPagina(strUrl):
            
        # Haciendo consulta GET para el link
        s = requests.Session()
        s.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    
        # Se intenta realizar peticion por Get
        r = None
        try:
            r = s.get(strUrl)
            
        except requests.exceptions.ConnectionError as e:
            #TODO Registrar error
            return None, str(e)
        

        if(r.status_code != 200):
            #TODO Registrar error de status
            return None, "Status Code != 200"

        
        htmlCode = r.text
        soup = BeautifulSoup(htmlCode)

        detalleRegistro = soup.find('div', {'class': '_3JPEe'})

        if(detalleRegistro is None):
            #TODO Registrar error
            return None, "div class != _3JPEe"

        # Se obtiene la lista de detalles.
        listaDetalle = Scrapping.obtenerDetalleRegistro(detalleRegistro.prettify())

        # Se obtiene el precio de la casa.
        precioRegistro = soup.find('span', {'class': '_2xKfz'}).string.strip()

        # Se agrega el precio como detalle a la lista.
        objDetalleApartamento = DetalleApartamento('Precio', precioRegistro)
        listaDetalle.append(objDetalleApartamento)

        # Se obtiene la ubicacion.
        registrosJS = soup.find_all('script', {'type': 'text/javascript'})
        
        if(registrosJS is None or len(registrosJS) == 0):
            #TODO Registrar error
            return None, "script type text/javascript"
        
        # Obtener informacion de la ubicacion
        listaUbicacion = Scrapping.obtenerUbicacion(registrosJS)

        if(listaUbicacion is not None):
            listaDetalle = listaDetalle + listaUbicacion

        strID = str(re.search("[0-9]+",re.search("iid-[0-9]+$", strUrl).group()).group())

        listaDetalle.append(DetalleApartamento('ID', strID))

        return listaDetalle, None
