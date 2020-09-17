
library(shiny)
library(httr)
library(leaflet)
library(ggplot2)
library(lubridate)
library(dplyr)
library(scales)

source('utility/CommonFunctions.R')

shinyServer(function(input, output, session) {
  
  
  valores <- reactiveValues()
  
  valores$coordenadas <- NULL
  
  
  # ==================================================================
  # [Funciones]
  
  # [Fnc0]: Funcion para inicializar valores y renderizados
  fncInit <- function(){
    # Inicializadores de precio
    output$precio <- renderValueBox({valueBox("Q0.00", "Precio Razonable", width = 2, icon = icon("credit-card"))})
    output$olxPrecio <- renderValueBox({valueBox("Q0.00", "Precio Olx", width = 3, icon = icon("credit-card"), color = "green")})
    output$predictionPrecio <- renderValueBox({valueBox("Q0.00", "Precio Razonable", width = 3, icon = icon("credit-card"))})
    
    fncObtenerRegistros()
    fncObtenerInfoModelo()
  }
  
  # [Fnc1]: Function para limpiar todos los marker y agregar uno al mapa.
  fncAgregarMarkMapa <- function(strNombreMapa, latitud, longitud){
    
    leafletProxy(strNombreMapa) %>%
      setView(lng = longitud, lat = latitud, zoom = 12) %>%
      clearMarkers() %>%
      addMarkers(lng = longitud, lat = latitud)
    
  }
  
  
  # [Fnc2]: Funcion que consulta los datos que son utilizados para generar las graficas de dashboard
  fncObtenerRegistros <- function(){
    
    # Obteniendo direccion URL
    urlApi <- fncObtenerRutaAccionAPI("DATA")
    
    # Generando parametros
    params <- data.frame(fechaFinal = format(Sys.Date(), "%Y-%m-%d"), fechaInicial = format(Sys.Date() - 365, "%Y-%m-%d"))
    
    # Ejecucion de la peticion
    res <- NULL
    withProgress(message = 'Consultando datos', detail = 'Esto puede tomar un tiempo...',  {
      # Ejecucion de peticion
      res <- POST(urlApi, body = params, encode = "json", parse_to_json = TRUE)
    })
    
    if(is.null(res))
      return(NULL)
    
    # Se obtienen los resultados del JSON
    jsonResp <- content(res, as = "parsed")
    dfRegistros <- fncTransformarRegistros(jsonResp)
    
    isolate(
      valores$dfRegistros <- dfRegistros
    );
    
  }
  
  # [Fnc3]: Funcion que se encarga de transformar el resultado JSON en un dataframe
  fncTransformarRegistros <- function(jsonRegistros){
    
    dfRegistros <- NULL
    
    dfRegistros <- data.frame(do.call(rbind, lapply(jsonRegistros, rbind)))
    
    dfRegistros$fechacreacion <- as.POSIXct(as.numeric(dfRegistros$fechacreacion)/1000, origin="1970-01-01", tz = "UTC")
    dfRegistros$fecharegistro <- as.POSIXct(as.numeric(dfRegistros$fecharegistro)/1000, origin="1970-01-01", tz = "UTC")
    dfRegistros$validohasta <- as.POSIXct(as.numeric(dfRegistros$validohasta)/1000, origin="1970-01-01", tz = "UTC")
    
    
    return(dfRegistros)
  }
  
  # [Fnc4]: Funcion que se encarga de consultar la info de modelo
  fncObtenerInfoModelo <- function(){
    
    # Obteniendo direccion URL
    urlApi <- fncObtenerRutaAccionAPI("MODEL_INFO")
    
    # Ejecucion de la peticion
    res <- NULL
    withProgress(message = 'Consultando datos', detail = 'Esto puede tomar un tiempo...',  {
      # Ejecucion de peticion
      res <- POST(urlApi, encode = "json", parse_to_json = TRUE)
    })
    
    if(is.null(res))
      return(NULL)
    
    # Se obtienen los resultados del JSON
    jsonResp <- content(res, as = "parsed")
    
    dfInfoModelo <- data.frame(do.call(rbind, lapply(jsonResp, rbind)))
    
    isolate(valores$dfInfoModelo <- dfInfoModelo);
    
  }
  
  fncObtenerValoresScrapping <- function(listaScrapping){
    
    listaResultado = list(
      TIPO = NULL, HABITACIONES = NULL, BANOS = NULL,
      ESPACIO_M2 = NULL, PARQUEO = NULL, PRECIO = NULL,
      MONEDA = NULL, LATITUDE = NULL, LONGITUDE = NULL
      
    )
    
    dfRegistros <- data.frame(do.call(rbind, lapply(listaScrapping, rbind)))
    
    for (registro in 1:nrow(dfRegistros)){
      strCampo = dfRegistros[registro, "campo"]
      strValor = dfRegistros[registro, "valor"]
      
      if(strCampo == "Tipo")
        listaResultado["TIPO"] = toupper(strValor)
      
      else if(strCampo == "Habitaciones")
        listaResultado["HABITACIONES"] = as.numeric(strValor)
      
      else if(strCampo == "Baños")
        listaResultado["BANOS"] = as.numeric(strValor)
      
      else if(strCampo == "Metros Cuadrados Totales")
        listaResultado["ESPACIO_M2"] = as.numeric(str_extract(strValor,"([0-9]*[.])?[0-9]+"))
      
      else if(strCampo == "Parqueadero")
        listaResultado["PARQUEO"] = ifelse(toupper(strValor) == "SI", TRUE, FALSE)
      
      else if(strCampo == "Precio"){
        listaResultado["PRECIO"] = as.numeric(str_extract(gsub(",", "", strValor),"([0-9]*[.])?[0-9]+"))
        listaResultado["MONEDA"] = str_extract(strValor,"[A-Z]+")
      }
      
      else if(strCampo == "Latitude")
        listaResultado["LATITUDE"] = as.numeric(strValor)
      
      
      else if(strCampo == "Longitude")
        listaResultado["LONGITUDE"] = as.numeric(strValor)
      
      
      else if(strCampo == "Tipo de vendedor")
        listaResultado["INMOBILIARIA"] = ifelse(toupper(strValor) == "INMOBILIARIA", TRUE, FALSE)
      
    }
    
    
    return(listaResultado)
    
  }
  
  fncInit()
  
  # =================================================================
  # [Renderizado mapas]
  
  output$predictionMap <- renderLeaflet({
    
  # Centre the map in the middle of Toronto
  leaflet() %>% addProviderTiles("CartoDB.Positron") %>% 
    #fitBounds(160, -30, 185, -50) %>%
    setView(lng = -90.5069, 
            lat = 14.6349, 
            zoom = 12) %>%
    addMarkers(lng = -90.5069, lat = 14.6349)
  })
  
  
  output$olxMap <- renderLeaflet({
    
    # Centre the map in the middle of Toronto
    leaflet() %>% addProviderTiles("CartoDB.Positron") %>% 
      #fitBounds(160, -30, 185, -50) %>%
      setView(lng = -90.5069, 
              lat = 14.6349, 
              zoom = 12) %>%
      addMarkers(lng = -90.5069, lat = 14.6349)
  })
  
  # =================================================================
  # [Renderizado graficas]
  
  output$dateCountsPlot <- renderPlot({
    
    # No renderiza grafica si no hay datos
    if(is.null(valores$dfRegistros))
      return(NULL)
    
    # Filtro de columnas
    registros <- valores$dfRegistros[,c('fechacreacion','idregistro')]
    registros <- unique(registros)
    
    # Creacion de grafica
    g <- ggplot(registros) + 
      aes(x = floor_date(fechacreacion, "month")) + 
      xlab("Mes") +
      ylab("Cantidad Registros") +
      geom_bar(fill = "steelblue") +
      theme_bw()
    
    return(g)
  })
  
  
  output$averagePricePlot <- renderPlot({
    
    # No renderiza grafica si no hay datos
    if(is.null(valores$dfRegistros))
      return(NULL)
    
    registros <- valores$dfRegistros[,c('fechacreacion', 'precio', 'moneda')]
    
    registros$moneda <- as.character(registros$moneda)
    registros$precio <- as.numeric(registros$precio)
    registros <- registros %>% group_by(fechacreacion, moneda) %>% summarise(precio_mean = mean(precio))
    
    # Creacion de grafica
    g <- ggplot(registros) + 
      aes(x = fechacreacion, y = precio_mean, color = moneda) + 
      ylab("Precio Promedio") +
      scale_y_continuous(labels = comma) +
      xlab("Fecha Registro") +
      geom_smooth(method = "loess", se = FALSE, linetype = "dashed") +
      theme_bw()
    
    return(g)
  })
  
  
  output$records <- renderInfoBox({
    # No renderiza valor si no hay datos
    if(is.null(valores$dfRegistros))
      return(NULL)
    
    infoBox(
      "Registros", as.character(nrow(valores$dfRegistros)), icon = icon("list"),
      color = "blue", fill = TRUE, width = 3
    )
  })
  
  
  output$lastupdate <- renderInfoBox({
    # No renderiza valor si no hay datos
    if(is.null(valores$dfRegistros))
      return(NULL)
    
    infoBox(
      "FECHA ACTUALIZACIÓN", as.character(max(valores$dfRegistros$fechacreacion)), icon = icon("calendar"),
      color = "blue", fill = TRUE, width = 3
    )
  })
  
  
  output$accuracy <- renderInfoBox({
    # No renderiza valor si no hay datos
    if(is.null(valores$dfInfoModelo))
      return(NULL)
    
    infoBox("R2", 
            paste(as.character(round(as.numeric(valores$dfInfoModelo$r2score[1]) * 100,2)), 
                               "% (", valores$dfInfoModelo$tipomodelo, ")", sep = ""), icon = icon("ruler"),
      color = "navy", fill = TRUE, width = 3
    )
  })
  
  output$predictions <- renderInfoBox({
    # No renderiza valor si no hay datos
    if(is.null(valores$dfInfoModelo))
      return(NULL)
    
    infoBox("Predicciones", valores$dfInfoModelo$predicciones[1], icon = icon("thumbs-up"),
            color = "navy", fill = TRUE, width = 3
    )
  })
  
  #red, yellow, aqua, blue, light-blue, green, navy, teal, olive, lime, orange, fuchsia, purple, maroon, black
  
  # =================================================================
  # [Renderizado de texto]
  
  output$seleccion_variables <- renderText({ 
    strSeleccion <- paste("<b>Espacio:</b> ", input$espacio_m2, "</br>",
                          "<b>Habitaciones:</b> ", input$habitaciones, "</br>",
                          "<b>Baños:</b> ", input$banos, "</br>",
                          "<b>Moneda Venta:</b> ", ifelse(input$moneda == 1, "Dolares", "Quetzales") , "</br>",
                          "<b>Parqueo:</b> ", ifelse(input$parqueo == 1, "Si", "No") , "</br>",
                          "<b>Vendedor:</b> ", ifelse(input$vendedor == 1, "Dueño Directo", "Inmobiliaria") , "</br>",
                          "<b>Latitud:</b> ", as.character(valores$coordenadas$lat) , "</br>",
                          "<b>Longitud:</b> ", as.character(valores$coordenadas$lng) , "</br>",
                          sep = "")
    
    return(strSeleccion)
  })
  
  output$seleccion_variables2 <- renderText({ 
    strSeleccion <- paste("<b>Espacio:</b> ", input$olxEspacio, "</br>",
                          "<b>Habitaciones:</b> ", input$olxHabitaciones, "</br>",
                          "<b>Baños:</b> ", input$olxBanos, "</br>",
                          "<b>Moneda Venta:</b> ", ifelse(input$olxMoneda == 1, "Dolares", "Quetzales") , "</br>",
                          "<b>Parqueo:</b> ", ifelse(input$olxParqueo == 1, "Si", "No") , "</br>",
                          "<b>Vendedor:</b> ", ifelse(input$olxVendedor == 1, "Dueño Directo", "Inmobiliaria") , "</br>",
                          "<b>Latitud:</b> ", as.character(valores$coordenadas$lat) , "</br>",
                          "<b>Longitud:</b> ", as.character(valores$coordenadas$lng) , "</br>",
                          sep = "")
    
    return(strSeleccion)
  })
  
  # =================================================================
  # [Observe Event]
  
  observeEvent(input$predictionMap_click, {
    click <- input$predictionMap_click
    if(!is.null(click))
      
      fncAgregarMarkMapa("predictionMap", click$lat, click$lng)
    
    isolate(
      valores$coordenadas <- list(lat = click$lat, lng = click$lng)
    );
      
  })
  
  
  observeEvent(input$calcular, {
    
    if(is.null(valores$coordenadas))
      return()
    
    
    # Lectura de variables del formulario
    espacio_m2 <- input$espacio_m2
    habitaciones <- input$habitaciones
    banos <- input$banos
    moneda <- input$moneda
    parqueo <- input$parqueo
    tipo_vendedor <- input$vendedor
    
    # Calculo de moneda
    moneda_q = 0
    moneda_d = 0
    if(moneda == 1){ # 1 = Dolar, 2 = Quetzales
      moneda_d = 1
    }else{
      moneda_q = 1
    }
    
    
    # Calculo de vendedor
    tipodueno = 0
    tipoinmobiliaria = 0
    if(tipo_vendedor == 1){ # 1 = Dueno Directo; 2 = Inmobiliaria
      tipodueno = 1
    }else{
      tipoinmobiliaria = 1
    }
    
    # Calculo de valor de parqueo
    parqueo <- ifelse(parqueo == 1, 1, 0)
    
    
    # Creacion de parametro para peticion
    parms <- data.frame(espacio_m2 = espacio_m2,
                        banos = banos,
                        habitaciones = habitaciones,
                        monedaq = moneda_q,
                        monedad = moneda_d,
                        parqueo = parqueo,
                        tipodueno = tipodueno,
                        tipoinmobiliaria = tipoinmobiliaria,
                        longitud = valores$coordenadas$lng,
                        latitud = valores$coordenadas$lat)
    
    # Obteniendo URL de API
    urlApi <- fncObtenerRutaAccionAPI("PREDICT")
    
    res <- NULL
    
    # Ejecucion de peticion POST
    withProgress(message = 'Consultando datos', detail = 'Esto puede tomar un tiempo...',  {
      res <- POST(urlApi, body = parms, encode = "json")
    })
    
    if(is.null(res))
      return(NULL)
    
    # Obtencion de respuesta y desplie en UI
    precio <- round(as.numeric(content(res, "text")), digits = 0)
    strSimbolo <- "Q"
    if(moneda_d == 1){
      precio <- precio / 7.69
      strSimbolo <- "US$"
    }
    strPrecio <- paste(strSimbolo, formatC(precio, format = "d", big.mark = ","), sep = "")
    output$precio <- renderValueBox({valueBox(strPrecio, "Precio Razonable", width = 2, icon = icon("credit-card"))})
    
  })
  
  
  observeEvent(input$btnScrapping, {
    
    # Obteniendo el URL del apartamento
    strUrl <- input$urlApartamento
    
    # Construccion de parametros
    params <- data.frame(url = strUrl)
    
    urlApi <- fncObtenerRutaAccionAPI("SCRAPPING")
    
    res <- NULL
    
    withProgress(message = 'Consultando datos', detail = 'Esto puede tomar un tiempo...',  {
      # Ejecucion de peticion
      res <- POST(urlApi, body = params, encode = "json", parse_to_json = TRUE)
    })
    
    if(is.null(res))
      return(NULL)
    
    jsonResp <- content(res, as = "parsed")
    
    
    # Parseo de valores JSON
    listaValores <- fncObtenerValoresScrapping(jsonResp)
    
    
    # Configurando valores por defecto en caso de scrapping con valores nulos
    
    numEspacioM2 = ifelse(!is.null(listaValores$ESPACIO_M2), listaValores$ESPACIO_M2, 25)
    numHabitaciones = ifelse(!is.null(listaValores$HABITACIONES), listaValores$HABITACIONES, 2)
    numBanos = ifelse(!is.null(listaValores$BANOS), listaValores$BANOS, 2)
    
    strMoneda = ifelse(!is.null(listaValores$MONEDA), listaValores$MONEDA, "Q")
    blnParqueo = ifelse(!is.null(listaValores$PARQUEO), listaValores$PARQUEO, TRUE)
    blnInmobiliaria = ifelse(!is.null(listaValores$INMOBILIARIA), listaValores$INMOBILIARIA, TRUE)
    
    
    # Configurando valores para controles UI
    
    updateTextInput(session, "olxEspacio", value = numEspacioM2)
    updateTextInput(session, "olxHabitaciones", value = numHabitaciones)
    updateTextInput(session, "olxBanos", value = numBanos)
    
    updateRadioButtons(session, "olxMoneda", selected = ifelse(strMoneda == "Q", 2, 1))
    updateRadioButtons(session,"olxParqueo", selected = ifelse(blnParqueo, 1, 2))
    updateRadioButtons(session, "olxVendedor", selected = ifelse(blnInmobiliaria, 2, 1))
    
    
    # Actualizando mapa de ubicacion
    if(!is.null(listaValores$LATITUD) && !is.null(listaValores$LONGITUD)){
      fncAgregarMarkMapa("olxMap", longitud = listaValores$LONGITUD, latitud = listaValores$LATITUD)
      isolate(
        valores$coordenadas <- list(lat = listaValores$LATITUD, lng = listaValores$LONGITUD)
      );
    }
    
    # Agregando precio de OLX
    # Obtencion de respuesta y desplie en UI
    precioOlx <- round(as.numeric(listaValores$PRECIO), digits = 0)
    strSimbolo <- ifelse(strMoneda != "Q", "US$", "Q")
    strPrecio <- paste(strSimbolo, formatC(precioOlx, format = "d", big.mark = ","), sep = "")
    output$olxPrecio <- renderValueBox({valueBox(strPrecio, "Precio OLX", width = 3, icon = icon("credit-card"), color = "green")})
    
  })
  
  
  observeEvent(input$btnComparar, {
    
    
    # Lectura de variables del formulario
    moneda <- input$olxMoneda
    parqueo <- input$olxParqueo
    tipo_vendedor <- input$olxVendedor
    
    # Calculo de moneda
    moneda_q = 0
    moneda_d = 0
    if(moneda == 1){ # 1 = Dolar, 2 = Quetzales
      moneda_d = 1
    }else{
      moneda_q = 1
    }
    
    
    # Calculo de vendedor
    tipodueno = 0
    tipoinmobiliaria = 0
    if(tipo_vendedor == 1){ # 1 = Dueno Directo; 2 = Inmobiliaria
      tipodueno = 1
    }else{
      tipoinmobiliaria = 1
    }
    
    # Calculo de valor de parqueo
    parqueo <- ifelse(parqueo == 1, 1, 0)
    
    
    # Creacion de parametro para peticion
    parms <- data.frame(espacio_m2 = input$olxEspacio,
                        banos = input$olxBanos,
                        habitaciones = input$olxHabitaciones,
                        monedaq = moneda_q,
                        monedad = moneda_d,
                        parqueo = parqueo,
                        tipodueno = tipodueno,
                        tipoinmobiliaria = tipoinmobiliaria,
                        longitud = valores$coordenadas$lng,
                        latitud = valores$coordenadas$lat)
    
    # Obteniendo URL de API
    urlApi <- fncObtenerRutaAccionAPI("PREDICT")
    
    res <- NULL
    # Ejecucion de peticion POST
    withProgress(message = 'Consultando datos', detail = 'Esto puede tomar un tiempo...',  {
      res <- POST(urlApi, body = parms, encode = "json")
    })
    
    if(is.null(res))
      return(NULL)
    
    # Obtencion de respuesta y desplie en UI
    precio <- round(as.numeric(content(res, "text")), digits = 0)
    
    strSimbolo <- "Q"
    if(moneda_d == 1){
      precio <- precio / 7.69
      strSimbolo <- "US$"
    }
    strPrecioOlx <- paste(strSimbolo, formatC(precio, format = "d", big.mark = ","), sep = "")
    output$predictionPrecio <- renderValueBox({valueBox(strPrecioOlx, "Precio Razonable", width = 2, icon = icon("credit-card"))})
    
    
  })
  
  
})
