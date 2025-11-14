# 🌤️ Weather-wise Planner Dashboard

This is a multi-page web application built with **Dash** and **Plotly** that provides a 7-day detailed weather forecast and a 3-day summary for major US cities. The application uses the **Open-Meteo API** to fetch up-to-date weather data and offers smart suggestions for activities and food based on the forecast, including an estimated budget for dining.

---

## ✨ Features

* **Dual-View Interface:** Navigate between a **Detailed 7-Day Forecast** page and a **3-Day Summary** page.
* **City Selection:** Easily switch between four pre-defined US cities (Honolulu, New York, Chicago, San Francisco) using a dropdown menu.
* **Temperature Trend Chart:** The detailed view includes a **Plotly line chart** visualizing the 7-day maximum and minimum temperature trends.
* **Smart Suggestions:** The 3-Day Summary provides suggestions for **Outdoor/Indoor Activities** and **Food/Restaurant Options** based on the temperature, rain, and cloud cover.
* **Estimated Budget:** Food suggestions include an **estimated dollar range** per person for the recommended dining option, clearly separated into new lines for readability.
* **Resilient API Handling:** Uses `requests_cache` and `retry_requests` to cache API data for 24 hours and automatically retry failed requests.
* **Key Callbacks:**
    * **Routing Callback:** Renders the correct page layout based on the URL.
    * **Summary Page Callback:** Updates the metric cards and the background image based on the selected city.
    * **Detailed Page Callback:** Updates the temperature graph and the detailed forecast table based on the selected city and a refresh interval.

---

## 🛠️ Prerequisites

Before running the application, ensure you have **Python 3.8+** installed.

The application relies on the following Python packages:

| Package | Description |
| :--- | :--- |
| `dash` | The main framework for building the web application. |
| `dash-bootstrap-components` | Provides responsive, professional layout components. |
| `plotly` | Used for generating the interactive temperature trend graph. |
| `pandas` | For efficient data processing and structuring. |
| `openmeteo-requests` | Client for the Open-Meteo weather API. |
| `requests-cache` | Caches API responses to reduce redundant calls. |
| `retry-requests` | Adds automatic retry logic for robust API calls.

---

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone [Your Repository URL]
    ```

2.  **Install dependencies:**
    It is highly recommended to use a virtual environment. Use the following command to install the necessary packages listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    # Alternatively, you can run:
    # pip install dash pandas plotly dash-bootstrap-components openmeteo-requests requests-cache retry-requests
    ```

---

## 🏃 Usage

1.  **Save the code:** Ensure the Python code is saved as a file (e.g., `app.py`).

2.  **Run the application:**
    ```bash
    python app.py
    ```

3.  **Access the Dashboard:**
    Open your web browser and navigate to the address displayed in your terminal, usually:
    
    `http://127.0.0.1:8050/`

**Note:** The application will default to the **Detailed 7-Day Forecast** page. Use the navigation links in the header to switch to the **3-Day City Summary**.

---

## 🌐 Data Source

Weather data is sourced from the **Open-Meteo Weather API**, which provides open-source, non-commercial weather data. **No API key is required.**
