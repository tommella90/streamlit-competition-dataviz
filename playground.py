import pandas as pd
import streamlit as st
import numpy as np
import os
import geopandas as gpd
import pandas as pd
import urllib
import folium
from streamlit_folium import st_folium
from IPython.display import display
import geojson
from branca.colormap import linear

#%%
#@st.cache(allow_output_mutation=True)
def load_data():
    #all_df = pd.read_csv("data/ess_9.csv")
    all_df = pd.read_csv("data/temp.csv")
    df_sampled = all_df[['region', 'polintr']]
    #df_sampled = all_df.sample(n=10000, random_state=1)
    #df_sampled.to_csv("data/temp.csv")

    df = df_sampled[['region', 'polintr']]
    df = df.loc[df['polintr']!="Don't know"]
    df = df.loc[df['polintr']!="Refusal"]
    df['polintr'] = df['polintr'].replace({
        "Not at all interested": 0,
        "Hardly interested": 1,
        "Quite interested": 2,
        "Very interested": 3
    })

    df['polintr'] = df['polintr'].astype(float)
    df = df.groupby("region").mean("polintr")
    df.reset_index(inplace=True)

    return df

#%%
df = load_data()

map = folium.Map(
    location = [54.5260, 15.2551],
    zoom_start = 3,
    scrollWheelZoom = True,
    tiles = 'cartodbpositron'
)
#%%
europe_nuts3 = gpd.read_file('data/NUTS_RG_60M_2021_4326.geojson', encoding='utf-8')

colormap = linear.YlOrRd_09.scale(
    df['polintr'].min(),
    df['polintr'].max()
)

choropleth = folium.Choropleth(
    geo_data=europe_nuts3,
    encodings = 'utf-8',
    data = df,
    columns = ('region', 'polintr'),
    key_on='feature.properties.NUTS_ID',
    line_opacity=0.9,
    fill_opacity=0.5,
    highlight=True,
    fill_color='YlOrRd',
    legend_name='Political Interest',
    reset=True,
).add_to(map)

#%%
#df = df.set_index('region')

#%%
for feature in choropleth.geojson.data['features']:
    region_name = feature['properties']['NUTS_ID']
    feature['properties']['data'] = "Political interest" + str(df.loc[region_name]['polintr'][0] if region_name in list(df.index) else "No data")

#%%

r = choropleth.geojson.data['features'][0]['properties']['NUTS_ID']
r
#%%
print("Political interest" + str(df.loc[region_name]['polintr'][0] if region_name in list(df.region) else "No data"))

#%%
choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['CNTR_CODE', 'NUTS_NAME', 'data'], label=False)
)

# Add a legend to the map
colormap.caption = 'Political Interest'
map.add_child(colormap)

# Add a layer control to the map


#choropleth.geojson.add_to(map)
st.write(df.head(1))
st_map = st_folium(map, width=500, height=700)
df.head(1)


"""
import geopandas as gpd
json = pd.read_json("data/NUTS_RG_20M_2021_3035.geojson")
json = gpd.read_file('data/NUTS_RG_20M_2021_3035.geojson')
"""
#%%
all_df = pd.read_csv("data/ess_9.csv")

#%%
nuts = all_df['region'].unique()

#%%
