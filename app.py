from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# CSV-Daten laden
df = pd.read_csv('vgsales.csv')
df.dropna(inplace=True)
df['Year'] = df['Year'].astype(int)
df['Global_Sales'] = df['Global_Sales'].astype(int)

# Falsche Plattformen entfernen
df = df[~df['Platform'].isin(['2600', 'PCFX', 'GG', '3DO', 'TG16', 'NG', 'WS'])]

app = Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial', 'margin': '0 auto', 'maxWidth': '1200px', 'padding': '20px'}, children=[
    html.H1("Videospiel-Verkaufsdashboard", style={'textAlign': 'center', 'color': '#4CAF50', 'fontSize': '48px', 'fontWeight': 'bold'}),
    
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
        html.Div(style={'backgroundColor': '#ffebcd', 'padding': '20px', 'borderRadius': '10px'}, children=[
            html.H2("Anteil Verkaufszahlen des gewählten Genres", style={'color': '#333'}),
            html.Label("Wähle ein Genre:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique()],
                value=df['Genre'].unique()[0],
                style={'width': '100%', 'marginBottom': '20px'}
            ),
            dcc.Graph(id='genre-sales-bar')
        ]),

        html.Div(style={'backgroundColor': '#f5f5f5', 'padding': '20px', 'borderRadius': '10px'}, children=[
            html.H2("Plattformanteil pro Jahr", style={'color': '#333'}),
            html.Label("Wähle ein Jahr:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
                value=2000,
                style={'width': '100%', 'marginBottom': '20px'}
            ),
            dcc.Graph(id='platform-pie-chart')
        ]),

        html.Div(style={'backgroundColor': '#d1e7dd', 'padding': '20px', 'borderRadius': '10px'}, children=[
            html.H2("Verkaufszahlen des ältesten bis neuesten Jahr", style={'color': '#333'}),
            html.Label("Wähle einen Jahresbereich:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year-range-slider',
                min=df['Year'].min(),
                max=df['Year'].max(),
                value=[df['Year'].min(), df['Year'].max()],
                marks={str(year): str(year) for year in range(df['Year'].min(), df['Year'].max()+1, 5)},
                step=1
            ),
            dcc.Graph(id='release-timeline')
        ]),

        html.Div(style={'backgroundColor': '#fff0f5', 'padding': '20px', 'borderRadius': '10px'}, children=[
            html.H2("Top 10 beliebte Spiele nach Plattform", style={'color': '#333'}),
            html.Label("Wähle eine Plattform:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='platform-dropdown',
                options=[{'label': platform, 'value': platform} for platform in df['Platform'].unique()],
                value=df['Platform'].unique()[0],
                style={'width': '100%', 'marginBottom': '20px'}
            ),
            dcc.Graph(id='top-10-games')
        ])
    ])
])

@app.callback(
    Output('genre-sales-bar', 'figure'),
    Input('genre-dropdown', 'value')
)
def update_genre_sales(selected_genre):
    genre_sales = df[df['Genre'] == selected_genre]['Global_Sales'].sum()
    total_sales = df['Global_Sales'].sum()
    fig = px.bar(
        x=['Selected Genre', 'Total Sales'], 
        y=[genre_sales, total_sales], 
        title='Anteil Verkaufszahlen des gewählten Genres',
        text_auto=True
    )
    fig.update_traces(marker_color=['blue', 'grey'], textposition='inside')
    return fig

@app.callback(
    Output('platform-pie-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_platform_pie(selected_year):
    year_data = df[df['Year'] == selected_year]
    fig = px.pie(year_data, names='Platform', values='Global_Sales', title=f'Plattformanteil im Jahr {selected_year}')
    return fig

@app.callback(
    Output('release-timeline', 'figure'),
    Input('year-range-slider', 'value')
)
def update_timeline(year_range):
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    fig = px.line(filtered_df.groupby('Year').size().reset_index(name='Count'), x='Year', y='Count', title='Verkaufszahlen über die Jahre')
    return fig

@app.callback(
    Output('top-10-games', 'figure'),
    Input('platform-dropdown', 'value')
)
def update_top_games(selected_platform):
    filtered_df = df[df['Platform'] == selected_platform].nlargest(10, 'Global_Sales')
    fig = px.bar(filtered_df, x='Name', y='Global_Sales', title=f'Top 10 Spiele auf {selected_platform}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
