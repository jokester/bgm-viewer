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
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")
    
    edges = repo.expand_s2s(subject)
    assert edges is not None
    assert isinstance(edges, list)
    
    # Test with subject that has no relations
    subject_no_relations = _rdb_repo.find_subject_by_id(999999)
    if subject_no_relations is None:
        # Create a dummy subject for testing
        import bgm_archive.loader.model as m
        subject_no_relations = m.Subject(
            id=999999,
            type=m.SubjectType.ANIME,
            name="Test Subject",
            name_cn="测试主题",
            infobox="",
            platform=0,
            summary="",
            nsfw=False,
            tags=[],
            score=0.0,
            rank=0,
            date=None,
            favorite=m.Favorite(wish=0, done=0, doing=0, on_hold=0, dropped=0),
            series=False
        )
    
    edges = repo.expand_s2s(subject_no_relations)
    assert edges == []


def test_expand_s2s_invalid_input():
    """Test expand_s2s with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_s2s(0)
    
    with pytest.raises(AssertionError):
        repo.expand_s2s(-1)
    
    with pytest.raises(AssertionError):
        repo.expand_s2s("invalid")


def test_expand_s2c():
    """Test expand_s2c (subject to character) method."""
    # Test valid subject ID
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")
    
    edges = repo.expand_s2c(subject)
    assert edges is not None
    assert isinstance(edges, list)
    
    # Test with subject that has no character relations
    subject_no_relations = _rdb_repo.find_subject_by_id(999999)
    if subject_no_relations is None:
        # Create a dummy subject for testing
        import bgm_archive.loader.model as m
        subject_no_relations = m.Subject(
            id=999999,
            type=m.SubjectType.ANIME,
            name="Test Subject",
            name_cn="测试主题",
            infobox="",
            platform=0,
            summary="",
            nsfw=False,
            tags=[],
            score=0.0,
            rank=0,
            date=None,
            favorite=m.Favorite(wish=0, done=0, doing=0, on_hold=0, dropped=0),
            series=False
        )
    
    edges = repo.expand_s2c(subject_no_relations)
    assert edges == []


def test_expand_s2c_invalid_input():
    """Test expand_s2c with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_s2c(0)
    
    with pytest.raises(AssertionError):
        repo.expand_s2c(-1)
    
    with pytest.raises(AssertionError):
        repo.expand_s2c("invalid")


def test_expand_s2p():
    """Test expand_s2p (subject to person) method."""
    # Test valid subject ID
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")
    
    edges = repo.expand_s2p(subject)
    assert edges is not None
    assert isinstance(edges, list)
    
    # Test with subject that has no person relations
    subject_no_relations = _rdb_repo.find_subject_by_id(999999)
    if subject_no_relations is None:
        # Create a dummy subject for testing
        import bgm_archive.loader.model as m
        subject_no_relations = m.Subject(
            id=999999,
            type=m.SubjectType.ANIME,
            name="Test Subject",
            name_cn="测试主题",
            infobox="",
            platform=0,
            summary="",
            nsfw=False,
            tags=[],
            score=0.0,
            rank=0,
            date=None,
            favorite=m.Favorite(wish=0, done=0, doing=0, on_hold=0, dropped=0),
            series=False
        )
    
    edges = repo.expand_s2p(subject_no_relations)
    assert edges == []


def test_expand_s2p_invalid_input():
    """Test expand_s2p with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_s2p(0)
    
    with pytest.raises(AssertionError):
        repo.expand_s2p(-1)
    
    with pytest.raises(AssertionError):
        repo.expand_s2p("invalid")


def test_expand_c2p():
    """Test expand_c2p (character to person) edges for a given character."""
    # Test valid character ID
    character = _rdb_repo.find_character_by_id(1)
    if character is None:
        pytest.skip("Character with ID 1 not found in test database")
    
    edges = repo.expand_c2p(character)
    assert edges is not None
    assert isinstance(edges, list)
    
    # Test with character that has no person relations
    character_no_relations = _rdb_repo.find_character_by_id(999999)
    if character_no_relations is None:
        # Create a dummy character for testing
        import bgm_archive.loader.model as m
        character_no_relations = m.Character(
            id=999999,
            role=m.CharacterRole.MAIN,
            name="Test Character",
            infobox="",
            summary="",
            comments=0,
            collects=0
        )
    
    edges = repo.expand_c2p(character_no_relations)
    assert edges == []


def test_expand_c2p_invalid_input():
    """Test expand_c2p with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_c2p(0)
    
    with pytest.raises(AssertionError):
        repo.expand_c2p(-1)
    
    with pytest.raises(AssertionError):
        repo.expand_c2p("invalid")


