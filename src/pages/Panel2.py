import dash_ag_grid as dag
import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.colors as colors
from dash_bootstrap_templates import load_figure_template
from . import ModDatosLogisticos as mdl

df_presupuesto = mdl.dataframe_presupuesto()

# Tiempo en horas
df_presupuesto['tiempo_hrs'] = round(df_presupuesto['tiempo_min'] / 60,2)
# Redondeamos Costos
df_presupuesto['costo_caseta'] = df_presupuesto['costo_caseta'].round(2)
df_presupuesto['costo_por_camion'] = df_presupuesto['costo_por_camion'].round(2)
df_presupuesto['costo_total'] = df_presupuesto['costo_total'].round(2)

### Primer Grafico ###
### Primer Grafico ###
### Primer Grafico ###
### Primer Grafico ###

### Grafico de Barras ###

### Promedio de Costo ####
promedio_costo = df_presupuesto["costo_total"].mean()

# Definir los colores base
verde = "#00ff00"
amarillo = "#ffff00"
rojo = "#ff0000"

# Crear la paleta de colores continua
paleta_continua = colors.make_colorscale([verde, amarillo, rojo])

# Grafico de Barras
grafico1 = px.bar(df_presupuesto,y='costo_total',x='pto_dist',title=f"Costos Totales por Ciudad de Destino",template=load_figure_template('bootstrap_dark'),labels={'pto_dist':'Ciudad', 'costo_total':'Costo Total'},
                  color='costo_total',color_continuous_scale=paleta_continua,color_continuous_midpoint=promedio_costo)

### Segundo Grafico ###
### Segundo Grafico ###
### Segundo Grafico ###
### Segundo Grafico ###

### Promedio de Costo ####
promedio_costo_por_camion = df_presupuesto["costo_por_camion"].mean()

# Grafico de Barras
grafico2 = px.bar(df_presupuesto,y='costo_por_camion',x='pto_dist',title="Costos por Camión por Ciudad de Destino",template=load_figure_template('bootstrap_dark'),labels={'pto_dist':'Ciudad', 'costo_por_camion':'Costo por Camión'},
                  color='costo_por_camion',color_continuous_scale=paleta_continua,color_continuous_midpoint=promedio_costo_por_camion)


### Tercer Grafico ###
### Tercer Grafico ###
### Tercer Grafico ###
### Tercer Grafico ###

### Promedio de Costo de Caseta ####
promedio_caseta = df_presupuesto['costo_caseta'].mean()

# Definir los colores base
verde = "#00ff00"
amarillo = "#ffff00"
rojo = "#ff0000"

# Crear la paleta de colores continua
paleta_continua = colors.make_colorscale([verde, amarillo, rojo])

grafico3 = px.scatter(
        df_presupuesto, x='long_km', y='costo_caseta', 
        color='costo_caseta', size='num_camiones',
        hover_data=['pto_dist','long_km','costo_caseta','num_camiones'], title='Costo de Caseta por Punto de Distribución',
        color_continuous_scale=paleta_continua,
        color_continuous_midpoint=promedio_caseta,
        labels={'pto_dist':'Destino','long_km':'Longitud','costo_caseta':'Casetas','num_camiones':'Camiones'})
grafico3.update_layout(xaxis_title="Longitud Km", yaxis_title="Costo de Casetas")


### Cuarto Grafico ###
### Cuarto Grafico ###
### Cuarto Grafico ###
### Cuarto Grafico ###

### Promedio de Costo por Camión ####
promedio_por_camion = df_presupuesto['costo_por_camion'].mean()

grafico4 = px.scatter(
        df_presupuesto, x='long_km', y='costo_por_camion',
        color='costo_por_camion', size='num_camiones',
        hover_data=['pto_dist','long_km','costo_por_camion','num_camiones'], title='Costo por Camión por Punto de Distribución',
        color_continuous_scale=paleta_continua,
        color_continuous_midpoint=promedio_por_camion,
        labels={'pto_dist':'Destino','long_km':'Longitud','costo_por_camion':'Costo','num_camiones':'Camiones'})
grafico4.update_layout(xaxis_title="Longitud Km", yaxis_title="Costo de Casetas")

### Grafico de Barra ###
grafico_barra_1 = dcc.Graph(id="asset-allocation-1",figure=grafico1,style={'height':'41vh'})
grafico_barra_2 = dcc.Graph(id="asset-allocation-2",figure=grafico2,style={'height':'41vh'})
grafico_barra_3 = dcc.Graph(id="asset-allocation-3",figure=grafico3,style={'height':'41vh'})
grafico_barra_4 = dcc.Graph(id="asset-allocation-4",figure=grafico4,style={'height':'41vh'})

