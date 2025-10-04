"""
SpaceX EDA - Total Payload Mass for NASA
Calculate the total payload carried by boosters from NASA
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

def calcular_payload_nasa(launches):
    """
    Calcula la masa total de payloads de NASA
    """
    print("Calculando masa total de payloads de NASA...")
    
    # Obtener datos de payloads y rockets
    print("Obteniendo datos de payloads y rockets...")
    payloads_data = obtener_datos_payloads()
    rockets_data = obtener_datos_rockets()
    
    # Convertir a DataFrame
    df = pd.DataFrame(launches)
    
    # Extraer información de payloads
    def extraer_payload_info(payload_ids):
        """Extrae información de todos los payloads"""
        if not payload_ids:
            return []
        
        payload_info = []
        for payload_id in payload_ids:
            if payload_id in payloads_data:
                payload = payloads_data[payload_id]
                payload_info.append({
                    'mass_kg': payload.get('mass_kg', 0),
                    'customers': payload.get('customers', []),
                    'name': payload.get('name', 'Unknown')
                })
        return payload_info
    
    # Extraer información de rockets
    def extraer_rocket_info(rocket_id):
        """Extrae información del rocket"""
        if rocket_id and rocket_id in rockets_data:
            return rockets_data[rocket_id]
        return None
    
    # Crear nuevas columnas
    df['payload_info'] = df['payloads'].apply(extraer_payload_info)
    df['rocket_info'] = df['rocket'].apply(extraer_rocket_info)
    df['launch_year'] = pd.to_datetime(df['date_utc']).dt.year
    df['success'] = df['success'].astype(bool)
    
    # Filtrar lanzamientos exitosos
    df_successful = df[df['success'] == True].copy()
    
    print(f"✅ Lanzamientos exitosos: {len(df_successful)}")
    
    # Calcular masa total de payloads de NASA
    total_nasa_mass = 0
    nasa_launches = []
    
    for _, row in df_successful.iterrows():
        launch_payloads = row['payload_info']
        launch_nasa_mass = 0
        
        for payload in launch_payloads:
            # Verificar si el payload es de NASA
            customers = payload.get('customers', [])
            if any('NASA' in customer.upper() for customer in customers):
                mass = payload.get('mass_kg', 0)
                if mass is not None and mass > 0:
                    launch_nasa_mass += mass
                    total_nasa_mass += mass
        
        if launch_nasa_mass > 0:
            nasa_launches.append({
                'flight_number': row['flight_number'],
                'name': row['name'],
                'date': row['date_utc'][:10],
                'nasa_mass': launch_nasa_mass,
                'rocket_name': row['rocket_info'].get('name', 'Unknown') if row['rocket_info'] else 'Unknown'
            })
    
    return total_nasa_mass, nasa_launches, df_successful

def mostrar_resultados_nasa(total_mass, nasa_launches, df_successful):
    """
    Muestra los resultados del cálculo de masa de NASA
    """
    print("\n" + "="*80)
    print("🚀 SPACEX NASA PAYLOAD MASS CALCULATION")
    print("="*80)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total NASA Payload Mass: {total_mass:,.2f} kg")
    print(f"   Total NASA Payload Mass: {total_mass/1000:.2f} metric tons")
    print(f"   Number of NASA launches: {len(nasa_launches)}")
    print(f"   Total successful launches: {len(df_successful)}")
    
    if len(nasa_launches) > 0:
        nasa_percentage = (len(nasa_launches) / len(df_successful)) * 100
        print(f"   NASA launches percentage: {nasa_percentage:.1f}%")
        
        print(f"\n📋 NASA LAUNCHES DETAILS:")
        print("-" * 80)
        
        # Mostrar los primeros 10 lanzamientos de NASA
        for i, launch in enumerate(nasa_launches[:10], 1):
            print(f"{i:2d}. Flight #{launch['flight_number']} - {launch['name']}")
            print(f"    Date: {launch['date']}")
            print(f"    Rocket: {launch['rocket_name']}")
            print(f"    NASA Payload Mass: {launch['nasa_mass']:,.2f} kg")
            print("-" * 80)
        
        if len(nasa_launches) > 10:
            print(f"... and {len(nasa_launches) - 10} more NASA launches")
        
        # Estadísticas adicionales
        nasa_masses = [launch['nasa_mass'] for launch in nasa_launches]
        print(f"\n📈 NASA PAYLOAD STATISTICS:")
        print(f"   Average NASA payload mass: {np.mean(nasa_masses):,.2f} kg")
        print(f"   Maximum NASA payload mass: {np.max(nasa_masses):,.2f} kg")
        print(f"   Minimum NASA payload mass: {np.min(nasa_masses):,.2f} kg")
        
        # Agrupar por año
        nasa_df = pd.DataFrame(nasa_launches)
        nasa_df['year'] = pd.to_datetime(nasa_df['date']).dt.year
        yearly_nasa = nasa_df.groupby('year')['nasa_mass'].agg(['sum', 'count']).reset_index()
        yearly_nasa.columns = ['Year', 'Total Mass (kg)', 'Launch Count']
        
        print(f"\n📅 NASA PAYLOADS BY YEAR:")
        for _, row in yearly_nasa.iterrows():
            print(f"   {int(row['Year'])}: {row['Total Mass (kg)']:,.2f} kg ({int(row['Launch Count'])} launches)")
    
    else:
        print("\n❌ No NASA payloads found in the data")

def grafica_nasa_payloads(nasa_launches):
    """
    Crea gráfica de masa de payloads de NASA
    """
    if len(nasa_launches) == 0:
        print("⚠️ No hay datos de NASA para graficar")
        return
    
    print("Creando gráfica de payloads de NASA...")
    
    # Preparar datos
    nasa_df = pd.DataFrame(nasa_launches)
    nasa_df['year'] = pd.to_datetime(nasa_df['date']).dt.year
    
    # Gráfica 1: Masa total por año
    plt.figure(figsize=(16, 10))
    
    plt.subplot(2, 1, 1)
    yearly_mass = nasa_df.groupby('year')['nasa_mass'].sum()
    plt.bar(yearly_mass.index, yearly_mass.values, color='#1f77b4', alpha=0.7)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('NASA Payload Mass (kg)', fontsize=12, fontweight='bold')
    plt.title('NASA Payload Mass by Year\nSpaceX Launches', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 2: Número de lanzamientos por año
    plt.subplot(2, 1, 2)
    yearly_count = nasa_df.groupby('year').size()
    plt.bar(yearly_count.index, yearly_count.values, color='#ff7f0e', alpha=0.7)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Number of NASA Launches', fontsize=12, fontweight='bold')
    plt.title('Number of NASA Launches by Year\nSpaceX Launches', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX NASA PAYLOAD MASS CALCULATION")
    print("="*50)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Calcular masa de payloads de NASA
    total_mass, nasa_launches, df_successful = calcular_payload_nasa(launches)
    
    # 3. Mostrar resultados
    mostrar_resultados_nasa(total_mass, nasa_launches, df_successful)
    
    # 4. Crear visualización
    grafica_nasa_payloads(nasa_launches)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
