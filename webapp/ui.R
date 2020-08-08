
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(shinydashboard)
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
              fluidRow(
                box(title = "Caractersiticas", width = 4, solidHeader = TRUE, status = "primary", 
                    numericInput("espacio_m2", h2("Espacio (m2)"), value = 25, min = 0),
                    numericInput("habitaciones", h2("Habitaciones"), value = 2, min = 0),
                    numericInput("banos", h2("Banos"), value = 2, min = 0),
                    radioButtons("moneda", h3("Moneda"), choices = list("Dolar" = 1, "Quetzales" = 2), selected = 1),
                    radioButtons("parqueo", h3("Parqueo"), choices = list("Si" = 1, "No" = 2), selected = 1),
                    radioButtons("vendedor", h3("Tipo Vendedor"), choices = list("Dueno Directo" = 1, "Inmobiliaria" = 2), selected = 1),
                    actionButton("calcular", "Calcular")
                    ),
                
                box(title = "Ubicacion", width = 6, solidHeader = TRUE,
                    leafletOutput("mymap")
                    ),
                
                valueBoxOutput("precio")
              )
      ),
      
      
      tabItem(tabName = "comparacion_olx",
              
              fluidRow(box(title = "URL", width = 6, solidHeader = TRUE, status = "primary",
                           
                           textInput("urlApartamento", label = "", value = ""),
                           actionButton("btnComparar", "Comparar")
                           
                           ))
  
              )
      
      
    )
  )
)