### Grafico 5 ###
### Grafico 5 ###
### Grafico 5 ###
### Grafico 5 ###

colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']

grafico5 = go.Figure(data=[go.Pie(labels=df_presupuesto['pto_dist'], values=df_presupuesto['costo_total'])])
grafico5.update_traces(
    hoverinfo=['label+percent'],
    textinfo='percent',
    textfont_size=20,
    textposition='outside',  # Coloca el texto por fuera del gráfico
    outsidetextfont=dict(size=20),  # Personaliza el formato del texto fuera del gráfico
    marker=dict(colors=colors, line=dict(color='#000000', width=2))
)
grafico_pastel = dcc.Graph(id='pie-chart',figure=grafico5,style={'height':'41vh'})

#### Dashboard ####
#### Dashboard ####
#### Dashboard ####
#### Dashboard ####

## Para posteriormente llamar a la app
dash.register_page(__name__)

#### Data Frame Costos ####
#### Data Frame Costos ####
#### Data Frame Costos ####
#### Data Frame Costos ####


### Ordenamos y filtramos el data frame con la información que tendrá la tabla
presupuesto_tabla = pd.DataFrame(df_presupuesto[['pto_dist', 'long_km', 'tiempo_hrs', 'costo_gas', 'costo_caseta', 'costo_por_camion', 'num_camiones', 'costo_total']])

### Nombras y pones caracteristicas a las columnas
columnDefs = [
    {
        "headerName": "Ciudad Destino",
        "field": "pto_dist",
        "filter": True,
    },
    {
        "headerName": "Distancia km",
        "field": "long_km",
        "filter": True,
    },
    {
        "headerName": "Tiempo hrs",
        "field": "tiempo_hrs",
        "editable": True,
        "type": "rightAligned",
    },
    {
        "headerName": "Costo Gasolina",
        "field": "costo_gas",
        "type": "rightAligned",
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
        "cellRenderer": "agAnimateShowChangeCellRenderer",
    },
    {
        "headerName": "Casetas",
        "field": "costo_caseta",
        "type": "rightAligned",
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
        "cellRenderer": "agAnimateShowChangeCellRenderer",
    },
    {
        "headerName": "Costo por Camión",
        "field": "costo_por_camion",
        "type": "rightAligned",
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
        "cellRenderer": "agAnimateShowChangeCellRenderer",
    },
    {
        "headerName": "Camiones",
        "field": "num_camiones",
        "filter": True,
    },
    {
        "headerName": "Costo Total",
        "field": "costo_total",
        "type": "rightAligned",
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
        "cellRenderer": "agAnimateShowChangeCellRenderer",
    }
]

### Caracteristicas default de las columnas
defaultColDef = {
    "filter": "agNumberColumnFilter",
    "resizable": True,
    "sortable": True,
    "editable": False,
    "floatingFilter": True,
    "minWidth": 125,
}

### Esta sera la tabla
grid = dag.AgGrid(
    id="tabla",
    className="ag-theme-alpine-dark",
    columnDefs=columnDefs,
    rowData=presupuesto_tabla.to_dict("records"),
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={"undoRedoCellEditing": True, "rowSelection": "multiple","rowMultiSelectWithClick": False},
    style={'height':'35vh'}
)

### Objetos ###
### Objetos ###
### Objetos ###
### Objetos ###

tabs_barplot = dbc.Card(dbc.Tabs(
    [
        dbc.Tab(grafico_barra_1, label="Costos Totales"),
        dbc.Tab(grafico_barra_2, label="Costos por Camión"),
        dbc.Tab(grafico_pastel, label="Proporción de Costos")
    ]
),body=True)

tabs_scatterplot = dbc.Card(dbc.Tabs(
    [
        dbc.Tab(grafico_barra_3, label="Costo de Caseta por Km"),
        dbc.Tab(grafico_barra_4, label="Costos por Camión por Km")
    ]
),body=True)


### Diseño del Dashboard  (layout) ###
### Diseño del Dashboard  (layout) ###
### Diseño del Dashboard  (layout) ###

layout = dbc.Container(
    [
        dbc.Row([dbc.Col(tabs_barplot,width=6),dbc.Col(tabs_scatterplot,width=6)]),
        dbc.Row(dbc.Col(grid, className="py-4")),
    ],fluid=True
)