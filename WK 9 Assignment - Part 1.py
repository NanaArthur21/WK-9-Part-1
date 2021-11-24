#!/usr/bin/env python
# coding: utf-8

# In[1]:


conda install jupyter_dashboards -c conda-forge


# In[2]:


get_ipython().system('conda install jupyter_dashboards -c conda-forge -y')


# In[3]:


from IPython.display import display, clear_output
import ipywidgets as widgets

from arcgis.features import SpatialDataFrame
from arcgis.geoenrichment import enrich
from arcgis.raster import ImageryLayer
from arcgis.geometry import Geometry
from arcgis.gis import GIS

gis = GIS('home')
img_svc ='https://landscape7.arcgis.com/arcgis/rest/services/World_Population_Density_Estimate_2016/ImageServer/'
img_lyr = ImageryLayer(img_svc, gis=gis)


# In[4]:


from arcgis.gis import GIS


# In[5]:


gis = GIS()


# In[6]:


public_content = gis.content.search("Fire", item_type="Feature Layer", max_items=5)


# In[7]:


public_content


# In[8]:


from IPython.display import display
for item in public_content:
    display(item)


# In[9]:


example_item = public_content[0]
display(example_item)


# In[10]:


#Create a new map object
map1 = gis.map()
#Focus the map to the part of the world containing the example item
map1.extent = example_item.extent
#Display the map
map1


# In[11]:


map1.add_layer(example_item)


# In[12]:


get_ipython().system('conda install jupyter_dashboards -c conda-forge -y')


# In[13]:


from arcgis.gis import GIS
from arcgis.geocoding import geocode
from arcgis.raster.functions import *
from arcgis import geometry
    
import pandas as pd

# connect as an anonymous user
gis = GIS()

# search for the landsat multispectral imagery layer
landsat_item = gis.content.search("Landsat Multispectral tags:'Landsat on AWS','landsat 8', 'Multispectral', 'Multitemporal', 'imagery', 'temporal', 'MS'", 'Imagery Layer', outside_org=True)[0]
landsat = landsat_item.layers[0]
df = None


# In[14]:


import ipywidgets as widgets

# text box widget
location = widgets.Text(value='Ranchi, India', placeholder='Ranchi, India',
                        description='Location:', disabled=False)

# command button widget
gobtn = widgets.Button(description='Go', disabled=False,
                       button_style='', tooltip='Go', icon='check')

# define what happens whent the command button is clicked
def on_gobutton_clicked(b):
    global df
    global m
    global oldslider
    
    # geocode the place name and set that as the map's extent
    area = geocode(location.value)[0]
    m.extent = area['extent']
    df = filter_images()
    
gobtn.on_click(on_gobutton_clicked)

location_items = [location, gobtn]
widgets.HBox(location_items)


# In[15]:


import ipywidgets as widgets

# text box widget
location = widgets.Text(value='Ranchi, India', placeholder='Ranchi, India',
                        description='Location:', disabled=False)

# command button widget
gobtn = widgets.Button(description='Go', disabled=False,
                       button_style='', tooltip='Go', icon='check')

# define what happens whent the command button is clicked
def on_gobutton_clicked(b):
    global df
    global m
    global oldslider
    
    # geocode the place name and set that as the map's extent
    area = geocode(location.value)[0]
    m.extent = area['extent']
    df = filter_images()
    
gobtn.on_click(on_gobutton_clicked)

location_items = [location, gobtn]
widgets.HBox(location_items)


# In[16]:


m = gis.map(location.value)
m.add_layer(landsat)
display(m)


# In[17]:


oldindex =  0 # int(len(df)/2)

# before image date slider
oldslider = widgets.IntSlider(value=oldindex, min=0,max=10, #len(df) - 1,
                              step=1, description='Older:', disabled=False,
                              continuous_update=True, orientation='horizontal',
                              readout=False, readout_format='f', slider_color='white')

old_label = widgets.Label(value='')#str(df.Time.iloc[oldindex].date()))

# define the slider behavior
def on_old_value_change(change):
    global df
    i = change['new']
    if df is not None:
        try:
            # print(df.Time.iloc[i].date())
            old_label.value = str(df.Time.iloc[i].date())
        except:
            pass
        
oldslider.observe(on_old_value_change, names='value')    
widgets.HBox([oldslider, old_label])


# In[18]:


newindex = 0 # len(df) - 1

# after image date slider
newslider = widgets.IntSlider(value=newindex, min=0, max=10, #len(df) - 1,
                              step=1, description='Newer:', disabled=False,
                              continuous_update=True, orientation='horizontal',
                              readout=False, readout_format='f', slider_color='white')

new_label = widgets.Label(value='') #str(df.Time.iloc[newindex].date()))

