"""
config.py - Environment Variable Loader for DNS Updater

This module provides utilities for loading environment variables from a .env file
(using python-dotenv if available) and for retrieving environment variables
with optional default values and required checks.

Functions:
    get_env_var(key: str, default: Optional[Any] = None, required: bool = False) -> Any
        Retrieve an environment variable, with support for default values and required checks.

Usage:
    - Automatically loads variables from a .env file if python-dotenv is installed.
    - Use get_env_var to safely access environment variables throughout the application.
"""

import os
from typing import Any, Optional

try:
    from dotenv import load_dotenv # type: ignore
except ImportError:
    import sys
    print("python-dotenv is not installed. Please run 'pip install python-dotenv'", file=sys.stderr)
    def load_dotenv(*_, **__):
        """
        Placeholder for load_dotenv if python-dotenv is not installed.
        Does nothing and returns False.
        """
        return False

load_dotenv()

def get_env_var(key: str, default: Optional[Any] = None, required: bool = False) -> Any:
    """
    Retrieve an environment variable value.

    Args:
        key (str): The name of the environment variable.
        default (Any, optional): The default value to return if the variable is not set.
            Defaults to None.
        required (bool, optional): If True, raises an error if the variable is not set.
            Defaults to False.

    Returns:
        Any: The value of the environment variable, or the default value if not set.

    Raises:
        EnvironmentError: If the variable is required but not set.
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(f"Required environment variable '{key}' is missing.")
    return value
