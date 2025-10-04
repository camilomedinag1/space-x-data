"""
SpaceX EDA - Rank Landing Outcomes Between 2010-06-04 and 2017-03-20
Rank the count of landing outcomes between the specified date range in descending order
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

def clasificar_resultados_aterrizaje(launches):
    """
    Clasifica los resultados de aterrizaje entre 2010-06-04 y 2017-03-20
    """
    print("Clasificando resultados de aterrizaje entre 2010-06-04 y 2017-03-20...")
    
    # Convertir a DataFrame
    df = pd.DataFrame(launches)
    
    # Filtrar por rango de fechas
    start_date = '2010-06-04'
    end_date = '2017-03-20'
    
    df['date_utc'] = pd.to_datetime(df['date_utc'])
    df_filtered = df[(df['date_utc'] >= start_date) & (df['date_utc'] <= end_date)].copy()
    
    print(f"✅ Lanzamientos en el rango de fechas: {len(df_filtered)}")
    
    # Analizar resultados de aterrizaje
    landing_outcomes = []
    
    for _, row in df_filtered.iterrows():
        cores = row['cores']
        if cores and len(cores) > 0:
            for core in cores:
                landing_success = core.get('landing_success', False)
                landing_type = core.get('landing_type', '')
                
                # Determinar el resultado del aterrizaje
                if landing_success:
                    if landing_type == 'RTLS':
                        outcome = 'Success (ground pad)'
                    elif landing_type == 'ASDS':
                        outcome = 'Success (drone ship)'
                    elif landing_type == 'Ocean':
                        outcome = 'Success (ocean)'
                    else:
                        outcome = 'Success (other)'
                else:
                    if landing_type == 'RTLS':
                        outcome = 'Failure (ground pad)'
                    elif landing_type == 'ASDS':
                        outcome = 'Failure (drone ship)'
                    elif landing_type == 'Ocean':
                        outcome = 'Failure (ocean)'
                    else:
                        outcome = 'Failure (other)'
                
                landing_outcomes.append({
                    'flight_number': row['flight_number'],
                    'name': row['name'],
                    'date_utc': row['date_utc'],
                    'outcome': outcome,
                    'landing_success': landing_success,
                    'landing_type': landing_type,
                    'core_id': core.get('core', 'Unknown')
                })
    
    # Contar resultados
    outcome_counts = pd.Series([outcome['outcome'] for outcome in landing_outcomes]).value_counts()
    
    print(f"✅ Resultados de aterrizaje encontrados: {len(landing_outcomes)}")
    
    return landing_outcomes, outcome_counts

def mostrar_ranking_resultados(landing_outcomes, outcome_counts):
    """
    Muestra el ranking de resultados de aterrizaje
    """
    print("\n" + "="*80)
    print("🚀 SPACEX LANDING OUTCOMES RANKING (2010-06-04 to 2017-03-20)")
    print("="*80)
    
    print(f"\n📊 LANDING OUTCOMES RANKING (Descending Order):")
    print("-" * 80)
    
    for i, (outcome, count) in enumerate(outcome_counts.items(), 1):
        percentage = (count / outcome_counts.sum()) * 100
        print(f"{i:2d}. {outcome}: {count} occurrences ({percentage:.1f}%)")
    
    # Mostrar detalles de cada resultado
    print(f"\n📋 DETAILED BREAKDOWN BY OUTCOME:")
    print("-" * 80)
    
    for outcome in outcome_counts.index:
        matching_outcomes = [lo for lo in landing_outcomes if lo['outcome'] == outcome]
        print(f"\n{outcome} ({len(matching_outcomes)} occurrences):")
        
        for i, outcome_detail in enumerate(matching_outcomes[:5], 1):  # Mostrar primeros 5
            success_icon = "✅" if outcome_detail['landing_success'] else "❌"
            print(f"  {i}. Flight #{outcome_detail['flight_number']} - {outcome_detail['name']} {success_icon}")
            print(f"     Date: {outcome_detail['date_utc'].strftime('%Y-%m-%d')}")
            print(f"     Landing Type: {outcome_detail['landing_type']}")
        
        if len(matching_outcomes) > 5:
            print(f"     ... and {len(matching_outcomes) - 5} more")
    
    # Estadísticas adicionales
    total_attempts = len(landing_outcomes)
    successful_attempts = sum(1 for outcome in landing_outcomes if outcome['landing_success'])
    failed_attempts = total_attempts - successful_attempts
    
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"   Total landing attempts: {total_attempts}")
    print(f"   Successful landings: {successful_attempts} ({(successful_attempts/total_attempts)*100:.1f}%)")
    print(f"   Failed landings: {failed_attempts} ({(failed_attempts/total_attempts)*100:.1f}%)")
    
    # Análisis por tipo de aterrizaje
    landing_types = [outcome['landing_type'] for outcome in landing_outcomes]
    type_counts = pd.Series(landing_types).value_counts()
    
    print(f"\n🏗️ LANDING TYPE DISTRIBUTION:")
    for landing_type, count in type_counts.items():
        print(f"   {landing_type}: {count} attempts")

def grafica_ranking_resultados(outcome_counts):
    """
    Crea gráfica del ranking de resultados de aterrizaje
    """
    print("Creando gráfica del ranking de resultados de aterrizaje...")
    
    plt.figure(figsize=(16, 10))
    
    # Gráfica 1: Ranking de resultados
    plt.subplot(2, 2, 1)
    colors = plt.cm.viridis(np.linspace(0, 1, len(outcome_counts)))
    bars = plt.bar(range(len(outcome_counts)), outcome_counts.values, color=colors, alpha=0.7)
    plt.xlabel('Landing Outcome', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Occurrences', fontsize=12, fontweight='bold')
    plt.title('Landing Outcomes Ranking\n(2010-06-04 to 2017-03-20)', fontsize=14, fontweight='bold')
    plt.xticks(range(len(outcome_counts)), outcome_counts.index, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar valores en las barras
    for i, (bar, count) in enumerate(zip(bars, outcome_counts.values)):
        plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                str(count), ha='center', va='bottom', fontweight='bold')
    
    # Gráfica 2: Distribución porcentual
    plt.subplot(2, 2, 2)
    colors = plt.cm.Set3(np.linspace(0, 1, len(outcome_counts)))
    plt.pie(outcome_counts.values, labels=outcome_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Landing Outcomes Distribution', fontsize=14, fontweight='bold')
    
    # Gráfica 3: Comparación éxito vs fallo
    plt.subplot(2, 2, 3)
    success_outcomes = [count for outcome, count in outcome_counts.items() if 'Success' in outcome]
    failure_outcomes = [count for outcome, count in outcome_counts.items() if 'Failure' in outcome]
    
    total_success = sum(success_outcomes)
    total_failure = sum(failure_outcomes)
    
    plt.bar(['Success', 'Failure'], [total_success, total_failure], 
            color=['#2ca02c', '#d62728'], alpha=0.7)
    plt.ylabel('Number of Occurrences', fontsize=12, fontweight='bold')
    plt.title('Success vs Failure Comparison', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar valores en las barras
    plt.text(0, total_success + 0.5, str(total_success), ha='center', va='bottom', fontweight='bold')
    plt.text(1, total_failure + 0.5, str(total_failure), ha='center', va='bottom', fontweight='bold')
    
    # Gráfica 4: Análisis por tipo de aterrizaje
    plt.subplot(2, 2, 4)
    landing_types = []
    for outcome in outcome_counts.index:
        if 'ground pad' in outcome:
            landing_types.append('Ground Pad')
        elif 'drone ship' in outcome:
            landing_types.append('Drone Ship')
        elif 'ocean' in outcome:
            landing_types.append('Ocean')
        else:
            landing_types.append('Other')
    
    type_analysis = pd.Series(landing_types).value_counts()
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(type_analysis)))
    plt.bar(type_analysis.index, type_analysis.values, color=colors, alpha=0.7)
    plt.xlabel('Landing Type', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Outcomes', fontsize=12, fontweight='bold')
    plt.title('Outcomes by Landing Type', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX LANDING OUTCOMES RANKING ANALYSIS")
    print("="*60)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Clasificar resultados de aterrizaje
    landing_outcomes, outcome_counts = clasificar_resultados_aterrizaje(launches)
    
    # 3. Mostrar ranking
    mostrar_ranking_resultados(landing_outcomes, outcome_counts)
    
    # 4. Crear visualización
    grafica_ranking_resultados(outcome_counts)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
