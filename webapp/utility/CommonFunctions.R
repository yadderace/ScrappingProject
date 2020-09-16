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
