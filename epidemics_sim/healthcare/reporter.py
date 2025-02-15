import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template
from collections import defaultdict
import json
import os
from datetime import datetime

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
        self.real_data = None  # Datos reales cargados desde un archivo JSON

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
            #self.municipal_data[municipality].append(cases)

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
    
    def load_real_data(self, json_file, start_day=1, end_day=30):
        """
        Carga datos reales desde un archivo JSON y permite seleccionar un rango de días.
        
        :param json_file: Ruta al archivo JSON con los datos reales.
        :param start_day: Día inicial del rango (por defecto 1).
        :param end_day: Día final del rango (por defecto None, que significa hasta el último día).
        """
        with open(json_file, "r") as file:
            data = json.load(file)
            #data = data["casos"]
        
        # Filtrar datos por rango de días
        days = data["casos"]["dias"]
        filtered_days = {day: day_data for day, day_data in days.items() 
                         if start_day <= int(day) <= (end_day if end_day else float('inf'))}
        
        # Procesar datos filtrados
        self.real_data = {
            "daily_cases": [],
            "daily_deaths": [],
            "total_cases": [],
            "total_deaths": []
        }
        
        for day, day_data in filtered_days.items():
            diagnosticados ={}
            sin_casos = False
            try:
                day_data["diagnosticados"]
            except KeyError:
                sin_casos = True
            
            if not sin_casos:
                casos_habana = [caso for caso in day_data["diagnosticados"] 
                                if caso["dpacode_provincia_deteccion"] == "23"]
                nuevos_casos = len(casos_habana)
                muertes = day_data.get("muertes_numero", 0)
            else:
                nuevos_casos = 0
                muertes = day_data.get("muertes_numero", 0)
            
            self.real_data["daily_cases"].append(nuevos_casos)
            self.real_data["daily_deaths"].append(muertes)
            self.real_data["total_cases"].append(sum(self.real_data["daily_cases"]))
            self.real_data["total_deaths"].append(sum(self.real_data["daily_deaths"]))

    def plot_cases(self):
        """
        Grafica los casos totales de la simulación y los compara con los datos reales.
        """
        days = range(1, len(self.daily_cases) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Casos Totales (Simulación)": [stat["total_cases"] for stat in self.daily_stats],
            "Casos Totales (Reales)": self.real_data["total_cases"][:len(days)] if self.real_data else None
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Días"], y=df["Casos Totales (Simulación)"], 
                                 mode='lines', name='Simulación', line=dict(color='blue')))
        if self.real_data:
            fig.add_trace(go.Scatter(x=df["Días"], y=df["Casos Totales (Reales)"], 
                                     mode='lines', name='Reales', line=dict(color='red', dash='dash')))

        fig.update_layout(
            title="Comparación de Casos Totales",
            xaxis_title="Días",
            yaxis_title="Casos Totales",
            template="plotly_white",
            legend=dict(x=0.1, y=0.9)
        )
        fig.update_xaxes(rangeslider_visible=True)
        fig.write_html("epidemics_sim/results/total_cases.html")
        print("Saved total cases plot as total_cases.html")

    def plot_daily_cases(self):
        """
        Grafica los nuevos casos diarios de la simulación y los compara con los datos reales.
        """
        days = range(1, len(self.daily_cases) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Nuevos Casos (Simulación)": self.daily_cases,
            "Nuevos Casos (Reales)": self.real_data["daily_cases"][:len(days)] if self.real_data else None
        })

        fig = go.Figure()
        # Cambiar go.Bar por go.Scatter con mode='lines'
        fig.add_trace(go.Scatter(x=df["Días"], y=df["Nuevos Casos (Simulación)"], 
                                mode='lines', name='Simulación', line=dict(color='blue')))
        if self.real_data:
            fig.add_trace(go.Scatter(x=df["Días"], y=df["Nuevos Casos (Reales)"], 
                                mode='lines', name='Reales', line=dict(color='red', dash='dash')))

        fig.update_layout(
            title="Comparación de Nuevos Casos Diarios",
            xaxis_title="Días",
            yaxis_title="Nuevos Casos",
            template="plotly_white",
            legend=dict(x=0.1, y=0.9)
        )
        fig.update_xaxes(rangeslider_visible=True)
        fig.write_html("epidemics_sim/results/daily_cases.html")
        print("Saved daily cases plot as daily_cases.html")
    # def plot_daily_cases(self):
    #     """
    #     Grafica los nuevos casos diarios de la simulación y los compara con los datos reales.
    #     """
    #     days = range(1, len(self.daily_cases) + 1)
    #     df = pd.DataFrame({
    #         "Días": days,
    #         "Nuevos Casos (Simulación)": self.daily_cases,
    #         "Nuevos Casos (Reales)": self.real_data["daily_cases"][:len(days)] if self.real_data else None
    #     })

    #     fig = go.Figure()
    #     fig.add_trace(go.Bar(x=df["Días"], y=df["Nuevos Casos (Simulación)"], 
    #                     name='Simulación', marker_color='blue'))
    #     if self.real_data:
    #         fig.add_trace(go.Scatter(x=df["Días"], y=df["Nuevos Casos (Reales)"], 
    #                        mode='lines', name='Reales', line=dict(color='red', dash='dash')))

    #     fig.update_layout(
    #         title="Comparación de Nuevos Casos Diarios",
    #         xaxis_title="Días",
    #         yaxis_title="Nuevos Casos",
    #         template="plotly_white",
    #         legend=dict(x=0.1, y=0.9)
    #     )
    #     fig.update_xaxes(rangeslider_visible=True)
    #     fig.write_html("epidemics_sim/results/daily_cases.html")
    #     print("Saved daily cases plot as daily_cases.html")

    def plot_deaths(self):
        """
        Grafica las muertes totales de la simulación y las compara con los datos reales.
        """
        days = range(1, len(self.daily_deaths) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Muertes Totales (Simulación)": [stat["total_deaths"] for stat in self.daily_stats],
            "Muertes Totales (Reales)": self.real_data["total_deaths"][:len(days)] if self.real_data else None
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Días"], y=df["Muertes Totales (Simulación)"], 
                                 mode='lines', name='Simulación', line=dict(color='blue')))
        if self.real_data:
            fig.add_trace(go.Scatter(x=df["Días"], y=df["Muertes Totales (Reales)"], 
                                     mode='lines', name='Reales', line=dict(color='red', dash='dash')))

        fig.update_layout(
            title="Comparación de Muertes Totales",
            xaxis_title="Días",
            yaxis_title="Muertes Totales",
            template="plotly_white",
            legend=dict(x=0.1, y=0.9)
        )
        fig.update_xaxes(rangeslider_visible=True)
        fig.write_html("epidemics_sim/results/total_deaths.html")
        print("Saved total deaths plot as total_deaths.html")
    
    def plot_daily_deaths(self):
        """
        Grafica las nuevas muertes diarias de la simulación y las compara con los datos reales.
        """
        days = range(1, len(self.daily_deaths) + 1)
        df = pd.DataFrame({
            "Días": days,
            "Nuevas Muertes (Simulación)": self.daily_deaths,
            "Nuevas Muertes (Reales)": self.real_data["daily_deaths"][:len(days)] if self.real_data else None
        })

        fig = go.Figure()
        # Cambiar go.Bar por go.Scatter con mode='lines'
        fig.add_trace(go.Scatter(x=df["Días"], y=df["Nuevas Muertes (Simulación)"], 
                                mode='lines', name='Simulación', line=dict(color='blue')))
        if self.real_data:
            fig.add_trace(go.Scatter(x=df["Días"], y=df["Nuevas Muertes (Reales)"], 
                                    mode='lines', name='Reales', line=dict(color='red', dash='dash')))

        fig.update_layout(
            title="Comparación de Nuevas Muertes Diarias",
            xaxis_title="Días",
            yaxis_title="Nuevas Muertes",
            template="plotly_white",
            legend=dict(x=0.1, y=0.9)
        )
        fig.update_xaxes(rangeslider_visible=True)
        fig.write_html("epidemics_sim/results/daily_deaths.html")
        print("Saved daily deaths plot as daily_deaths.html")
    # def plot_daily_deaths(self):
    #     """
    #     Grafica las nuevas muertes diarias de la simulación y las compara con los datos reales.
    #     """
    #     days = range(1, len(self.daily_deaths) + 1)
    #     df = pd.DataFrame({
    #         "Días": days,
    #         "Nuevas Muertes (Simulación)": self.daily_deaths,
    #         "Nuevas Muertes (Reales)": self.real_data["daily_deaths"][:len(days)] if self.real_data else None
    #     })

    #     fig = go.Figure()
    #     fig.add_trace(go.Bar(x=df["Días"], y=df["Nuevas Muertes (Simulación)"], 
    #                     name='Simulación', marker_color='blue'))
    #     if self.real_data:
    #         fig.add_trace(go.Scatter(x=df["Días"], y=df["Nuevas Muertes (Reales)"], 
    #                        mode='lines', name='Reales', line=dict(color='red', dash='dash')))

    #     fig.update_layout(
    #         title="Comparación de Nuevas Muertes Diarias",
    #         xaxis_title="Días",
    #         yaxis_title="Nuevas Muertes",
    #         template="plotly_white",
    #         legend=dict(x=0.1, y=0.9)
    #     )
    #     fig.update_xaxes(rangeslider_visible=True)
    #     fig.write_html("epidemics_sim/results/daily_deaths.html")
    #     print("Saved daily deaths plot as daily_deaths.html")

    def generate_municipality_table(self):
        sorted_municipalities = sorted(self.municipal_cases.items(), key=lambda x: x[1], reverse=True)
        total_cases = self.total_cases if self.total_cases > 0 else 1  # Para evitar división por cero
        table_rows = "".join(f"<tr><td>{m}</td><td>{cases}</td><td>{(cases / total_cases) * 100:.2f}%</td></tr>" for m, cases in sorted_municipalities)
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
        # Cambiar px.bar por px.line
        fig = px.line(df, x='Municipality', y='Cases', title='Comparación de Casos por Municipio', 
                    labels={'Cases': 'Casos Acumulados'}, markers=True)
        fig.update_layout(template="plotly_white", xaxis_title="Municipio", yaxis_title="Casos Acumulados")
        fig.write_html("epidemics_sim/results/municipality_comparison.html")
        print("Municipality comparison chart saved as municipality_comparison.html")
    # def plot_municipality_comparison(self):
    #     df = pd.DataFrame(list(self.municipal_cases.items()), columns=["Municipality", "Cases"])
    #     fig = px.bar(df, x='Municipality', y='Cases', title='Comparación de Casos por Municipio', 
    #                  labels={'Cases': 'Casos Acumulados'}, color='Cases', color_continuous_scale='Viridis')
    #     fig.update_layout(template="plotly_white", xaxis_title="Municipio", yaxis_title="Casos Acumulados")
    #     fig.write_html("epidemics_sim/results/municipality_comparison.html")
    #     print("Municipality comparison chart saved as municipality_comparison.html")

    def plot_municipality_interactive(self):
        # Crear un DataFrame con los datos diarios de cada municipio
        days = range(1, len(self.daily_cases) + 1)
        data = {"Días": days}
        
        # Asegurar que todas las listas de casos tengan la misma longitud
        max_length = len(days)
        for municipality, cases in self.municipal_data.items():
            if len(cases) < max_length:
                # Rellenar con ceros si la lista es más corta
                cases.extend([0] * (max_length - len(cases)))
            data[municipality] = cases

        # Verificar que todos los municipios estén en el diccionario
        print("Municipios en municipal_data:", list(self.municipal_data.keys()))
        print("Municipios en data:", list(data.keys()))

        df = pd.DataFrame(data)
        fig = px.line(df, x="Días", y=df.columns[1:], title="Comparación de Casos por Municipio",
                    labels={"value": "Casos", "variable": "Municipio"})
        fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Casos")
        fig.update_xaxes(rangeslider_visible=True)  # Agregar un slider para ajustar el intervalo de tiempo
        fig.write_html("epidemics_sim/results/municipality_interactive.html")
        print("Interactive municipality comparison chart saved as municipality_interactive.html")

    def generate_full_report(self, json_file='epidemics_sim/data/cuba_covid_data/covid19-cuba-old.json', start_day=1, end_day=30):
        """
        Genera un informe completo con todos los gráficos y el reporte HTML.
        
        :param json_file: Ruta al archivo JSON con los datos reales (opcional).
        :param start_day: Día inicial del rango para los datos reales (por defecto 1).
        :param end_day: Día final del rango para los datos reales (por defecto 30).
        """
        # Cargar datos reales si se proporciona un archivo JSON
        if json_file:
            self.load_real_data(json_file, start_day = 6, end_day = 36)
        
        # Generar todos los gráficos
        self.plot_cases()
        self.plot_daily_cases()
        self.plot_deaths()
        self.plot_daily_deaths()
        self.plot_municipality_comparison()
        self.plot_municipality_interactive()

        # Obtener la fecha y hora actual
        now = datetime.now()

        # Formatear la fecha y hora como una cadena
        timestamp = now.strftime("%Y%m%d_%H%M%S")  # Formato: AñoMesDía_HoraMinutoSegundo

        # Crear el nombre del archivo
        filename = f"epidemics_sim/results/json/simulation_{timestamp}.json"
        self.save_simulation_results(filename)
        
        # Generar el informe HTML
        self.generate_html_report()
        
        print("✅ Informe completo generado con éxito.")

    def save_simulation_results(self, filename):
        """
        Guarda los resultados de la simulación en un archivo JSON.
        
        :param filename: Nombre del archivo JSON donde se guardarán los resultados.
        """
        results = {
            "daily_cases": self.daily_cases,
            "daily_deaths": self.daily_deaths,
            "total_cases": self.total_cases,
            "total_deaths": self.total_deaths,
            "municipal_cases": self.municipal_cases,
            "municipal_data": self.municipal_data
        }
        
        with open(filename, "w") as file:
            json.dump(results, file, indent=4)
        print(f"Simulation results saved to {filename}")

    def plot_all_simulations(self, results_dir="epidemics_sim/results"):
        """
        Grafica todos los resultados de las simulaciones guardados en archivos JSON.
        
        :param results_dir: Directorio donde se encuentran los archivos JSON con los resultados.
        """
        fig_cases = go.Figure()
        fig_deaths = go.Figure()
        
        for filename in os.listdir(results_dir):
            if filename.endswith(".json"):
                with open(os.path.join(results_dir, filename), "r") as file:
                    data = json.load(file)
                    days = range(1, len(data["daily_cases"]) + 1)
                    
                    # Graficar casos
                    fig_cases.add_trace(go.Scatter(
                        x=days,
                        y=data["daily_cases"],
                        mode='lines',
                        name=f'Simulación {filename}'
                    ))
                    
                    # Graficar muertes
                    fig_deaths.add_trace(go.Scatter(
                        x=days,
                        y=data["daily_deaths"],
                        mode='lines',
                        name=f'Simulación {filename}'
                    ))
        
        # Configurar layout para casos
        fig_cases.update_layout(
            title="Comparación de Nuevos Casos Diarios de Todas las Simulaciones",
            xaxis_title="Días",
            yaxis_title="Nuevos Casos",
            template="plotly_white",
            legend=dict(x=0.1, y=0.9)
        )
        fig_cases.update_xaxes(rangeslider_visible=True)
        fig_cases.write_html(os.path.join(results_dir, "all_simulations_cases.html"))
        print("Saved all simulations cases plot as all_simulations_cases.html")

        # Configurar layout para muertes
        fig_deaths.update_layout(
            title="Comparación de Nuevas Muertes Diarias de Todas las Simulaciones",
            xaxis_title="Días",
            yaxis_title="Nuevas Muertes",
            template="plotly_white",
            legend=dict(x=0.1, y=0.9)
        )
        fig_deaths.update_xaxes(rangeslider_visible=True)
        fig_deaths.write_html(os.path.join(results_dir, "all_simulations_deaths.html"))
        print("Saved all simulations deaths plot as all_simulations_deaths.html")    