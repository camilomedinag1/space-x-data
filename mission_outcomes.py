"""
SpaceX EDA - Total Number of Successful and Failure Mission Outcomes
Calculate the total number of successful and failure mission outcomes
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

def calcular_resultados_misiones(launches):
    """
    Calcula el número total de misiones exitosas y fallidas
    """
    print("Calculando resultados de misiones...")
    
    # Convertir a DataFrame
    df = pd.DataFrame(launches)
    
    # Filtrar datos válidos
    df_valid = df[df['success'].notna()].copy()
    
    print(f"✅ Lanzamientos con datos válidos: {len(df_valid)}")
    
    # Calcular resultados
    successful_missions = df_valid[df_valid['success'] == True]
    failed_missions = df_valid[df_valid['success'] == False]
    
    total_missions = len(df_valid)
    success_count = len(successful_missions)
    failure_count = len(failed_missions)
    
    success_rate = (success_count / total_missions) * 100
    failure_rate = (failure_count / total_missions) * 100
    
    return {
        'total_missions': total_missions,
        'successful_missions': success_count,
        'failed_missions': failure_count,
        'success_rate': success_rate,
        'failure_rate': failure_rate,
        'successful_data': successful_missions,
        'failed_data': failed_missions
    }

def mostrar_resultados_misiones(results):
    """
    Muestra los resultados de las misiones
    """
    print("\n" + "="*80)
    print("🚀 SPACEX MISSION OUTCOMES ANALYSIS")
    print("="*80)
    
    print(f"\n📊 MISSION OUTCOMES SUMMARY:")
    print(f"   Total Missions: {results['total_missions']}")
    print(f"   Successful Missions: {results['successful_missions']} ({results['success_rate']:.1f}%)")
    print(f"   Failed Missions: {results['failed_missions']} ({results['failure_rate']:.1f}%)")
    
    # Mostrar algunos ejemplos de misiones exitosas
    print(f"\n✅ SUCCESSFUL MISSIONS (First 5):")
    print("-" * 80)
    for i, (_, mission) in enumerate(results['successful_data'].head(5).iterrows(), 1):
        print(f"{i}. Flight #{mission['flight_number']} - {mission['name']}")
        print(f"   Date: {mission['date_utc'][:10]}")
        print(f"   Success: {'✅ Yes' if mission['success'] else '❌ No'}")
        print("-" * 80)
    
    # Mostrar algunos ejemplos de misiones fallidas
    if len(results['failed_data']) > 0:
        print(f"\n❌ FAILED MISSIONS (First 5):")
        print("-" * 80)
        for i, (_, mission) in enumerate(results['failed_data'].head(5).iterrows(), 1):
            print(f"{i}. Flight #{mission['flight_number']} - {mission['name']}")
            print(f"   Date: {mission['date_utc'][:10]}")
            print(f"   Success: {'✅ Yes' if mission['success'] else '❌ No'}")
            print("-" * 80)
    else:
        print(f"\n❌ FAILED MISSIONS: None found")
    
    # Análisis por año
    df_all = pd.concat([results['successful_data'], results['failed_data']])
    df_all['year'] = pd.to_datetime(df_all['date_utc']).dt.year
    
    yearly_outcomes = df_all.groupby(['year', 'success']).size().unstack(fill_value=0)
    yearly_outcomes.columns = ['Failed', 'Successful']
    
    print(f"\n📅 MISSION OUTCOMES BY YEAR:")
    for year, row in yearly_outcomes.iterrows():
        total_year = row['Successful'] + row['Failed']
        success_rate_year = (row['Successful'] / total_year) * 100 if total_year > 0 else 0
        print(f"   {int(year)}: {int(row['Successful'])} successful, {int(row['Failed'])} failed ({success_rate_year:.1f}% success rate)")

def grafica_resultados_misiones(results):
    """
    Crea gráfica de resultados de misiones
    """
    print("Creando gráfica de resultados de misiones...")
    
    plt.figure(figsize=(16, 10))
    
    # Gráfica 1: Resumen general
    plt.subplot(2, 2, 1)
    labels = ['Successful', 'Failed']
    sizes = [results['successful_missions'], results['failed_missions']]
    colors = ['#2ca02c', '#d62728']
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title('Mission Outcomes Distribution', fontsize=14, fontweight='bold')
    
    # Gráfica 2: Barras de comparación
    plt.subplot(2, 2, 2)
    plt.bar(['Successful', 'Failed'], [results['successful_missions'], results['failed_missions']], 
            color=colors, alpha=0.7)
    plt.ylabel('Number of Missions', fontsize=12, fontweight='bold')
    plt.title('Mission Outcomes Count', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar valores en las barras
    for i, v in enumerate([results['successful_missions'], results['failed_missions']]):
        plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    # Gráfica 3: Tasa de éxito por año
    df_all = pd.concat([results['successful_data'], results['failed_data']])
    df_all['year'] = pd.to_datetime(df_all['date_utc']).dt.year
    
    yearly_outcomes = df_all.groupby(['year', 'success']).size().unstack(fill_value=0)
    yearly_outcomes.columns = ['Failed', 'Successful']
    yearly_outcomes['Success_Rate'] = (yearly_outcomes['Successful'] / 
                                      (yearly_outcomes['Successful'] + yearly_outcomes['Failed'])) * 100
    
    plt.subplot(2, 2, 3)
    plt.plot(yearly_outcomes.index, yearly_outcomes['Success_Rate'], 
             marker='o', linewidth=2, markersize=6, color='#2ca02c')
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    plt.title('Success Rate by Year', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)
    
    # Gráfica 4: Número de misiones por año
    plt.subplot(2, 2, 4)
    yearly_outcomes[['Successful', 'Failed']].plot(kind='bar', ax=plt.gca(), 
                                                   color=['#2ca02c', '#d62728'], alpha=0.7)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Missions', fontsize=12, fontweight='bold')
    plt.title('Missions by Year', fontsize=14, fontweight='bold')
    plt.legend(['Successful', 'Failed'])
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el análisis
    """
    print("🚀 SPACEX MISSION OUTCOMES ANALYSIS")
    print("="*50)
    
    # 1. Obtener datos
    launches = obtener_datos_spacex()
    if launches is None:
        return
    
    # 2. Calcular resultados de misiones
    results = calcular_resultados_misiones(launches)
    
    # 3. Mostrar resultados
    mostrar_resultados_misiones(results)
    
    # 4. Crear visualización
    grafica_resultados_misiones(results)
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()

