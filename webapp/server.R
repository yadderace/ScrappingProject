
library(shiny)
library(httr)
library(leaflet)

source('utility/CommonFunctions.R')

shinyServer(function(input, output, session) {
  
  
  valores <- reactiveValues()
  
  valores$coordenadas <- NULL
  
  
  # ==================================================================
  # [Funciones]
  
  # [Fnc0]: Funcion para inicializar valores y renderizados
  fncInit <- function(){
    # Inicializadores de precio
    output$precio <- renderValueBox({valueBox("Q0.00", "Precio Sugerido", width = 2, icon = icon("credit-card"))})
    output$olxPrecio <- renderValueBox({valueBox("Q0.00", "Precio Olx", width = 3, icon = icon("credit-card"), color = "green")})
    output$predictionPrecio <- renderValueBox({valueBox("Q0.00", "Precio Sugerido", width = 3, icon = icon("credit-card"))})
  }
  fncInit()
  
  # [Fnc1]: Function para limpiar todos los marker y agregar uno al mapa.
  fncAgregarMarkMapa <- function(strNombreMapa, latitud, longitud){
    
    leafletProxy(strNombreMapa) %>%
      setView(lng = longitud, lat = latitud, zoom = 12) %>%
      clearMarkers() %>%
      addMarkers(lng = longitud, lat = latitud)
    
  }
  
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
    output$precio <- renderValueBox({valueBox(strPrecio, "Precio Sugerido", width = 2, icon = icon("credit-card"))})
    
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
    output$predictionPrecio <- renderValueBox({valueBox(strPrecioOlx, "Precio Sugerido", width = 2, icon = icon("credit-card"))})
    
    
  })
  
  
})