def test_expand_c2s():
    """Test expand_c2s (character to subject) method."""
    # Test valid character ID
    character = _rdb_repo.find_character_by_id(1)
    if character is None:
        pytest.skip("Character with ID 1 not found in test database")
    
    edges = repo.expand_c2s(character)
    assert edges is not None
    assert isinstance(edges, list)
    
    # Test with character that has no subject relations
    character_no_relations = _rdb_repo.find_character_by_id(999999)
    if character_no_relations is None:
        # Create a dummy character for testing
        import bgm_archive.loader.model as m
        character_no_relations = m.Character(
            id=999999,
            role=m.CharacterRole.MAIN,
            name="Test Character",
            infobox="",
            summary="",
            comments=0,
            collects=0
        )
    
    edges = repo.expand_c2s(character_no_relations)
    assert edges == []


def test_expand_c2s_invalid_input():
    """Test expand_c2s with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_c2s(0)
    
    with pytest.raises(AssertionError):
        repo.expand_c2s(-1)
    
    with pytest.raises(AssertionError):
        repo.expand_c2s("invalid")


def test_expand_p2s():
    """Test expand_p2s (person to subject) method."""
    # Test valid person ID
    person = _rdb_repo.find_person_by_id(1)
    if person is None:
        pytest.skip("Person with ID 1 not found in test database")
    
    edges = repo.expand_p2s(person)
    assert edges is not None
    assert isinstance(edges, list)
    
    # Test with person that has no subject relations
    person_no_relations = _rdb_repo.find_person_by_id(999999)
    if person_no_relations is None:
        # Create a dummy person for testing
        import bgm_archive.loader.model as m
        person_no_relations = m.Person(
            id=999999,
            name="Test Person",
            type=m.PersonType.INDIVIDUAL,
            career=[],
            infobox="",
            summary="",
            comments=0,
            collects=0
        )
    
    edges = repo.expand_p2s(person_no_relations)
    assert edges == []


def test_expand_p2s_invalid_input():
    """Test expand_p2s with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_p2s(0)
    
    with pytest.raises(AssertionError):
        repo.expand_p2s(-1)
    
    with pytest.raises(AssertionError):
        repo.expand_p2s("invalid")


def test_graph_edge_structure():
    """Test that returned edges have the correct structure."""
    # Test s2s edges
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")
    
    edges = repo.expand_s2s(subject)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'to_subject')
        assert hasattr(edge, 's2s_relation_type')
    
    # Test s2c edges
    edges = repo.expand_s2c(subject)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'to_character')
        assert hasattr(edge, 's2c_type')
    
    # Test s2p edges
    edges = repo.expand_s2p(subject)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'to_person')
        assert hasattr(edge, 's2p_position')
    
    # Test c2p edges
    character = _rdb_repo.find_character_by_id(1)
    if character is None:
        pytest.skip("Character with ID 1 not found in test database")
    
    edges = repo.expand_c2p(character)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'to_person')
        assert hasattr(edge, 'p2c_summary')
    
    # Test c2s edges
    edges = repo.expand_c2s(character)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'to_subject')
        assert hasattr(edge, 's2c_type')
    
    # Test p2s edges
    person = _rdb_repo.find_person_by_id(1)
    if person is None:
        pytest.skip("Person with ID 1 not found in test database")
    
    edges = repo.expand_p2s(person)
    if edges:
        edge = edges[0]
        assert hasattr(edge, 'to_subject')
        assert hasattr(edge, 's2p_position')


def test_empty_results():
    """Test that methods return empty lists for non-existent IDs."""
    # Create dummy entities for testing
    import bgm_archive.loader.model as m
    
    non_existent_subject = m.Subject(
        id=999999,
        type=m.SubjectType.ANIME,
        name="Test Subject",
        name_cn="测试主题",
        infobox="",
        platform=0,
        summary="",
        nsfw=False,
        tags=[],
        score=0.0,
        rank=0,
        date=None,
        favorite=m.Favorite(wish=0, done=0, doing=0, on_hold=0, dropped=0),
        series=False
    )
    
    non_existent_character = m.Character(
        id=999999,
        role=m.CharacterRole.MAIN,
        name="Test Character",
        infobox="",
        summary="",
        comments=0,
        collects=0
    )
    
    non_existent_person = m.Person(
        id=999999,
        name="Test Person",
        type=m.PersonType.INDIVIDUAL,
        career=[],
        infobox="",
        summary="",
        comments=0,
        collects=0
    )
    
    assert repo.expand_s2s(non_existent_subject) == []
    assert repo.expand_s2c(non_existent_subject) == []
    assert repo.expand_s2p(non_existent_subject) == []
    assert repo.expand_c2p(non_existent_character) == []
    assert repo.expand_c2s(non_existent_character) == []
    assert repo.expand_p2s(non_existent_person) == []
