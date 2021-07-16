# install.packages('shiny')

library(shiny)

# Define UI for data upload app ----
ui <- fluidPage(
  
  titlePanel("Parse samplesheet for spaceranger analysis"),
  sidebarLayout(
    sidebarPanel(
      # Input: Select a file ----
      fileInput("file1", "Choose tab-delimited file:",
                multiple = F,
                accept = c(".tsv",
                           ".txt")),
      
      tags$hr(),
      
      #Input: Select number of rows to display ----
      radioButtons("disp", "Display",
                   choices = c(Head = "head",
                               All = "all"),
                   selected = "head"),
      tags$hr(),
      strong('Required column headers:'),
      tags$ul(style = "list-style-position: outside;padding-left: 2em;",
        tags$li("sample"), 
        tags$li("index"),
        tags$li("fastq"),
        tags$li("genome",
          tags$ul(style = "list-style-position: inside; padding-left: 0",
            tags$li("mm10 (mouse)"),
            tags$li("GRCh38 (human)"),
            tags$li("GRCh38_mm10 (both)"))),
        tags$li("slide"),
        tags$li("area"),
        tags$li("image*")
      ),
      strong('Optional columns:'),
      tags$ul(
        tags$li("lane (defaults to all)"), 
        tags$li("description")
      ),
      "*Note: Please place slide serial.gpr files in same directory as the image files."
    ),
    
    
    mainPanel(
      tableOutput("contents"),
      htmlOutput("parse")
    )
  )
)

server <- function(input, output) {
  
  output$contents <- renderTable({
  
    req(input$file1)
    ext <- tools::file_ext(input$file1$datapath)
    validate(need(ext == "txt" | ext == "tsv", "Please upload a text file (*.txt or *.tsv)"))
    
    df <- read.delim(input$file1$datapath)
    df <- data.frame('#' = 1:nrow(df),df,check.names=F)
    
    if(input$disp == "head") {
      return(head(df))
    }
    else {
      return(df)
    }
    
  })
  
  runcommand <- reactiveValues(out = '')
  observeEvent(input$file1,{

    ext <- tools::file_ext(input$file1$datapath)
    validate(need(ext == "txt" | ext == "tsv", "Please upload a text file (*.txt or *.tsv)"))
    
    inputFileName = sub('.tsv','',sub('.txt','',basename(input$file1$name)))
    inputFilePath = input$file1$datapath
    # runcommand$out <- system(paste('python /SFS/project/shinyapps/ctchpcvashy005/open/R363/tsoij/parse_samplesheet/parse_samplesheet_shiny.py',inputFilePath,inputFileName,sep=" "), intern=T)
    runcommand$out <- system(paste('python parse_samplesheet.py',inputFilePath,inputFileName,sep=" "), intern=T)
    
  })
  
  output$parse <- renderText({
    runcommand$out
    
  })
}

# Create Shiny app ----
shinyApp(ui, server)
