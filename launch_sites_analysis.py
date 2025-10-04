"""
SpaceX EDA - Launch Sites Analysis
Find all unique launch site names from SpaceX launches
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

def analizar_sitios_lanzamiento(launches):
    """
    Analiza los sitios de lanzamiento únicos
    """
    print("Analizando sitios de lanzamiento...")
    
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
    
    # Filtrar datos válidos
    df_clean = df[df['launch_site_name'] != 'Unknown'].copy()
    
    print(f"✅ Datos procesados: {len(df_clean)} lanzamientos con sitios válidos")
    
    return df_clean

def mostrar_sitios_unicos(df):
    """
    Muestra todos los sitios de lanzamiento únicos
    """
    print("\n" + "="*80)
    print("🚀 SPACEX LAUNCH SITES - UNIQUE SITE NAMES")
    print("="*80)
    
    # Obtener sitios únicos
    sitios_unicos = df.groupby(['launch_site_name', 'launch_site_full_name', 'launch_site_locality', 'launch_site_region']).size().reset_index()
    sitios_unicos.columns = ['Site Name', 'Full Name', 'Locality', 'Region', 'Launch Count']
    sitios_unicos = sitios_unicos.sort_values('Launch Count', ascending=False)
    
    print(f"\n📊 Total Unique Launch Sites: {len(sitios_unicos)}")
    print(f"🚀 Total Launches Analyzed: {len(df)}")
    
    print("\n📍 LAUNCH SITES DETAILS:")
    print("-" * 80)
    
    for i, (_, row) in enumerate(sitios_unicos.iterrows(), 1):
        print(f"{i:2d}. {row['Site Name']}")
        print(f"    Full Name: {row['Full Name']}")
        print(f"    Location: {row['Locality']}, {row['Region']}")
        print(f"    Total Launches: {row['Launch Count']}")
        print()
    
    return sitios_unicos

def grafica_sitios_lanzamiento(df, sitios_unicos):
    """
    Crea gráfica de barras: Launch Sites Distribution
    """
    print("Creando gráfica: Launch Sites Distribution...")
    
    plt.figure(figsize=(16, 10))
    
    # Crear gráfica de barras
    bars = plt.bar(range(len(sitios_unicos)), 
                   sitios_unicos['Launch Count'], 
                   color=plt.cm.viridis(np.linspace(0, 1, len(sitios_unicos))))
    
    # Personalizar gráfica
    plt.xlabel('Launch Site', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Launches', fontsize=12, fontweight='bold')
    plt.title('SpaceX Launch Sites Distribution\nTotal Launches by Site', 
              fontsize=14, fontweight='bold')
    
    # Configurar ejes
    plt.xticks(range(len(sitios_unicos)), sitios_unicos['Site Name'], rotation=45, ha='right')
    
    # Agregar valores en las barras
    for i, (bar, count) in enumerate(zip(bars, sitios_unicos['Launch Count'])):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{count}', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Estadísticas adicionales
    print("\n📈 Launch Site Statistics:")
    total_launches = sitios_unicos['Launch Count'].sum()
    for _, row in sitios_unicos.iterrows():
        percentage = (row['Launch Count'] / total_launches) * 100
        print(f"{row['Site Name']}: {row['Launch Count']} launches ({percentage:.1f}%)")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX LAUNCH SITES ANALYSIS")
    print("="*50)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Analizar sitios de lanzamiento
    df = analizar_sitios_lanzamiento(launches)
    if df is None or len(df) == 0:
        print("❌ No se pudieron procesar los datos")
        return
    
    # 3. Mostrar sitios únicos
    sitios_unicos = mostrar_sitios_unicos(df)
    
    # 4. Crear visualización
    grafica_sitios_lanzamiento(df, sitios_unicos)
    
    print("\n✅ Análisis completado exitosamente!")
    print("🎯 Todos los sitios de lanzamiento únicos han sido identificados")

if __name__ == "__main__":
    main()


