"""
SpaceX EDA - Launch Success Count for All Sites (Pie Chart)
Create a pie chart showing launch success count for all launch sites
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

def analizar_exito_por_sitio(launches):
    """
    Analiza el éxito de lanzamientos por sitio
    """
    print("Analizando éxito de lanzamientos por sitio...")
    
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
    
    # Filtrar datos válidos
    df_clean = df[df['launch_site_name'] != 'Unknown'].copy()
    
    print(f"✅ Lanzamientos con sitios válidos: {len(df_clean)}")
    
    # Calcular éxito por sitio
    site_success = df_clean.groupby('launch_site_name')['success'].agg(['sum', 'count']).reset_index()
    site_success.columns = ['launch_site', 'successful_launches', 'total_launches']
    site_success['success_rate'] = (site_success['successful_launches'] / site_success['total_launches']) * 100
    site_success = site_success.sort_values('successful_launches', ascending=False)
    
    return site_success, df_clean

def crear_pie_chart_exito(site_success):
    """
    Crea gráfica de pastel del éxito de lanzamientos por sitio
    """
    print("Creando gráfica de pastel del éxito de lanzamientos...")
    
    plt.figure(figsize=(16, 12))
    
    # Gráfica 1: Número de lanzamientos exitosos por sitio
    plt.subplot(2, 2, 1)
    colors = plt.cm.Set3(np.linspace(0, 1, len(site_success)))
    wedges, texts, autotexts = plt.pie(site_success['successful_launches'], 
                                       labels=site_success['launch_site'],
                                       autopct='%1.1f%%',
                                       colors=colors,
                                       startangle=90)
    plt.title('Successful Launches by Site\n(Pie Chart)', fontsize=14, fontweight='bold')
    
    # Mejorar la legibilidad
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    # Gráfica 2: Tasa de éxito por sitio
    plt.subplot(2, 2, 2)
    colors = plt.cm.viridis(np.linspace(0, 1, len(site_success)))
    bars = plt.bar(range(len(site_success)), site_success['success_rate'], color=colors, alpha=0.7)
    plt.xlabel('Launch Site', fontsize=12, fontweight='bold')
    plt.ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    plt.title('Success Rate by Launch Site', fontsize=14, fontweight='bold')
    plt.xticks(range(len(site_success)), site_success['launch_site'], rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar valores en las barras
    for i, (bar, rate) in enumerate(zip(bars, site_success['success_rate'])):
        plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Gráfica 3: Comparación de lanzamientos totales vs exitosos
    plt.subplot(2, 2, 3)
    x = np.arange(len(site_success))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, site_success['successful_launches'], width, 
                   label='Successful', color='#2ca02c', alpha=0.7)
    bars2 = plt.bar(x + width/2, site_success['total_launches'], width, 
                   label='Total', color='#1f77b4', alpha=0.7)
    
    plt.xlabel('Launch Site', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Launches', fontsize=12, fontweight='bold')
    plt.title('Successful vs Total Launches by Site', fontsize=14, fontweight='bold')
    plt.xticks(x, site_success['launch_site'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 4: Distribución porcentual de lanzamientos exitosos
    plt.subplot(2, 2, 4)
    # Crear datos para mostrar tanto exitosos como fallidos
    site_data = []
    for _, row in site_success.iterrows():
        site_data.append(f"{row['launch_site']}\n({row['successful_launches']} successful)")
    
    failed_launches = site_success['total_launches'] - site_success['successful_launches']
    
    # Crear gráfica de pastel con éxito y fallo
    success_data = site_success['successful_launches'].values
    failure_data = failed_launches.values
    
    # Combinar datos para mostrar éxito vs fallo por sitio
    combined_data = []
    combined_labels = []
    for i, site in enumerate(site_success['launch_site']):
        combined_data.extend([success_data[i], failure_data[i]])
        combined_labels.extend([f"{site}\n(Success)", f"{site}\n(Failure)"])
    
    colors = []
    for i in range(len(site_success)):
        colors.extend(['#2ca02c', '#d62728'])  # Verde para éxito, rojo para fallo
    
    plt.pie(combined_data, labels=combined_labels, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Success vs Failure by Site', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def mostrar_estadisticas_sitios(site_success):
    """
    Muestra estadísticas detalladas por sitio
    """
    print("\n" + "="*80)
    print("🚀 SPACEX LAUNCH SUCCESS BY SITE - DETAILED STATISTICS")
    print("="*80)
    
    print(f"\n📊 LAUNCH SUCCESS STATISTICS BY SITE:")
    print("-" * 80)
    
    for _, row in site_success.iterrows():
        print(f"Site: {row['launch_site']}")
        print(f"  Successful Launches: {row['successful_launches']}")
        print(f"  Total Launches: {row['total_launches']}")
        print(f"  Success Rate: {row['success_rate']:.1f}%")
        print(f"  Failed Launches: {row['total_launches'] - row['successful_launches']}")
        print("-" * 80)
    
    # Estadísticas generales
    total_successful = site_success['successful_launches'].sum()
    total_launches = site_success['total_launches'].sum()
    overall_success_rate = (total_successful / total_launches) * 100
    
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   Total Successful Launches: {total_successful}")
    print(f"   Total Launches: {total_launches}")
    print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
    
    # Mejor y peor sitio
    best_site = site_success.loc[site_success['success_rate'].idxmax()]
    worst_site = site_success.loc[site_success['success_rate'].idxmin()]
    
    print(f"\n🏆 BEST PERFORMING SITE:")
    print(f"   {best_site['launch_site']}: {best_site['success_rate']:.1f}% success rate")
    
    print(f"\n📉 WORST PERFORMING SITE:")
    print(f"   {worst_site['launch_site']}: {worst_site['success_rate']:.1f}% success rate")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX LAUNCH SUCCESS PIE CHART ANALYSIS")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Analizar éxito por sitio
    site_success, df_clean = analizar_exito_por_sitio(launches)
    
    # 3. Mostrar estadísticas
    mostrar_estadisticas_sitios(site_success)
    
    # 4. Crear gráfica de pastel
    crear_pie_chart_exito(site_success)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
