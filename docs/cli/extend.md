# Extending Nova CLI

This document describes how to add new commands and plugins to the Nova CLI.

## Adding a New Command

1. Create a handler module in `handlers/` following the naming convention.
2. Implement the command logic in the handler.
3. Register the command in `cli/cli.py` by adding an entry point.
4. Update the manifest configuration if needed.

## Plugin Architecture

Nova supports loading plugins at runtime. Place plugin files in the `plugins/` directory and they will be automatically discovered.

## Configuration

Configuration files are located in `config.yaml`. You can extend this file to store command-specific settings.

## CI/CD

The CI pipeline ensures that all changes pass linting and tests before merging.