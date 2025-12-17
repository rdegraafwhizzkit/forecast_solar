# Simple Forecast Solar HA entities

## Links
* https://forecast.solar/

## Prerequisites
* https://github.com/RomRider/apexcharts-card
* Supported Python version, tested with 3.13.5
* Recent (as of December 2025) Home Assistant, tested with 2025.12.2
* Optional: HACS, tested with 2.0.5

## Develop
```
deactivate || :
rm -rf .venv/
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip pip-tools
pip-compile dev_requirements.in
pip install -r dev_requirements.txt
```

## Installation (manual)
* Copy forecast_solar directory into your config/custom_components directory

## Installation (using HACS)
* Install HACS in Home Assistant using instructions found at https://hacs.xyz/docs/use/
* Add a custom _integration_ repository in HACS with url https://github.com/rdegraafwhizzkit/forecast_solar
* You may need to refresh your browser for the repository to show up in the 'New' section
* Select the Forecast Solar custom repository in HACS and click 'DOWNLOAD'
* Add the Config Editor add on in Home Assistant. Using that (or use vi), add the following entry in your `<config_dir>/configuration.yaml`:

## HA configuration in configuration.yaml
```
sensor:
  - platform: forecast_solar
#    api_key: dummy      # Set it if you have it (untested functionality)
    latitude: 52.155172  # Set to your PV's gps location
    longitude: 5.387201  # Set to your PV's gps location
    declination: 10      # Set to the 'angle' of your panels. 0 = flat, 90 = straight up
    azimuth: 0           # Which way your panels are facing. -180 = north, -90 = east, 0 = south, 90 = west, 180 = north
    kilo_watt_peak: 11   # kWp of your PV's installation, +/- # panels * 0.3
    resources:           # Leave this for all entities, comment out what is not needed. I only use watt_hours_period
      - watts
      - watt_hours_period
      - watt_hours
      - watt_hours_day
```
Reboot HA (very important)

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
