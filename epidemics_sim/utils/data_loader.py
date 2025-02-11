import pandas as pd
import json

# Cargar los archivos CSV con la codificación correcta
poblacion_path = "epidemics_sim/data/habana/csv_files/poblacion.csv"
comorbilidades_path = "epidemics_sim/data/habana/csv_files/comorbilidades.csv"
escuelas_path = "epidemics_sim/data/habana/csv_files/escuelas.csv"

poblacion_df = pd.read_csv(poblacion_path, encoding="utf-8")
comorbilidades_df = pd.read_csv(comorbilidades_path, encoding="utf-8")
escuelas_df = pd.read_csv(escuelas_path, encoding="utf-8")

# Inspeccionar las primeras filas de cada dataset
poblacion_df.head(), comorbilidades_df.head(), escuelas_df.head()

# Procesar datos de población
poblacion_df = poblacion_df.rename(columns={"Provincias/Municipios": "Municipio", "TOTAL": "total_population", 
                                            "VARONES": "VARONES", "HEMBRAS": "HEMBRAS", 
                                            "0-15": "0-15", "16-59": "16-59", "60 y +": "60 y +",
                                            "Promedio de Personas por Unidad de Alojamiento": "personas_por_alojamiento"})

# Eliminar el filtro para incluir todos los municipios
municipios_data = {}
for _, row in poblacion_df.iterrows():
    municipio = row["Municipio"]
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
escuelas_df = escuelas_df.rename(columns={"CONCEPTO": "Tipo"})
escuelas_data = escuelas_df.set_index("Tipo").to_dict()

print(escuelas_df.columns)  # Ver nombres de columnas
print(escuelas_df["Tipo"].unique())  # Ver nombres de tipos de escuela
print(escuelas_data["Total"])  # Ver nombres de columnas en el diccionario

# Agregar datos de escuelas a los municipios
for municipio in municipios_data.keys():
    if municipio in escuelas_data["Total"]:
        municipios_data[municipio]["Escuelas"] = {
            "Total": int(escuelas_data["Total"][municipio]),
            "Circulos infantiles": int(escuelas_data["Círculos infantiles"][municipio]),
            "Primaria": int(escuelas_data["Primaria"][municipio]),
            "Media": int(escuelas_data["Media"][municipio]),
            "Secundaria basica": int(escuelas_data["Secundaria básica"][municipio]),
            "Preuniversitario": int(escuelas_data["Preuniversitario"][municipio]),
            "Tecnica y profesional": int(escuelas_data["Técnica y profesional"][municipio])
        }

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
    "total_tiendas": 101,
    "Escuelas_Total": {
        "Total": limpiar_numero(escuelas_data["Total"]["Total"]),
        "Círculos infantiles": limpiar_numero(escuelas_data["Total"]["Círculos infantiles"]),
        "Primaria": limpiar_numero(escuelas_data["Total"]["Primaria"]),
        "Media": limpiar_numero(escuelas_data["Total"]["Media"]),
        "Secundaria": limpiar_numero(escuelas_data["Total"]["Secundaria básica"]),
        "Preuniversitario": limpiar_numero(escuelas_data["Total"]["Preuniversitario"]),
        "Tecnica y profesional": limpiar_numero(escuelas_data["Total"]["Técnica y profesional"])
    }
}

# Guardar en un archivo JSON
json_path = "epidemics_sim/data/habana/json_files/habana.json"
with open(json_path, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)


# import pandas as pd
# import json

# # Cargar los archivos CSV con la codificación correcta
# poblacion_path = "epidemics_sim/data/csv_files/poblacion.csv"
# comorbilidades_path = "epidemics_sim/data/csv_files/comorbilidades.csv"
# escuelas_path = "epidemics_sim/data/csv_files/escuelas.csv"

# poblacion_df = pd.read_csv(poblacion_path, encoding="utf-8")
# comorbilidades_df = pd.read_csv(comorbilidades_path, encoding="utf-8")
# escuelas_df = pd.read_csv(escuelas_path, encoding="utf-8")

# # Inspeccionar las primeras filas de cada dataset
# poblacion_df.head(), comorbilidades_df.head(), escuelas_df.head()



# # Procesar datos de población
# poblacion_df = poblacion_df.rename(columns={"Provincias/Municipios": "Municipio", "TOTAL": "total_population", 
#                                             "VARONES": "VARONES", "HEMBRAS": "HEMBRAS", 
#                                             "0-15": "0-15", "16-59": "16-59", "60 y +": "60 y +",
#                                             "Promedio de Personas por Unidad de Alojamiento": "personas_por_alojamiento"})

