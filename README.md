# HUGAI Methodology Documentation

A comprehensive documentation site for the HUGAI (Human-Guided AI Dev) Methodology, maintained with MkDocs Material. This repository contains the source files and the configuration needed to build, serve, and publish the documentation.

Table of Contents
-----------------
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Local Development](#local-development)
- [Building the Site](#building-the-site)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

Overview
--------

The HUGAI Methodology provides a structured approach to design, develop, and maintain AI-driven solutions, emphasizing human-guided processes that augment developer capabilities. This documentation guides you through the core principles, lifecycle phases, tooling, agent-based workflows, and best practices for successful AI projects.

Prerequisites
-------------

- Python 3.8 or higher
- pip (Python package installer)

Installation
------------

1. Clone this repository:

       git clone https://github.com/hugaidev/methodology.git
       cd methodology

2. Install Python dependencies:

       pip install -r requirements.txt

Local Development
-----------------

Serve the documentation locally with live reloading:

    ./sdc-serve.sh

or:

    mkdocs serve

Building the Site
-----------------

Generate the static site for deployment:

    ./sdc-build.sh

or:

    mkdocs build --clean

The built site will be available in the `site/` directory.

Project Structure
-----------------

    .
    ├── docs/                # Markdown pages for MkDocs
    ├── material/            # Custom theme overrides (MkDocs Material)
    ├── mkdocs.yml           # Site configuration file
    ├── requirements.txt     # Python dependencies for building the site
    ├── sdc-serve.sh         # Script to serve the site locally
    ├── sdc-build.sh         # Script to build the static site
    └── README.md            # This file

Contributing
------------

We welcome contributions to improve and expand the HUGAI Methodology documentation. To contribute:

1. Fork the repository and create a new branch for your feature or fix.
2. Commit your changes with clear, descriptive messages.
3. Submit a pull request describing the changes and linking any relevant issues.

Please ensure your contributions follow the style guidelines and formatting conventions of Markdown and MkDocs Material.

License
-------

© 2024–2025 Sebastian Larrauri. Documentation is released under the Creative Commons Attribution 4.0 International (CC BY 4.0). For more details, see the `mkdocs.yml` license configuration.
