"""
SpaceX EDA - Average Payload Mass by F9 v1.1
Calculate the average payload mass carried by booster version F9 v1.1
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

def calcular_payload_f9_v11(launches):
    """
    Calcula la masa promedio de payloads para F9 v1.1
    """
    print("Calculando masa promedio de payloads para F9 v1.1...")
    
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
    
    # Verificar qué versiones de Falcon 9 existen
    print("Verificando versiones de Falcon 9 disponibles...")
    falcon9_versions = set()
    for _, row in df.iterrows():
        rocket_info = row['rocket_info']
        if rocket_info and 'Falcon 9' in rocket_info.get('name', ''):
            falcon9_versions.add(rocket_info.get('name', ''))
    
    print(f"Versiones de Falcon 9 encontradas: {list(falcon9_versions)}")
    
    # Filtrar lanzamientos de Falcon 9 (cualquier versión)
    f9_launches = []
    
    for _, row in df.iterrows():
        rocket_info = row['rocket_info']
        if rocket_info and 'Falcon 9' in rocket_info.get('name', ''):
            f9_launches.append(row)
    
    if len(f9_launches) == 0:
        print("❌ No se encontraron lanzamientos de Falcon 9")
        return None, None, None
    
    print(f"✅ Lanzamientos de Falcon 9 encontrados: {len(f9_launches)}")
    
    # Calcular masa total de payloads para Falcon 9
    total_payload_mass = 0
    valid_launches = 0
    launch_details = []
    
    for launch in f9_launches:
        launch_payloads = launch['payload_info']
        launch_total_mass = 0
        
        for payload in launch_payloads:
            mass = payload.get('mass_kg', 0)
            if mass is not None and mass > 0:
                launch_total_mass += mass
        
        if launch_total_mass > 0:
            total_payload_mass += launch_total_mass
            valid_launches += 1
            launch_details.append({
                'flight_number': launch['flight_number'],
                'name': launch['name'],
                'date': launch['date_utc'][:10],
                'payload_mass': launch_total_mass,
                'success': launch['success']
            })
    
    if valid_launches == 0:
        print("❌ No se encontraron lanzamientos válidos con masa de payload")
        return None, None, None
    
    average_payload_mass = total_payload_mass / valid_launches
    
    return average_payload_mass, launch_details, f9_launches

def mostrar_resultados_f9_v11(avg_mass, launch_details, f9_launches):
    """
    Muestra los resultados del cálculo de masa promedio para Falcon 9
    """
    print("\n" + "="*80)
    print("🚀 SPACEX FALCON 9 AVERAGE PAYLOAD MASS CALCULATION")
    print("="*80)
    
    if avg_mass is None:
        print("❌ No se pudieron calcular los resultados")
        return
    
    print(f"\n📊 RESULTS:")
    print(f"   Average Payload Mass: {avg_mass:,.2f} kg")
    print(f"   Average Payload Mass: {avg_mass/1000:.2f} metric tons")
    print(f"   Total Falcon 9 launches: {len(f9_launches)}")
    print(f"   Valid launches with payload data: {len(launch_details)}")
    
    if len(launch_details) > 0:
        success_rate = sum(1 for launch in launch_details if launch['success']) / len(launch_details) * 100
        print(f"   Success rate: {success_rate:.1f}%")
        
        # Estadísticas adicionales
        payload_masses = [launch['payload_mass'] for launch in launch_details]
        print(f"\n📈 PAYLOAD MASS STATISTICS:")
        print(f"   Minimum payload mass: {np.min(payload_masses):,.2f} kg")
        print(f"   Maximum payload mass: {np.max(payload_masses):,.2f} kg")
        print(f"   Median payload mass: {np.median(payload_masses):,.2f} kg")
        print(f"   Standard deviation: {np.std(payload_masses):,.2f} kg")
        
        print(f"\n📋 FALCON 9 LAUNCHES DETAILS:")
        print("-" * 80)
        
        # Mostrar los primeros 10 lanzamientos de Falcon 9
        for i, launch in enumerate(launch_details[:10], 1):
            success_icon = "✅" if launch['success'] else "❌"
            print(f"{i:2d}. Flight #{launch['flight_number']} - {launch['name']} {success_icon}")
            print(f"    Date: {launch['date']}")
            print(f"    Payload Mass: {launch['payload_mass']:,.2f} kg")
            print("-" * 80)
        
        if len(launch_details) > 10:
            print(f"... and {len(launch_details) - 10} more Falcon 9 launches")
        
        # Agrupar por año
        launch_df = pd.DataFrame(launch_details)
        launch_df['year'] = pd.to_datetime(launch_df['date']).dt.year
        yearly_stats = launch_df.groupby('year')['payload_mass'].agg(['mean', 'count']).reset_index()
        yearly_stats.columns = ['Year', 'Average Mass (kg)', 'Launch Count']
        
        print(f"\n📅 FALCON 9 PAYLOADS BY YEAR:")
        for _, row in yearly_stats.iterrows():
            print(f"   {int(row['Year'])}: {row['Average Mass (kg)']:,.2f} kg avg ({int(row['Launch Count'])} launches)")

def grafica_f9_v11_payloads(launch_details):
    """
    Crea gráfica de masa de payloads para Falcon 9
    """
    if launch_details is None or len(launch_details) == 0:
        print("⚠️ No hay datos de Falcon 9 para graficar")
        return
    
    print("Creando gráfica de payloads para Falcon 9...")
    
    # Preparar datos
    launch_df = pd.DataFrame(launch_details)
    launch_df['year'] = pd.to_datetime(launch_df['date']).dt.year
    
    plt.figure(figsize=(16, 10))
    
    # Gráfica 1: Masa de payload por lanzamiento
    plt.subplot(2, 1, 1)
    colors = ['green' if success else 'red' for success in launch_df['success']]
    plt.bar(range(len(launch_df)), launch_df['payload_mass'], color=colors, alpha=0.7)
    plt.xlabel('Launch Number', fontsize=12, fontweight='bold')
    plt.ylabel('Payload Mass (kg)', fontsize=12, fontweight='bold')
    plt.title('Falcon 9 Payload Mass by Launch\n(Green=Success, Red=Failure)', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar línea de promedio
    avg_mass = launch_df['payload_mass'].mean()
    plt.axhline(y=avg_mass, color='blue', linestyle='--', linewidth=2, 
                label=f'Average: {avg_mass:,.0f} kg')
    plt.legend()
    
    # Gráfica 2: Masa promedio por año
    plt.subplot(2, 1, 2)
    yearly_avg = launch_df.groupby('year')['payload_mass'].mean()
    plt.bar(yearly_avg.index, yearly_avg.values, color='skyblue', alpha=0.7)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Average Payload Mass (kg)', fontsize=12, fontweight='bold')
    plt.title('Falcon 9 Average Payload Mass by Year', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX FALCON 9 AVERAGE PAYLOAD MASS CALCULATION")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Calcular masa promedio de payloads para Falcon 9
    avg_mass, launch_details, f9_launches = calcular_payload_f9_v11(launches)
    
    # 3. Mostrar resultados
    mostrar_resultados_f9_v11(avg_mass, launch_details, f9_launches)
    
    # 4. Crear visualización
    grafica_f9_v11_payloads(launch_details)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
