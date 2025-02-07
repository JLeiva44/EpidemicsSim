import csv
import os

def detect_delimiter(file_path):
    """Detect the delimiter used in the CSV file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        sample = file.readline()
        return ',' if ',' in sample else ';'

def load_csv_data(file_path):
    """
    Load an entire CSV file into a dictionary where:
    - Columns are the main keys.
    - Rows (municipios) are subkeys.
    - Values are stored accordingly.
    """
    data = {}
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: {file_path} not found!")
        return data

    delimiter = detect_delimiter(file_path)
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        municipios = []
        column_names = reader.fieldnames[1:]  # Omitimos la primera columna (municipio)
        
        for row in reader:
            municipio = row[reader.fieldnames[0]].strip()
            municipios.append(municipio)
            for col in column_names:
                if col not in data:
                    data[col] = {}
                data[col][municipio] = float(row[col]) if row[col] else 0  # Convertir valores a float

    return data

def load_all_csvs(csv_files):
    """
    Load multiple CSV files into a structured dictionary.
    """
    all_data = {}
    
    for category, file_path in csv_files.items():
        all_data[category] = load_csv_data(file_path)
    
    return all_data

# Example CSV file definitions
csv_files = {
    "poblacion": "epidemics_sim/data/poblacion.csv",
    "escuelas": "epidemics_sim/data/escuelas.csv",
    "comorbilidades": "epidemics_sim/data/comorbilidades.csv",
    "centros": "epidemics_sim/data/empresas.csv"
}

# Load all data
dataset = load_all_csvs(csv_files)

# Print sample output
import json
print(json.dumps(dataset, indent=4, ensure_ascii=False))
