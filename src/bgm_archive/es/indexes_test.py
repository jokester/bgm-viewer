import pytest
from .test_common import (
    mock_es_client,
    subjects_index,
    characters_index,
    persons_index,
    episodes_index,
    test_search_empty_results_all_indexes,
    test_search_invalid_data_handling_all_indexes,
)


# This file now contains only the common tests that span multiple indexes.
# Individual index tests have been moved to separate files:
# - test_subject_index.py
# - test_character_index.py  
# - test_person_index.py
# - test_episode_index.py
# - test_common.py (contains shared fixtures and common tests)
