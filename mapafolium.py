#!/usr/bin/env python3
"""
SpaceX Interactive Map with Folium
Author: Camilo Medina
Description: Interactive visualization of SpaceX launch sites and landing outcomes
"""

import folium
import pandas as pd
import numpy as np
from folium import plugins
from folium.features import DivIcon
import requests
import json
import math

def create_spacex_interactive_map():
    """
    Create an interactive Folium map showing SpaceX launch sites and landing outcomes
    """
    
    # SpaceX launch sites data (based on the lab data)
    launch_sites_data = {
        'Launch Site': ['CCAFS SLC 40', 'KSC LC 39A', 'VAFB SLC 4E'],
        'Lat': [28.561857, 28.573255, 34.632834],
        'Long': [-80.577366, -80.646895, -120.610745],
        'Name': ['Cape Canaveral Air Force Station Space Launch Complex 40', 
                'Kennedy Space Center Launch Complex 39A',
                'Vandenberg Air Force Base Space Launch Complex 4E']
    }
    
    # Create launch sites DataFrame
    launch_sites_df = pd.DataFrame(launch_sites_data)
    
    # Sample SpaceX launch data (based on the lab results)
    spacex_launch_data = {
        'Lat': [28.561857, 28.561857, 28.561857, 28.573255, 28.573255, 34.632834],
        'Long': [-80.577366, -80.577366, -80.577366, -80.646895, -80.646895, -120.610745],
        'class': [1, 0, 1, 1, 0, 1],  # 1 = Success, 0 = Failure
        'Launch_Site': ['CCAFS SLC 40', 'CCAFS SLC 40', 'CCAFS SLC 40', 
                       'KSC LC 39A', 'KSC LC 39A', 'VAFB SLC 4E'],
        'Date': ['2010-06-04', '2010-12-08', '2012-05-22', '2017-02-19', '2017-06-03', '2018-01-31']
    }
    
    # Create SpaceX launch DataFrame
    spacex_df = pd.DataFrame(spacex_launch_data)
    
    # Create marker color column
    def assign_marker_color(launch_outcome):
        if launch_outcome == 1:
            return 'green'
        else:
            return 'red'
    
    spacex_df['marker_color'] = spacex_df['class'].apply(assign_marker_color)
    
    # NASA coordinate (approximate center of launch sites)
    nasa_coordinate = [28.573255, -80.646895]
    
    # Create the map
    site_map = folium.Map(location=nasa_coordinate, zoom_start=5)
    
    # Add launch site markers and circles
    for index, row in launch_sites_df.iterrows():
        # Create a Circle object for each launch site
        circle = folium.Circle(
            [row['Lat'], row['Long']],
            radius=1000,
            color='#d35400',
            fill=True,
            popup=row['Launch Site']
        )
        
        # Create a Marker object for each launch site
        marker = folium.Marker(
            [row['Lat'], row['Long']],
            icon=DivIcon(
                icon_size=(20, 20),
                icon_anchor=(0, 0),
                html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % row['Launch Site'],
            )
        )
        
        # Add the circle and marker to the map
        site_map.add_child(circle)
        site_map.add_child(marker)
    
    # Create marker cluster for launch outcomes
    marker_cluster = plugins.MarkerCluster()
    
    # Add marker cluster to the map
    site_map.add_child(marker_cluster)
    
    # Add launch outcome markers
    for index, record in spacex_df.iterrows():
        # Create and add a Marker cluster to the site map
        marker = folium.Marker(
            [record['Lat'], record['Long']],
            icon=folium.Icon(color='white', icon_color=record['marker_color']),
            popup=f"Launch Site: {record['Launch_Site']}<br>Date: {record['Date']}<br>Outcome: {'Success' if record['class'] == 1 else 'Failure'}"
        )
        marker_cluster.add_child(marker)
    
    # Add distance calculations and markers
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    # Add coastline distance marker for CCAFS SLC 40
    launch_site_lat = 28.561857
    launch_site_lon = -80.577366
    coastline_lat = 28.56367
    coastline_lon = -80.57163
    
    distance_coastline = calculate_distance(launch_site_lat, launch_site_lon, coastline_lat, coastline_lon)
    
    # Create coastline distance marker
    distance_marker = folium.Marker(
        [coastline_lat, coastline_lon],
        icon=DivIcon(
            icon_size=(20, 20),
            icon_anchor=(0, 0),
            html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % "{:10.2f} KM".format(distance_coastline),
        )
    )
    
    # Add the distance marker to the map
    site_map.add_child(distance_marker)
    
    # Draw a line between launch site and coastline
    coordinates = [[launch_site_lat, launch_site_lon], [coastline_lat, coastline_lon]]
    lines = folium.PolyLine(locations=coordinates, weight=1)
    site_map.add_child(lines)
    
    # Add city distance marker (Cocoa Beach)
    city_lat = 28.3200
    city_lon = -80.6100
    distance_city = calculate_distance(launch_site_lat, launch_site_lon, city_lat, city_lon)
    
    # Create city marker
    city_marker = folium.Marker(
        [city_lat, city_lon],
        icon=DivIcon(
            icon_size=(20, 20),
            icon_anchor=(0, 0),
            html='<div style="font-size: 12; color:#blue;"><b>%s</b></div>' % "{:10.2f} KM".format(distance_city),
        )
    )
    
    # Create line to city
    city_coordinates = [[launch_site_lat, launch_site_lon], [city_lat, city_lon]]
    city_lines = folium.PolyLine(locations=city_coordinates, weight=1, color='blue')
    
    # Add city marker and line to map
    site_map.add_child(city_marker)
    site_map.add_child(city_lines)
    
    # Add mouse position plugin
    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
    mouse_position = plugins.MousePosition(
        position='topright',
        separator=' | ',
        empty_string='NaN',
        lng_first=True,
        num_digits=20,
        prefix='Coordinates:',
        lat_formatter=formatter,
        lng_formatter=formatter,
    )
    site_map.add_child(mouse_position)
    
    # Add fullscreen plugin
    plugins.Fullscreen().add_to(site_map)
    
    # Add layer control
    folium.LayerControl().add_to(site_map)
    
    # Print summary information
    print("=== SpaceX Interactive Map Summary ===")
    print(f"Launch Sites: {len(launch_sites_df)}")
    print(f"Launch Records: {len(spacex_df)}")
    print(f"Success Rate: {spacex_df['class'].mean():.2%}")
    print(f"Distance to Coastline: {distance_coastline:.2f} km")
    print(f"Distance to City: {distance_city:.2f} km")
    
    # Save the map
    site_map.save('spacex_launch_sites_map.html')
    print("\nMap saved as 'spacex_launch_sites_map.html'")
    
    return site_map

