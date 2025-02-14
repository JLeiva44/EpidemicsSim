import pandas as pd
import json

# Cargar los archivos CSV con la codificación correcta
poblacion_path = "epidemics_sim/data/habana/csv_files/poblacion.csv"
comorbilidades_path = "epidemics_sim/data/habana/csv_files/comorbilidades.csv"
escuelas_path = "epidemics_sim/data/habana/csv_files/escuelas.csv"
centros_path = "epidemics_sim/data/habana/csv_files/centros.csv"
poblacion_laboral_path = "epidemics_sim/data/habana/csv_files/poblacion_la_habana.csv"

poblacion_df = pd.read_csv(poblacion_path, encoding="utf-8")
comorbilidades_df = pd.read_csv(comorbilidades_path, encoding="utf-8")
escuelas_df = pd.read_csv(escuelas_path, encoding="utf-8")
centros_df = pd.read_csv(centros_path, encoding="utf-8")
poblacion_laboral_df = pd.read_csv(poblacion_laboral_path, encoding="utf-8")

# Inspeccionar las primeras filas de cada dataset
print(poblacion_df.head())
print(comorbilidades_df.head())
print(escuelas_df.head())
print(centros_df.head())
print(poblacion_laboral_df.head())

# Procesar datos de población
poblacion_df = poblacion_df.rename(columns={
    "Provincias/Municipios": "Municipio",  # Cambiar el nombre de la columna
    "TOTAL": "total_population", 
    "VARONES": "VARONES", 
    "HEMBRAS": "HEMBRAS", 
    "0-15": "0-15", 
    "16-59": "16-59", 
    "60 y +": "60 y +",
    "Promedio de Personas por Unidad de Alojamiento": "personas_por_alojamiento"
})

# Filtrar los datos para excluir "LA HABANA" (la provincia)
poblacion_df = poblacion_df[poblacion_df["Municipio"] != "LA HABANA"]

# Convertir a diccionario con estructura deseada
municipios_data = {}
for _, row in poblacion_df.iterrows():
    municipio = row["Municipio"]  # Ahora usa la columna renombrada
    municipios_data[municipio] = {
        "population": {
            "total_population": row["total_population"],
            "VARONES": row["VARONES"],
            "HEMBRAS": row["HEMBRAS"],
            "Habitantes_por_edad": {
                "0-15": row["0-15"],
                "16-59": row["16-59"],
                "60 y +": row["60 y +"]
            }
        },
        "Promedio de Personas por Unidad de Alojamiento": row["personas_por_alojamiento"]
    }

# Procesar datos de escuelas
# Filtrar solo las filas que nos interesan (de "Total" a "Técnica y profesional")
escuelas_df = escuelas_df[escuelas_df["CONCEPTO"].isin([
    "Total", "Círculos infantiles", "Primaria", "Media", 
    "Secundaria básica", "Preuniversitario", "Técnica y profesional"
])]

# Convertir los datos de escuelas a un formato más manejable
escuelas_data = {}
for _, row in escuelas_df.iterrows():
    tipo_escuela = row["CONCEPTO"]
    for municipio in escuelas_df.columns[1:]:  # Ignorar la columna "CONCEPTO"
        if municipio not in escuelas_data:
            escuelas_data[municipio] = {}
        
        # Convertir el valor a cadena y manejar valores nulos o flotantes
        valor = row[municipio]
        if pd.isna(valor):  # Si el valor es NaN (celda vacía), lo establecemos a 0
            valor = 0
        elif isinstance(valor, float):  # Si es un float, lo convertimos a entero
            valor = int(valor)
        else:  # Si es una cadena, eliminamos comas y convertimos a entero
            valor = int(str(valor).replace(",", ""))
        
        escuelas_data[municipio][tipo_escuela] = valor

# Eliminar la clave "Total" de los datos de escuelas
for municipio in escuelas_data:
    if "Total" in escuelas_data[municipio]:
        del escuelas_data[municipio]["Total"]

# Procesar datos de centros laborales
centros_df = centros_df.rename(columns={"PROVINCIA/MUNICIPIO": "Municipio"})
centros_data = {}
for _, row in centros_df.iterrows():
    municipio = row["Municipio"]
    if municipio != "La Habana":  # Ignorar la fila de La Habana en general
        centros_data[municipio] = int(row["Total"])

# Procesar datos de población en edad laboral
poblacion_laboral_df = poblacion_laboral_df.rename(columns={
    "PROVINCIA Y MUNICIPIOS": "Municipio",
    "Total (Edad Laboral)": "Total_Edad_Laboral",
    "Hombres (Edad Laboral)": "Hombres_Edad_Laboral",
    "Mujeres (Edad Laboral)": "Mujeres_Edad_Laboral",
    "Total (Fuera de Edad Laboral)": "Total_Fuera_Edad_Laboral",
    "Hombres (Fuera de Edad Laboral)": "Hombres_Fuera_Edad_Laboral",
    "Mujeres (Fuera de Edad Laboral)": "Mujeres_Fuera_Edad_Laboral"
})

# Filtrar los datos para excluir "LA HABANA" (la provincia)
poblacion_laboral_df = poblacion_laboral_df[poblacion_laboral_df["Municipio"] != "LA HABANA"]

poblacion_laboral_data = {}
for _, row in poblacion_laboral_df.iterrows():
    municipio = row["Municipio"]
    poblacion_laboral_data[municipio] = {
        "Edad_Laboral": {
            "Hombres": int(row["Hombres_Edad_Laboral"]),
            "Mujeres": int(row["Mujeres_Edad_Laboral"])
        },
        "Fuera_Edad_Laboral": {
            "Hombres": int(row["Hombres_Fuera_Edad_Laboral"]),
            "Mujeres": int(row["Mujeres_Fuera_Edad_Laboral"])
        }
    }

# Agregar datos de escuelas, centros laborales y población en edad laboral a los municipios
for municipio in municipios_data.keys():
    # Escuelas
    if municipio in escuelas_data:
        municipios_data[municipio]["Escuelas"] = escuelas_data[municipio]
    
    # Centros laborales
    if municipio in centros_data:
        municipios_data[municipio]["Centros_Laborales"] = centros_data[municipio]
    
    # Población en edad laboral
    if municipio in poblacion_laboral_data:
        municipios_data[municipio]["Poblacion_Edad_Laboral"] = poblacion_laboral_data[municipio]

# Procesar datos de comorbilidades
comorbilidades_habana = comorbilidades_df[comorbilidades_df["Provincia"] == "La Habana"].iloc[0]
comorbilidades_data = {
    "hipertension_arterial": comorbilidades_habana["Hipertensión arterial"],  # Convertir a porcentaje
    "asma": comorbilidades_habana["Asma bronquial"],
    "diabetes": comorbilidades_habana["Diabetes mellitus"],
    "enfermedad_cerebrovascular": comorbilidades_habana["Enfermedad cerebrovascular"]
}

# Función auxiliar para limpiar valores numéricos
def limpiar_numero(valor):
    if isinstance(valor, str):  
        return int(valor.replace(",", ""))  # Eliminar comas y convertir a int
    return int(valor)  # Si ya es un número, solo convertir a int

# Agregar datos generales
json_data = {
    "municipios": municipios_data,
    "Comorbilidades": comorbilidades_data,
    "total_empresas": 515,  # Valores fijos según tu ejemplo
    "total_tiendas": 101
}

# Guardar en un archivo JSON
json_path = "epidemics_sim/data/habana/json_files/habana5.json"
with open(json_path, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
