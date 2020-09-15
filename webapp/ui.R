
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(shinydashboard)
library(shinyWidgets)
library(leaflet)
library(shinyjs)

ui <- dashboardPage(skin = "green",
  dashboardHeader(title = "UVG"),
  
  dashboardSidebar(
    sidebarMenu(
      menuItem("Dashboard", tabName = "dashboard", icon = icon("tachometer-alt")),
      menuItem("Prediccion Precio", tabName = "prediccion_precio", icon = icon("calculator")),
      menuItem("Comparacion OLX", tabName = "comparacion_olx", icon=icon("search")),
      menuItem("Configuraciones", tabName = "configuraciones", icon = icon("user-cog"))
    )
  ),
  
  dashboardBody(
    tabItems(
      
      tabItem(tabName = "dashboard", 
              fluidRow(width = 12,
                       
                       box(title = "Registros por mes", width = 6, align = "center",  solidHeader = TRUE, status = "primary",
                           plotOutput("dateCountsPlot")
                       ),
                       
                       box(title = "Precios promedios", width = 6, align = "center",  solidHeader = TRUE, status = "primary",
                           plotOutput("averagePricePlot")
                       )
                       
              )),
      
      tabItem(tabName = "prediccion_precio",
              fluidRow(width = 12, align = "center",
                column(12, align = "center",
                       box(title = "Caractersiticas", width = 12, align = "center",  solidHeader = TRUE, status = "primary", 
                           
                           
                           column(4, align = "left", 
                                  numericInput("espacio_m2", h3("Area (metros cuadrados)"), value = 25, min = 0),
                                  radioButtons("moneda", h3("Moneda Venta"), choices = list("Dolar" = 1, "Quetzales" = 2), selected = 1)),
                           
                           column(4, align = "left", 
                                  numericInput("habitaciones", h3("Habitaciones"), value = 2, min = 0),
                                  radioButtons("parqueo", h3("Parqueo"), choices = list("Si" = 1, "No" = 2), selected = 1)),
                           
                           column(4, align = "left", 
                                  numericInput("banos", h3("Baños"), value = 2, min = 0),
                                  radioButtons("vendedor", h3("Tipo Vendedor"), choices = list("Dueño Directo" = 1, "Inmobiliaria" = 2), selected = 1))
                           
                           
                           
                       ))
                
              ),
              
              fluidRow(
                box(title = "Ubicacion", width = 6, align = "center",  solidHeader = TRUE, status = "primary",
                    leafletOutput("predictionMap")
                ),
                
                box(title = "Resultados", width = 6, align = "center",  solidHeader = TRUE, status = "primary",
                    
                    column(6, align = "left", htmlOutput("seleccion_variables")),
                    
                    column(6, align = "center", 
                           valueBoxOutput("precio", width = 12),
                           actionBttn(
                             inputId = "calcular",
                             label = "Calcular Precio",
                             color = "primary",
                             style = "bordered",
                             size = "md"
                           )))
              )
      ),
      
      
      tabItem(tabName = "comparacion_olx",
              useShinyjs(),
              fluidRow(
                
                box(title = "Caracteristicas", width = 12, solidHeader = TRUE, status = "primary", 
                     
                    
                    fluidRow(width = 12, 
                             
                             column(8, textInput("urlApartamento", h3("Direccion URL (OLX)"), value = "")),
                             
                             column(4, align = "center", 
                                    actionBttn( inputId = "btnScrapping",
                                      label = "Obtener Datos",
                                      color = "primary",
                                      style = "bordered",
                                      size = "md"
                             ))),
                    
                    fluidRow(width = 12,
                             
                             disabled(column(4, 
                                    numericInput("olxEspacio", h3("Area (metros cuadrados)"), value = 25, min = 0),
                                    radioButtons("olxMoneda", h3("Moneda"), choices = list("Dolar" = 1, "Quetzales" = 2), selected = 1)),
                             
                             column(4, 
                                    numericInput("olxHabitaciones", h3("Habitaciones"), value = 2, min = 0),
                                    radioButtons("olxParqueo", h3("Parqueo"), choices = list("Si" = 1, "No" = 2), selected = 1)),
                             
                             column(4, 
                                    numericInput("olxBanos", h3("Baños"), value = 2, min = 0),
                                    radioButtons("olxVendedor", h3("Tipo Vendedor"), choices = list("Dueno Directo" = 1, "Inmobiliaria" = 2), selected = 1))
                             )))),
              
              
              
              fluidRow(width = 12, 
                       box(title = "Ubicacion", width = 6, align = "center",  solidHeader = TRUE, status = "primary",
                           disabled(leafletOutput("olxMap"))),
                       
                       box(title = "Resultados", width = 6, align = "center",  solidHeader = TRUE, status = "primary",
                           
                           column(6, align = "left", htmlOutput("seleccion_variables2")),
                           
                           column(6, align = "center", 
                                  
                                  valueBoxOutput("olxPrecio", width = 12),
                                  
                                  valueBoxOutput("predictionPrecio", width = 12)),
                           
                           column(12, align = "center", actionBttn(
                             inputId = "btnComparar",
                             label = "Calcular Precio",
                             color = "primary",
                             style = "bordered",
                             size = "md"
                           ))))
      
))))
