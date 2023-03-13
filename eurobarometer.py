import pandas as pd
import folium
from streamlit_folium import st_folium
from IPython.display import display
import geojson
from branca.colormap import linear
import streamlit as st
import numpy as np
import os
import geopandas as gpd

#%%
#df = pd.read_stata('data/harmonised_EB_2004-2021.dta', convert_categoricals=False)
#df.to_parquet("data_clean/eurobarometer.parquet.gzip", compression="gzip")

#%%
@st.cache(allow_output_mutation=True)
def load_data():
    countries = pd.read_excel('data/countries.xlsx')
    countries = countries.iloc[:, 0:2]
    df = pd.read_parquet('data_clean/eurobarometer.parquet.gzip')
    df = df.sample(frac=.01)
    df = df[['country_label', 'year', 'treu']]
    df = df.dropna()
    df = df.groupby("country_label").mean("treu")
    df.reset_index(inplace=True)
    df = df.merge(countries, left_on='country_label', right_on="country")
    df = df.groupby("iso2").mean("treu")
    df.reset_index(inplace=True)
    return df

#%%
@st.cache(allow_output_mutation=True)
def create_map():
    map = folium.Map(
        location = [54.5260, 15.2551],
        zoom_start = 3,
        scrollWheelZoom = True,
        tiles = 'cartodbpositron'
    )
    return map

def load_geojson():
    europe_nuts3 = gpd.read_file('data/NUTS_RG_60M_2021_4326.geojson', encoding='utf-8')
    return europe_nuts3

#%%
df = load_data()
map = create_map()
europe_nuts3 = load_geojson()

def create_choropleth(map):
    colormap = linear.YlOrRd_09.scale(
        df['treu'].min(),
        df['treu'].max()
    )

    choropleth = folium.Choropleth(
        geo_data = europe_nuts3,
        encodings ='utf-8',
        data = df,
        columns = ('iso2', 'treu'),
        key_on='feature.properties.CNTR_CODE',
        line_opacity = 0.9,
        fill_opacity = 0.5,
        highlight = True,
        fill_color = 'YlGnBu',
        #legend_name='Political Interest',
        #reset = False,
    ).add_to(map)
    return choropleth

choropleth = create_choropleth(map)

#%%

def add_values_to_map(df, choropleth):
    df = df.set_index('iso2')
    for feature in choropleth.geojson.data['features']:
        region_name = feature['properties']['CNTR_CODE']
        feature['properties']['data'] = "EU TRUST: " + str(df.loc[region_name]['treu'] if region_name in list(df.index) else "No data")

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['CNTR_CODE', 'NUTS_NAME', 'data'], label=False)
    )

# Add a legend to the map
st_map = st_folium(map, width=500, height=700)
add_values_to_map(df, choropleth)