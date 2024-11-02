import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Загрузка данных
data = pd.read_csv("data.csv")
data['Дата'] = pd.to_datetime(data['Дата'])

# Инициализация приложения
app = dash.Dash(__name__)

# Описание макета приложения
app.layout = html.Div([
    html.H1("Анализ продаж товаров и услуг"),
    html.P("Интерактивный дашборд для анализа выручки и структуры продаж"),

    # Выпадающий список для выбора периода анализа
    html.Label("Выберите период:"),
    dcc.Dropdown(
        id="period_dropdown",
        options=[
            {"label": "День", "value": "D"},
            {"label": "Месяц", "value": "M"},
            {"label": "Год", "value": "Y"}
        ],
        value="M"
    ),

    # Фильтр по категориям
    html.Label("Выберите категорию:"),
    dcc.Dropdown(
        id="category_dropdown",
        options=[{"label": cat, "value": cat} for cat in data['Категория'].unique()],
        value=data['Категория'].unique().tolist(),
        multi=True
    ),

    # График временного ряда
    dcc.Graph(id="time_series_graph"),

    # Круговая диаграмма по категориям
    dcc.Graph(id="pie_chart"),

    # Гистограмма прибыли
    dcc.Graph(id="histogram_profit"),

    # Таблица с ключевыми показателями
    html.Div(id="table_kpi"),

    # График рассеяния
    dcc.Graph(id="scatter_plot")
])

# Обработчики обратных вызовов
@app.callback(
    [Output("time_series_graph", "figure"),
     Output("pie_chart", "figure"),
     Output("histogram_profit", "figure"),
     Output("table_kpi", "children"),
     Output("scatter_plot", "figure")],
    [Input("period_dropdown", "value"),
     Input("category_dropdown", "value")]
)
def update_dashboard(period, selected_categories):
    # Фильтрация данных по категории
    filtered_data = data[data['Категория'].isin(selected_categories)]

    # Агрегация данных по выбранному периоду
    period_data = filtered_data.resample(period, on='Дата').sum()

    # График временного ряда
    time_series_fig = px.line(period_data, x=period_data.index, y="Сумма (в рублях)", title="Динамика доходов")

    # Круговая диаграмма по категориям
    pie_chart_fig = px.pie(filtered_data, names="Категория", values="Сумма (в рублях)", title="Структура выручки по категориям")

    # Гистограмма прибыли
    profit_data = filtered_data.groupby("Товар")['Сумма (в рублях)'].sum()
    histogram_fig = px.histogram(profit_data, x=profit_data.index, y=profit_data.values, title="Распределение прибыли по товарам")

    # Таблица с ключевыми показателями
    kpi_table = html.Table([
        html.Tr([html.Th("Ключевые показатели"), html.Th("Значение")]),
        html.Tr([html.Td("Общая выручка"), html.Td(filtered_data["Сумма (в рублях)"].sum())]),
        html.Tr([html.Td("Общие расходы"), html.Td((filtered_data["Количество"] * 0.7 * filtered_data["Сумма (в рублях)"] / filtered_data["Количество"]).sum())]),  # Условные расходы
        html.Tr([html.Td("Прибыль"), html.Td((filtered_data["Сумма (в рублях)"] - (filtered_data["Количество"] * 0.7 * filtered_data["Сумма (в рублях)"] / filtered_data["Количество"])).sum())]),
    ])

    # График рассеяния
    scatter_fig = px.scatter(filtered_data, x="Количество", y="Сумма (в рублях)", title="Корреляция между количеством и доходом")

    return time_series_fig, pie_chart_fig, histogram_fig, kpi_table, scatter_fig

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
