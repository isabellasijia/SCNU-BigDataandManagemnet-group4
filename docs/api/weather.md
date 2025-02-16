# Weather API

## Endpoints

### GET /api/weather/{city}

Get current weather and forecast for a specific city.

#### Parameters
- `city` (string): City name in English

#### Response
```json
{
    "current": {
        "temp": 20.5,
        "humidity": 65,
        "wind_speed": 5.2
    },
    "forecast": [...]
}
```
