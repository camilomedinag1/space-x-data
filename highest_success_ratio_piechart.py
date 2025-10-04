"""
SpaceX EDA - Pie Chart for Launch Site with Highest Success Ratio
Create a pie chart for the launch site with the highest launch success ratio
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

def encontrar_sitio_mayor_exito(launches):
    """
    Encuentra el sitio de lanzamiento con la mayor tasa de éxito
    """
    print("Encontrando el sitio de lanzamiento con mayor tasa de éxito...")
    
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
    site_success = site_success.sort_values('success_rate', ascending=False)
    
    # Encontrar el sitio con mayor tasa de éxito
    best_site = site_success.iloc[0]
    
    print(f"🏆 Sitio con mayor tasa de éxito: {best_site['launch_site']}")
    print(f"   Tasa de éxito: {best_site['success_rate']:.1f}%")
    print(f"   Lanzamientos exitosos: {best_site['successful_launches']}")
    print(f"   Total de lanzamientos: {best_site['total_launches']}")
    
    return best_site, site_success

def crear_pie_chart_mejor_sitio(best_site, site_success):
    """
    Crea gráfica de pastel para el sitio con mayor tasa de éxito
    """
    print("Creando gráfica de pastel para el sitio con mayor tasa de éxito...")
    
    # Preparar datos para el sitio con mayor éxito
    successful = best_site['successful_launches']
    failed = best_site['total_launches'] - best_site['successful_launches']
    
    # Crear figura con múltiples gráficas
    plt.figure(figsize=(20, 12))
    
    # Gráfica 1: Pie chart principal del mejor sitio
    plt.subplot(2, 3, 1)
    labels = ['Successful Launches', 'Failed Launches']
    sizes = [successful, failed]
    colors = ['#2ca02c', '#d62728']
    explode = (0.05, 0)  # Separar ligeramente la sección de éxito
    
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                       colors=colors, explode=explode, startangle=90,
                                       shadow=True, textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    plt.title(f'{best_site["launch_site"]}\nHighest Success Rate: {best_site["success_rate"]:.1f}%', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Mejorar la legibilidad
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    # Gráfica 2: Comparación de todos los sitios
    plt.subplot(2, 3, 2)
    colors_all = plt.cm.viridis(np.linspace(0, 1, len(site_success)))
    wedges, texts, autotexts = plt.pie(site_success['successful_launches'], 
                                       labels=site_success['launch_site'],
                                       autopct='%1.1f%%',
                                       colors=colors_all,
                                       startangle=90)
    plt.title('Successful Launches by All Sites', fontsize=14, fontweight='bold')
    
    # Gráfica 3: Tasa de éxito por sitio (barras)
    plt.subplot(2, 3, 3)
    colors = ['#2ca02c' if site == best_site['launch_site'] else '#1f77b4' 
              for site in site_success['launch_site']]
    bars = plt.bar(range(len(site_success)), site_success['success_rate'], 
                   color=colors, alpha=0.7)
    plt.xlabel('Launch Site', fontsize=12, fontweight='bold')
    plt.ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    plt.title('Success Rate by Launch Site', fontsize=14, fontweight='bold')
    plt.xticks(range(len(site_success)), site_success['launch_site'], rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar valores en las barras
    for i, (bar, rate) in enumerate(zip(bars, site_success['success_rate'])):
        plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Gráfica 4: Distribución de lanzamientos del mejor sitio
    plt.subplot(2, 3, 4)
    # Crear datos para mostrar éxito vs fallo del mejor sitio
    success_data = [successful, failed]
    success_labels = [f'Successful\n({successful} launches)', f'Failed\n({failed} launches)']
    success_colors = ['#2ca02c', '#d62728']
    
    wedges, texts, autotexts = plt.pie(success_data, labels=success_labels, autopct='%1.1f%%',
                                       colors=success_colors, startangle=90, explode=(0.1, 0))
    plt.title(f'{best_site["launch_site"]}\nLaunch Outcomes Breakdown', fontsize=14, fontweight='bold')
    
    # Gráfica 5: Comparación con otros sitios
    plt.subplot(2, 3, 5)
    # Mostrar solo los primeros 4 sitios para mejor visualización
    top_sites = site_success.head(4)
    x = np.arange(len(top_sites))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, top_sites['successful_launches'], width, 
                   label='Successful', color='#2ca02c', alpha=0.7)
    bars2 = plt.bar(x + width/2, top_sites['total_launches'], width, 
                   label='Total', color='#1f77b4', alpha=0.7)
    
    plt.xlabel('Launch Site', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Launches', fontsize=12, fontweight='bold')
    plt.title('Top 4 Sites: Successful vs Total Launches', fontsize=14, fontweight='bold')
    plt.xticks(x, top_sites['launch_site'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    # Gráfica 6: Estadísticas del mejor sitio
    plt.subplot(2, 3, 6)
    # Crear gráfica de dona con estadísticas
    stats_data = [successful, failed]
    stats_labels = ['Success', 'Failure']
    stats_colors = ['#2ca02c', '#d62728']
    
    wedges, texts, autotexts = plt.pie(stats_data, labels=stats_labels, autopct='%1.1f%%',
                                       colors=stats_colors, startangle=90,
                                       pctdistance=0.85, labeldistance=1.1)
    
    # Crear dona
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.title(f'{best_site["launch_site"]}\nSuccess Rate: {best_site["success_rate"]:.1f}%', 
              fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def mostrar_estadisticas_mejor_sitio(best_site, site_success):
    """
    Muestra estadísticas detalladas del mejor sitio
    """
    print("\n" + "="*80)
    print("🚀 SPACEX LAUNCH SITE WITH HIGHEST SUCCESS RATIO")
    print("="*80)
    
    print(f"\n🏆 BEST PERFORMING LAUNCH SITE:")
    print(f"   Site Name: {best_site['launch_site']}")
    print(f"   Success Rate: {best_site['success_rate']:.1f}%")
    print(f"   Successful Launches: {best_site['successful_launches']}")
    print(f"   Total Launches: {best_site['total_launches']}")
    print(f"   Failed Launches: {best_site['total_launches'] - best_site['successful_launches']}")
    
    print(f"\n📊 COMPARISON WITH OTHER SITES:")
    print("-" * 80)
    for _, row in site_success.iterrows():
        if row['launch_site'] == best_site['launch_site']:
            print(f"🏆 {row['launch_site']}: {row['success_rate']:.1f}% (BEST)")
        else:
            print(f"   {row['launch_site']}: {row['success_rate']:.1f}%")
    
    # Calcular diferencia con el segundo mejor
    if len(site_success) > 1:
        second_best = site_success.iloc[1]
        difference = best_site['success_rate'] - second_best['success_rate']
        print(f"\n📈 PERFORMANCE GAP:")
        print(f"   Difference from 2nd best site: {difference:.1f} percentage points")
        print(f"   2nd best site: {second_best['launch_site']} ({second_best['success_rate']:.1f}%)")

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX HIGHEST SUCCESS RATIO SITE PIE CHART")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Encontrar sitio con mayor tasa de éxito
    best_site, site_success = encontrar_sitio_mayor_exito(launches)
    
    # 3. Mostrar estadísticas
    mostrar_estadisticas_mejor_sitio(best_site, site_success)
    
    # 4. Crear gráfica de pastel
    crear_pie_chart_mejor_sitio(best_site, site_success)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