# # Filtrar municipios relevantes
# municipios_interes = ["PLAYA", "REGLA", "LA HABANA DEL ESTE", "GUANABACOA", "SAN MIGUEL DEL PADRON", "DIEZ DE OCTUBRE"]
# poblacion_df = poblacion_df[poblacion_df["Municipio"].isin(municipios_interes)]

# # Convertir a diccionario con estructura deseada
# municipios_data = {}
# for _, row in poblacion_df.iterrows():
#     municipio = row["Municipio"]
#     municipios_data[municipio] = {
#         "population": {
#             "total_population": row["total_population"],
#             "VARONES": row["VARONES"],
#             "HEMBRAS": row["HEMBRAS"],
#             "Habitantes_por_edad": {
#                 "0-15": row["0-15"],
#                 "16-59": row["16-59"],
#                 "60 y +": row["60 y +"]
#             }
#         },
#         "Promedio de Personas por Unidad de Alojamiento": row["personas_por_alojamiento"]
#     }

# # Procesar datos de escuelas
# escuelas_df = escuelas_df.rename(columns={"CONCEPTO": "Tipo"})
# escuelas_data = escuelas_df.set_index("Tipo").to_dict()

# print(escuelas_df.columns)  # Ver nombres de columnas
# print(escuelas_df["Tipo"].unique())  # Ver nombres de tipos de escuela
# print(escuelas_data["Total"])  # Ver nombres de columnas en el diccionario

# # Agregar datos de escuelas a los municipios
# for municipio in municipios_interes:
#     if municipio in escuelas_data["Total"]:
#         municipios_data[municipio]["Escuelas"] = {
#             "Total": int(escuelas_data["Total"][municipio]),
#             "Circulos infantiles": int(escuelas_data["Círculos infantiles"][municipio]),
#             "Primaria": int(escuelas_data["Primaria"][municipio]),
#             "Media": int(escuelas_data["Media"][municipio]),
#             "Secundaria basica": int(escuelas_data["Secundaria básica"][municipio]),
#             "Preuniversitario": int(escuelas_data["Preuniversitario"][municipio]),
#             "Tecnica y profesional": int(escuelas_data["Técnica y profesional"][municipio])
#         }

# # Procesar datos de comorbilidades
# comorbilidades_habana = comorbilidades_df[comorbilidades_df["Provincia"] == "La Habana"].iloc[0]
# comorbilidades_data = {
#     "hipertension_arterial": comorbilidades_habana["Hipertensión arterial"] / 10,  # Convertir a porcentaje
#     "asma": comorbilidades_habana["Asma bronquial"] / 10,
#     "diabetes": comorbilidades_habana["Diabetes mellitus"] / 10,
#     "enfermedad_cerebrovascular": comorbilidades_habana["Enfermedad cerebrovascular"] / 10
# }

# # Función auxiliar para limpiar valores numéricos
# def limpiar_numero(valor):
#     if isinstance(valor, str):  
#         return int(valor.replace(",", ""))  # Eliminar comas y convertir a int
#     return int(valor)  # Si ya es un número, solo convertir a int


# # Agregar datos generales
# json_data = {
#     "municipios": municipios_data,
#     "Comorbilidades": comorbilidades_data,
#     "total_empresas": 515,  # Valores fijos según tu ejemplo
#     "total_tiendas": 101,
#     "Escuelas_Total": {
#         "Total": limpiar_numero(escuelas_data["Total"]["Total"]),
#         "Círculos infantiles": limpiar_numero(escuelas_data["Total"]["Círculos infantiles"]),
#         "Primaria": limpiar_numero(escuelas_data["Total"]["Primaria"]),
#         "Media": limpiar_numero(escuelas_data["Total"]["Media"]),
#         "Secundaria": limpiar_numero(escuelas_data["Total"]["Secundaria básica"]),
#         "Preuniversitario": limpiar_numero(escuelas_data["Total"]["Preuniversitario"]),
#         "Tecnica y profesional": limpiar_numero(escuelas_data["Total"]["Técnica y profesional"])
#     }
# }

# # Guardar en un archivo JSON
# json_path = "epidemics_sim/data/json_files/habana.json"
# with open(json_path, "w", encoding="utf-8") as json_file:
#     json.dump(json_data, json_file, ensure_ascii=False, indent=4)

# #json_path