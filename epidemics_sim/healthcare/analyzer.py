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
        self.age_groups = defaultdict(list)
        self.gender_data = {"mujeres": [], "hombres": []}
        self.severity_data = {"graves": [], "criticos": [], "muertes": []}

    def load_json_data(self, casos_file, fallecidos_file):
        # Cargar casos diarios
        with open(casos_file, "r") as file:
            casos_data = json.load(file)
        
        # Cargar fallecidos
        with open(fallecidos_file, "r") as file:
            fallecidos_data = json.load(file)
        
        # Procesar casos diarios
        for day, day_data in casos_data["casos"]["dias"].items():
            fecha = day_data["fecha"]
            
            # Filtrar casos de La Habana (dpacode_provincia_deteccion == "23")
            casos_habana = [caso for caso in day_data["diagnosticados"] 
                            if caso["dpacode_provincia_deteccion"] == "23"]
            
            nuevos_casos = len(casos_habana)
            graves = day_data.get("graves_numero", 0)
            criticos = day_data.get("criticos_numero", 0)
            asintomaticos = day_data.get("asintomaticos_numero", 0)
            mujeres = day_data.get("mujeres", 0)
            hombres = day_data.get("hombres", 0)
            edad_19 = day_data.get("_19", 0)
            edad_20_39 = day_data.get("20_39", 0)
            edad_40_59 = day_data.get("40_59", 0)
            edad_60 = day_data.get("60_", 0)

            # Obtener muertes del JSON de fallecidos
            muertes = fallecidos_data["fallecidos"]["dias"].get(day, {}).get("muertes_numero", 0)

            # Registrar estadísticas diarias
            stats = {
                "day": int(day),
                "fecha": fecha,
                "total_cases": sum(len([c for c in d["diagnosticados"] 
                                     if c["dpacode_provincia_deteccion"] == "23"]) 
                               for d in casos_data["casos"]["dias"].values() if int(d) <= int(day)),
                "new_cases": nuevos_casos,
                "total_deaths": sum(d.get("muertes_numero", 0) for d in fallecidos_data["fallecidos"]["dias"].values() 
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

    def generate_simulation_report(self, filename="epidemics_sim/results/simulation_report.json"):
        report = {
            "total_cases": self.total_cases,
            "total_deaths": self.total_deaths,
            "daily_stats": self.daily_stats,
            "municipal_data": {municipio: sum(cases) for municipio, cases in self.municipal_data.items()},
            "age_groups": {group: sum(cases) for group, cases in self.age_groups.items()},
            "gender_data": self.gender_data,
            "severity_data": self.severity_data
        }
        
        with open(filename, "w") as file:
            json.dump(report, file, indent=4)
        print(f"Simulation report saved as {filename}")

    def plot_comparison(self, real_data):
        days = range(1, len(self.daily_stats) + 1)
        
        # Datos de la simulación
        sim_cases = [stat["total_cases"] for stat in self.daily_stats]
        sim_deaths = [stat["total_deaths"] for stat in self.daily_stats]
        
        # Datos reales
        real_cases = [stat["total_cases"] for stat in real_data["daily_stats"]]
        real_deaths = [stat["total_deaths"] for stat in real_data["daily_stats"]]
        
        # Gráfico de casos totales
        df_cases = pd.DataFrame({
            "Días": days,
            "Simulación": sim_cases,
            "Reales": real_cases
        })
        fig_cases = px.line(df_cases, x="Días", y=["Simulación", "Reales"], 
                            title="Comparación de Casos Totales (Simulación vs Reales)",
                            labels={"value": "Casos", "variable": "Tipo"})
        fig_cases.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Casos Totales")
        fig_cases.write_html("epidemics_sim/results/comparison_cases.html")
        print("Saved comparison cases plot as comparison_cases.html")
        
        # Gráfico de muertes totales
        df_deaths = pd.DataFrame({
            "Días": days,
            "Simulación": sim_deaths,
            "Reales": real_deaths
        })
        fig_deaths = px.line(df_deaths, x="Días", y=["Simulación", "Reales"], 
                             title="Comparación de Muertes Totales (Simulación vs Reales)",
                             labels={"value": "Muertes", "variable": "Tipo"})
        fig_deaths.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Muertes Totales")
        fig_deaths.write_html("epidemics_sim/results/comparison_deaths.html")
        print("Saved comparison deaths plot as comparison_deaths.html")

    def analyze_results(self, real_data, filename="epidemics_sim/results/comparison_analysis.json"):
        analysis = {
            "total_cases": {
                "simulation": self.total_cases,
                "real": real_data["total_cases"],
                "difference": self.total_cases - real_data["total_cases"]
            },
            "total_deaths": {
                "simulation": self.total_deaths,
                "real": real_data["total_deaths"],
                "difference": self.total_deaths - real_data["total_deaths"]
            },
            "daily_cases_mae": self.calculate_mae(
                [stat["total_cases"] for stat in self.daily_stats],
                [stat["total_cases"] for stat in real_data["daily_stats"]]
            ),
            "daily_deaths_mae": self.calculate_mae(
                [stat["total_deaths"] for stat in self.daily_stats],
                [stat["total_deaths"] for stat in real_data["daily_stats"]]
            )
        }
        
        with open(filename, "w") as file:
            json.dump(analysis, file, indent=4)
        print(f"Comparison analysis saved as {filename}")

    def calculate_mae(self, simulated, real):
        return sum(abs(s - r) for s, r in zip(simulated, real)) / len(simulated)

    def generate_municipality_table(self):
        sorted_municipalities = sorted(self.municipal_cases.items(), key=lambda x: sum(x[1]), reverse=True)
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
            <iframe src='comparison_cases.html' width='100%' height='500'></iframe>
            <iframe src='comparison_deaths.html' width='100%' height='500'></iframe>
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
        days = range(1, len(self.daily_cases) + 1)
        data = {"Días": days}
        
        max_length = len(days)
        for municipality, cases in self.municipal_data.items():
            if len(cases) < max_length:
                cases.extend([0] * (max_length - len(cases)))
            data[municipality] = cases

        df = pd.DataFrame(data)
        fig = px.line(df, x="Días", y=df.columns[1:], title="Comparación de Casos por Municipio",
                      labels={"value": "Casos", "variable": "Municipio"})
        fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Casos")
        fig.update_xaxes(rangeslider_visible=True)
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
        fig.update_xaxes(rangeslider_visible=True)
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
        fig.update_xaxes(rangeslider_visible=True)
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
        fig.update_xaxes(rangeslider_visible=True)
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
        fig.update_xaxes(rangeslider_visible=True)
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