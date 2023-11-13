import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import INEGIpy
import requests
import json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiLineString, Point
import folium
import webbrowser
import dash_canvas
import dash_daq as daq
import time
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import plotly.colors as colors
from dash_bootstrap_templates import load_figure_template

# Data Frame con la información de los Autobuses y sus Destinos
df = pd.read_csv('centro_de_distribucion_puntos.csv')

# Importando la clase ruteo que pertenece a la librería INEGIpy, con token para acceder a la información
ruteo = INEGIpy.Ruteo('kqvCNH1V-keUF-rSVa-O1tf-gdqFN6DynMNN')

# Precio Gasolina Diesel
combustibles = ruteo.Combustibles()
costo = combustibles.loc[2,'costo']


### Base de Datos con Cálculo de Costos ###
### Base de Datos con Cálculo de Costos ###
### Base de Datos con Cálculo de Costos ###

# Coordenada del centro de distribución, que en este caso es MTY
centro_de_distribucion = 'Monterrey, Nuevo León'
buscar = ruteo.BuscarDestino(busqueda=centro_de_distribucion, cantidad=1)

# Linea Inicial del centro de distribucion, parte del proceso para determinar costos
linea_inicial = ruteo.BuscarLinea(lat = buscar['geometry'].y, lng = buscar['geometry'].x)

# Creamos  data frame
df1 = pd.DataFrame()

# Obtener la información de geometría para cada punto de distribucion
for punto in df['punto_de_distribucion'].unique():
    # Geometría de el destino
    geometry = ruteo.BuscarDestino(busqueda=punto, cantidad=1)['geometry']

    # Linea final, no se necesitan datos de aqui
    linea_final = ruteo.BuscarLinea(lat=geometry.y,lng=geometry.x)
    
    # Ruta optima. Ya como data frame
    ruta_optima = ruteo.CalcularRuta(linea_inicial = linea_inicial, linea_final = linea_final, tipo_vehiculo = 2, ruta = 'optima')[['costo_caseta', 'tiempo_min', 'long_km', 'geometry']]
    ruta_optima['costo_gas'] = ruta_optima['long_km'] * costo * .25
    
    geometry = pd.DataFrame(geometry)
    
    concatenado = pd.concat([ruta_optima,geometry], axis=1, ignore_index=True)
    
    concatenado['pto_dist'] = punto
    
    df1 = pd.concat([df1,concatenado], axis=0, ignore_index=True)
    
df1.columns = ['costo_caseta', 'tiempo_min', 'long_km', 'geometry_ruta', 'costo_gas', 'geometry_destino','pto_dist']
    
df1['costo_por_camion'] = df1['costo_caseta'] + df1['costo_gas']
    
df_presupuesto = pd.DataFrame()
conteo_camiones = df['punto_de_distribucion'].value_counts()
df_conteo_camiones = pd.DataFrame({'pto_dist': conteo_camiones.index, 'num_camiones': conteo_camiones.values})
df_presupuesto = pd.merge(df1, df_conteo_camiones, on='pto_dist')
df_presupuesto['costo_total'] = df_presupuesto['num_camiones'] * df_presupuesto['costo_por_camion']
df_presupuesto.to_csv('centro_de_distribucion_costos.csv',index=False)


### Conexión con SQLite3 ###
### Conexión con SQLite3 ###
### Conexión con SQLite3 ###
### Conexión con SQLite3 ###

costo = pd.read_csv('centro_de_distribucion_costos.csv')
# Conéctate a la base de datos SQLite (si no existe, se creará)
conn = sqlite3.connect('/Users/macbook/Desktop/Programación/Actividad/gestion_camiones.db')

# Crea una tabla en la base de datos utilizando el método to_sql de pandas
costo.to_sql('costo', conn, if_exists='replace', index=False)
df.to_sql('distribucion_camiones', conn, if_exists='replace', index=False)

query1 = 'SELECT pto_dist, costo_total FROM costo'

costo_por_destino = pd.read_sql_query(query1,conn)

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

grafico1 = px.bar(df_presupuesto,y='costo_total',x='pto_dist',title=f"Costos por Ciudad de Destino",template=load_figure_template('bootstrap_dark'),labels={'pto_dist':'Ciudad', 'costo_total':'Costo'},
                  color='costo_total',color_continuous_scale=paleta_continua,color_continuous_midpoint=promedio_costo)


## Para posteriormente llamar a la app
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


### Aqui haces un dataframe
presupuesto_tabla = pd.DataFrame(df_presupuesto[['pto_dist', 'long_km', 'tiempo_min', 'costo_gas', 'costo_caseta', 'costo_por_camion', 'num_camiones', 'costo_total']])

