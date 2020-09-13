
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(shinydashboard)
library(shinyWidgets)
library(leaflet)

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
              
              fluidRow(
                  box(title = "URL", width = 6, solidHeader = TRUE, status = "primary",
                      textInput("urlApartamento", label = "", value = ""),
                      actionButton("btnComparar", "Comparar")),
                  
                  valueBoxOutput("olxPrecio", width = 3),
                  
                  valueBoxOutput("predictionPrecio", width = 3)),
              
              
              fluidRow(
                box(title = "Caracteristicas", width = 4, solidHeader = TRUE, status = "primary", 
                           numericInput("olxEspacio", h2("Espacio (m2)"), value = 25, min = 0),
                           numericInput("olxHabitaciones", h2("Habitaciones"), value = 2, min = 0),
                           numericInput("olxBanos", h2("Banos"), value = 2, min = 0),
                           radioButtons("olxMoneda", h3("Moneda"), choices = list("Dolar" = 1, "Quetzales" = 2), selected = 1),
                           radioButtons("olxParqueo", h3("Parqueo"), choices = list("Si" = 1, "No" = 2), selected = 1),
                           radioButtons("olxVendedor", h3("Tipo Vendedor"), choices = list("Dueno Directo" = 1, "Inmobiliaria" = 2), selected = 1)),
              
                box(title = "Ubicacion", width = 6, solidHeader = TRUE,
                      leafletOutput("olxMap"))
              ))
      
      
    )
  )
)