# define the slider behavior
def on_new_value_change(change):
    global df
    i = change['new']
    if df is not None:
        try:
        # print(df.Time.iloc[i].date())
            new_label.value = str(df.Time.iloc[i].date())
        except:
            pass
newslider.observe(on_new_value_change, names='value')
widgets.HBox([newslider, new_label])


# In[19]:


def update_sliders(tdf):
    global oldslider
    global newslider
    
    oldslider.max = len(tdf) - 1
    newslider.max = len(tdf) -1
    oldindex = int(len(tdf)/2)
    newindex = int(len(tdf) -1)
    oldslider.value = oldindex
    newslider.value = newindex
    old_label.value = str(tdf.Time.iloc[oldindex].date())
    new_label.value = str(tdf.Time.iloc[newindex].date())


def filter_images():
    global df
    area = geocode(location.value, out_sr=landsat.properties.spatialReference)[0]
    extent = area['extent']

    selected = landsat.filter_by(where="(Category = 1) AND (CloudCover <=0.10)", 
                             geometry=geometry.filters.intersects(extent))
    fs = selected.query(out_fields="AcquisitionDate, GroupName, Best, CloudCover, WRS_Row, WRS_Path, Month, Name", 
                  return_geometry=True,
                  return_distinct_values=False,
                  order_by_fields="AcquisitionDate")
    tdf = fs.sdf
    df = tdf
    tdf['Time'] = pd.to_datetime(tdf['AcquisitionDate'], unit='ms')    
    
    if len(tdf) > 1:
        update_sliders(tdf)

    # m.draw(tdf.iloc[oldslider.value].SHAPE)
    
    return tdf


# In[20]:


df = filter_images()


# In[21]:


# create the action button
diffbtn = widgets.Button(description='Detect changes', disabled=False,
                         button_style='success', tooltip='Show Different Image',
                         icon='check')

def on_diffbutton_clicked(b):
    # m.clear_graphics()
    first = df.iloc[oldslider.value].OBJECTID
    last = df.iloc[newslider.value].OBJECTID
    old = landsat.filter_by('OBJECTID='+str(first))
    new = landsat.filter_by('OBJECTID='+str(last))
    diff = stretch(composite_band([ndvi(old, '5 4'),
                               ndvi(new, '5 4'),
                               ndvi(old, '5 4')]), 
                               stretch_type='stddev',  num_stddev=3, min=0, max=255, dra=True, astype='u8')
    m.add_layer(diff)
    
diffbtn.on_click(on_diffbutton_clicked)
diffbtn


# In[22]:


get_ipython().system('conda install jupyter_dashboards -c conda-forge -y')


# In[23]:


from ipywidgets import widgets
from IPython.display import clear_output


# In[24]:


from arcgis.gis import GIS
from arcgis.raster.functions import *

gis = GIS()

landsat_item = gis.content.search("Landsat Multispectral tags:'Landsat on AWS','landsat 8', 'Multispectral', 'Multitemporal', 'imagery', 'temporal', 'MS'", 'Imagery Layer')[0]
landsat = landsat_item.layers[0]


# In[25]:


map1 = gis.map("California, USA")
map1


# In[26]:


map1.add_layer(landsat)


# In[27]:


rfts = []
for idx,props in enumerate(landsat.properties['rasterFunctionInfos']):
    rfts.append(landsat.properties['rasterFunctionInfos'][idx]['name'])


# In[28]:


rft_select = widgets.Dropdown(
    options=rfts,
    value='None',
    description='Raster Function',
    disabled=False,
)

def on_rft_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        map1.remove_layers()
        map1.add_layer(landsat, {"imageServiceParameters" :{ "renderingRule": { "rasterFunction": rft_select.value}}})

rft_select.observe(on_rft_change)
display(rft_select)


# In[29]:


from arcgis.geocoding import geocode
from arcgis.features import FeatureLayer

study_area_dict = {'California':'http://services.arcgis.com/PpEMp4p6SBYbe0zW/arcgis/rest/services/California_Counties/FeatureServer/0',
                   'Montana':'http://services.arcgis.com/iTQUx5ZpNUh47Geb/arcgis/rest/services/Montana_Mask/FeatureServer/0',
                   'Nevada':'http://services.arcgis.com/pGfbNJoYypmNq86F/arcgis/rest/services/28R04_Nevada_Region/FeatureServer/5',
                   'Oregon':'https://services.arcgis.com/uUvqNMGPm7axC2dD/arcgis/rest/services/Oregon_Boundary_generalized/FeatureServer/0',
                   'Texas':'http://services2.arcgis.com/5MVN2jsqIrNZD4tP/arcgis/rest/services/Texas_Outline/FeatureServer/0'}

