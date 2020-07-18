
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(shinydashboard)

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
                box(title = "Caractersiticas", width = 6, solidHeader = TRUE, status = "primary", "Caracteristicas"),
                valueBox("Q15,000.00", "Precio", width = 2, icon = icon("credit-card"))
              )
      )
      
      
    )
  )
)
