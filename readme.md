# Parcel Forecasting Web Application

This repository contains a web application for Analytical Parcel Management Information System (APMIS) For Sorting Centers. The application is built using Dash for the web interface and TensorFlow for the forecasting model. Attached also is the documentation.

## Table of Contents

- [Features](#features)
- [Database Schema](#database-schema)
- [Database Connection](#database-connection)

## Features

- Enables parcel management transactions such as adding parcels, updating status, and dispatcing parcel groups
- Basic dashboard showing metrics in terms of the processes
- Forecast parcel counts for the next 30 days.



## Database Schema

The database schema consists of the following tables:

- `soc_staff`
- `pl3_rider`
- `parcel`
- `parcelstatus_mapping`
- `parcel_group`
- `parcel_status`


## Database Connection

The Python functions for database interaction are defined as follows:

- `getdblocation()`
- `modifydatabase(sql, values)`
- `querydatafromdatabase(sql, values, dfcolumns)`
