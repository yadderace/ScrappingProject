
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(httr)
library(leaflet)

shinyServer(function(input, output) {
  
  valores <- reactiveValues()
  
  valores$coordenadas <- NULL
  
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
    
    parqueo <- ifelse(parqueo == 1, 1, 0)
    
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
    
    url <- "http://127.0.0.1:5000/predict"
    
    
    res <- POST(url, body = parms, encode = "json")
    
    precio <- round(as.numeric(content(res, "text")), digits = 0)
    
    strSimbolo <- "Q"
    if(moneda_d == 1){
      precio <- precio / 7.69
      strSimbolo <- "US$"
    }
    strPrecio <- paste(strSimbolo, formatC(precio, format = "d", big.mark = ","), sep = "")
    
    output$precio <- renderValueBox({valueBox(strPrecio, 
                                              "Precio", width = 2, icon = icon("credit-card"))})
    
  })
  
  output$mymap <- renderLeaflet({
    
  # Centre the map in the middle of Toronto
  leaflet() %>% addProviderTiles("CartoDB.Positron") %>% 
    #fitBounds(160, -30, 185, -50) %>%
    setView(lng = -90.5069, 
            lat = 14.6349, 
            zoom = 12) %>%
    addMarkers(lng = -90.5069, lat = 14.6349)
  })
  
  observeEvent(input$mymap_click, {
    click <- input$mymap_click
    if(!is.null(click))
      leafletProxy("mymap") %>%
      setView(lng = click$lng, lat = click$lat, zoom = 12) %>%
      clearMarkers() %>%
      addMarkers(lng = click$lng, lat = click$lat)
    
    isolate(
      valores$coordenadas <- list(lat = click$lat, lng = click$lng)
    );
      
  })
  
})
