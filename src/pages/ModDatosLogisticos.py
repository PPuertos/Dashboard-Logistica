import INEGIpy
import numpy as np
import pandas as pd
from shapely.geometry import MultiLineString, Point
import folium

# Data Frame con la información de los Autobuses y sus Destinos
df = pd.read_csv('/Users/macbook/Documents/Semestre 5/Programación/Dashboard-Logística/Dashboard-Logistica/centro_de_distribucion_puntos.csv')
####################################################################
# Importando la clase ruteo que pertenece a la librería INEGIpy, con token para acceder a la información
ruteo = INEGIpy.Ruteo('xVC8A3aI-kema-ZmWE-jPzF-8f2GfLCp6jb9')
    
# Precio Gasolina Diesel
combustibles = ruteo.Combustibles()
costo = combustibles.loc[0,'costo']

### Base de Datos con Cálculo de Costos ###
def Data_CentroDistr():
    # Coordenada del centro de distribución, que en este caso es MTY
    centro_de_distribucion = 'Monterrey, Nuevo León'
    buscar = ruteo.BuscarDestino(busqueda=centro_de_distribucion, cantidad=1)

    # Linea Inicial del centro de distribucion, parte del proceso para determinar costos
    linea_inicial = ruteo.BuscarLinea(lat = buscar['geometry'].y, lng = buscar['geometry'].x)

    return linea_inicial

def dataframe_presupuesto():

    linea_inicial = Data_CentroDistr()

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
        ruta_optima['costo_gas'] = ruta_optima['long_km']  * costo * .25
        
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
    
    return df_presupuesto


df_presupuesto = dataframe_presupuesto()

#### Mapa Con Todos los Trayectos ####

def mapa_logistico():

    linea_inicial = Data_CentroDistr()

    # Definir la función de estilo para las GeoJSON
    def style_function(feature):
        return {
            'color': 'green',  # Cambia el color del trazo a verde
            'weight': 2,         # Puedes ajustar el grosor del trazo según tus preferencias
            'opacity': 1,
        }

    # Crear un mapa una vez
    m = folium.Map(location=[22.6345, -102.5528], zoom_start=5)

    # Agregar la capa 'cartodbdark_matter' al mapa
    #folium.TileLayer('cartodbdark_matter').add_to(m)

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
        folium.GeoJson(ruta_optima['geometry_ruta'].__geo_interface__,style_function=style_function,zoom_on_click=True).add_to(feature_group)
            
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

    mapa_trayectos = m

    return mapa_trayectos
