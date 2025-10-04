"""
SpaceX EDA - Payload vs Launch Outcome Scatter Plot for All Sites
Create a scatter plot with range slider for payload selection
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

def procesar_datos_para_scatter(launches):
    """
    Procesa los datos para crear el scatter plot
    """
    print("Procesando datos para scatter plot...")
    
    # Obtener datos de payloads y launchpads
    print("Obteniendo datos de payloads y launchpads...")
    payloads_data = obtener_datos_payloads()
    launchpads_data = obtener_datos_launchpads()
    
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
    
    # Extraer información de launchpads
    def extraer_launchpad_info(launchpad_id):
        """Extrae información del launchpad"""
        if launchpad_id and launchpad_id in launchpads_data:
            return launchpads_data[launchpad_id]
        return None
    
    # Crear nuevas columnas
    df['payload_info'] = df['payloads'].apply(extraer_payload_info)
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
    df['success'] = df['success'].astype(bool)
    df['launch_year'] = pd.to_datetime(df['date_utc']).dt.year
    
    # Calcular masa total de payload para cada lanzamiento
    launch_data = []
    
    for _, row in df.iterrows():
        total_payload_mass = 0
        payload_names = []
        
        for payload in row['payload_info']:
            mass = payload.get('mass_kg', 0)
            if mass is not None and mass > 0:
                total_payload_mass += mass
                payload_names.append(payload.get('name', 'Unknown'))
        
        if total_payload_mass > 0:  # Solo incluir lanzamientos con masa de payload
            launch_data.append({
                'flight_number': row['flight_number'],
                'name': row['name'],
                'date_utc': row['date_utc'],
                'payload_mass': total_payload_mass,
                'payload_names': payload_names,
                'success': row['success'],
                'launch_site_name': row['launch_site_name'],
                'launch_site_full_name': row['launch_site_full_name'],
                'launch_site_locality': row['launch_site_locality'],
                'launch_site_region': row['launch_site_region'],
                'launch_year': row['launch_year']
            })
    
    # Convertir a DataFrame
    df_launches = pd.DataFrame(launch_data)
    
    print(f"✅ Lanzamientos con datos de payload: {len(df_launches)}")
    
    return df_launches

def crear_scatter_plot_interactivo(df_launches):
    """
    Crea scatter plot interactivo con diferentes rangos de payload
    """
    print("Creando scatter plot interactivo...")
    
    # Definir rangos de payload para el "slider"
    payload_ranges = [
        (0, 1000, "0-1000 kg"),
        (1000, 3000, "1000-3000 kg"),
        (3000, 6000, "3000-6000 kg"),
        (6000, 10000, "6000-10000 kg"),
        (10000, 20000, "10000+ kg")
    ]
    
    # Crear figura con múltiples subplots
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Payload vs Launch Outcome Scatter Plot for All Sites\n(Interactive Range Selection)', 
                 fontsize=16, fontweight='bold')
    
    # Colores para diferentes sitios
    sites = df_launches['launch_site_name'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(sites)))
    site_colors = {site: colors[i] for i, site in enumerate(sites)}
    
    # Crear scatter plots para diferentes rangos
    for i, (min_mass, max_mass, range_label) in enumerate(payload_ranges):
        if i >= 6:  # Solo mostrar 6 subplots
            break
            
        ax = axes[i//3, i%3] if i < 6 else axes[1, 2]
        
        # Filtrar datos por rango de payload
        if max_mass == 20000:  # Para el último rango, usar >= min_mass
            mask = df_launches['payload_mass'] >= min_mass
        else:
            mask = (df_launches['payload_mass'] >= min_mass) & (df_launches['payload_mass'] < max_mass)
        
        df_filtered = df_launches[mask]
        
        if len(df_filtered) == 0:
            ax.text(0.5, 0.5, f'No data in range\n{range_label}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'Payload Range: {range_label}', fontsize=12, fontweight='bold')
            continue
        
        # Crear scatter plot
        for site in sites:
            site_data = df_filtered[df_filtered['launch_site_name'] == site]
            if len(site_data) > 0:
                # Separar éxitos y fallos
                success_data = site_data[site_data['success'] == True]
                failure_data = site_data[site_data['success'] == False]
                
                # Plot éxitos
                if len(success_data) > 0:
                    ax.scatter(success_data['payload_mass'], 
                             [1] * len(success_data),  # Y=1 para éxitos
                             c=site_colors[site], 
                             marker='o', 
                             s=60, 
                             alpha=0.7, 
                             label=f'{site} (Success)' if len(success_data) > 0 else '',
                             edgecolors='black', linewidth=0.5)
                
                # Plot fallos
                if len(failure_data) > 0:
                    ax.scatter(failure_data['payload_mass'], 
                             [0] * len(failure_data),  # Y=0 para fallos
                             c=site_colors[site], 
                             marker='x', 
                             s=60, 
                             alpha=0.7, 
                             label=f'{site} (Failure)' if len(failure_data) > 0 else '',
                             edgecolors='black', linewidth=1)
        
        # Configurar ejes
        ax.set_xlabel('Payload Mass (kg)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Launch Outcome', fontsize=10, fontweight='bold')
        ax.set_title(f'Payload Range: {range_label}\n({len(df_filtered)} launches)', 
                    fontsize=12, fontweight='bold')
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Failure', 'Success'])
        ax.grid(True, alpha=0.3)
        
        # Agregar leyenda solo si hay datos
        if len(df_filtered) > 0:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # Crear gráfica de resumen en el último subplot
    ax_summary = axes[1, 2]
    
    # Scatter plot de resumen con todos los datos
    for site in sites:
        site_data = df_launches[df_launches['launch_site_name'] == site]
        success_data = site_data[site_data['success'] == True]
        failure_data = site_data[site_data['success'] == False]
        
        if len(success_data) > 0:
            ax_summary.scatter(success_data['payload_mass'], 
                             [1] * len(success_data),
                             c=site_colors[site], 
                             marker='o', 
                             s=40, 
                             alpha=0.6, 
                             label=f'{site} (Success)',
                             edgecolors='black', linewidth=0.3)
        
        if len(failure_data) > 0:
            ax_summary.scatter(failure_data['payload_mass'], 
                             [0] * len(failure_data),
                             c=site_colors[site], 
                             marker='x', 
                             s=40, 
                             alpha=0.6, 
                             label=f'{site} (Failure)',
                             edgecolors='black', linewidth=0.5)
    
    ax_summary.set_xlabel('Payload Mass (kg)', fontsize=10, fontweight='bold')
    ax_summary.set_ylabel('Launch Outcome', fontsize=10, fontweight='bold')
    ax_summary.set_title('All Payload Ranges\n(Complete Dataset)', fontsize=12, fontweight='bold')
    ax_summary.set_yticks([0, 1])
    ax_summary.set_yticklabels(['Failure', 'Success'])
    ax_summary.grid(True, alpha=0.3)
    ax_summary.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    plt.tight_layout()
    plt.show()

def mostrar_estadisticas_rangos(df_launches):
    """
    Muestra estadísticas por rangos de payload
    """
    print("\n" + "="*80)
    print("🚀 PAYLOAD VS LAUNCH OUTCOME STATISTICS BY RANGE")
    print("="*80)
    
    # Definir rangos
    payload_ranges = [
        (0, 1000, "0-1000 kg"),
        (1000, 3000, "1000-3000 kg"),
        (3000, 6000, "3000-6000 kg"),
        (6000, 10000, "6000-10000 kg"),
        (10000, 20000, "10000+ kg")
    ]
    
    print(f"\n📊 STATISTICS BY PAYLOAD RANGE:")
    print("-" * 80)
    
    for min_mass, max_mass, range_label in payload_ranges:
        if max_mass == 20000:
            mask = df_launches['payload_mass'] >= min_mass
        else:
            mask = (df_launches['payload_mass'] >= min_mass) & (df_launches['payload_mass'] < max_mass)
        
        df_range = df_launches[mask]
        
        if len(df_range) > 0:
            success_count = len(df_range[df_range['success'] == True])
            failure_count = len(df_range[df_range['success'] == False])
            success_rate = (success_count / len(df_range)) * 100
            
            print(f"\n{range_label}:")
            print(f"   Total launches: {len(df_range)}")
            print(f"   Successful: {success_count} ({success_rate:.1f}%)")
            print(f"   Failed: {failure_count}")
            
            # Estadísticas por sitio
            site_stats = df_range.groupby('launch_site_name')['success'].agg(['sum', 'count']).reset_index()
            site_stats.columns = ['site', 'successful', 'total']
            site_stats['success_rate'] = (site_stats['successful'] / site_stats['total']) * 100
            
            print(f"   By site:")
            for _, row in site_stats.iterrows():
                print(f"     {row['site']}: {row['successful']}/{row['total']} ({row['success_rate']:.1f}%)")
        else:
            print(f"\n{range_label}: No data")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX PAYLOAD VS LAUNCH OUTCOME SCATTER PLOT")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Procesar datos
    df_launches = procesar_datos_para_scatter(launches)
    
    # 3. Mostrar estadísticas
    mostrar_estadisticas_rangos(df_launches)
    
    # 4. Crear scatter plot interactivo
    crear_scatter_plot_interactivo(df_launches)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
