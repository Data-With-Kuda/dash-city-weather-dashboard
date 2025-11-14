# Import client to access the Open-Meteo weather API service
import openmeteo_requests
# Import pandas for data manipulation and tabular structuring
import pandas as pd
# Caches API responses to reduce redundant calls and improve speed
import requests_cache
# Automatically retries failed API requests for resilience
from retry_requests import retry
# Dash components for building the web interface (charts, inputs, layout)
from dash import Dash, html, dcc, Input, Output, State, dash_table
# Bootstrap components for responsive, styled UI layout
import dash_bootstrap_components as dbc
# Used for creating interactive visualizations (e.g., line charts)
import plotly.graph_objects as go  # For plotting temperature trends

import logging

logging.basicConfig(
    filename='api_pull.log',  # Log file name
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

# Setup Open-Meteo API
# Cache API data for 24 hours to prevent repeated API calls
cache_session = requests_cache.CachedSession('.cache', expire_after=3600 * 24)
# Set up automatic retries with a small delay for reliability
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
# Create a weather API client using the retry-enabled session
openmeteo = openmeteo_requests.Client(session=retry_session)

# City coordinates and display names
city_info = {
    "Honolulu": {"coords": (21.31, -157.86), "display_name": "Honolulu, HI",
                 "image_url": "https://a.cdn-hotels.com/gdcs/production89/d1001/2e2f2638-33ce-4919-afcf-42ad381e2ac8.jpg"},
    "New York": {"coords": (40.71, -74.01), "display_name": "New York, NY",
                 "image_url": "https://1.bp.blogspot.com/-klHXHFbBkcg/Vh_oH8aFeyI/AAAAAAAADkI/WvdVpR4LWTc/s1600/CORT-NYC-StudyUSA07.jpg"},
    "Chicago": {"coords": (41.88, -87.63), "display_name": "Chicago, IL",
                "image_url": "https://64.media.tumblr.com/13afe8611d96ea09f138e6b34bc7f672/tumblr_omvl5ulmDa1up9mboo1_1280.jpg"},
    "San Francisco": {"coords": (37.77, -122.42), "display_name": "San Francisco, CA",
                      "image_url": "https://images.squarespace-cdn.com/content/v1/5eb9e1f6a256591412b55263/1589316856542-UCHOZOT51ASHZPBDUTW5/Golden-Gate-at-Night.jpg?format=2500w"}
}

# City-Specific Activity Data
city_activities = {
    "Honolulu": {
        "Outdoor": "Beach Day, Surfing, Diamond Head Hike",
        "Indoor": "Pearl Harbor Museum, Iolani Palace, Aquarium"
    },
    "New York": {
        "Outdoor": "Central Park Stroll, Brooklyn Bridge Walk, Rooftop Drinks",
        "Indoor": "Museum of Modern Art (MoMA), Broadway Show, Met Museum"
    },
    "Chicago": {
        "Outdoor": "Millennium Park/The Bean, Architectural Boat Tour, Lakefront Biking",
        "Indoor": "Art Institute of Chicago, Field Museum, Deep Dish Pizza"
    },
    "San Francisco": {
        "Outdoor": "Golden Gate Park, Golden Gate Bridge Walk, Fisherman's Wharf",
        "Indoor": "Exploratorium, Academy of Sciences, Alcatraz Tour"
    }
}

# MODIFIED: City-Specific Food and Restaurant Suggestions with explicit dollar budget ranges
# Ranges are estimated per person for a main course or tasting menu experience.
city_food_suggestions = {
    "Honolulu": {
        "Cold/Rainy": {"Food": "Warm Saimin Noodle Soup", "Suggestion": "Try Zippy's for quick takeout.",
                       "Budget": "$5 - $15"},
        "Warm/Clear": {"Food": "Fresh Poke Bowl",
                       "Suggestion": "Check out Ono Seafood or a local farmers market stand.", "Budget": "$15 - $35"},
        "Restaurant": {"Food": "Dinner with a view",
                       "Suggestion": "Miro Kaimuki (Contemporary) or Duke's Waikiki (Casual).", "Budget": "$35 - $75"}
    },
    "New York": {
        "Cold/Rainy": {"Food": "Classic New York Pizza",
                       "Suggestion": "Order delivery from Joe's Pizza or Artichoke Basille's.", "Budget": "$5 - $15"},
        "Warm/Clear": {"Food": "Street Food/Deli Sandwich",
                       "Suggestion": "Grab a hot dog from a street vendor or a sandwich from Katz's Deli.",
                       "Budget": "$15 - $35"},
        "Restaurant": {"Food": "Global Cuisine",
                       "Suggestion": "Via Carota (Italian) in Greenwich or Keens Steakhouse (Steak).",
                       "Budget": "$100 - $400"}
    },
    "Chicago": {
        "Cold/Rainy": {"Food": "Deep Dish Pizza", "Suggestion": "Lou Malnati's or Giordano's.", "Budget": "$15 - $35"},
        "Warm/Clear": {"Food": "Chicago-style Hot Dog/Street Tacos",
                       "Suggestion": "Hot dog from Portillo's or tacos from Birrieria Zaragoza.", "Budget": "$5 - $15"},
        "Restaurant": {"Food": "Modern American",
                       "Suggestion": "Alinea (Fine Dining) or Girl & The Goat (Contemporary).", "Budget": "$100 - $400"}
    },
    "San Francisco": {
        "Cold/Rainy": {"Food": "Clam Chowder in a Sourdough Bowl",
                       "Suggestion": "Get takeout from Boudin Bakery in Fisherman's Wharf.", "Budget": "$15 - $35"},
        "Warm/Clear": {"Food": "Mission Burrito or Seafood Grill",
                       "Suggestion": "A burrito from La Taqueria or grilled fish from Swan Oyster Depot.",
                       "Budget": "$15 - $35"},
        "Restaurant": {"Food": "Coastal California Cuisine",
                       "Suggestion": "Foreign Cinema (Mediterranean) or House of Prime Rib (Classic).",
                       "Budget": "$35 - $75"}
    }
}


# Helper functions
def suffix(day):
    return (
        "st" if day % 10 == 1 and day != 11 else
        "nd" if day % 10 == 2 and day != 12 else
        "rd" if day % 10 == 3 and day != 13 else
        "th"
    )


def format_date(d):
    return d.strftime('%A, %B ') + str(d.day) + suffix(d.day)


def get_weather_icon(code):
    code = int(code)
    if code == 0:
        return "☀️ Sunny"
    elif code == 1:
        return "🌤️ Mostly Clear"
    elif code == 2:
        return "⛅ Partly Cloudy"
    elif code == 3:
        return "☁️ Cloudy"
    elif code in [45, 48]:
        return "🌫️ Fog"
    elif 51 <= code <= 67:
        return "🌦️ Rain/Drizzle"
    elif 71 <= code <= 77:
        return "❄️ Snow"
    elif 80 <= code <= 82:
        return "🌧️ Showers"
    elif 95 <= code <= 99:
        return "⛈️ Thunderstorm"
    else:
        return "🌈"


def get_activity_suggestions(df, city_key):
    suggestions = []

    outdoor_activities = city_activities[city_key]["Outdoor"]
    indoor_activities = city_activities[city_key]["Indoor"]

    for index, row in df.iterrows():
        code = row["Weather Code"]
        rain = row["Rain (in)"]
        max_temp = row["Max Temp (°F)"]

        if 51 <= code <= 82 or 95 <= code <= 99:
            suggestions.append(f"INDOOR: {indoor_activities}")
        elif 71 <= code <= 77:
            if city_key in ["New York", "Chicago"]:
                suggestions.append(f"MIXED: Snow sports (if available), or {indoor_activities}")
            else:
                suggestions.append(f"INDOOR: {indoor_activities}")
        elif (code in [0, 1]) and rain == 0 and max_temp >= 60:
            suggestions.append(f"OUTDOOR: {outdoor_activities}")
        elif (code in [2, 3]) and rain == 0 and max_temp < 60 and max_temp >= 45:
            suggestions.append(f"MIXED: {outdoor_activities} (Dress Warmly), or {indoor_activities}")
        else:
            suggestions.append(f"INDOOR: {indoor_activities}")

    return suggestions


# MODIFIED FUNCTION: Logic to determine food/restaurant suggestions and include dollar budget
def get_food_suggestions(df, city_key):
    suggestions = []

    food_data = city_food_suggestions[city_key]

    for index, row in df.iterrows():
        code = row["Weather Code"]
        rain = row["Rain (in)"]
        max_temp = row["Max Temp (°F)"]

        # Rule 1: Cold or Rainy (Comfort Food / Takeout)
        if rain > 0 or max_temp < 50:
            sugg = food_data["Cold/Rainy"]
            food_type = "Takeout/Delivery"

        # Rule 2: Warm and Clear (Casual Dining / Outdoor Seating)
        elif (code in [0, 1]) and rain == 0 and max_temp >= 70:
            sugg = food_data["Warm/Clear"]
            food_type = "Casual Dine-In/Takeout"

        # Rule 3: Pleasant Weather (Go out to a nicer restaurant)
        elif (code in [0, 1, 2, 3]) and rain == 0 and max_temp >= 50:
            sugg = food_data["Restaurant"]
            food_type = "Restaurant/Dine-in"

        # Rule 4: Default (Indoor Comfort)
        else:
            sugg = food_data["Cold/Rainy"]
            food_type = "Comfort Food (Takeout/Delivery)"

        food_name = sugg['Food']
        suggestion_text = sugg['Suggestion']
        budget = sugg['Budget']

        # Formatted output with the estimated dollar budget explicitly included
        suggestions.append(
            f"**{food_name}** ({food_type}). **Suggestion:** {suggestion_text}. **Estimated Budget: {budget}**")

    return suggestions


# Fetches and processes 7-day forecast data for the selected city
def get_city_data(city_key):
    lat, lon = city_info[city_key]["coords"]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max", "temperature_2m_min",
            "rain_sum", "wind_speed_10m_max", "weather_code"
        ],
        "timezone": "auto", "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch", "wind_speed_unit": "mph"
    }
    logging.info(f"Pulling weather data for {city_key} at lat/lon: {lat}, {lon}")
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    timezone_str = response.Timezone().decode('utf-8')
    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True).tz_convert(timezone_str),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True).tz_convert(timezone_str),
        freq=pd.Timedelta(seconds=daily.Interval()), inclusive="left"
    )
    date_labels = [format_date(d) for d in dates]
    weather_descriptions = [get_weather_icon(code) for code in daily.Variables(4).ValuesAsNumpy().astype(float)]

    df = pd.DataFrame({
        "Date": date_labels,
        "Max Temp (°F)": daily.Variables(0).ValuesAsNumpy().round(2).astype(int),
        "Min Temp (°F)": daily.Variables(1).ValuesAsNumpy().round(2).astype(int),
        "Rain (in)": daily.Variables(2).ValuesAsNumpy().round(2).astype(int),
        "Wind (mph)": daily.Variables(3).ValuesAsNumpy().round(2).astype(int),
        "Weather Code": daily.Variables(4).ValuesAsNumpy().astype(int),
        "Description": weather_descriptions
    })

    # Adding Activity and Food Suggestions columns
    df["Activity Suggestions"] = get_activity_suggestions(df, city_key)
    df["Food/Restaurant Suggestions"] = get_food_suggestions(df, city_key)

    return df


