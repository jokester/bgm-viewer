#!/usr/bin/env python3
"""
Test script for the ArchiveLoader class.

This script tests the ArchiveLoader with the test_archive.zip file.
"""

import logging
import os
import sys
from pathlib import Path

from .wiki_archive_loader import WikiArchiveLoader


def test_loader():
    # Get the path to the test archive
    current_dir = Path(__file__).parent
    test_archive_path = current_dir / "__test_data" / "test_archive.zip"

    assert test_archive_path.exists(), f"Test archive not found at {test_archive_path}"
    loader = WikiArchiveLoader(str(test_archive_path))

    # Test loading each type of data
    test_methods = [
        ("subjects", loader.subjects),
        ("persons", loader.persons),
        ("characters", loader.characters),
        ("episodes", loader.episodes),
        ("subject_relations", loader.subject_relations),
        ("subject_persons", loader.subject_persons),
        ("subject_characters", loader.subject_characters),
        ("person_characters", loader.person_characters),
    ]

    for method_name, method in test_methods:
        print(f"Testing {method_name}...")
        entries = list(method())
        assert entries, f"No entries found for {method_name}"
        print(f"Found {len(entries)} entries for {method_name}")