### Nombras y pones caracteristicas a las columnas
columnDefs = [
    {
        "headerName": "Ciudad Destino",
        "field": "pto_dist",
        "filter": True,
    },
    {
        "headerName": "Distancia",
        "field": "long_km",
        "filter": True,
    },
    {
        "headerName": "Tiempo",
        "field": "tiempo_min",
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

#### Mapa Con Todos los Trayectos ####
#### Mapa Con Todos los Trayectos ####
#### Mapa Con Todos los Trayectos ####
#### Mapa Con Todos los Trayectos ####
#### Mapa Con Todos los Trayectos ####

### Diseño Mapa ###
### Diseño Mapa ###
### Diseño Mapa ###

# Definir la función de estilo para las GeoJSON
def style_function(feature):
    return {
        'color': 'orange',  # Cambia el color del trazo a naranja
        'weight': 2,         # Puedes ajustar el grosor del trazo según tus preferencias
        'opacity': 1,
    }


# Crear un mapa una vez
m = folium.Map(location=[25.68202029529298, -100.31768851930713], zoom_start=4.2)

# Agregar la capa 'cartodbdark_matter' al mapa
folium.TileLayer('cartodbdark_matter').add_to(m)

folium.Marker(
    location=[linea_inicial['geometry'].y, linea_inicial['geometry'].x],
    popup="Centro de Distribución: Transpor-T ",
    icon=folium.Icon(color="darkblue", icon="home"),
    max_width=1000  # Ajusta el ancho del popup
    ).add_to(m)

folium.Circle(location=[linea_inicial['geometry'].y, linea_inicial['geometry'].x],
            color="#928000", fill_color="#DCC000", radius=20000, weigth=4, fill_opacity=0.5
            ).add_to(m)
    
# Crear un grupo de características para las rutas
feature_group = folium.FeatureGroup()   

## Calcular y mostrar las rutas para cada camión
for destino in df_presupuesto['pto_dist']:
        
    ruta_optima = df_presupuesto[df_presupuesto['pto_dist'] == destino]
    # Agregar la ruta al grupo de características
    folium.GeoJson(ruta_optima['geometry_ruta'].__geo_interface__,style_function=style_function).add_to(feature_group)
        
    popup_content = f"<b>Ciudad:_</b>{destino}<br> <b>Tiempo:_{round(ruta_optima['tiempo_min'].values[0]/60,2)}Hrs.</b><br><b>Caseta:_$</b>{ruta_optima['costo_caseta'].values[0]}<br><b>Distancia:_{ruta_optima['long_km'].values[0]}Km.</b>"

    folium.Marker(
    location=[ruta_optima['geometry_destino'].y, ruta_optima['geometry_destino'].x],
    popup=popup_content,
    icon=folium.Icon(color="darkred", icon="flag"),
    max_width=1000  # Ajusta el ancho del popup
    ).add_to(m)
        

    # Agregar el grupo de características al mapa
    feature_group.add_to(m)

# Mostrar el mapa
m.save("mapa_multilinestring.html")

mapa_trayectos = m._repr_html_()


##### Dashboard #####
##### Dashboard #####
##### Dashboard #####
##### Dashboard #####
##### Dashboard #####
##### Dashboard #####
##### Dashboard #####
##### Dashboard #####

### Objetos ###
### Objetos ###
### Objetos ###

### Mapa ###
mapa = dbc.Card(html.Iframe(id="mapa",style={'width':'100%','height':'45vh'}), body=True,className="mi-mapa")

### Grafico de Barra ###
grafico_barra = dbc.Card(dcc.Graph(id="asset-allocation",figure=grafico1,style={'height':'45vh'}), body=True)

### Titulo del dashboard ###
header = html.Div("Transpor-T", className="h2 p-2 text-white bg-primary text-center",id='titulo')

### Diseño del Dashboard ###
### Diseño del Dashboard ###
### Diseño del Dashboard ###
app.layout = dbc.Container(
    [
        header,
        dbc.Row([dbc.Col(mapa), dbc.Col(grafico_barra)]),
        dbc.Row(dbc.Col(grid, className="py-4")),
    ],
)

### Callbacks ###
### Callbacks ###
### Callbacks ###
@app.callback(
    Output("mapa",'srcDoc'),
    [Input("tabla", "selectedRows")]
)
def update_map(selected_row):
    # Lógica para determinar el mapa a mostrar
    if not selected_row:
        # Si no hay selección, mostrar el mapa_trayectos por defecto
        return mapa_trayectos
    else:
        # Si la selección actual es diferente a la anterior, mostrar otro_mapa
        punto = selected_row[0]['pto_dist']
        # Crear un mapa una vez
        map = folium.Map(location=[25.68202029529298, -100.31768851930713], zoom_start=4.2)
        
        # Agregar la capa 'cartodbdark_matter' al mapa
        folium.TileLayer('cartodbdark_matter').add_to(map)

        folium.Marker(
            location=[linea_inicial['geometry'].y, linea_inicial['geometry'].x],
            popup="Centro de Distribución: Transpor-T ",
            icon=folium.Icon(color="darkblue", icon="home"),
            max_width=1000  # Ajusta el ancho del popup
            ).add_to(map)

        folium.Circle(location=[linea_inicial['geometry'].y, linea_inicial['geometry'].x],
                    color="#928000", fill_color="#DCC000", radius=20000, weigth=4, fill_opacity=0.5
                    ).add_to(map)
        
        # Crear un grupo de características para las rutas
        feature_group = folium.FeatureGroup()   

        ruta_optima = df_presupuesto[df_presupuesto['pto_dist'] == punto]
        # Agregar la ruta al grupo de características
        folium.GeoJson(ruta_optima['geometry_ruta'].__geo_interface__,style_function=style_function).add_to(feature_group)
            
        popup_content = f"<b>Ciudad:_</b>{punto}<br> <b>Tiempo:_{round(ruta_optima['tiempo_min'].values[0]/60,2)}Hrs.</b><br><b>Caseta:_$</b>{ruta_optima['costo_caseta'].values[0]}<br><b>Distancia:_{ruta_optima['long_km'].values[0]}Km.</b>"

        folium.Marker(
        location=[ruta_optima['geometry_destino'].y, ruta_optima['geometry_destino'].x],
        popup=popup_content,
        icon=folium.Icon(color="#darkred", icon='flag'),
        max_width=1000  # Ajusta el ancho del popup
        ).add_to(map)
            

        # Agregar el grupo de características al mapa
        feature_group.add_to(map)

        # Abre el archivo HTML en el navegador predeterminado
        return map._repr_html_()  
     
if __name__ == "__main__":
    app.run_server(debug=True)