from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Url de pagina web
urlBase = "https://www.olx.com.gt"
urlApartamentos = urlBase + "/ciudad-de-guatemala_g4168811/q-apartamentos"
strTextoBoton = "CARGAR MÁS"
timeout = 15
intNumeroClics = 50

driver = webdriver.Chrome()
driver.get(urlApartamentos)
driver.implicitly_wait(timeout)


elements = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))


# Busca el boton de cargar mas.
btnWebElement = None
for element in elements:
    print("->" + str(element.text + "<-"))
    if(str(element.text) == strTextoBoton):
        btnWebElement = element
        break

# Se termina el programa en caso de no encontrarse el boton
if(btnWebElement is None):
    print("No se encontro el boton de cargar mas")
    exit()



for i in range(1, intNumeroClics):
    btnWebElement.click()
    print("Iteracion: " + str(i))


soup = BeautifulSoup(driver.page_source)
registros = soup.find_all('li', {'class' : 'EIR5N'})
print(registros)
print("Cantidad Registros:"+ str(len(registros)))



#while True:
#    try:
#        loadmore = driver.find_elements_by_css_selector("button.rui-3sH3b rui-23TLR rui-1zK8h")
#        loadmore.click()
#        print("Va aqui")
#    except NoSuchElementException:
#        print("Reached bottom of page")
#        break


#soup = BeautifulSoup(driver.page_source,'html.parser')

#for item in soup.find_all('div',class_="variant-tile js-varnt-tile"):
#    links.append(item.find('a')['href'])