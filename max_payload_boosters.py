"""
SpaceX EDA - Boosters Carried Maximum Payload
List the names of the booster which have carried the maximum payload mass
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

def buscar_max_payload_boosters(launches):
    """
    Busca los boosters que han transportado la masa máxima de payload
    """
    print("Buscando boosters con máxima masa de payload...")
    
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
    
    # Calcular masa total de payload para cada lanzamiento
    launch_payloads = []
    
    for _, row in df.iterrows():
        total_payload_mass = 0
        payload_names = []
        
        for payload in row['payload_info']:
            mass = payload.get('mass_kg', 0)
            if mass is not None and mass > 0:
                total_payload_mass += mass
                payload_names.append(payload.get('name', 'Unknown'))
        
        if total_payload_mass > 0:
            launch_payloads.append({
                'flight_number': row['flight_number'],
                'name': row['name'],
                'date_utc': row['date_utc'],
                'payload_mass': total_payload_mass,
                'payload_names': payload_names,
                'rocket_name': row['rocket_info'].get('name', 'Unknown') if row['rocket_info'] else 'Unknown',
                'success': row['success']
            })
    
    # Encontrar la masa máxima
    if not launch_payloads:
        print("❌ No se encontraron datos de payload")
        return None, None
    
    max_payload_mass = max(launch['payload_mass'] for launch in launch_payloads)
    
    # Encontrar todos los lanzamientos con la masa máxima
    max_payload_launches = [launch for launch in launch_payloads 
                           if launch['payload_mass'] == max_payload_mass]
    
    print(f"✅ Masa máxima de payload encontrada: {max_payload_mass:,.2f} kg")
    print(f"✅ Lanzamientos con masa máxima: {len(max_payload_launches)}")
    
    return max_payload_launches, max_payload_mass

def mostrar_resultados_max_payload(launches, max_mass):
    """
    Muestra los resultados de los boosters con máxima masa de payload
    """
    print("\n" + "="*80)
    print("🚀 SPACEX BOOSTERS WITH MAXIMUM PAYLOAD MASS")
    print("="*80)
    
    if not launches:
        print("❌ No se encontraron datos")
        return
    
    print(f"\n📊 MAXIMUM PAYLOAD MASS: {max_mass:,.2f} kg ({max_mass/1000:.2f} metric tons)")
    print(f"📊 Number of launches with maximum payload: {len(launches)}")
    
    # Mostrar todos los lanzamientos con masa máxima
    print(f"\n📋 BOOSTERS WITH MAXIMUM PAYLOAD MASS:")
    print("-" * 80)
    
    for i, launch in enumerate(launches, 1):
        success_icon = "✅" if launch['success'] else "❌"
        print(f"{i}. Flight #{launch['flight_number']} - {launch['name']} {success_icon}")
        print(f"   Date: {launch['date_utc'][:10]}")
        print(f"   Rocket: {launch['rocket_name']}")
        print(f"   Payload Mass: {launch['payload_mass']:,.2f} kg")
        print(f"   Payload Names: {', '.join(launch['payload_names'])}")
        print(f"   Success: {'Yes' if launch['success'] else 'No'}")
        print("-" * 80)
    
    # Estadísticas adicionales
    rocket_names = [launch['rocket_name'] for launch in launches]
    rocket_counts = pd.Series(rocket_names).value_counts()
    
    print(f"\n📈 ROCKET TYPE DISTRIBUTION:")
    for rocket, count in rocket_counts.items():
        print(f"   {rocket}: {count} launches")
    
    # Análisis por año
    launch_df = pd.DataFrame(launches)
    launch_df['year'] = pd.to_datetime(launch_df['date_utc']).dt.year
    yearly_launches = launch_df.groupby('year').size().reset_index()
    yearly_launches.columns = ['Year', 'Launch Count']
    
    print(f"\n📅 MAXIMUM PAYLOAD LAUNCHES BY YEAR:")
    for _, row in yearly_launches.iterrows():
        print(f"   {int(row['Year'])}: {int(row['Launch Count'])} launches")
    
    # Análisis de éxito
    success_count = sum(1 for launch in launches if launch['success'])
    success_rate = (success_count / len(launches)) * 100
    print(f"\n📊 SUCCESS RATE: {success_rate:.1f}% ({success_count}/{len(launches)} successful)")

def grafica_max_payload_boosters(launches, max_mass):
    """
    Crea gráfica de boosters con máxima masa de payload
    """
    if not launches:
        print("⚠️ No hay datos para graficar")
        return
    
    print("Creando gráfica de boosters con máxima masa de payload...")
    
    # Preparar datos
    launch_df = pd.DataFrame(launches)
    launch_df['year'] = pd.to_datetime(launch_df['date_utc']).dt.year
    
    plt.figure(figsize=(16, 10))
    
    # Gráfica 1: Distribución por tipo de rocket
    plt.subplot(2, 2, 1)
    rocket_counts = launch_df['rocket_name'].value_counts()
    colors = plt.cm.Set3(np.linspace(0, 1, len(rocket_counts)))
    plt.pie(rocket_counts.values, labels=rocket_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Rocket Types with Maximum Payload', fontsize=14, fontweight='bold')
    
    # Gráfica 2: Lanzamientos por año
    plt.subplot(2, 2, 2)
    yearly_launches = launch_df.groupby('year').size()
    plt.bar(yearly_launches.index, yearly_launches.values, color='skyblue', alpha=0.7)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Launches', fontsize=12, fontweight='bold')
    plt.title('Maximum Payload Launches by Year', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 3: Comparación de masa de payload
    plt.subplot(2, 2, 3)
    colors = ['green' if success else 'red' for success in launch_df['success']]
    plt.bar(range(len(launch_df)), launch_df['payload_mass'], color=colors, alpha=0.7)
    plt.xlabel('Launch Number', fontsize=12, fontweight='bold')
    plt.ylabel('Payload Mass (kg)', fontsize=12, fontweight='bold')
    plt.title('Maximum Payload Mass by Launch\n(Green=Success, Red=Failure)', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar línea de referencia
    plt.axhline(y=max_mass, color='blue', linestyle='--', linewidth=2, 
                label=f'Max Payload: {max_mass:,.0f} kg')
    plt.legend()
    
    # Gráfica 4: Análisis de éxito
    plt.subplot(2, 2, 4)
    success_data = [sum(1 for launch in launches if launch['success']), 
                   sum(1 for launch in launches if not launch['success'])]
    labels = ['Successful', 'Failed']
    colors = ['#2ca02c', '#d62728']
    
    plt.pie(success_data, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title('Success Rate for Maximum Payload Launches', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX BOOSTERS WITH MAXIMUM PAYLOAD MASS")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Buscar boosters con máxima masa de payload
    max_payload_launches, max_mass = buscar_max_payload_boosters(launches)
    
    if max_payload_launches is None:
        return
    
    # 3. Mostrar resultados
    mostrar_resultados_max_payload(max_payload_launches, max_mass)
    
    # 4. Crear visualización
    grafica_max_payload_boosters(max_payload_launches, max_mass)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
