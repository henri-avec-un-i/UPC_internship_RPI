# Python Pressure and Temperature data acquisition with Raspberry Pi and MCC HATs board MCC 128 and MCC 134

This repository contains python scripts for pressure and temperature acquisition data acquisition using a Raspberry Pi model 4B and MCC HATs board MCC 128 and MCC 134.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Contact Information](#contact-information)
- [Troubleshooting](#troubleshooting)
- [Version History](#version-history)

## Installation

Check MCC official documentation for MCC HATs set up procedure [here](https://mccdaq.github.io/daqhats/install.html).

Library needed for script execution : csv, time, sys, numpy, datetime, PRI.GPIO, RPLCD, daqhats. daqhats_utils.py and T_P_acq_func.py needs to be in the same folder as the acquisition script.

Use `python3 pip install [library_name]` in linux terminal to install any missing library.

Regularly check for updates using `sudo apt update` and `sudo apt upgrade`.


## Usage

There is 3 different acquisition scripts in this repository that provides different acquisition modes.

1. T_P_acq_man.py

     This script allow to manually save a CSV file containing temperature and pressure data. Execute it if you want to record T and P data without a trigger input to start the acquisition. Modify the script with desired acquisition parameters. No LCD display support

2. T_P_acq_trigger_asynchronous.py

     This script allow to save a CSV file containing temperature and pressure data. The acquisition frequency and number of points are defined by the user in the script. The script waits for a trigger input to start the acquisition. Monitors T and P with terminal output while waiting for a trigger input. No LCD display support

3. T_P_acq_trigger_synchronous.py

     **This is the main acquisition script**. Execute it for experimental data acquisition. This scripts monitors T and P with terminal output and LCD output while waiting for a trigger input. When a trigger input is received, it updates a data_array containing T1, T2, P1, P2 data as well as index and relative time of measure (compared to first data point). When the script is interrupted through Ctrl+C, it saves the data array as a CSV file.

To execute the scripts, open a terminal, go to the repository location with `cd [repository path]` and then type `python3 [script_name]`.

## Features

List the key features and functionalities of the codebase, highlighting what problems it solves and what it can do.

## Documentation

Mention any extensive documentation available for the project and provide links or instructions on how to access it. This could include API documentation, user guides, or additional resources.