study_areas = ['California',
               'Montana',
               'Nevada',
               'Oregon',
               'Texas']

country = widgets.Dropdown(
    options=study_areas,
    value='California',
    description='Region to Process:',
    disabled=False,
)

def on_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        location = geocode(str(country.value) + ', USA')[0]
        map1.extent = location['extent']
        #fl = FeatureLayer(study_area_dict[country.value])
        #map1.extent = fl.properties['extent']
        #print("changed to %s" % change['new'])

country.observe(on_change)

display(country)


# In[30]:


from datetime import datetime

def on_button_click(b):
    #map1.extentx = getextent
    clear_output()
    print("Job submitted at " + f"{datetime.now():%Y-%m-%d %H:%M:%S}")

button = widgets.Button(description="Run Raster Analytics", 
                        disabled=False,
                        button_style='success',
                        tooltip='Kick Off A Raster Analytics Job',
                        icon='check')
display(button)
button.on_click(on_button_click)


# In[31]:


from arcgis.gis import GIS


# In[32]:


from arcgis.raster.functions import *


# In[33]:


gis = GIS()


# In[34]:


landsat_item = gis.content.search('"Multispectral Landsat"', 'Imagery Layer')[0]


# In[35]:


landsat_item


# In[36]:


landsat = landsat_item.layers[0]


# In[37]:


def extract_stretch(bandids):
    return stretch(extract_band(landsat, bandids),
                   stretch_type='PercentClip',
                   min_percent=2, 
                   max_percent=2,
                   dra=True, 
                   gamma=[0.8,0.8,0.8])


# In[38]:


cambridge_gulf = extract_stretch([5, 4, 1])
cambridge_gulf.extent = {'xmax': 128.96, 'xmin': 127.62, 'ymax': -14.72, 'ymin': -15.25, 'spatialReference': 4326}
cambridge_gulf


# In[39]:


eye_of_sahara = extract_stretch([6,3,1])
eye_of_sahara.extent = {'xmax': -10.6, 'xmin': -11.94, 'ymax': 21.38, 'ymin': 20.86, 'spatialReference': 4326}
eye_of_sahara


# In[40]:


gosses_bluff = extract_stretch([6,3,1])
gosses_bluff.extent = {'xmax': 133.23, 'xmin': 131.89, 'ymax': -23.7, 'ymin': -24.2, 'spatialReference': 4326}
gosses_bluff


# In[41]:


exumas_bahamas = extract_stretch([5, 3, 0])
exumas_bahamas.extent = {'xmax':-75.31, 'xmin':-75.98, 'ymax':23.62, 'ymin':23.37, 'spatialReference':4326}
exumas_bahamas


# In[42]:


mexico_city = extract_stretch([6, 5, 3])
mexico_city.extent = {'xmax': -98.76, 'xmin': -99.44, 'ymax': 19.54, 'ymin': 19.28,'spatialReference': 4326}
mexico_city


# In[43]:


central_saudi_arabia = extract_stretch([5, 4, 1])
central_saudi_arabia.extent = {'xmax': 45.18, 'xmin': 43.82, 'ymax': 26.0, 'ymin': 25.5, 'spatialReference': 4326}
central_saudi_arabia


# In[44]:


bahr_al_milh = extract_stretch([5, 1, 0])
bahr_al_milh.extent = {'xmax': 44.48, 'xmin': 43.13, 'ymax': 32.86, 'ymin': 32.4, 'spatialReference': 4326}
bahr_al_milh


# In[1]:


from arcgis.gis import GIS


# In[2]:


from arcgis.raster.functions import *


# In[3]:


gis = GIS()


# In[4]:


landsat_item = gis.content.search("Landsat 8 Views tags: 'imagery','multispectral','temporal','landsat 8','landsat','landsat on aws','amazon','MS'",'Imagery Layer')[0]
landsat = landsat_item.layers[0]


# In[5]:


map1 = gis.map("Ghana, Africa")
map1


# In[6]:


map1.add_layer(landsat)


# In[7]:


print('Landsat on Google:')
filepath = 'https://storage.googleapis.com/gcp-public-data-landsat/LC08/01/042/034/LC08_L1TP_042034_20170616_20170629_01_T1/LC08_L1TP_042034_20170616_20170629_01_T1_B4.TIF'
with rasterio.open(filepath) as src:
    print(src.profile)


# In[8]:


print('Landsat on AWS:')
filepath = 'http://landsat-pds.s3.amazonaws.com/c1/L8/042/034/LC08_L1TP_042034_20170616_20170629_01_T1/LC08_L1TP_042034_20170616_20170629_01_T1_B4.TIF'
with rasterio.open(filepath) as src:
    print(src.profile)


# In[ ]:




