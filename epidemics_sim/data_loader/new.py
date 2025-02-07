import csv
import json
def csv_to_nested_dict(filename):
    """
    Convierte un archivo CSV en un diccionario anidado donde las columnas son las llaves principales,
    las filas son las llaves secundarias y los valores son los datos correspondientes.
    """
    data = {}
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Obtener el encabezado (nombres de las columnas)
        
        # Inicializar el diccionario con las columnas como llaves principales
        for column in header[1:]:  # Excluir la primera columna (encabezados de las filas)
            data[column] = {}
            
        row_header = []
        for row in reader:
            row_header.append(row[0])
                
        # Llenar el diccionario con los datos
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            for row, row_title in zip(reader, row_header):
                for i, column in enumerate(header[1:]):
                    data[column][row_title] = row[i+1]
    
    return data
def dict_to_json(data, filename):
    """
    Convierte un diccionario a formato JSON y lo guarda en un archivo.
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # indent para una mejor legibilidad

# Ejemplo de uso:
filename = 'epidemics_sim/data/escuelas.csv'
diccionario = csv_to_nested_dict(filename)
dict_to_json(diccionario,'epidemics_sim/data/escuelas.json')
#print(diccionario.keys())
