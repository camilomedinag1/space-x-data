#!/usr/bin/env python3
"""
SpaceX Success Rate vs. Orbit Type Analysis - Versión Rápida
Author: Camilo Medina
Description: Análisis rápido de tasa de éxito por tipo de órbita
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def create_realistic_orbit_data():
    """
    Crear datos de muestra realistas para tipos de órbita
    """
    print("=== SpaceX Success Rate vs. Orbit Type Analysis ===")
    print("Author: Camilo Medina")
    print("=" * 60)
    print("1. Creando datos realistas de SpaceX...")
    
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
    ]
    
    # Generar datos realistas
    np.random.seed(42)
    n_launches = 200
    
    data = []
    
    for i in range(n_launches):
        # Seleccionar tipo de órbita con probabilidades realistas
        orbit_weights = [0.40, 0.25, 0.15, 0.08, 0.05, 0.03, 0.02, 0.02]
        orbit = np.random.choice(orbit_types, p=orbit_weights)
        
        # Generar tasa de éxito basada en el tipo de órbita
        if orbit == 'LEO':
            success_prob = 0.96  # LEO es más fácil
        elif orbit == 'GTO':
            success_prob = 0.89  # GTO es más desafiante
        elif orbit == 'SSO':
            success_prob = 0.93  # SSO es moderadamente desafiante
        elif orbit == 'ISS':
            success_prob = 0.98  # ISS es muy confiable
        elif orbit == 'PO':
            success_prob = 0.91  # Polar es moderadamente desafiante
        elif orbit == 'ES-L1':
            success_prob = 0.87  # L1 es muy desafiante
        elif orbit == 'HEO':
            success_prob = 0.88  # HEO es desafiante
        elif orbit == 'MEO':
            success_prob = 0.90  # MEO es moderadamente desafiante
        
        # Añadir variabilidad
        success_prob += np.random.normal(0, 0.03)
        success_prob = max(0.70, min(0.99, success_prob))
        
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
    print("\n2. Creando gráfico de barras de tasa de éxito...")
    
    if df is None or len(df) == 0:
        print("   - No hay datos disponibles para el gráfico")
        return
    
    # Calcular tasa de éxito por tipo de órbita
    success_by_orbit = df.groupby('Orbit')['Success'].agg(['mean', 'count']).reset_index()
    success_by_orbit.columns = ['Orbit', 'SuccessRate', 'Count']
    
    # Filtrar órbitas con al menos 5 lanzamientos para estadísticas confiables
    success_by_orbit = success_by_orbit[success_by_orbit['Count'] >= 5]
    
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
    plt.title('SpaceX: Tasa de Éxito por Tipo de Órbita\n(Análisis EDA con Datos Realistas)', 
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

def create_additional_analysis(df):
    """
    Crear análisis adicional
    """
    print("\n3. Creando análisis adicional...")
    
    if df is None or len(df) == 0:
        print("   - No hay datos disponibles para análisis adicional")
        return
    
    # Crear figura con múltiples subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
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
    success_by_orbit = success_by_orbit[df['Orbit'].value_counts() >= 5]  # Al menos 5 lanzamientos
    
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
    orbit_counts_filtered = orbit_counts_filtered[orbit_counts_filtered >= 5]
    
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
        axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Comparación de éxito vs fallo por órbita
    orbit_success_data = []
    for orbit in df['Orbit'].unique():
        orbit_data = df[df['Orbit'] == orbit]
        if len(orbit_data) >= 5:
            success_count = orbit_data['Success'].sum()
            failure_count = len(orbit_data) - success_count
            orbit_success_data.append({
                'Orbit': orbit,
                'Success': success_count,
                'Failure': failure_count
            })
    
    if orbit_success_data:
        orbit_df = pd.DataFrame(orbit_success_data)
        x = np.arange(len(orbit_df))
        width = 0.35
        
        axes[1, 1].bar(x - width/2, orbit_df['Success'], width, label='Exitosos', 
                      color='green', alpha=0.8)
        axes[1, 1].bar(x + width/2, orbit_df['Failure'], width, label='Fallos', 
                      color='red', alpha=0.8)
        
        axes[1, 1].set_title('Éxitos vs Fallos por Tipo de Órbita', fontweight='bold', fontsize=14)
        axes[1, 1].set_xlabel('Tipo de Órbita', fontsize=12)
        axes[1, 1].set_ylabel('Número de Lanzamientos', fontsize=12)
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(orbit_df['Orbit'], rotation=45, ha='right')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('spacex_orbit_detailed_analysis.png', dpi=300, bbox_inches='tight')
    print("   - Análisis detallado guardado como: spacex_orbit_detailed_analysis.png")
    plt.show()

def generate_statistics(df):
    """
    Generar estadísticas detalladas
    """
    print("\n4. Estadísticas del Análisis:")
    
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
        if stats['Total'] >= 5:  # Solo mostrar órbitas con al menos 5 lanzamientos
            print(f"     * {orbit}:")
            print(f"       - Lanzamientos: {int(stats['Total'])}")
            print(f"       - Exitosos: {int(stats['Exitosos'])}")
            print(f"       - Tasa de Éxito: {stats['Tasa_Exito']:.1%}")
    
    print("\n5. Insights Clave:")
    best_orbit = orbit_stats.iloc[0]
    worst_orbit = orbit_stats.iloc[-1]
    
    print(f"   - Mejor Tipo de Órbita: {best_orbit.name} ({best_orbit['Tasa_Exito']:.1%})")
    print(f"   - Tipo de Órbita Más Desafiante: {worst_orbit.name} ({worst_orbit['Tasa_Exito']:.1%})")
    print(f"   - Diferencia de Rendimiento: {best_orbit['Tasa_Exito'] - worst_orbit['Tasa_Exito']:.1%}")
    
    # Análisis de confiabilidad
    reliable_orbits = orbit_stats[orbit_stats['Tasa_Exito'] >= 0.9]
    challenging_orbits = orbit_stats[orbit_stats['Tasa_Exito'] < 0.85]
    
    print(f"   - Órbitas Altamente Confiables (≥90%): {len(reliable_orbits)}")
    print(f"   - Órbitas Desafiantes (<85%): {len(challenging_orbits)}")
    
    if len(reliable_orbits) > 0:
        print(f"     * Confiables: {', '.join(reliable_orbits.index.tolist())}")
    if len(challenging_orbits) > 0:
        print(f"     * Desafiantes: {', '.join(challenging_orbits.index.tolist())}")

if __name__ == "__main__":
    print("🚀 SpaceX Success Rate vs. Orbit Type Analysis - Versión Rápida")
    print("=" * 70)
    
    # Crear datos realistas
    df = create_realistic_orbit_data()
    
    if df is not None and len(df) > 0:
        # Crear gráfico principal de barras
        plot_filename = create_success_rate_bar_chart(df)
        
        # Crear análisis detallado
        create_additional_analysis(df)
        
        # Generar estadísticas
        generate_statistics(df)
        
        print("\n" + "=" * 70)
        print("✅ Análisis de Tasa de Éxito por Tipo de Órbita Completado!")
        print("📊 Archivos Generados:")
        print("   - spacex_success_rate_vs_orbit_type.png")
        print("   - spacex_orbit_detailed_analysis.png")
        print("\n🎯 Beneficios del Análisis:")
        print("   - Identificación de tipos de órbita más confiables")
        print("   - Análisis de desafíos por tipo de misión")
        print("   - Datos realistas basados en patrones de SpaceX")
        print("   - Visualizaciones profesionales y detalladas")
    else:
        print("❌ No se pudo crear ningún dato para el análisis")
