library(stringr)


# ======================================================== [ fncObtenerRutaAccionAPI ]
# Obtiene la ruta adecuada a consultar en API

fncObtenerRutaAccionAPI <- function(strAccion){
  
  strUrlBase <- "http://127.0.0.1:5000/"
  
  if(toupper(strAccion) == "PREDICT"){
    strUrlBase <- paste(strUrlBase, "/predict", sep = "")
  }
  else if(toupper(strAccion) == "SCRAPPING"){
    strUrlBase <- paste(strUrlBase, "/scrapping", sep = "")
  }
  else if(toupper(strAccion) == "DATA"){
    strUrlBase <- paste(strUrlBase, "/data", sep = "")
  }
  else if(toupper(strAccion) == "MODEL_INFO"){
    strUrlBase <- paste(strUrlBase, "/model_info", sep = "")
  }else{
    strUrlBase <- NULL
  }
  
  return(strUrlBase)
  
}


# ======================================================== [ fncObtenerRutaAccionAPI ]
# Convierte el listado de valores obtenidos en API a un listado que se puede utilizar en R
fncObtenerValoresScrapping <- function(listaScrapping){
  
  listaResultado = list(
    TIPO = NULL, HABITACIONES = NULL, BANOS = NULL,
    ESPACIO_M2 = NULL, PARQUEO = NULL, PRECIO = NULL,
    MONEDA = NULL, LATITUDE = NULL, LONGITUDE = NULL
    
  )
  
  # Verificar cada elemento del scrapping
  for(elemento in listaScrapping){
    
    if(elemento$campo == "Tipo")
      listaResultado["TIPO"] = toupper(elemento$valor)
    
    else if(elemento$campo == "Habitaciones")
      listaResultado["HABITACIONES"] = as.numeric(elemento$valor)
    
    else if(elemento$campo == "Baños")
      listaResultado["BANOS"] = as.numeric(elemento$valor)
    
    else if(elemento$campo == "Metros Cuadrados Totales")
      listaResultado["ESPACIO_M2"] = as.numeric(str_extract(elemento$valor,"([0-9]*[.])?[0-9]+"))
    
    else if(elemento$campo == "Parqueadero")
      listaResultado["PARQUEO"] = ifelse(toupper(elemento$valor) == "SI", TRUE, FALSE)
    
    else if(elemento$campo == "Precio"){
      listaResultado["PRECIO"] = as.numeric(str_extract(gsub(",", "", elemento$valor),"([0-9]*[.])?[0-9]+"))
      listaResultado["MONEDA"] = str_extract(elemento$valor,"[A-Z]+")
    }
    
    else if(elemento$campo == "Latitude")
      listaResultado["LATITUDE"] = as.numeric(elemento$valor)
    
    
    else if(elemento$campo == "Longitude")
      listaResultado["LONGITUDE"] = as.numeric(elemento$valor)
    
    
    else if(elemento$campo == "Tipo de vendedor")
      listaResultado["INMOBILIARIA"] = ifelse(toupper(elemento$valor) == "INMOBILIARIA", TRUE, FALSE)
    
  }
  
  
  
  return(listaResultado)
  
}