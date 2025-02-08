import json


def order_by_municipios(data):
    """
    Reordena el diccionario JSON para organizar la información por municipios.
    """
    municipios = [
        "PLAYA", "REGLA", "LA HABANA DEL ESTE", "GUANABACOA",
        "SAN MIGUEL DEL PADRON", "DIEZ DE OCTUBRE", "CERRO",
        "MARIANAO", "LA LISA", "BOYEROS", "ARROYO NARANJO", "COTORRO",
        "PLAZA DE LA REVOLUCION", "CENTRO HABANA", "LA HABANA VIEJA", "LA HABANA"
    ]

    ordered_data = {}

    #Procesa cada municipio
    for municipio in municipios:
        ordered_data[municipio] = {}

        #Procesa population
        ordered_data[municipio]["population"] = {}
        ordered_data[municipio]["population"]["total_population"] = data["population"]["total_population"].get(municipio, None)
        ordered_data[municipio]["population"]["VARONES"] = data["population"]["VARONES"].get(municipio, None)
        ordered_data[municipio]["population"]["HEMBRAS"] = data["population"]["HEMBRAS"].get(municipio, None)
        ordered_data[municipio]["population"]["Habitantes_por_edad"] = {}
        ordered_data[municipio]["population"]["Habitantes_por_edad"]["0-15"] = data["population"]["Habitantes_por_edad"]["0-15"].get(municipio, None)
        ordered_data[municipio]["population"]["Habitantes_por_edad"]["16-59"] = data["population"]["Habitantes_por_edad"]["16-59"].get(municipio, None)
        ordered_data[municipio]["population"]["Habitantes_por_edad"]["60 y +"] = data["population"]["Habitantes_por_edad"]["60 y +"].get(municipio, None)
        
        #Procesa Escuelas
        ordered_data[municipio]["Escuelas"] = data["Escuelas"].get(municipio, None)

        #Procesa el promedio de personas por unidad de alojamiento
        ordered_data[municipio]["Promedio de Personas por Unidad de Alojamiento"] = data["Promedio de Personas por Unidad de Alojamiento"].get(municipio, None)
    
    # Agrega datos que no son por municipios
    ordered_data["Comorbilidades"] = data["Comorbilidades"]
    ordered_data["total_empresas"] = data["total_empresas"]
    ordered_data["Escuelas_Total"] = data["Escuelas"]["Total"]

    return ordered_data

data = {}
with open('epidemics_sim/data/habana.json', 'r') as archivo:
    # Cargar los datos del archivo en un diccionario
    data = json.load(archivo)

ordered_data = order_by_municipios(data)

# Convertir a JSON con indentación para mejor legibilidad
json_output = json.dumps(ordered_data, indent=4)

# Especifica el nombre del archivo JSON
filename = "epidemics_sim/data/municipios.json"

# Escribir el JSON resultante en un archivo
with open(filename, "w") as json_file:
    json_file.write(json_output)
# Convertir a JSON con indentación para mejor legibilidad
json_output = json.dumps(ordered_data, indent=4)
print(json_output)
