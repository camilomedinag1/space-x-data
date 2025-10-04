"""
SpaceX EDA - Flight Number vs Orbit Type
Individual chart for Flight Number vs Orbit Type analysis
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

def obtener_datos_payloads():
    """
    Obtiene datos de payloads desde la API de SpaceX
    """
    try:
        response = requests.get('https://api.spacexdata.com/v4/payloads')
        response.raise_for_status()
        payloads = response.json()
        return {payload['id']: payload for payload in payloads}
    except:
        return {}

def procesar_datos(launches):
    """
    Procesa los datos de lanzamientos y extrae información relevante
    """
    print("Procesando datos...")
    
    # Obtener datos de payloads
    print("Obteniendo datos de payloads...")
    payloads_data = obtener_datos_payloads()
    
    # Convertir a DataFrame
    df = pd.DataFrame(launches)
    
    # Extraer información de payloads
    def extraer_orbit(payload_ids):
        """Extrae el tipo de órbita del primer payload"""
        if payload_ids and len(payload_ids) > 0:
            payload_id = payload_ids[0]
            if payload_id in payloads_data:
                return payloads_data[payload_id].get('orbit', 'Unknown')
        return 'Unknown'
    
    # Crear nuevas columnas
    df['orbit_type'] = df['payloads'].apply(extraer_orbit)
    df['launch_year'] = pd.to_datetime(df['date_utc']).dt.year
    df['success'] = df['success'].astype(bool)
    
    # Filtrar datos válidos
    df_clean = df[df['orbit_type'] != 'Unknown'].copy()
    
    print(f"✅ Datos procesados: {len(df_clean)} lanzamientos válidos")
    print(f"📊 Tipos de órbita encontrados: {df_clean['orbit_type'].nunique()}")
    
    return df_clean

def grafica_flight_vs_orbit(df):
    """
    Crea gráfica de dispersión: Flight Number vs Orbit Type
    """
    print("Creando gráfica: Flight Number vs Orbit Type...")
    
    plt.figure(figsize=(14, 8))
    
    # Crear gráfica de dispersión con colores por tipo de órbita
    orbit_types = df['orbit_type'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(orbit_types)))
    
    for i, orbit in enumerate(orbit_types):
        mask = df['orbit_type'] == orbit
        plt.scatter(df[mask]['flight_number'], 
                   [i] * mask.sum(),  # Posición Y basada en el índice del tipo de órbita
                   c=[colors[i]], 
                   label=orbit, 
                   alpha=0.7, 
                   s=60)
    
    plt.xlabel('Flight Number', fontsize=12, fontweight='bold')
    plt.ylabel('Orbit Type', fontsize=12, fontweight='bold')
    plt.title('Flight Number vs Orbit Type\nSpaceX Launches', 
              fontsize=14, fontweight='bold')
    
    # Configurar ejes
    plt.yticks(range(len(orbit_types)), orbit_types)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Ajustar layout
    plt.tight_layout()
    plt.show()
    
    # Estadísticas adicionales
    print("\n📈 Estadísticas por tipo de órbita:")
    stats = df.groupby('orbit_type')['flight_number'].agg(['count', 'min', 'max', 'mean']).round(2)
    print(stats)

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 FLIGHT NUMBER VS ORBIT TYPE ANALYSIS")
    print("="*50)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Procesar datos
    df = procesar_datos(launches)
    if df is None or len(df) == 0:
        print("❌ No se pudieron procesar los datos")
        return
    
    # 3. Crear visualización
    grafica_flight_vs_orbit(df)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()



