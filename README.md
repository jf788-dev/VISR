# VISR Stack: Quick Start Guide

This stack launches a full sensor data pipeline including:
- **Mosquitto** (MQTT broker)
- **Telegraf** (data collection)
- **InfluxDB** (time-series database)
- **Grafana** (dashboard visualization)

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed (includes Docker Compose)
- Git installed
- Access to this GitHub repo

---

## Clone the Repository

```bash
git clone https://github.com/jf788-dev/VISR.git
cd VISR
```


## Starting, Stopping and Resetting the Stack

Start the Docker stack, pulling all required images and launching containers
Automatically opens Grafana and InfluxDB in the browser
```bash
bash start.sh
```

Stop the stack (retains all data)
```bash
bash stop.sh
```

Reset the stack (removes all data and containers for a clean start)
```bash
bash reset.sh
```

## Access and Logins

Grafana - https://localhost:3000
Default sign in:
Username: admin
Password: admin

Grafana - https://localhost:8086
Default sign in:
Username: admin
Password: adminpass



## Setting up InfluxDB Data Source

Login to Grafana as admin using given credentials. Optionally change password. //

Navigate to Data Sources, Add data Source (http://localhost:3000/connections/datasources/new) and select influxdb: 

Query language 'Flux' URL set to http://influxdb:8086 

turn off 'basic auth'

Set 'Oranization' to VISR

'Token' to visr-token

'Default Bucket' to Data

leave everything else as blank or default and press 'save & test' then 'building a dashboard' in the green popup.

Before building a dashboard run the following script to generate a live feed of test data. 

## Test Telemetry
```bash
python3 data_sim.py
```

## Building a Basic Dashboard

Select add visualisation and select the influxdb data source that have just added. Change the time frame above the pane to last 5 minutes and refresh dropdown to Auto.

In the influxdb query scripting box below the 'no data' panel, copy the following code to load in the sim data.

```bash
  from(bucket: "Data")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "count_rate")
  |> filter(fn: (r) => r["host"] == "VISR")
  |> filter(fn: (r) => r["sensor_id"] == "detector-1" or r["sensor_id"] == "detector-2" or r["sensor_id"] == "detector-3")
  |> filter(fn: (r) => r["topic"] == "radiation/detectors")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

  Press 'Query Inspector' and then 'Refresh' afterwhich some data should appear. 

  On the right hand side, Give the panel a name and optional description. Then press save dashboard. and press back to dashboard on the top panel.

  This will take you to your first dashboard. Here you can resize using the bottom right corner drag, change the time window and refresh rates. You can interact with the data by hovering over the dashboard. It is better to turn autorefresh off before interacting with the data. You can turn on and off each data type by pressing on the legend below the panel, a single click isolates that data source, shift click adds a second, third etc to the selection.

  We will now explore other data visualisation options. On the top right of the panel, find the three dots and press edit. On the right hand panel, scroll down and play around with the extensive options to tune your timeseries visualisation. Options include visual affects, units, axis, threshold alerting, grid lines, decimal places, interpolation options, statisical calculations (mean, mode, min, max, std)
  
  
  To select a different visualisation from the drop down box. Pressing suggestions will give you a range of options suited to your data type or manually select using the drop down box. Play around with the options.

  You can add additional visualisations to your dashboard or additional dashboards.

  ## Data Export

  You can export the time series data to a locally downloaded CSV by selecting inspect then data from the three dots at the top right of a dashboard visualisation. There will be options to select the specifc data for export, then select 'Download CSV' which will store locally and be available for further analytics. 

  




