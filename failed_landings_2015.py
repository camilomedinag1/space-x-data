"""
SpaceX EDA - 2015 Launch Records
List the failed landing_outcomes in drone ship, their booster versions, and launch site names for year 2015
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

def obtener_datos_rockets():
    """
    Obtiene datos de rockets desde la API de SpaceX
    """
    try:
        response = requests.get('https://api.spacexdata.com/v4/rockets')
        response.raise_for_status()
        rockets = response.json()
        return {rocket['id']: rocket for rocket in rockets}
    except:
        return {}

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

def buscar_aterrizajes_fallidos_2015(launches):
    """
    Busca aterrizajes fallidos en drone ship para el año 2015
    """
    print("Buscando aterrizajes fallidos en drone ship para 2015...")
    
    # Obtener datos de rockets y launchpads
    print("Obteniendo datos de rockets y launchpads...")
    rockets_data = obtener_datos_rockets()
    launchpads_data = obtener_datos_launchpads()
    
    # Convertir a DataFrame
    df = pd.DataFrame(launches)
    
    # Filtrar lanzamientos de 2015
    df['launch_year'] = pd.to_datetime(df['date_utc']).dt.year
    df_2015 = df[df['launch_year'] == 2015].copy()
    
    print(f"✅ Lanzamientos de 2015: {len(df_2015)}")
    
    # Extraer información de rockets
    def extraer_rocket_info(rocket_id):
        """Extrae información del rocket"""
        if rocket_id and rocket_id in rockets_data:
            return rockets_data[rocket_id]
        return None
    
    # Extraer información de launchpads
    def extraer_launchpad_info(launchpad_id):
        """Extrae información del launchpad"""
        if launchpad_id and launchpad_id in launchpads_data:
            return launchpads_data[launchpad_id]
        return None
    
    # Crear nuevas columnas
    df_2015['rocket_info'] = df_2015['rocket'].apply(extraer_rocket_info)
    df_2015['launchpad_info'] = df_2015['launchpad'].apply(extraer_launchpad_info)
    
    # Buscar aterrizajes fallidos en drone ship
    failed_drone_ship_landings = []
    
    for _, row in df_2015.iterrows():
        cores = row['cores']
        if cores and len(cores) > 0:
            for core in cores:
                # Verificar si el aterrizaje fue fallido y en drone ship (ASDS)
                landing_success = core.get('landing_success', False)
                landing_type = core.get('landing_type', '')
                
                if not landing_success and landing_type == 'ASDS':
                    failed_drone_ship_landings.append({
                        'flight_number': row['flight_number'],
                        'name': row['name'],
                        'date_utc': row['date_utc'],
                        'date_local': row['date_local'],
                        'rocket_name': row['rocket_info'].get('name', 'Unknown') if row['rocket_info'] else 'Unknown',
                        'rocket_type': row['rocket_info'].get('type', 'Unknown') if row['rocket_info'] else 'Unknown',
                        'launch_site_name': row['launchpad_info'].get('name', 'Unknown') if row['launchpad_info'] else 'Unknown',
                        'launch_site_full_name': row['launchpad_info'].get('full_name', 'Unknown') if row['launchpad_info'] else 'Unknown',
                        'launch_site_locality': row['launchpad_info'].get('locality', 'Unknown') if row['launchpad_info'] else 'Unknown',
                        'launch_site_region': row['launchpad_info'].get('region', 'Unknown') if row['launchpad_info'] else 'Unknown',
                        'landing_type': landing_type,
                        'landing_success': landing_success,
                        'landpad': core.get('landpad', 'Unknown'),
                        'reused': core.get('reused', False),
                        'core_id': core.get('core', 'Unknown')
                    })
    
    # Ordenar por fecha
    failed_drone_ship_landings.sort(key=lambda x: x['date_utc'])
    
    print(f"✅ Aterrizajes fallidos en drone ship para 2015: {len(failed_drone_ship_landings)}")
    
    return failed_drone_ship_landings

def mostrar_resultados_2015(landings):
    """
    Muestra los resultados de aterrizajes fallidos en 2015
    """
    print("\n" + "="*80)
    print("🚀 SPACEX 2015 FAILED DRONE SHIP LANDINGS")
    print("="*80)
    
    if len(landings) == 0:
        print("❌ No se encontraron aterrizajes fallidos en drone ship para 2015")
        print("\n📋 All 2015 launches with drone ship attempts:")
        
        # Mostrar todos los lanzamientos de 2015 que intentaron aterrizaje en drone ship
        print("   (This would show all 2015 launches that attempted drone ship landings)")
        return
    
    print(f"\n📊 RESULTS:")
    print(f"   Total failed drone ship landings in 2015: {len(landings)}")
    
    # Mostrar todos los aterrizajes fallidos
    print(f"\n📋 FAILED DRONE SHIP LANDINGS IN 2015:")
    print("-" * 80)
    
    for i, landing in enumerate(landings, 1):
        print(f"{i}. Flight #{landing['flight_number']} - {landing['name']}")
        print(f"   Date (UTC): {landing['date_utc'][:10]}")
        print(f"   Date (Local): {landing['date_local'][:10]}")
        print(f"   Booster Version: {landing['rocket_name']}")
        print(f"   Booster Type: {landing['rocket_type']}")
        print(f"   Launch Site Name: {landing['launch_site_name']}")
        print(f"   Launch Site Full Name: {landing['launch_site_full_name']}")
        print(f"   Launch Site Location: {landing['launch_site_locality']}, {landing['launch_site_region']}")
        print(f"   Landing Type: {landing['landing_type']}")
        print(f"   Landing Success: {'✅ Yes' if landing['landing_success'] else '❌ No'}")
        print(f"   Landpad: {landing['landpad']}")
        print(f"   Reused: {'Yes' if landing['reused'] else 'No'}")
        print(f"   Core ID: {landing['core_id']}")
        print("-" * 80)
    
    # Estadísticas adicionales
    rocket_names = [landing['rocket_name'] for landing in landings]
    rocket_counts = pd.Series(rocket_names).value_counts()
    
    print(f"\n📈 BOOSTER VERSION DISTRIBUTION:")
    for rocket, count in rocket_counts.items():
        print(f"   {rocket}: {count} failed landings")
    
    launch_sites = [landing['launch_site_name'] for landing in landings]
    site_counts = pd.Series(launch_sites).value_counts()
    
    print(f"\n🏗️ LAUNCH SITE DISTRIBUTION:")
    for site, count in site_counts.items():
        print(f"   {site}: {count} failed landings")
    
    # Análisis por mes
    landing_df = pd.DataFrame(landings)
    landing_df['month'] = pd.to_datetime(landing_df['date_utc']).dt.month
    monthly_landings = landing_df.groupby('month').size().reset_index()
    monthly_landings.columns = ['Month', 'Failed Landing Count']
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    print(f"\n📅 FAILED LANDINGS BY MONTH:")
    for _, row in monthly_landings.iterrows():
        month_name = month_names[int(row['Month']) - 1]
        print(f"   {month_name} 2015: {int(row['Failed Landing Count'])} failed landings")

def grafica_aterrizajes_fallidos_2015(landings):
    """
    Crea gráfica de aterrizajes fallidos en 2015
    """
    if len(landings) == 0:
        print("⚠️ No hay datos de aterrizajes fallidos para graficar")
        return
    
    print("Creando gráfica de aterrizajes fallidos en 2015...")
    
    # Preparar datos
    landing_df = pd.DataFrame(landings)
    landing_df['month'] = pd.to_datetime(landing_df['date_utc']).dt.month
    
    plt.figure(figsize=(16, 10))
    
    # Gráfica 1: Distribución por booster
    plt.subplot(2, 2, 1)
    rocket_counts = landing_df['rocket_name'].value_counts()
    colors = plt.cm.Set3(np.linspace(0, 1, len(rocket_counts)))
    plt.bar(rocket_counts.index, rocket_counts.values, color=colors, alpha=0.7)
    plt.xlabel('Booster Version', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Failed Landings', fontsize=12, fontweight='bold')
    plt.title('Failed Drone Ship Landings by Booster Version (2015)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 2: Distribución por sitio de lanzamiento
    plt.subplot(2, 2, 2)
    site_counts = landing_df['launch_site_name'].value_counts()
    colors = plt.cm.viridis(np.linspace(0, 1, len(site_counts)))
    plt.bar(site_counts.index, site_counts.values, color=colors, alpha=0.7)
    plt.xlabel('Launch Site', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Failed Landings', fontsize=12, fontweight='bold')
    plt.title('Failed Drone Ship Landings by Launch Site (2015)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 3: Distribución por mes
    plt.subplot(2, 2, 3)
    monthly_landings = landing_df.groupby('month').size()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_labels = [month_names[int(month) - 1] for month in monthly_landings.index]
    
    plt.bar(month_labels, monthly_landings.values, color='red', alpha=0.7)
    plt.xlabel('Month', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Failed Landings', fontsize=12, fontweight='bold')
    plt.title('Failed Drone Ship Landings by Month (2015)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 4: Resumen general
    plt.subplot(2, 2, 4)
    total_failed = len(landings)
    total_2015_launches = 7  # Total SpaceX launches in 2015
    
    labels = ['Failed Drone Ship Landings', 'Other 2015 Launches']
    sizes = [total_failed, total_2015_launches - total_failed]
    colors = ['#d62728', '#2ca02c']
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title('2015 Launch Outcomes\n(Drone Ship Landing Failures)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX 2015 FAILED DRONE SHIP LANDINGS ANALYSIS")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Buscar aterrizajes fallidos en drone ship para 2015
    landings = buscar_aterrizajes_fallidos_2015(launches)
    
    # 3. Mostrar resultados
    mostrar_resultados_2015(landings)
    
    # 4. Crear visualización
    grafica_aterrizajes_fallidos_2015(landings)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
