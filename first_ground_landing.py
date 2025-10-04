"""
SpaceX EDA - First Successful Ground Landing Date
Find the dates of the first successful landing outcome on ground pad
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

def buscar_primer_aterrizaje_exitoso(launches):
    """
    Busca el primer aterrizaje exitoso en tierra
    """
    print("Buscando el primer aterrizaje exitoso en tierra...")
    
    # Convertir a DataFrame
    df = pd.DataFrame(launches)
    
    # Filtrar lanzamientos con información de cores
    df_with_cores = df[df['cores'].notna()].copy()
    
    print(f"✅ Lanzamientos con información de cores: {len(df_with_cores)}")
    
    # Buscar aterrizajes exitosos en tierra
    successful_ground_landings = []
    
    for _, row in df_with_cores.iterrows():
        cores = row['cores']
        if cores and len(cores) > 0:
            for core in cores:
                # Verificar si el aterrizaje fue exitoso y en tierra
                landing_success = core.get('landing_success', False)
                landing_type = core.get('landing_type', '')
                
                # Tipos de aterrizaje en tierra
                ground_landing_types = ['RTLS', 'ASDS', 'Ocean']
                
                if landing_success and landing_type in ground_landing_types:
                    successful_ground_landings.append({
                        'flight_number': row['flight_number'],
                        'name': row['name'],
                        'date_utc': row['date_utc'],
                        'date_local': row['date_local'],
                        'landing_type': landing_type,
                        'landing_success': landing_success,
                        'landpad': core.get('landpad', 'Unknown'),
                        'reused': core.get('reused', False)
                    })
    
    # Ordenar por fecha
    successful_ground_landings.sort(key=lambda x: x['date_utc'])
    
    print(f"✅ Aterrizajes exitosos en tierra encontrados: {len(successful_ground_landings)}")
    
    return successful_ground_landings

def mostrar_resultados_aterrizaje(landings):
    """
    Muestra los resultados del primer aterrizaje exitoso
    """
    print("\n" + "="*80)
    print("🚀 SPACEX FIRST SUCCESSFUL GROUND LANDING")
    print("="*80)
    
    if len(landings) == 0:
        print("❌ No se encontraron aterrizajes exitosos en tierra")
        return
    
    # Primer aterrizaje exitoso
    first_landing = landings[0]
    
    print(f"\n📊 FIRST SUCCESSFUL GROUND LANDING:")
    print(f"   Flight Number: #{first_landing['flight_number']}")
    print(f"   Mission Name: {first_landing['name']}")
    print(f"   Date (UTC): {first_landing['date_utc'][:10]}")
    print(f"   Date (Local): {first_landing['date_local'][:10]}")
    print(f"   Landing Type: {first_landing['landing_type']}")
    print(f"   Landing Success: {'✅ Yes' if first_landing['landing_success'] else '❌ No'}")
    print(f"   Landpad: {first_landing['landpad']}")
    print(f"   Reused Core: {'Yes' if first_landing['reused'] else 'No'}")
    
    # Mostrar los primeros 5 aterrizajes exitosos
    print(f"\n📋 FIRST 5 SUCCESSFUL GROUND LANDINGS:")
    print("-" * 80)
    
    for i, landing in enumerate(landings[:5], 1):
        print(f"{i}. Flight #{landing['flight_number']} - {landing['name']}")
        print(f"   Date: {landing['date_utc'][:10]}")
        print(f"   Landing Type: {landing['landing_type']}")
        print(f"   Landpad: {landing['landpad']}")
        print(f"   Reused: {'Yes' if landing['reused'] else 'No'}")
        print("-" * 80)
    
    # Estadísticas adicionales
    landing_types = {}
    for landing in landings:
        landing_type = landing['landing_type']
        landing_types[landing_type] = landing_types.get(landing_type, 0) + 1
    
    print(f"\n📈 LANDING TYPE STATISTICS:")
    for landing_type, count in landing_types.items():
        print(f"   {landing_type}: {count} successful landings")
    
    # Agrupar por año
    landing_df = pd.DataFrame(landings)
    landing_df['year'] = pd.to_datetime(landing_df['date_utc']).dt.year
    yearly_landings = landing_df.groupby('year').size().reset_index()
    yearly_landings.columns = ['Year', 'Landing Count']
    
    print(f"\n📅 SUCCESSFUL GROUND LANDINGS BY YEAR:")
    for _, row in yearly_landings.iterrows():
        print(f"   {int(row['Year'])}: {int(row['Landing Count'])} landings")

def grafica_aterrizajes_exitosos(landings):
    """
    Crea gráfica de aterrizajes exitosos
    """
    if len(landings) == 0:
        print("⚠️ No hay datos de aterrizajes para graficar")
        return
    
    print("Creando gráfica de aterrizajes exitosos...")
    
    # Preparar datos
    landing_df = pd.DataFrame(landings)
    landing_df['year'] = pd.to_datetime(landing_df['date_utc']).dt.year
    landing_df['month'] = pd.to_datetime(landing_df['date_utc']).dt.month
    
    plt.figure(figsize=(16, 10))
    
    # Gráfica 1: Aterrizajes por año
    plt.subplot(2, 1, 1)
    yearly_landings = landing_df.groupby('year').size()
    plt.bar(yearly_landings.index, yearly_landings.values, color='green', alpha=0.7)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Successful Ground Landings', fontsize=12, fontweight='bold')
    plt.title('SpaceX Successful Ground Landings by Year', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 2: Tipos de aterrizaje
    plt.subplot(2, 1, 2)
    landing_types = landing_df['landing_type'].value_counts()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    plt.pie(landing_types.values, labels=landing_types.index, autopct='%1.1f%%', 
            colors=colors[:len(landing_types)], startangle=90)
    plt.title('Distribution of Landing Types', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX FIRST SUCCESSFUL GROUND LANDING ANALYSIS")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Buscar primer aterrizaje exitoso
    landings = buscar_primer_aterrizaje_exitoso(launches)
    
    # 3. Mostrar resultados
    mostrar_resultados_aterrizaje(landings)
    
    # 4. Crear visualización
    grafica_aterrizajes_exitosos(landings)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()

