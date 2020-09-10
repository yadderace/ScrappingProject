import requests
import re
import json
import math
import DBController.DBController as localdb

from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from DBController.AccionSistema import AccionSistema

# Texto del boton de carga
strTextoBoton = "CARGAR MÁS"

# Url de pagina web
urlBase = "https://www.olx.com.gt"

# Creacion de header para peticion
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}



##################################################################################
# CLASES


# Clase para el detalle de apartamento
class DetalleApartamento:
    def __init__(self, campo, valor):
        self.campo = campo
        self.valor = valor


# Clase de registro apartamento para generar objetos que se utilizaran para almacenar 
# en base de datos.
class RegistroApartamento:
    def __init__(self, id, linkPagina, atributos):
        self.id = id
        self.linkPagina = linkPagina
        self.atributos = atributos


#####################################################################################
# FUNCIONES

# Obtiene el html donde se encuentran los detalles de un apartamento y devuelve la
# lista de detalles para ese apartamento.
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

# Obtiene el detalle del registro, hace la consulta del link y obtiene informacion del 
# div que posee la informacion de detalle.
def obtenerInformacionRegistro(linkRegistro):
    
    # Haciendo consulta GET para el link
    urlPeticion = linkRegistro
    s = requests.Session()
    s.headers = headers

    # Se intenta realizar peticion por Get
    r = None
    try:
        r = s.get(urlPeticion)
        
    except requests.exceptions.ConnectionError as e:
        print("Error al realizar peticion Get")
        return None
    
    if r.status_code == 200:
        # Creacion de objeto Soup
        html = r.text
        soup = BeautifulSoup(html)

        # Obtener detalles del registro.
        detalleRegistro = soup.find('div', {'class': '_3JPEe'})

        # Validacion que existe tag de detalle.
        if(detalleRegistro is None):
            print("No se encontro detalle para el registro (div - class _3JPEe)")
            return(None)

        # Se obtiene la lista de detalles.
        listaDetalle = obtenerDetalleRegistro(detalleRegistro.prettify())

        # Se obtiene el precio de la casa.
        precioRegistro = soup.find('span', {'class': '_2xKfz'}).string.strip()


        # Se agrega el precio como detalle a la lista.
        objDetalleApartamento = DetalleApartamento('Precio', precioRegistro)
        listaDetalle.append(objDetalleApartamento)


        # Se obtiene la ubicacion.
        registrosJS = soup.find_all('script', {'type': 'text/javascript'})
        if(registrosJS is not None and len(registrosJS) > 0):
            listaUbicacion = obtenerUbicacion(registrosJS)

            if (listaUbicacion is not None):
                listaDetalle = listaDetalle + listaUbicacion
            else:
                print("No se ubtuvo detalles de ubicacion.")

            
        else:
            print('No se encontro ubicacion para el registro.')

        return listaDetalle
        
    else:
        print ("No se obtuvo un status code 200 [obtenerInformacionRegistro]")

# ------------------------------------------------------------------------------------------------------------------

# Se obtienen todos los registros de apartamentos/casas de la pagina principal
# Para cada uno se obtienen el link y luego se hace una peticion para obtener informacion
# especifica del registro
def obtenerRegistros(intCantidadLimite, registros):

    listaRegistrosApt = []
    
    if(intCantidadLimite > len(registros)):
        intCantidadLimite = len(registros)

    # Recorremos cada uno de los registros
    for idx in range(0, intCantidadLimite):
        
        # Se obtiene el nuevo link a consultar
        registro = registros[idx]
        soup = BeautifulSoup(registro.prettify())
        objInfoRegistro = soup.find('a')
        linkRegistro = objInfoRegistro['href']
        nuevoLink = urlBase + linkRegistro 
        
        print(str(idx) + ".- " + nuevoLink)

        strID = str(re.search("[0-9]+",re.search("iid-[0-9]+$", nuevoLink).group()).group())

        # Si se puede obtener un ID procedemos a intentar obtener el detalle del registro.
        if(strID):

            # Ejecucion de metodo para obtener informacion especifica del link.
            listaDetalle = obtenerInformacionRegistro(nuevoLink)

            # Verficamos que existan detalles del registro para crear un nuevo objeto de registro de apartamento.
            if(listaDetalle is not None and len(listaDetalle) > 0):
                objRegistroApt = RegistroApartamento(int(strID), nuevoLink, listaDetalle)
                listaRegistrosApt.append(objRegistroApt)

    # Devolvemos la lista con todos los apartamentos registrados
    return listaRegistrosApt            

# ------------------------------------------------------------------------------------------------------------------

# Intenta obtener la fuente de la pagina determinada por la cantidad de clics que se le 
# debe dar al boton CARGAR MAS de la pagina.
def obtenerFuentePagina(pTimeout, pNumeroClics, urlPeticion):
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options, executable_path = './chromedriver')
    driver.get(urlPeticion)
    driver.implicitly_wait(pTimeout)

    elements = WebDriverWait(driver, pTimeout).until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))

    # Busca el boton de cargar mas.
    btnWebElement = None
    for element in elements:
        if(str(element.text).upper() == strTextoBoton):
            btnWebElement = element
            break
    
    # Verifica que se haya encontrado el boton
    if(btnWebElement is None):
        return None
    
    
    # Ejecuta la cantidad de clics ingresadas en el parametro sobre el boton CARGAR MAS
    if(pNumeroClics > 0):
        for i in range(0, pNumeroClics):
            btnWebElement.click()
    
    # Obtiene el codigo fuente de la pagina
    strPageSource = driver.page_source

    driver.quit()

    return(strPageSource)


