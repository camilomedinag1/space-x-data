"""
SpaceX EDA - Success Rate vs Orbit Type
Individual chart for Success Rate vs Orbit Type analysis
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

def grafica_success_rate_vs_orbit(df):
    """
    Crea gráfica de barras: Success Rate vs Orbit Type
    """
    print("Creando gráfica: Success Rate vs Orbit Type...")
    
    # Calcular tasa de éxito por tipo de órbita
    success_rate = df.groupby('orbit_type')['success'].agg(['mean', 'count']).reset_index()
    success_rate.columns = ['orbit_type', 'success_rate', 'total_launches']
    success_rate = success_rate.sort_values('success_rate', ascending=False)
    
    plt.figure(figsize=(14, 8))
    
    # Crear gráfica de barras
    bars = plt.bar(range(len(success_rate)), 
                   success_rate['success_rate'], 
                   color=plt.cm.viridis(np.linspace(0, 1, len(success_rate))))
    
    # Personalizar gráfica
    plt.xlabel('Orbit Type', fontsize=12, fontweight='bold')
    plt.ylabel('Success Rate', fontsize=12, fontweight='bold')
    plt.title('Success Rate vs Orbit Type\nSpaceX Launches', 
              fontsize=14, fontweight='bold')
    
    # Configurar ejes
    plt.xticks(range(len(success_rate)), success_rate['orbit_type'], rotation=45)
    plt.ylim(0, 1.1)
    
    # Agregar valores en las barras
    for i, (bar, rate, count) in enumerate(zip(bars, success_rate['success_rate'], success_rate['total_launches'])):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{rate:.2f}\n({count} launches)', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Mostrar estadísticas detalladas
    print("\n📊 Success Rate by Orbit Type:")
    for _, row in success_rate.iterrows():
        print(f"{row['orbit_type']}: {row['success_rate']:.2%} ({row['total_launches']} launches)")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SUCCESS RATE VS ORBIT TYPE ANALYSIS")
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
    grafica_success_rate_vs_orbit(df)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()