# Function to create the 3-day summary cards
def create_metric_cards(city_key):
    city_df_full = get_city_data(city_key)
    df = city_df_full.head(3)
    dates = list(df["Date"])

    # Defining common styles for uniformity and professional look
    card_base_style = {
        "width": "100%", "margin": "3px", "height": "90px",
        "boxShadow": "3px 3px 10px rgba(0, 0, 0, 0.15)",  # Subtle shadow for lift
        "borderRadius": "8px"
    }
    card_header_style = {"height": "65px", "margin": "3px", "textAlign": "center", "padding": "5px",
                         "background-color": "#f8f9fa"}  # Light gray header
    title_style = {"textAlign": "center", "fontSize": "1.1rem", "margin": "0", "fontFamily": "Arial, sans-serif",
                   "fontWeight": "bold"}
    body_style = {"padding": "5px 10px"}

    # Date Row
    date_cards = dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H4(date, className="card-title", style=title_style)])
                          ], style={**card_header_style, "height": "65px"}, body=True), width=4) for date in dates
    ], justify="center")

    # Weather Description Row
    weather_row_cards = [
        dbc.Card([dbc.CardBody([html.Div(df.iloc[i]["Description"],
                                         style={"fontSize": "1.3rem", "margin": "0.2rem 0", "textAlign": "center",
                                                "fontFamily": "Arial, sans-serif", "color": "#007bff"})],
                               style=body_style)  # Blue for primary info
                  ], style={**card_header_style, "height": "65px"}) for i in range(3)
    ]
    forecast_row = dbc.Row([dbc.Col(card, width=4) for card in weather_row_cards], justify="center")

    metrics = [
        ("Max Temp (°F)", "Max Temp (°F)", "°F", "🌡️", "#dc3545"),  # Red for Max Temp
        ("Rain (in)", "Rain (in)", "in", "💧", "#17a2b8"),  # Cyan for Rain
        ("Wind (mph)", "Wind (mph)", "mph", "🌬️", "#6c757d")  # Gray for Wind
    ]
    rows = []
    for display_metric, col_metric, unit, icon, color in metrics:
        value_style = {"fontSize": "1.2rem", "marginTop": "0.3rem", "fontFamily": "Arial, sans-serif", "color": color,
                       "fontWeight": "bold"}
        row_items = [
            dbc.Card([dbc.CardBody([
                html.H5(display_metric, className="card-subtitle",
                        style={"fontSize": "0.8rem", "margin": "0", "fontFamily": "Arial, sans-serif"}),
                html.H2(f"{df.iloc[i][col_metric]} {unit if display_metric != 'Max Temp (°F)' else ''}",
                        style=value_style),
                html.Div(icon, style={"fontSize": "1.1rem", "marginTop": "0.1rem"})
            ], style=body_style)], style={**card_base_style, "height": "90px"}) for i in range(3)
        ]
        rows.append(dbc.Row([dbc.Col(card, width=4) for card in row_items], justify="center"))

    # Activity Suggestions Row
    activity_row = [
        dbc.Card([dbc.CardBody([
            html.H5("Suggested Activity", className="card-subtitle",
                    style={"textAlign": "center", "fontSize": "0.9rem", "margin": "0",
                           "fontFamily": "Arial, sans-serif"}),
            html.Div(dcc.Markdown(df.iloc[i]["Activity Suggestions"],
                                  style={"fontSize": "0.8rem", "marginTop": "0.2rem", "textAlign": "center",
                                         "fontFamily": "Arial, sans-serif"}))
        ], style=body_style)], style={**card_base_style, "height": "90px"}) for i in range(3)
    ]
    rows.append(dbc.Row([dbc.Col(card, width=4) for card in activity_row], justify="center"))

    # Food/Restaurant Suggestions with Dollar Budget estimates
    food_row = [
        dbc.Card([dbc.CardBody([
            html.H5("Food Suggestion 🍔", className="card-subtitle",
                    style={"textAlign": "center", "fontSize": "0.9rem", "margin": "0",
                           "fontFamily": "Arial, sans-serif"}),
            # Use dcc.Markdown to render bold text from the suggestion string
            html.Div(dcc.Markdown(df.iloc[i]["Food/Restaurant Suggestions"],
                                  style={"fontSize": "0.8rem", "marginTop": "0.2rem", "textAlign": "center",
                                         "fontFamily": "Arial, sans-serif", "whiteSpace": "normal"}))
        ], style=body_style)], style={**card_base_style, "height": "90px"}) for i in range(3)
    ]
    rows.append(dbc.Row([dbc.Col(card, width=4) for card in food_row], justify="center"))

    return html.Div([date_cards, forecast_row] + rows)