def create_advanced_spacex_map():
    """
    Create an advanced SpaceX map with additional features
    """
    
    # Create base map with different tile layers
    m = folium.Map(
        location=[28.573255, -80.646895],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add different tile layers
    folium.TileLayer('Stamen Terrain').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.TileLayer('Stamen Watercolor').add_to(m)
    
    # Launch sites with detailed information
    launch_sites = [
        {
            'name': 'CCAFS SLC 40',
            'lat': 28.561857,
            'lon': -80.577366,
            'description': 'Cape Canaveral Air Force Station<br>Space Launch Complex 40<br>Primary SpaceX launch site'
        },
        {
            'name': 'KSC LC 39A',
            'lat': 28.573255,
            'lon': -80.646895,
            'description': 'Kennedy Space Center<br>Launch Complex 39A<br>Historic Apollo launch pad'
        },
        {
            'name': 'VAFB SLC 4E',
            'lat': 34.632834,
            'lon': -120.610745,
            'description': 'Vandenberg Air Force Base<br>Space Launch Complex 4E<br>Polar orbit launches'
        }
    ]
    
    # Add launch sites with custom icons
    for site in launch_sites:
        # Create custom icon
        icon = folium.Icon(
            color='red',
            icon='rocket',
            prefix='fa'
        )
        
        # Add marker
        folium.Marker(
            [site['lat'], site['lon']],
            popup=folium.Popup(site['description'], max_width=300),
            tooltip=site['name'],
            icon=icon
        ).add_to(m)
        
        # Add circle around launch site
        folium.Circle(
            [site['lat'], site['lon']],
            radius=5000,  # 5km radius
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.1,
            popup=f"{site['name']} - 5km radius"
        ).add_to(m)
    
    # Add success/failure markers with different colors
    success_marker = folium.Icon(color='green', icon='check', prefix='fa')
    failure_marker = folium.Icon(color='red', icon='times', prefix='fa')
    
    # Sample launch outcomes
    launch_outcomes = [
        {'lat': 28.561857, 'lon': -80.577366, 'outcome': 'Success', 'date': '2020-01-01'},
        {'lat': 28.561857, 'lon': -80.577366, 'outcome': 'Failure', 'date': '2019-12-01'},
        {'lat': 28.573255, 'lon': -80.646895, 'outcome': 'Success', 'date': '2020-02-01'},
        {'lat': 34.632834, 'lon': -120.610745, 'outcome': 'Success', 'date': '2020-03-01'},
    ]
    
    for launch in launch_outcomes:
        icon = success_marker if launch['outcome'] == 'Success' else failure_marker
        folium.Marker(
            [launch['lat'], launch['lon']],
            popup=f"Outcome: {launch['outcome']}<br>Date: {launch['date']}",
            icon=icon
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add plugins
    plugins.Fullscreen().add_to(m)
    plugins.MeasureControl().add_to(m)
    
    # Save advanced map
    m.save('spacex_advanced_map.html')
    print("Advanced map saved as 'spacex_advanced_map.html'")
    
    return m

if __name__ == "__main__":
    print("Creating SpaceX Interactive Maps...")
    print("=" * 50)
    
    # Create basic interactive map
    print("\n1. Creating basic interactive map...")
    basic_map = create_spacex_interactive_map()
    
    # Create advanced map
    print("\n2. Creating advanced map with additional features...")
    advanced_map = create_advanced_spacex_map()
    
    print("\n" + "=" * 50)
    print("Maps created successfully!")
    print("Files generated:")
    print("- spacex_launch_sites_map.html")
    print("- spacex_advanced_map.html")
    print("\nOpen these files in your web browser to view the interactive maps.")