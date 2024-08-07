import INEGIpy
import numpy as np
import pandas as pd
from shapely.geometry import MultiLineString, Point
import folium
from . import ModDatosLogisticos
import webbrowser
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_ag_grid as dag



## Para posteriormente llamar a la app
dash.register_page(__name__, path = '/')

### Aqui haces un dataframe
df_presupuesto = ModDatosLogisticos.dataframe_presupuesto()

Tabla_PtoCost_Data = pd.DataFrame(df_presupuesto[['pto_dist', 'costo_total']])

def style_function(feature):
    return {
        'color': 'green',  # Cambia el color del trazo a naranja
        'weight': 2,         # Puedes ajustar el grosor del trazo según tus preferencias
        'opacity': 1,
    }


### Caracteristicas default de las columnas
defaultColDef = {
    "filter": "agNumberColumnFilter",
    "resizable": True,
    "sortable": True,
    "editable": False,
    "floatingFilter": True,
    "minWidth": 125,
}


columnDefs_Tabla_PtoCost = [
    {
        "headerName": "Ciudad Destino",
        "field": "pto_dist",
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

### Esta sera la tabla para el panel principal
Tabla_PtoCost = dag.AgGrid(
    id="tabla_PtoCost",
    className="ag-theme-alpine-dark",
    columnDefs=columnDefs_Tabla_PtoCost,
    rowData=Tabla_PtoCost_Data.to_dict("records"),
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={"undoRedoCellEditing": True, "rowSelection": "multiple","rowMultiSelectWithClick": False},
    style={'height':'80vh'}
)

mapa_trayectos = ModDatosLogisticos.mapa_logistico()._repr_html_()

offcanvas = html.Div(
    [
        dbc.Button("Open Offcanvas", id="open-offcanvas", n_clicks=0),
        dbc.Offcanvas(
            html.Div([Tabla_PtoCost],style={'heigth': '100%', 'float': 'center'}),
            id="offcanvas",
            title="Costos Totales por Destino",
            is_open=False,
        )
    ]
)

layout = html.Div(
    [ 

        html.Div([
            ### Mapa ###
            dbc.Card(html.Iframe(id="mapa", style={'width': '100%', 'height': 'calc(100vh - 150px)', 'border': 'none'}), body=True,className="mi-mapa") 
        ], style={'width': '100%', 'float': 'left'}),
       
        offcanvas
    ]
)

@callback(
    Output("mapa",'srcDoc'),
    [Input("tabla_PtoCost", "selectedRows")]
)
def update_map(selected_row):

    linea_inicial = ModDatosLogisticos.Data_CentroDistr()

    # Lógica para determinar el mapa a mostrar
    if not selected_row:
        # Si no hay selección, mostrar el mapa_trayectos por defecto
        return mapa_trayectos
    else:
        # Si la selección actual es diferente a la anterior, mostrar otro_mapa
        punto = selected_row[0]['pto_dist']
        # Crear un mapa una vez
        map = folium.Map(location=[22.6345, -102.5528], zoom_start=5)

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
        folium.GeoJson(ruta_optima['geometry_ruta'].__geo_interface__,style_function=style_function,zoom_on_click=True).add_to(feature_group)
            
        popup_content = f"<b>Ciudad:_</b>{punto}<br> <b>Tiempo:_{round(ruta_optima['tiempo_min'].values[0]/60,2)}Hrs.</b><br><b>Caseta:_$</b>{ruta_optima['costo_caseta'].values[0]}<br><b>Distancia:_{ruta_optima['long_km'].values[0]}Km.</b>"

        folium.Marker(
        location=[ruta_optima['geometry_destino'].y, ruta_optima['geometry_destino'].x],
        popup=popup_content,
        icon=folium.Icon(color="darkred", icon='flag'),
        max_width=1000  # Ajusta el ancho del popup
        ).add_to(map)
            

        # Agregar el grupo de características al mapa
        feature_group.add_to(map)

        # Abre el archivo HTML en el navegador predeterminado
        return map._repr_html_() 

@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

@callback(Output('page-content', 'children'),
              [Input('url','pathname')])
def display_page(pathname):
    if pathname == '/Panel1':
        return html.P("Contenido del Panel Principal")
    elif pathname == '/Panel1':
        return html.P("Contenido del Reporte Logistico")
    else:
        return html.P("Página no encontrada")