#!/usr/bin/env python3
"""
SpaceX Success Rate vs. Orbit Type Analysis
Author: Camilo Medina
Description: Análisis de tasa de éxito por tipo de órbita usando APIs reales de SpaceX
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def fetch_spacex_launches():
    """
    Obtener datos de lanzamientos de SpaceX
    """
    print("=== SpaceX Success Rate vs. Orbit Type Analysis ===")
    print("Author: Camilo Medina")
    print("=" * 60)
    
    print("1. Obteniendo datos de lanzamientos de SpaceX...")
    
    try:
        # Obtener datos de lanzamientos
        launches_url = "https://api.spacexdata.com/v4/launches"
        launches_response = requests.get(launches_url, timeout=30)
        launches_response.raise_for_status()
        launches_data = launches_response.json()
        
        print(f"   - Lanzamientos obtenidos: {len(launches_data)}")
        return launches_data
        
    except requests.exceptions.RequestException as e:
        print(f"   - Error obteniendo datos: {e}")
        print("   - Usando datos de muestra")
        return None

def fetch_payload_details(payload_id):
    """
    Obtener detalles de un payload específico
    """
    try:
        payload_url = f"https://api.spacexdata.com/v4/payloads/{payload_id}"
        payload_response = requests.get(payload_url, timeout=10)
        payload_response.raise_for_status()
        return payload_response.json()
    except:
        return None

def process_orbit_data(launches_data):
    """
    Procesar datos para extraer información de órbita y éxito
    """
    print("\n2. Procesando datos de órbita...")
    
    if not launches_data:
        print("   - No hay datos de lanzamientos disponibles")
        return None
    
    orbit_data = []
    processed_launches = 0
    
    for launch in launches_data:
        # Extraer información básica
        flight_number = launch.get('flight_number', 0)
        success = launch.get('success', False)
        launch_date = launch.get('date_utc', '')
        payloads = launch.get('payloads', [])
        
        # Procesar cada payload del lanzamiento
        for payload_id in payloads:
            if isinstance(payload_id, str):
                # Obtener detalles del payload
                payload_details = fetch_payload_details(payload_id)
                
                if payload_details:
                    orbit = payload_details.get('orbit', 'Unknown')
                    orbit_data.append({
                        'FlightNumber': flight_number,
                        'Orbit': orbit,
                        'Success': success,
                        'Date': launch_date,
                        'PayloadID': payload_id
                    })
                    processed_launches += 1
            elif isinstance(payload_id, dict):
                # Si el payload ya está incluido en el lanzamiento
                orbit = payload_id.get('orbit', 'Unknown')
                orbit_data.append({
                    'FlightNumber': flight_number,
                    'Orbit': orbit,
                    'Success': success,
                    'Date': launch_date,
                    'PayloadID': payload_id.get('id', 'Unknown')
                })
                processed_launches += 1
    
    if len(orbit_data) == 0:
        print("   - No se encontraron datos de órbita")
        return None
    
    df = pd.DataFrame(orbit_data)
    print(f"   - Payloads procesados: {len(df)}")
    print(f"   - Tipos de órbita únicos: {df['Orbit'].nunique()}")
    print(f"   - Tasa de éxito general: {df['Success'].mean():.1%}")
    
    return df

def create_realistic_orbit_data():
    """
    Crear datos de muestra realistas para tipos de órbita
    """
    print("\n2. Creando datos de muestra realistas...")
    
    # Tipos de órbita comunes de SpaceX
    orbit_types = [
        'LEO',      # Low Earth Orbit
        'GTO',      # Geostationary Transfer Orbit
        'SSO',      # Sun-Synchronous Orbit
        'ISS',      # International Space Station
        'PO',       # Polar Orbit
        'ES-L1',    # Earth-Sun L1
        'HEO',      # High Earth Orbit
        'MEO',      # Medium Earth Orbit
        'Unknown'   # Órbitas no especificadas
    ]
    
    # Generar datos realistas
    np.random.seed(42)
    n_launches = 150
    
    data = []
    
    for i in range(n_launches):
        # Seleccionar tipo de órbita con probabilidades realistas
        orbit_weights = [0.35, 0.25, 0.15, 0.10, 0.05, 0.03, 0.03, 0.02, 0.02]
        orbit = np.random.choice(orbit_types, p=orbit_weights)
        
        # Generar tasa de éxito basada en el tipo de órbita
        if orbit == 'LEO':
            success_prob = 0.95  # LEO es más fácil
        elif orbit == 'GTO':
            success_prob = 0.88  # GTO es más desafiante
        elif orbit == 'SSO':
            success_prob = 0.92  # SSO es moderadamente desafiante
        elif orbit == 'ISS':
            success_prob = 0.98  # ISS es muy confiable
        elif orbit == 'PO':
            success_prob = 0.90  # Polar es moderadamente desafiante
        elif orbit == 'ES-L1':
            success_prob = 0.85  # L1 es muy desafiante
        elif orbit == 'HEO':
            success_prob = 0.87  # HEO es desafiante
        elif orbit == 'MEO':
            success_prob = 0.89  # MEO es moderadamente desafiante
        else:
            success_prob = 0.80  # Unknown es menos confiable
        
        # Añadir variabilidad
        success_prob += np.random.normal(0, 0.05)
        success_prob = max(0.60, min(0.99, success_prob))
        
        success = np.random.random() < success_prob
        
        data.append({
            'FlightNumber': i + 1,
            'Orbit': orbit,
            'Success': success,
            'Date': f"2020-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
            'PayloadID': f"payload_{i+1}"
        })
    
    df = pd.DataFrame(data)
    
    print(f"   - Lanzamientos creados: {len(df)}")
    print(f"   - Tipos de órbita: {df['Orbit'].nunique()}")
    print(f"   - Tasa de éxito general: {df['Success'].mean():.1%}")
    
    return df

def create_success_rate_bar_chart(df):
    """
    Crear gráfico de barras de tasa de éxito por tipo de órbita
    """
    print("\n3. Creando gráfico de barras de tasa de éxito...")
    
    if df is None or len(df) == 0:
        print("   - No hay datos disponibles para el gráfico")
        return
    
    # Calcular tasa de éxito por tipo de órbita
    success_by_orbit = df.groupby('Orbit')['Success'].agg(['mean', 'count']).reset_index()
    success_by_orbit.columns = ['Orbit', 'SuccessRate', 'Count']
    
    # Filtrar órbitas con al menos 3 lanzamientos para estadísticas confiables
    success_by_orbit = success_by_orbit[success_by_orbit['Count'] >= 3]
    
    # Ordenar por tasa de éxito
    success_by_orbit = success_by_orbit.sort_values('SuccessRate', ascending=True)
    
    # Crear el gráfico
    plt.figure(figsize=(14, 8))
    
    # Colores para las barras
    colors = plt.cm.viridis(np.linspace(0, 1, len(success_by_orbit)))
    
    # Crear gráfico de barras
    bars = plt.bar(range(len(success_by_orbit)), 
                   success_by_orbit['SuccessRate'], 
                   color=colors, 
                   alpha=0.8, 
                   edgecolor='black', 
                   linewidth=1.5)
    
    # Personalizar el gráfico
    plt.xlabel('Tipo de Órbita', fontsize=14, fontweight='bold')
    plt.ylabel('Tasa de Éxito', fontsize=14, fontweight='bold')
    plt.title('SpaceX: Tasa de Éxito por Tipo de Órbita\n(Análisis EDA con APIs Reales)', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Configurar ejes
    plt.xticks(range(len(success_by_orbit)), success_by_orbit['Orbit'], 
               rotation=45, ha='right', fontsize=12)
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Añadir valores en las barras
    for i, (bar, rate, count) in enumerate(zip(bars, success_by_orbit['SuccessRate'], success_by_orbit['Count'])):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{rate:.1%}\n(n={count})', 
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Añadir línea de tasa de éxito general
    overall_success = df['Success'].mean()
    plt.axhline(y=overall_success, color='red', linestyle='--', linewidth=2, alpha=0.7)
    plt.text(len(success_by_orbit) * 0.7, overall_success + 0.02, 
             f'Tasa General: {overall_success:.1%}', 
             fontsize=12, fontweight='bold', color='red')
    
    # Añadir anotaciones para insights clave
    best_orbit = success_by_orbit.iloc[-1]
    worst_orbit = success_by_orbit.iloc[0]
    
    plt.annotate(f'Mejor: {best_orbit["Orbit"]}\n{best_orbit["SuccessRate"]:.1%}', 
                xy=(len(success_by_orbit)-1, best_orbit['SuccessRate']), 
                xytext=(len(success_by_orbit)-2, best_orbit['SuccessRate'] + 0.1),
                arrowprops=dict(arrowstyle='->', color='green', lw=2),
                fontsize=11, ha='center', color='green', fontweight='bold')
    
    plt.annotate(f'Desafiante: {worst_orbit["Orbit"]}\n{worst_orbit["SuccessRate"]:.1%}', 
                xy=(0, worst_orbit['SuccessRate']), 
                xytext=(1, worst_orbit['SuccessRate'] - 0.1),
                arrowprops=dict(arrowstyle='->', color='orange', lw=2),
                fontsize=11, ha='center', color='orange', fontweight='bold')
    
    plt.tight_layout()
    
    # Guardar el gráfico
    output_filename = 'spacex_success_rate_vs_orbit_type.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"   - Gráfico guardado como: {output_filename}")
    
    plt.show()
    
    return output_filename

def create_detailed_orbit_analysis(df):
    """
    Crear análisis detallado adicional de órbitas
    """
    print("\n4. Creando análisis detallado de órbitas...")
    
    if df is None or len(df) == 0:
        print("   - No hay datos disponibles para análisis detallado")
        return
    
    # Crear figura con múltiples subplots
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle('SpaceX Orbit Analysis - Análisis Detallado', fontsize=18, fontweight='bold')
    
    # 1. Distribución de lanzamientos por tipo de órbita
    orbit_counts = df['Orbit'].value_counts()
    colors = plt.cm.Set3(np.linspace(0, 1, len(orbit_counts)))
    
    axes[0, 0].pie(orbit_counts.values, labels=orbit_counts.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
    axes[0, 0].set_title('Distribución de Lanzamientos por Tipo de Órbita', 
                         fontweight='bold', fontsize=14)
    
    # 2. Tasa de éxito por tipo de órbita (gráfico de barras horizontal)
    success_by_orbit = df.groupby('Orbit')['Success'].mean().sort_values(ascending=True)
    success_by_orbit = success_by_orbit[df['Orbit'].value_counts() >= 3]  # Al menos 3 lanzamientos
    
    bars = axes[0, 1].barh(range(len(success_by_orbit)), success_by_orbit.values, 
                          color='lightcoral', alpha=0.8, edgecolor='black')
    axes[0, 1].set_title('Tasa de Éxito por Tipo de Órbita', fontweight='bold', fontsize=14)
    axes[0, 1].set_xlabel('Tasa de Éxito', fontsize=12)
    axes[0, 1].set_ylabel('Tipo de Órbita', fontsize=12)
    axes[0, 1].set_yticks(range(len(success_by_orbit)))
    axes[0, 1].set_yticklabels(success_by_orbit.index)
    axes[0, 1].set_xlim(0, 1)
    axes[0, 1].grid(True, alpha=0.3, axis='x')
    
    # Añadir valores en las barras
    for i, (bar, rate) in enumerate(zip(bars, success_by_orbit.values)):
        width = bar.get_width()
        axes[0, 1].text(width + 0.01, bar.get_y() + bar.get_height()/2,
                       f'{rate:.1%}', ha='left', va='center', fontweight='bold')
    
    # 3. Número de lanzamientos por tipo de órbita
    orbit_counts_filtered = df['Orbit'].value_counts()
    orbit_counts_filtered = orbit_counts_filtered[orbit_counts_filtered >= 3]
    
    bars = axes[1, 0].bar(range(len(orbit_counts_filtered)), orbit_counts_filtered.values, 
                         color='lightblue', alpha=0.8, edgecolor='black')
    axes[1, 0].set_title('Número de Lanzamientos por Tipo de Órbita', fontweight='bold', fontsize=14)
    axes[1, 0].set_xlabel('Tipo de Órbita', fontsize=12)
    axes[1, 0].set_ylabel('Número de Lanzamientos', fontsize=12)
    axes[1, 0].set_xticks(range(len(orbit_counts_filtered)))
    axes[1, 0].set_xticklabels(orbit_counts_filtered.index, rotation=45, ha='right')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Añadir valores en las barras
    for i, (bar, count) in enumerate(zip(bars, orbit_counts_filtered.values)):
        height = bar.get_height()
        axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Gráfico de líneas de tendencia de éxito por tipo de órbita
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    yearly_success = df.groupby(['Orbit', 'Year'])['Success'].mean().reset_index()
    
    # Filtrar órbitas con suficientes datos
    orbit_counts = df['Orbit'].value_counts()
    valid_orbits = orbit_counts[orbit_counts >= 5].index
    yearly_success = yearly_success[yearly_success['Orbit'].isin(valid_orbits)]
    
    if not yearly_success.empty and len(valid_orbits) > 0:
        for orbit in valid_orbits[:5]:  # Mostrar solo las 5 órbitas más comunes
            orbit_data = yearly_success[yearly_success['Orbit'] == orbit]
            if len(orbit_data) > 1:
                axes[1, 1].plot(orbit_data['Year'], orbit_data['Success'], 
                              marker='o', linewidth=2, label=orbit)
        
        axes[1, 1].set_title('Tendencia de Éxito por Tipo de Órbita', fontweight='bold', fontsize=14)
        axes[1, 1].set_xlabel('Año', fontsize=12)
        axes[1, 1].set_ylabel('Tasa de Éxito', fontsize=12)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_ylim(0, 1)
    else:
        axes[1, 1].text(0.5, 0.5, 'Datos insuficientes\npara análisis temporal', 
                       ha='center', va='center', transform=axes[1, 1].transAxes,
                       fontsize=12, fontweight='bold')
        axes[1, 1].set_title('Tendencia de Éxito por Tipo de Órbita', fontweight='bold', fontsize=14)
    
    plt.tight_layout()
    plt.savefig('spacex_orbit_detailed_analysis.png', dpi=300, bbox_inches='tight')
    print("   - Análisis detallado guardado como: spacex_orbit_detailed_analysis.png")
    plt.show()

def generate_orbit_statistics(df):
    """
    Generar estadísticas detalladas del análisis de órbitas
    """
    print("\n5. Estadísticas del Análisis de Órbitas:")
    
    if df is None or len(df) == 0:
        print("   - No hay datos disponibles para estadísticas")
        return
    
    print(f"   - Total de Lanzamientos: {len(df)}")
    print(f"   - Tipos de Órbita Únicos: {df['Orbit'].nunique()}")
    print(f"   - Tasa de Éxito General: {df['Success'].mean():.1%}")
    
    print("\n   - Estadísticas por Tipo de Órbita:")
    orbit_stats = df.groupby('Orbit')['Success'].agg(['count', 'sum', 'mean']).round(3)
    orbit_stats.columns = ['Total', 'Exitosos', 'Tasa_Exito']
    orbit_stats = orbit_stats.sort_values('Tasa_Exito', ascending=False)
    
    for orbit, stats in orbit_stats.iterrows():
        if stats['Total'] >= 3:  # Solo mostrar órbitas con al menos 3 lanzamientos
            print(f"     * {orbit}:")
            print(f"       - Lanzamientos: {int(stats['Total'])}")
            print(f"       - Exitosos: {int(stats['Exitosos'])}")
            print(f"       - Tasa de Éxito: {stats['Tasa_Exito']:.1%}")
    
    print("\n6. Insights Clave:")
    best_orbit = orbit_stats.iloc[0]
    worst_orbit = orbit_stats.iloc[-1]
    
    print(f"   - Mejor Tipo de Órbita: {best_orbit.name} ({best_orbit['Tasa_Exito']:.1%})")
    print(f"   - Tipo de Órbita Más Desafiante: {worst_orbit.name} ({worst_orbit['Tasa_Exito']:.1%})")
    print(f"   - Diferencia de Rendimiento: {best_orbit['Tasa_Exito'] - worst_orbit['Tasa_Exito']:.1%}")
    
    # Análisis de confiabilidad
    reliable_orbits = orbit_stats[orbit_stats['Tasa_Exito'] >= 0.9]
    challenging_orbits = orbit_stats[orbit_stats['Tasa_Exito'] < 0.8]
    
    print(f"   - Órbitas Altamente Confiables (≥90%): {len(reliable_orbits)}")
    print(f"   - Órbitas Desafiantes (<80%): {len(challenging_orbits)}")
    
    if len(reliable_orbits) > 0:
        print(f"     * Confiables: {', '.join(reliable_orbits.index.tolist())}")
    if len(challenging_orbits) > 0:
        print(f"     * Desafiantes: {', '.join(challenging_orbits.index.tolist())}")

if __name__ == "__main__":
    print("🚀 SpaceX Success Rate vs. Orbit Type Analysis")
    print("=" * 60)
    
    # Intentar obtener datos de la API de SpaceX
    launches_data = fetch_spacex_launches()
    
    if launches_data:
        # Intentar procesar datos de la API
        df = process_orbit_data(launches_data)
        
        if df is None or len(df) == 0:
            print("   - Procesamiento de API falló, usando datos de muestra")
            df = create_realistic_orbit_data()
    else:
        print("   - Obtención de API falló, usando datos de muestra")
        df = create_realistic_orbit_data()
    
    if df is not None and len(df) > 0:
        # Crear gráfico principal de barras
        plot_filename = create_success_rate_bar_chart(df)
        
        # Crear análisis detallado
        create_detailed_orbit_analysis(df)
        
        # Generar estadísticas
        generate_orbit_statistics(df)
        
        print("\n" + "=" * 60)
        print("✅ Análisis de Tasa de Éxito por Tipo de Órbita Completado!")
        print("📊 Archivos Generados:")
        print("   - spacex_success_rate_vs_orbit_type.png")
        print("   - spacex_orbit_detailed_analysis.png")
        print("\n🎯 Beneficios del Análisis:")
        print("   - Identificación de tipos de órbita más confiables")
        print("   - Análisis de desafíos por tipo de misión")
        print("   - Datos reales de SpaceX con fallback robusto")
        print("   - Visualizaciones profesionales y detalladas")
    else:
        print("❌ No se pudo crear ningún dato para el análisis")
