##### Final Project Proposal LA 5580
###### Alex Cecil

# Project Title: Soil Nutrient Modeling

### Abstract:
Using soil sample data, maps of estimated nutrient values for the surrounding areas are created to be utilized by farms and researchers working in the area to help plan out their management for the varying conditions of the fields they will be working in. Without the need of comprehensive soil testing in every field.

### Overview:
For this project, I will use sample data from various fields in the ames area to estimate the soil nutrient content in the surround area. Once I have the estimation I will produce maps of the areas with the different values present and accessabile to users. The goal will be to have the data in a format which is accessible even to someone with little to no experience with GIS and formated such that any information presented has a clear use and can be applied to a growers field directly without any post-processing. To produce the data I will use R, Python, ArcGIS Pro and Arc GIS online. Once maps have been produced the different nutrients and values will be displayed ina single multilayer map or multiple maps depenting on the relation of the values to each other. I hope to include the abbility of assiging an Area of Interest (AOI) to the map to allow the user to zoom to their AOI and focus on that area with the potential to export the data of a given AOI as a csv file or smaller map layer file.

### Technology:
- ArcGIS Pro
- ArcGIS Online
- Python
- R
- Html/Javascript/CSS
- Github

### Data:
- Iowa State Ag-Engineering and Agronomy Farm
- Google Earth Engine Satellite Data (which satellites and bands to be determined)
- USGS Lidar Data
- GLSI (in-house lab data)

### Process/Methods:
I will use a R and python Libraries together to produce the data set, with the data exported to CSV or directly to a map using leaflet. Once in a CSV format using ArcGIS pro or QGIS I can produce maps on a county/area basis with the option of zooming to a specific area using html and javascript to host the search function.

### Inspiration:
My current inspiration is from UC Davis Soil web (https://casoilresource.lawr.ucdavis.edu/gmap/) which allows quick access to soil survey data, looking at something like that to create a similar product for the area soil nutrient estimate.
### Potential Challenges:
Producing the data for this website and setting up an AOI search function are the only challenges I see and the data accuracy is more of a challenge than the actual production of data.


### Timeline for Completion:
I can produce data within the next week and can produce the maps within the following week with the webpage being produced within a week of that.





