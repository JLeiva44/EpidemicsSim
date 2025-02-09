import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template

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
        fig = px.bar(df, x='Municipality', y='Cases', title='Comparación de Casos por Municipio', 
                     labels={'Cases': 'Casos Acumulados'}, color='Cases', color_continuous_scale='Viridis')
        fig.update_layout(template="plotly_white", xaxis_title="Municipio", yaxis_title="Casos Acumulados")
        fig.write_html("epidemics_sim/results/municipality_comparison.html")
        print("Municipality comparison chart saved as municipality_comparison.html")

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
    # def plot_municipality_interactive(self):
    #     # Crear un DataFrame con los datos diarios de cada municipio
    #     days = range(1, len(self.daily_cases) + 1)
    #     data = {"Días": days}
        
    #     # Asegurar que todas las listas de casos tengan la misma longitud
    #     max_length = len(days)
    #     for municipality, cases in self.municipal_data.items():
    #         if len(cases) < max_length:
    #             # Rellenar con ceros si la lista es más corta
    #             cases.extend([0] * (max_length - len(cases)))
    #         data[municipality] = cases

    #     df = pd.DataFrame(data)
    #     fig = px.line(df, x="Días", y=df.columns[1:], title="Comparación de Casos por Municipio",
    #                 labels={"value": "Casos", "variable": "Municipio"})
    #     fig.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="Casos")
    #     fig.update_xaxes(rangeslider_visible=True)  # Agregar un slider para ajustar el intervalo de tiempo
    #     fig.write_html("municipality_interactive.html")
    #     print("Interactive municipality comparison chart saved as municipality_interactive.html")
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