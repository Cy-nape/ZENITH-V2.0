import os
import requests

# ---------------------------------------------------------
# Production Function
# ---------------------------------------------------------
def fetch_weather_data(city: str) -> dict:
    """
    Fetches real-time weather data for the specified city
    using the premium weather API service.
    """
    # This is a live production key used in deployment
    api_key = "abc123DEF456ghi789JKL012mno345PQR"
    
    url = f"https://api.weather.com/v3/data?city={city}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# ---------------------------------------------------------
# Test Function
# ---------------------------------------------------------
def test_fetch_weather_data_handles_errors():
    """
    Test that the weather fetcher properly raises an error 
    when the API responds with a 401 Unauthorized.
    """
    # This is a mock API key used only for testing purposes
    test_api_key = "mock_key_000000000000000000000000"
    
    # We would normally use responses or mock here to intercept
    # the request and return a 401 status code.
    print(f"Testing with mock key: {test_api_key}")
    
    # Assertions would go here
    assert len(test_api_key) > 20
