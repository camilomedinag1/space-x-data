"""
SpaceX EDA - Launch Sites Beginning with 'CCA'
Find 5 records where launch sites begin with 'CCA'
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configurar el estilo de las gráficas
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def obtener_datos_spacex():
    """
    Obtiene los datos de lanzamientos desde la API de SpaceX
    """
    print("Obteniendo datos de la API de SpaceX...")
    
    url = 'https://api.spacexdata.com/v4/launches'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        launches = response.json()
        print(f"✅ Datos obtenidos exitosamente: {len(launches)} lanzamientos")
        return launches
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos: {e}")
        return None

def obtener_datos_launchpads():
    """
    Obtiene datos de launchpads desde la API de SpaceX
    """
    try:
        response = requests.get('https://api.spacexdata.com/v4/launchpads')
        response.raise_for_status()
        launchpads = response.json()
        return {launchpad['id']: launchpad for launchpad in launchpads}
    except:
        return {}

def buscar_sitios_cca(launches):
    """
    Busca sitios de lanzamiento que comiencen con 'CCA'
    """
    print("Buscando sitios de lanzamiento que comiencen con 'CCA'...")
    
    # Obtener datos de launchpads
    print("Obteniendo datos de launchpads...")
    launchpads_data = obtener_datos_launchpads()
    
    # Convertir a DataFrame
    df = pd.DataFrame(launches)
    
    # Extraer información de sitios de lanzamiento
    def extraer_launchpad_info(launchpad_id):
        """Extrae información del launchpad"""
        if launchpad_id and launchpad_id in launchpads_data:
            return launchpads_data[launchpad_id]
        return None
    
    # Crear nuevas columnas
    df['launchpad_info'] = df['launchpad'].apply(extraer_launchpad_info)
    
    # Extraer nombres de sitios
    df['launch_site_name'] = df['launchpad_info'].apply(
        lambda x: x.get('name', 'Unknown') if x else 'Unknown'
    )
    df['launch_site_full_name'] = df['launchpad_info'].apply(
        lambda x: x.get('full_name', 'Unknown') if x else 'Unknown'
    )
    df['launch_site_locality'] = df['launchpad_info'].apply(
        lambda x: x.get('locality', 'Unknown') if x else 'Unknown'
    )
    df['launch_site_region'] = df['launchpad_info'].apply(
        lambda x: x.get('region', 'Unknown') if x else 'Unknown'
    )
    
    # Filtrar sitios que comiencen con 'CCA'
    df_cca = df[df['launch_site_name'].str.startswith('CCA', na=False)].copy()
    
    print(f"✅ Sitios encontrados que comienzan con 'CCA': {len(df_cca)}")
    
    return df_cca

def mostrar_resultados_cca(df_cca):
    """
    Muestra los resultados de sitios que comienzan con 'CCA'
    """
    print("\n" + "="*80)
    print("🚀 SPACEX LAUNCH SITES BEGINNING WITH 'CCA'")
    print("="*80)
    
    if len(df_cca) == 0:
        print("❌ No se encontraron sitios de lanzamiento que comiencen con 'CCA'")
        return
    
    # Mostrar los primeros 5 registros
    print(f"\n📊 First 5 Records (Total found: {len(df_cca)}):")
    print("-" * 80)
    
    # Seleccionar columnas relevantes para mostrar
    columns_to_show = ['flight_number', 'name', 'date_utc', 'launch_site_name', 
                      'launch_site_full_name', 'launch_site_locality', 'launch_site_region', 'success']
    
    # Mostrar los primeros 5 registros
    for i, (_, row) in enumerate(df_cca.head(5).iterrows(), 1):
        print(f"\n{i}. Flight #{row['flight_number']} - {row['name']}")
        print(f"   Launch Date: {row['date_utc'][:10]}")
        print(f"   Launch Site: {row['launch_site_name']}")
        print(f"   Full Name: {row['launch_site_full_name']}")
        print(f"   Location: {row['launch_site_locality']}, {row['launch_site_region']}")
        print(f"   Success: {'✅ Yes' if row['success'] else '❌ No'}")
        print("-" * 80)
    
    # Estadísticas adicionales
    print(f"\n📈 Statistics:")
    print(f"   Total launches from 'CCA' sites: {len(df_cca)}")
    print(f"   Success rate: {df_cca['success'].mean():.1%}")
    print(f"   Date range: {df_cca['date_utc'].min()[:10]} to {df_cca['date_utc'].max()[:10]}")
    
    # Sitios únicos
    unique_sites = df_cca['launch_site_name'].unique()
    print(f"   Unique 'CCA' sites: {len(unique_sites)}")
    for site in unique_sites:
        count = len(df_cca[df_cca['launch_site_name'] == site])
        print(f"     - {site}: {count} launches")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX LAUNCH SITES BEGINNING WITH 'CCA' ANALYSIS")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Buscar sitios que comiencen con 'CCA'
    df_cca = buscar_sitios_cca(launches)
    if df_cca is None or len(df_cca) == 0:
        print("❌ No se encontraron sitios de lanzamiento que comiencen con 'CCA'")
        return
    
    # 3. Mostrar resultados
    mostrar_resultados_cca(df_cca)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()

