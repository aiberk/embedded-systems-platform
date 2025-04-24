# embedded-systems-platform

## Folder Structure

One level/directory per device

- Platform/
  - Random Number Generator/
  - OLED Screen/
  - Stoplight/
  - Glove/
  - Vision Module/
  - API/

## Contibuting to Repo

1. Git clone repo
2. Add your code to your designated folder
3. Push it!

## Help Commands

# 1. Launch the InfluxDB shell, pointing at the broker

influx -host localhost -port 8086

# 2. In the influx> prompt, switch to iot_data database

> USE iot_data

# 3. List all measurements (you should see things like device\_<deviceID>)

> SHOW MEASUREMENTS

# 4. For a given device measurement, inspect its schema:

> SHOW FIELD KEYS FROM "device*<yourDeviceID>"
> SHOW TAG KEYS FROM "device*<yourDeviceID>"

# 5. Peek at the latest points for that device:

> SELECT \* FROM "device\_<yourDeviceID>" ORDER BY time DESC LIMIT 5

# 1. Connect to the 'devices' DB as the postgres user

psql "postgres://postgres@localhost:5432/devices"

# 2. List all tables — you should see device_registry and conditions

devices=> \dt

# 3. Describe the device_registry table

devices=> \d+ device_registry

# 4. Describe the conditions table

devices=> \d+ conditions

# 5. Preview some rows

devices=> SELECT _ FROM device_registry LIMIT 5;
devices=> SELECT _ FROM conditions LIMIT 5;
