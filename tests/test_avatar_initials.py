"""Unit tests for dynamic avatar initials in MainWindow."""

import pytest
from ui.main_window import MainWindow


def test_compute_initials():
    cases = [
        ('Vishnu Raval', 'VR'),
        ('Vishnu Raval (Admin)', 'VR'),
        ('VISHNU RAVAL', 'VR'),
        ('Parth Raval', 'PR'),
        ('Parth Raval (Admin)', 'PR'),
        ('Administrator', 'AD'),
        ('Admin', 'AD'),
        ('વિષ્ણુ રાવલ', 'VR'),
        ('પાર્થ રાવલ', 'PR'),
        ('સંચાલક (Admin)', 'SN'),
        ('John Doe', 'JD'),
        ('', 'AD'),
    ]

    for input_name, expected in cases:
        result = MainWindow._compute_initials(input_name)
        assert result == expected, f"Failed for '{input_name}': expected '{expected}', got '{result}'"
