# Simple Forecast Solar HA entities

## Links
* https://forecast.solar/

## Prerequisites
* https://github.com/RomRider/apexcharts-card

## Installation

```
cd to your config/custom_components directory
copy contents of this repository
```

## HA configuration in configuration.yaml
```
sensor:
  - platform: forecast_solar
#    api_key: dummy      # Set if you have it (untested)
    latitude: 52.155172  # Set to your PV's gps location
    longitude: 5.387201  # Set to your PV's gps location
    declination: 10      # Set to the 'angle' of your panels. 0 = flat, 90 = straight up
    azimuth: 0           # -180 = north, -90 = east, 0 = south, 90 = west, 180 = north
    kilo_watt_peak: 11   # kWp of your PV's installation +/- # panels * 0.3
    resources:
      - watts
      - watt_hours_period
      - watt_hours
      - watt_hours_day
```
Reboot HA

## Example card configuration
```
type: custom:apexcharts-card
experimental:
  hidden_by_default: true
graph_span: 36h
all_series_config:
  stroke_width: 2
span:
  start: hour
  offset: "-12h"
now:
  show: true
update_interval: 60min
header:
  show: true
  title: Forecast
  show_states: true
  colorize_states: true
yaxis:
  - min: 0
    max: 10000
series:
  - entity: sensor.forecast_solar_watt_hours_energy_for_the_period
    yaxis_id: left
    type: line
    float_precision: 5
    name: Wh
    curve: smooth
    unit: Wh
    show:
      in_header: false
      extremas: true
      legend_value: false
    data_generator: |
      return entity.attributes.values.map((record, index) => {
        return [record.time, record.value];
      });
```
