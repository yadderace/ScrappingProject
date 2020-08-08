
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
  else{
    strUrlBase <- NULL
  }
  
  return(strUrlBase)
  
}