# Header component
def create_header(page_title, link_text, link_href):
    return html.Header([
        # Removed the floating image for a cleaner header
        html.Div(style={'height': '10px'}),  # Spacer
        html.H2(page_title,
                style={"textAlign": "center", "color": "white", "textShadow": "1px 1px 2px black", "fontSize": "2rem"}),
        html.Div([dcc.Link(link_text, href=link_href,
                           style={"marginLeft": "20px", "color": "lightblue", "fontWeight": "bold"})]),
        html.Br(),
    ], style={"background-color": "rgba(0,0,0,0.4)",
              "padding": "10px 0 20px 0"})  # Darker, more defined header background


summary_page_content_id = 'summary-page-content-wrapper'
summary_layout = html.Div(id=summary_page_content_id, children=[
    create_header("City 3-Day Forecast Summary", "← Back to Detailed Forecast", "/"),
    html.Div([
        dcc.Dropdown(
            id='city-dropdown-summary',
            options=[{"label": city_info[key]["display_name"], "value": key} for key in city_info],
            value="Honolulu", clearable=False,
            style={'width': '300px', 'margin': '0 auto', "fontFamily": "Arial, sans-serif"}
        )], style={'textAlign': 'center', "padding": "20px 0"}),
    html.Div(id='summary-cards', style={
        "marginTop": "10px",
        "padding": "20px 40px",
        "backgroundColor": "rgba(255, 255, 255, 0.95)",  # Near opaque white background
        "borderRadius": "10px",
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.2)"  # Main container shadow
    })
], style={
    "padding": "20px", "minHeight": "100vh", "backgroundSize": "cover",
    "backgroundPosition": "center", "transition": "background-image 0.5s ease-in-out"
})

