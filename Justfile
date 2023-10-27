# SPDX-FileCopyrightText: 2023 Brown, E. M., Nesbitt, A., Hébert-Dufresne, L., Veytsman, B., Pimentel, J. F., Druskat, S., Mietchen, D.
# SPDX-FileCopyrightText: 2023 Brown, E. M., Nesbitt, A., Hébert-Dufresne, L., Veytsman, B., Pimentel, J. F., Druskat, S., Mietchen, D., Howison, J.
#
# SPDX-License-Identifier: CC0-1.0

# list all available commands
default:
  just --list

###############################################################################
# Basic project and env management

# clean all build, python, and lint files
clean:
	rm -fr dist
	rm -fr .eggs
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .mypy_cache

# install with all deps
install:
    pip install -e ".[lint]"

# lint, format, and check all files
lint:
	pre-commit run --all-files