# ------------------------------------------------------------------------------------------------------------------
# Funcion para ejecutar el proceso de scrapping en una determinada pagina
def ejecutarScrapping(strUrlPagina, intNumeroClics, intCantidadLimiteRegistros, intRegistosPorPagina, intRegistroMin):
    
    intTimeout = 15 # Timeout de 15 segundos

    # Obtenemos el html de la pagina web
    strResultado = obtenerFuentePagina(intTimeout, intNumeroClics, strUrlPagina)

    # Verificamos que haya existido resultado
    if(strResultado is None):
        return None, "No se pudo obtener informacion de la fuente"
    
    # Utilizamos la libreria SOUP para hacer busqeda sobre la fuente HTML
    soup = BeautifulSoup(strResultado, features="html.parser")
    
    # Buscamos todos los registros de apartamentos haciendo una busqieda por clase de etiqueda li
    registros = soup.find_all('li', {'class' : 'EIR5N'})

    if registros is None:
        return None, "No se encontraron registros de apartamentos para la clase (EIR5N) mencionada"

    # Establecemos el registro minimo
    if(intRegistroMin < len(registros) - 1):
        registros = registros[intRegistroMin:len(registros)]

    # Recortamos los registros a la cantidad limite
    if(len(registros) > intCantidadLimiteRegistros):
        registros = registros[0:(intCantidadLimiteRegistros - 1)]

    # Calculamos la cantidad de paginas a utilizar
    intPaginas = math.ceil(len(registros) / intRegistosPorPagina)
    
    # Para devolver la cantidad de registros totales
    intRegistrosTotales = 0

    for pagina in range(1, 2): #intPaginas):

        print("Pagina #" + str(pagina)) 

        # Se obtienen los limites para obtener los subregistros de pagina
        intLimiteInicial = (pagina - 1) * intRegistosPorPagina
        intLimiteFinal = intLimiteInicial + intRegistosPorPagina
        if(intLimiteFinal > len(registros) - 1):
            intLimiteFinal = len(registros)
            
        # Se obtienen los subregistros y se procesan las consultas
        listaSubRegistros = registros[intLimiteInicial:intLimiteFinal]
        listaRegistrosEncontrados = obtenerRegistros(intCantidadLimiteRegistros, listaSubRegistros)

        # Se verifica si se obtuvieron registros de respuesta para procesarlos a base de datos
        if(len(listaRegistrosEncontrados) > 0):
            print("La cantidad de registros obtenidos: " + str(len(listaRegistrosEncontrados)))
            intRegistrados = localdb.DBController.registrarDatosScrapping(listaRegistrosEncontrados)

            # Aumentamos el valor de registros totales
            intRegistrosTotales += intRegistrados

    
    return intRegistrosTotales, None

def main():
    
    # Especificando la fecha actual para realizar scrapping
    dateFechaActual = date.today()

    dfRegistros, strError = localdb.DBController.obtenerUrlScrapping(dateFechaActual)

    if(dfRegistros is None or len(dfRegistros) == 0):
        localdb.DBController.registrarAccion(AccionSistema.WARNING.name, "No se pudieron obtener los registros de URL para scraping. [Scrapping.py | main]. " + str(strError))
        exit()

    # Iteramos por cada registro encontrado de URL
    for index, registro in dfRegistros.iterrows():

        # Obtenemos valores de cada campo
        idUrlScrapping = registro['idurlscrapping']
        strUrlScrapping = registro['urlscrapping']
        intCantidadLimiteRegistros = registro['cantidadlimiteregistros']
        intNumeroClics = registro['numeroclics']
        intRegistrosXPagina = registro['registrosxpagina']
        intRegistrosMin = registro['registrosmin']

        # Ejecutamos el proceso de scrapping por cada registro de URL.
        intCantidadRegistros, strError = ejecutarScrapping(strUrlScrapping, intNumeroClics, intCantidadLimiteRegistros, intRegistrosXPagina, intRegistrosMin)

        # Actualizamos los registros
        if(strError is not None or intCantidadRegistros == 0):
            intCantidadRegistros = 0
        
        # Registro de la cantidad de registros scrappeados para la URL
        blnResultado, strError = localdb.DBController.actualizarLogScrapping(dateFechaActual, idUrlScrapping, intCantidadRegistros)

        # Verificamos si se actualizo el registro para log de scrapping
        if(blnResultado == False or strError is not None):
            localdb.DBController.registrarAccion(AccionSistema.ERROR.name, "Para IdUrlScrapping " + str(idUrlScrapping) + " no se pudo registrar la cantidad de registros. [Scrapping.py | main]. " + str(strError))
        else:
            localdb.DBController.registrarAccion(AccionSistema.SCRAPPING.name, "Para IdUrlScrapping " + str(idUrlScrapping) + " se completo el proceso de scrapping. [Scrapping.py | main]. ")


main()