detailed_forecast_page_content_id = 'detailed-forecast-page-content'
detailed_forecast_background_url = "https://static.vecteezy.com/system/resources/previews/003/692/649/large_2x/beautiful-clear-blue-sky-in-summer-look-lke-heaven-free-photo.jpg"


def detailed_forecast_layout():
    return html.Div(id=detailed_forecast_page_content_id, children=[
        create_header("7-Day Detailed Weather Forecast", "→ Go to 3-Day City Summary", "/summary"),
        dcc.Dropdown(
            id='city-dropdown-detailed',
            options=[{"label": city_info[key]["display_name"], "value": key} for key in city_info],
            value="Honolulu",
            clearable=False,
            style={'width': '300px', 'margin': '10px auto'}
        ),
        html.Div([
            dcc.Graph(id='temp-trend-graph'),
            html.Div(id='detailed-forecast-table-div')
        ], style={"backgroundColor": "rgba(255,255,255,0.8)", "padding": "20px", "borderRadius": "10px",
                  "marginTop": "20px"})
    ], style={
        "padding": "20px",
        "minHeight": "100vh",
        "backgroundImage": f'url("{detailed_forecast_background_url}")',
        "backgroundSize": "cover",
        "backgroundPosition": "center"
    })


# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div(id='page-content'),
    dcc.Interval(id='interval-component', interval=24 * 60 * 60 * 1000, n_intervals=0)
])


