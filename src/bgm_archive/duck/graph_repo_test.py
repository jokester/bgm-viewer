import os
import pytest

from bgm_archive.duck.data import GraphEdge
from .graph_repo import GraphRepository
from .rdb_repo import RdbRepository

_rdb_repo = RdbRepository(db=os.environ["TEST_DUCKDB"])
repo = GraphRepository(db=os.environ["TEST_DUCKDB"], rdb=_rdb_repo)


def test_expand_s2s():
    """Test expand_s2s (subject to subject) method."""
    # Test valid subject ID
    edges = repo.expand_s2s(1)
    assert edges is not None
    assert isinstance(edges, list)

    # Test with subject that has no relations
    edges = repo.expand_s2s(999999)
    assert edges == []


def test_expand_s2s_invalid_input():
    """Test expand_s2s with invalid input."""
    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2s(0)

    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2s(-1)

    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2s("invalid")


def test_expand_s2c():
    """Test expand_s2c (subject to character) method."""
    # Test valid subject ID
    edges = repo.expand_s2c(1)
    assert edges is not None
    assert isinstance(edges, list)

    # Test with subject that has no character relations
    edges = repo.expand_s2c(999999)
    assert edges == []


def test_expand_s2c_invalid_input():
    """Test expand_s2c with invalid input."""
    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2c(0)

    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2c(-1)

    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2c("invalid")


def test_expand_s2p():
    """Test expand_s2p (subject to person) method."""
    # Test valid subject ID
    edges = repo.expand_s2p(1)
    assert edges is not None
    assert isinstance(edges, list)

    # Test with subject that has no person relations
    edges = repo.expand_s2p(999999)
    assert edges == []


def test_expand_s2p_invalid_input():
    """Test expand_s2p with invalid input."""
    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2p(0)

    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2p(-1)

    with pytest.raises(AssertionError, match="subject_id must be a positive integer"):
        repo.expand_s2p("invalid")


def test_expand_c2p():
    """Test expand_c2p (character to person) method."""
    # Test valid character ID
    edges = repo.expand_c2p(1)
    assert edges is not None
    assert isinstance(edges, list)

    # Test with character that has no person relations
    edges = repo.expand_c2p(999999)
    assert edges == []


def test_expand_c2p_invalid_input():
    """Test expand_c2p with invalid input."""
    with pytest.raises(AssertionError, match="character_id must be a positive integer"):
        repo.expand_c2p(0)

    with pytest.raises(AssertionError, match="character_id must be a positive integer"):
        repo.expand_c2p(-1)

    with pytest.raises(AssertionError, match="character_id must be a positive integer"):
        repo.expand_c2p("invalid")


def test_expand_c2s():
    """Test expand_c2s (character to subject) method."""
    # Test valid character ID
    edges = repo.expand_c2s(1)
    assert edges is not None
    assert isinstance(edges, list)

    # Test with character that has no subject relations
    edges = repo.expand_c2s(999999)
    assert edges == []


def test_expand_c2s_invalid_input():
    """Test expand_c2s with invalid input."""
    with pytest.raises(AssertionError, match="character_id must be a positive integer"):
        repo.expand_c2s(0)

    with pytest.raises(AssertionError, match="character_id must be a positive integer"):
        repo.expand_c2s(-1)

    with pytest.raises(AssertionError, match="character_id must be a positive integer"):
        repo.expand_c2s("invalid")


def test_expand_p2s():
    """Test expand_p2s (person to subject) method."""
    # Test valid person ID
    edges = repo.expand_p2s(1)
    assert edges is not None
    assert isinstance(edges, list)

    # Test with person that has no subject relations
    edges = repo.expand_p2s(999999)
    assert edges == []


def test_expand_p2s_invalid_input():
    """Test expand_p2s with invalid input."""
    with pytest.raises(AssertionError, match="person_id must be a positive integer"):
        repo.expand_p2s(0)

    with pytest.raises(AssertionError, match="person_id must be a positive integer"):
        repo.expand_p2s(-1)

    with pytest.raises(AssertionError, match="person_id must be a positive integer"):
        repo.expand_p2s("invalid")


def test_graph_edge_structure():
    """Test that returned edges have the correct structure."""
    # Test s2s edges
    edges = repo.expand_s2s(1)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'from_subject')
        assert hasattr(edge, 'to_subject')
        assert hasattr(edge, 's2s_relation_type')

    # Test s2c edges
    edges = repo.expand_s2c(1)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'from_subject')
        assert hasattr(edge, 'to_character')
        assert hasattr(edge, 's2c_type')

    # Test s2p edges
    edges = repo.expand_s2p(1)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'from_subject')
        assert hasattr(edge, 'to_person')
        assert hasattr(edge, 's2p_position')

    # Test c2p edges
    edges = repo.expand_c2p(1)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'from_character')
        assert hasattr(edge, 'to_person')
        assert hasattr(edge, 'p2c_summary')

    # Test c2s edges
    edges = repo.expand_c2s(1)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'from_character')
        assert hasattr(edge, 'to_subject')
        assert hasattr(edge, 's2c_type')

    # Test p2s edges
    edges = repo.expand_p2s(1)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'from_person')
        assert hasattr(edge, 'to_subject')
        assert hasattr(edge, 's2p_position')


def test_empty_results():
    """Test that methods return empty lists for non-existent IDs."""
    non_existent_id = 999999

    assert repo.expand_s2s(non_existent_id) == []
    assert repo.expand_s2c(non_existent_id) == []
    assert repo.expand_s2p(non_existent_id) == []
    assert repo.expand_c2p(non_existent_id) == []
    assert repo.expand_c2s(non_existent_id) == []
    assert repo.expand_p2s(non_existent_id) == []
