import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template
from collections import defaultdict
import json
class SimulationAnalyzer:
    def __init__(self):
        self.daily_stats = []
        self.total_cases = 0
        self.total_deaths = 0
        self.daily_cases = []
        self.daily_deaths = []
        self.report_data = []
        self.municipal_cases = {}  # Diccionario para almacenar casos por municipio
        self.municipal_data = {}   # Diccionario para almacenar datos diarios por municipio

    def record_daily_stats(self, new_cases, new_deaths, municipality_data):
        self.total_cases += new_cases
        self.total_deaths += new_deaths
        self.daily_cases.append(new_cases)
        self.daily_deaths.append(new_deaths)
        
        # Actualizar casos por municipio
        for municipality, cases in municipality_data.items():
            if municipality not in self.municipal_cases:
                self.municipal_cases[municipality] = 0
                self.municipal_data[municipality] = []
            self.municipal_cases[municipality]  = municipality_data[municipality]
            self.municipal_data[municipality].append(cases)

        stats = {
            "day": len(self.daily_cases),
            "total_cases": self.total_cases,
            "new_cases": new_cases,
            "total_deaths": self.total_deaths,
            "new_deaths": new_deaths
        }
        self.daily_stats.append(stats)
        
        if len(self.daily_cases) % 10 == 0:
            self.report_data.append(stats)
    
    def load_json_data(self, json_file):
        with open(json_file, "r") as file:
            data = json.load(file)
        
        # Inicializar estructuras de datos
        self.daily_stats = []
        self.municipal_data = defaultdict(list)
        self.age_groups = defaultdict(list)
        self.gender_data = {"mujeres": [], "hombres": []}
        self.severity_data = {"graves": [], "criticos": [], "muertes": []}

        # Procesar cada día
        for day, day_data in data["casos"]["dias"].items():
            fecha = day_data["fecha"]
            
            # Filtrar casos de La Habana (dpacode_provincia_deteccion == "23")
            casos_habana = [caso for caso in day_data["diagnosticados"] 
                            if caso["dpacode_provincia_deteccion"] == "23"]
            
            nuevos_casos = len(casos_habana)
            muertes = day_data.get("muertes_numero", 0)
            graves = day_data.get("graves_numero", 0)
            criticos = day_data.get("criticos_numero", 0)
            asintomaticos = day_data.get("asintomaticos_numero", 0)
            mujeres = day_data.get("mujeres", 0)
            hombres = day_data.get("hombres", 0)
            edad_19 = day_data.get("_19", 0)
            edad_20_39 = day_data.get("20_39", 0)
            edad_40_59 = day_data.get("40_59", 0)
            edad_60 = day_data.get("60_", 0)

            # Registrar estadísticas diarias
            stats = {
                "day": int(day),
                "fecha": fecha,
                "total_cases": sum(len([c for c in d["diagnosticados"] 
                                    if c["dpacode_provincia_deteccion"] == "23"]) 
                            for d in data["casos"]["dias"].values() if int(d) <= int(day)),
                "new_cases": nuevos_casos,
                "total_deaths": sum(d.get("muertes_numero", 0) for d in data["casos"]["dias"].values() 
                                if int(d) <= int(day)),
                "new_deaths": muertes,
                "graves": graves,
                "criticos": criticos,
                "asintomaticos": asintomaticos,
                "mujeres": mujeres,
                "hombres": hombres,
                "_19": edad_19,
                "20_39": edad_20_39,
                "40_59": edad_40_59,
                "60_": edad_60
            }
            self.daily_stats.append(stats)

            # Registrar datos por municipio (solo La Habana)
            for caso in casos_habana:
                municipio = caso["municipio_detección"]
                self.municipal_data[municipio].append(1)  # Contar casos por municipio

            # Registrar datos por grupo de edad
            self.age_groups["_19"].append(edad_19)
            self.age_groups["20_39"].append(edad_20_39)
            self.age_groups["40_59"].append(edad_40_59)
            self.age_groups["60_"].append(edad_60)

            # Registrar datos por género
            self.gender_data["mujeres"].append(mujeres)
            self.gender_data["hombres"].append(hombres)

            # Registrar datos de gravedad
            self.severity_data["graves"].append(graves)
            self.severity_data["criticos"].append(criticos)
            self.severity_data["muertes"].append(muertes)
            
    def generate_municipality_table(self):
        # Filtrar municipios de La Habana
        sorted_municipalities = sorted(self.municipal_data.items(), key=lambda x: sum(x[1]), reverse=True)
        total_cases = self.total_cases if self.total_cases > 0 else 1  # Para evitar división por cero
        table_rows = "".join(f"<tr><td>{m}</td><td>{sum(cases)}</td><td>{(sum(cases) / total_cases) * 100:.2f}%</td></tr>" 
                        for m, cases in sorted_municipalities)
        return f"""
        <table border='1'>
            <tr><th>Municipio</th><th>Total Casos</th><th>Porcentaje del Total</th></tr>
            {table_rows}
        </table>
        """

    def generate_html_report(self, filename="epidemics_sim/results/simulation_report.html"):
        template = Template("""
        <html>
        <head>
            <title>Reporte de Simulación</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #333; }
                iframe { border: none; margin-bottom: 20px; }
                table { border-collapse: collapse; width: 50%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .summary { margin-bottom: 20px; }
                .summary p { font-size: 18px; }
            </style>
        </head>
        <body>
            <h1>Reporte de Simulación</h1>
            <div class="summary">
                <p><strong>Casos Acumulados:</strong> {{ total_cases }}</p>
                <p><strong>Muertes Acumuladas:</strong> {{ total_deaths }}</p>
            </div>
            <h2>Casos Acumulados por Municipio</h2>
            {{ municipality_table }}
            <h2>Gráficos</h2>
            <iframe src='total_cases.html' width='100%' height='500'></iframe>
            <iframe src='daily_cases.html' width='100%' height='500'></iframe>
            <iframe src='total_deaths.html' width='100%' height='500'></iframe>
            <iframe src='daily_deaths.html' width='100%' height='500'></iframe>
            <iframe src='municipality_comparison.html' width='100%' height='600'></iframe>
            <iframe src='municipality_interactive.html' width='100%' height='600'></iframe>
        </body>
        </html>
        """)
        
        html_content = template.render(
            total_cases=self.total_cases,
            total_deaths=self.total_deaths,
            municipality_table=self.generate_municipality_table()
        )
        with open(filename, "w") as file:
            file.write(html_content)
        print(f"HTML report saved as {filename}")

    def plot_municipality_comparison(self):
        df = pd.DataFrame(list(self.municipal_cases.items()), columns=["Municipality", "Cases"])
        fig = px.bar(df, x='Municipality', y='Cases', title='Comparación de Casos por Municipio', 
                     labels={'Cases': 'Casos Acumulados'}, color='Cases', color_continuous_scale='Viridis')
        fig.update_layout(template="plotly_white", xaxis_title="Municipio", yaxis_title="Casos Acumulados")
        fig.write_html("epidemics_sim/results/municipality_comparison.html")
        print("Municipality comparison chart saved as municipality_comparison.html")

    def plot_municipality_interactive(self):
        # Crear un DataFrame con los datos diarios de cada municipio de La Habana
        days = range(1, len(self.daily_cases) + 1)
        data = {"Días": days}
        
        # Asegurar que todas las listas de casos tengan la misma longitud
        max_length = len(days)
        for municipality, cases in self.municipal_data.items():
            if len(cases) < max_length:
                # Rellenar con ceros si la lista es más corta
                cases.extend([0] * (max_length - len(cases)))
            data[municipality] = cases

        df = pd.DataFrame(data)
        fig = px.line(df, x="Días", y=df.columns[1:], title="Comparación de Casos por Municipio (La Habana)",
                    labels={"value": "Casos", "variable": "Municipio"})
        fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Casos")
        fig.update_xaxes(rangeslider_visible=True)  # Agregar un slider para ajustar el intervalo de tiempo
        fig.write_html("epidemics_sim/results/municipality_interactive.html")
        print("Interactive municipality comparison chart saved as municipality_interactive.html")
        
    def plot_cases(self):
        days = range(1, len(self.daily_cases) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Casos Totales": [stat["total_cases"] for stat in self.daily_stats]
        })
        fig = px.line(df, x="Días", y="Casos Totales", title="Casos Totales a lo Largo del Tiempo",
                      labels={"Casos Totales": "Casos Totales", "Días": "Días"})
        fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Casos Totales")
        fig.update_xaxes(rangeslider_visible=True)  # Agregar un slider para ajustar el intervalo de tiempo
        fig.write_html("epidemics_sim/results/total_cases.html")
        print("Saved total cases plot as total_cases.html")

    def plot_daily_cases(self):
        days = range(1, len(self.daily_cases) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Nuevos Casos": self.daily_cases
        })
        fig = px.bar(df, x="Días", y="Nuevos Casos", title="Nuevos Casos por Día",
                     labels={"Nuevos Casos": "Nuevos Casos", "Días": "Días"})
        fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Nuevos Casos")
        fig.update_xaxes(rangeslider_visible=True)  # Agregar un slider para ajustar el intervalo de tiempo
        fig.write_html("epidemics_sim/results/daily_cases.html")
        print("Saved daily cases plot as daily_cases.html")

    def plot_deaths(self):
        days = range(1, len(self.daily_deaths) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Muertes Totales": [stat["total_deaths"] for stat in self.daily_stats]
        })
        fig = px.line(df, x="Días", y="Muertes Totales", title="Muertes Totales a lo Largo del Tiempo",
                      labels={"Muertes Totales": "Muertes Totales", "Días": "Días"})
        fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Muertes Totales")
        fig.update_xaxes(rangeslider_visible=True)  # Agregar un slider para ajustar el intervalo de tiempo
        fig.write_html("epidemics_sim/results/total_deaths.html")
        print("Saved total deaths plot as total_deaths.html")

    def plot_daily_deaths(self):
        days = range(1, len(self.daily_deaths) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Nuevas Muertes": self.daily_deaths
        })
        fig = px.bar(df, x="Días", y="Nuevas Muertes", title="Nuevas Muertes por Día",
                     labels={"Nuevas Muertes": "Nuevas Muertes", "Días": "Días"})
        fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Nuevas Muertes")
        fig.update_xaxes(rangeslider_visible=True)  # Agregar un slider para ajustar el intervalo de tiempo
        fig.write_html("epidemics_sim/results/daily_deaths.html")
        print("Saved daily deaths plot as daily_deaths.html")

    def generate_full_report(self):
        self.plot_cases()
        self.plot_daily_cases()
        self.plot_deaths()
        self.plot_daily_deaths()
        self.plot_municipality_comparison()
        self.plot_municipality_interactive()
        self.generate_html_report()