@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/summary":
        return summary_layout
    return detailed_forecast_layout()


@app.callback(
    [Output('summary-cards', 'children'), Output(summary_page_content_id, 'style')],
    Input('city-dropdown-summary', 'value'),
    State(summary_page_content_id, 'style')
)
def update_city_summary(city_key, current_style):
    cards = create_metric_cards(city_key)
    image_url = city_info[city_key]["image_url"]
    new_style = current_style.copy()
    new_style[
        'backgroundImage'] = f'linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url("{image_url}")'  # Added subtle dark overlay to background image
    return cards, new_style


@app.callback(
    [Output('temp-trend-graph', 'figure'), Output('detailed-forecast-table-div', 'children')],
    Input('city-dropdown-detailed', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_detailed_forecast(city_key, n_intervals):
    print(
        f"Updating detailed forecast for {city_info[city_key]['display_name']} due to dropdown or interval (n={n_intervals})")
    df_city = get_city_data(city_key)

    fig = go.Figure()
    # Max Temp line color to Red
    fig.add_trace(go.Scatter(
        x=df_city["Date"], y=df_city["Max Temp (°F)"], name='Max Temp',
        mode='lines+markers', line=dict(color='red')
    ))
    # Min Temp line color to Blue
    fig.add_trace(go.Scatter(
        x=df_city["Date"], y=df_city["Min Temp (°F)"], name='Min Temp',
        mode='lines+markers', line=dict(color='blue')
    ))
    fig.update_layout(
        title=f'7-day Temperature Trend for {city_info[city_key]["display_name"]}',
        xaxis_title='Date', yaxis_title='Temperature (°F)',
        legend_title_text='Temperature',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black")
    )

    # Table for detailed page
    table_df = df_city[["Date", "Description", "Rain (in)", "Wind (mph)", "Activity Suggestions"]].copy()
    detailed_table = dash_table.DataTable(
        data=table_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in table_df.columns],
        style_table={'overflowX': 'auto', 'padding': '10px', 'marginTop': '20px'},
        # Set consistent font/size for the table cells
        style_cell={'textAlign': 'left', 'padding': '8px', 'fontFamily': 'Arial', 'fontSize': '14px',
                    'backgroundColor': 'white', 'whiteSpace': 'normal', 'textOverflow': 'inherit'},
        style_header={'backgroundColor': '#f2f2f2', 'fontWeight': 'bold', 'color': 'black'},
        style_cell_conditional=[
            {'if': {'column_id': 'Activity Suggestions'},
             'width': '30%', 'textAlign': 'left', 'whiteSpace': 'normal', 'textOverflow': 'inherit'},
            {'if': {'column_id': 'Description'},
             'width': '15%'},
        ]
    )
    return fig, html.Div([
        html.H4(f"7-Day Forecast Details for {city_info[city_key]['display_name']}",
                style={"textAlign": "center", "marginTop": "20px", "color": "black"}),
        detailed_table
    ])


if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        if 'cache_session' in globals() and cache_session:
            cache_session.close()