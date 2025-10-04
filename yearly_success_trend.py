"""
SpaceX EDA - Launch Success Yearly Trend
Individual chart for Launch Success Yearly Trend analysis
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

def grafica_yearly_success_trend(df):
    """
    Crea gráfica de línea: Launch Success Yearly Trend
    """
    print("Creando gráfica: Launch Success Yearly Trend...")
    
    plt.figure(figsize=(14, 8))
    
    # Calcular tasa de éxito anual
    yearly_success = df.groupby('launch_year')['success'].agg(['mean', 'count']).reset_index()
    yearly_success.columns = ['year', 'success_rate', 'total_launches']
    yearly_success = yearly_success.sort_values('year')
    
    # Crear gráfica de línea
    plt.plot(yearly_success['year'], 
             yearly_success['success_rate'], 
             marker='o', 
             linewidth=3, 
             markersize=8, 
             color='#2E8B57', 
             alpha=0.8)
    
    # Agregar puntos con tamaño basado en número de lanzamientos
    scatter = plt.scatter(yearly_success['year'], 
                         yearly_success['success_rate'], 
                         s=yearly_success['total_launches']*20,  # Tamaño basado en número de lanzamientos
                         alpha=0.6, 
                         color='#FF6B6B', 
                         edgecolors='black', 
                         linewidth=1)
    
    plt.xlabel('Launch Year', fontsize=12, fontweight='bold')
    plt.ylabel('Success Rate', fontsize=12, fontweight='bold')
    plt.title('Launch Success Yearly Trend\nSpaceX Launches', 
              fontsize=14, fontweight='bold')
    
    # Configurar ejes
    plt.ylim(0, 1.1)
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0], ['0%', '20%', '40%', '60%', '80%', '100%'])
    plt.grid(True, alpha=0.3)
    
    # Agregar línea de referencia al 100%
    plt.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='100% Success')
    
    # Agregar valores en los puntos
    for i, (year, rate, count) in enumerate(zip(yearly_success['year'], 
                                                yearly_success['success_rate'], 
                                                yearly_success['total_launches'])):
        plt.annotate(f'{rate:.1%}\n({count})', 
                    (year, rate), 
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center', 
                    fontsize=9, 
                    fontweight='bold')
    
    # Agregar leyenda
    plt.legend(['Success Rate Trend', '100% Success Line', 'Launch Count (size)'], 
               loc='upper left')
    
    plt.tight_layout()
    plt.show()
    
    # Estadísticas adicionales
    print("\n📈 Yearly Success Rate Statistics:")
    for _, row in yearly_success.iterrows():
        print(f"{int(row['year'])}: {row['success_rate']:.1%} ({int(row['total_launches'])} launches)")
    
    # Calcular tendencia general
    overall_trend = yearly_success['success_rate'].mean()
    print(f"\n📊 Overall Average Success Rate: {overall_trend:.1%}")
    print(f"📈 Best Year: {yearly_success.loc[yearly_success['success_rate'].idxmax(), 'year']} ({yearly_success['success_rate'].max():.1%})")
    print(f"📉 Worst Year: {yearly_success.loc[yearly_success['success_rate'].idxmin(), 'year']} ({yearly_success['success_rate'].min():.1%})")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 LAUNCH SUCCESS YEARLY TREND ANALYSIS")
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
    grafica_yearly_success_trend(df)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()



