
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(httr)

shinyServer(function(input, output) {
  
  observeEvent(input$calcular, {
    
    
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
    if(moneda == "Dolar"){
      moneda_d = 1
    }else{
      moneda_q = 1
    }
    
    
    # Calculo de vendedor
    tipodueno = 0
    tipoinmobiliaria = 0
    if(tipo_vendedor == "Inmobiliaria"){
      tipoinmobiliaria = 1
    }else{
      tipodueno = 1
    }
    
    parqueo <- ifelse(parqueo == "Si", 1, 0)
    
    parms <- data.frame(espacio_m2 = espacio_m2,
                  banos = banos,
                  habitaciones = habitaciones,
                  monedaq = moneda_q,
                  monedad = moneda_d,
                  parqueo = parqueo,
                  tipodueno = tipodueno,
                  tipoinmobiliaria = tipoinmobiliaria)
    
    url <- "http://127.0.0.1:5000/predict"
    
    print("Hola")
    
    precio <- POST(url, body = parms, encode = "json")
    
    print(precio)
    
    
  })
  
})
