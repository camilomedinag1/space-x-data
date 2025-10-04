"""
SpaceX EDA - Launch Sites Pattern Search
Find records where launch sites begin with specific patterns
"""

import requests
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

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

def buscar_sitios_patron(launches, pattern):
    """
    Busca sitios de lanzamiento que comiencen con un patrón específico
    """
    print(f"Buscando sitios de lanzamiento que comiencen con '{pattern}'...")
    
    # Obtener datos de launchpads
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
    
    # Filtrar sitios que comiencen con el patrón
    df_pattern = df[df['launch_site_name'].str.startswith(pattern, na=False)].copy()
    
    print(f"✅ Sitios encontrados que comienzan con '{pattern}': {len(df_pattern)}")
    
    return df_pattern

def mostrar_resultados(df_pattern, pattern):
    """
    Muestra los resultados de sitios que comiencen con el patrón
    """
    print("\n" + "="*80)
    print(f"🚀 SPACEX LAUNCH SITES BEGINNING WITH '{pattern}'")
    print("="*80)
    
    if len(df_pattern) == 0:
        print(f"❌ No se encontraron sitios de lanzamiento que comiencen con '{pattern}'")
        print("\n📋 Available launch site names:")
        print("- CCSFS SLC 40")
        print("- KSC LC 39A") 
        print("- VAFB SLC 4E")
        print("- VAFB SLC 3W")
        print("- Kwajalein Atoll")
        print("- STLS")
        return
    
    # Mostrar los primeros 5 registros
    print(f"\n📊 First 5 Records (Total found: {len(df_pattern)}):")
    print("-" * 80)
    
    # Mostrar los primeros 5 registros
    for i, (_, row) in enumerate(df_pattern.head(5).iterrows(), 1):
        print(f"\n{i}. Flight #{row['flight_number']} - {row['name']}")
        print(f"   Launch Date: {row['date_utc'][:10]}")
        print(f"   Launch Site: {row['launch_site_name']}")
        print(f"   Full Name: {row['launch_site_full_name']}")
        print(f"   Location: {row['launch_site_locality']}, {row['launch_site_region']}")
        print(f"   Success: {'✅ Yes' if row['success'] else '❌ No'}")
        print("-" * 80)
    
    # Estadísticas adicionales
    print(f"\n📈 Statistics:")
    print(f"   Total launches from '{pattern}' sites: {len(df_pattern)}")
    print(f"   Success rate: {df_pattern['success'].mean():.1%}")
    print(f"   Date range: {df_pattern['date_utc'].min()[:10]} to {df_pattern['date_utc'].max()[:10]}")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX LAUNCH SITES PATTERN SEARCH")
    print("="*50)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Buscar sitios que comiencen con 'CCA' (no existen)
    print("\n🔍 Searching for sites beginning with 'CCA':")
    df_cca = buscar_sitios_patron(launches, 'CCA')
    mostrar_resultados(df_cca, 'CCA')
    
    # 3. Buscar sitios que comiencen con 'CCSFS' (existen)
    print("\n🔍 Searching for sites beginning with 'CCSFS':")
    df_ccsfs = buscar_sitios_patron(launches, 'CCSFS')
    mostrar_resultados(df_ccsfs, 'CCSFS')
    
    # 4. Buscar sitios que comiencen con 'KSC' (existen)
    print("\n🔍 Searching for sites beginning with 'KSC':")
    df_ksc = buscar_sitios_patron(launches, 'KSC')
    mostrar_resultados(df_ksc, 'KSC')
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()

