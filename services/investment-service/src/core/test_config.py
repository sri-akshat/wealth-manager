# src/core/test_config.py
import os
from typing import Optional

def get_test_settings():
    return {
        "TESTING": True,
        "DATABASE_URL": "sqlite:///./test.db",
        "TEST_MODE": True
    }