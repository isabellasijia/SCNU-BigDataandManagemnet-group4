# Weather Dashboard

Welcome to the Weather Dashboard documentation.

## Quick Links

- [Getting Started](guide/getting-started.md)
- [API Documentation](api/index.md)
- [Development Guide](dev/index.md)

## Modules

- [Main Module](reference/app/main.md)
- [Weather Service](reference/app/services/weather.md)

## API Endpoints

### GET /api/weather/{city}

Get weather data for a specific city.

**Parameters:**
- city (string): City name in English

**Returns:**
- 200: Weather data successfully returned
- 404: City not found
- 500: Server error

## Data Models

### WeatherData

Complete weather data model, including:
- Temperature information
- Wind data
- Weather conditions
- Location information 