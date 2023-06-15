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

There is 3 acquisition script in this repository with different that provides different acquisition modes.

1. T_P_acq_man.py

     This script allow to manually save a CSV file containing temperature and pressure data. Execute it if you want to record T and P data without a trigger input to start the acquisition. Modify the script with desired acquisition parameters

3. T_P_acq_trigger_asynchronous.py

4. T_P_acq_trigger_synchronous.py

   

Explanation of how to use the code or project, including examples, code snippets, and command-line instructions. Include any necessary configurations or environment variables.

## Features

List the key features and functionalities of the codebase, highlighting what problems it solves and what it can do.

## Documentation

Mention any extensive documentation available for the project and provide links or instructions on how to access it. This could include API documentation, user guides, or additional resources.

## Contributing

Guidelines for contributing to the project, including bug reporting, feature requests, and pull requests. Specify any coding standards or formatting guidelines to follow.

## License

Specify the license under which the code is distributed and provide the terms and conditions for using, modifying, or redistributing the code.

## Credits

Acknowledge and give credit to any external libraries, frameworks, or resources used in the project. Include links to their respective websites or repositories.

## Contact Information

Provide your contact details, such as email or GitHub username, for users to reach out to you with questions, feedback, or issues.

## Troubleshooting

Provide troubleshooting tips or workarounds for common problems or known issues with the code. Address frequently asked questions to help users overcome any hurdles they may face.

## Version History

Optional section to highlight major updates, bug fixes, and improvements in each release of the codebase.
