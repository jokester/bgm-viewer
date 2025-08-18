import os
import pytest

from .graph_repo import GraphRepository
from .rdb_repo import RdbRepository
from .data import Subgraph, GraphEdgeSimple

_rdb_repo = RdbRepository(db=os.environ["TEST_DUCKDB"])
repo = GraphRepository(db=os.environ["TEST_DUCKDB"])


def test_expand_s2s():
    """Test expand_s2s (subject to subject) method."""
    # Test valid subject ID
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")

    subgraph = repo.expand_s2s(subject)
    assert subgraph is not None
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject == subject
    assert subgraph.center_character is None
    assert subgraph.center_person is None
    assert isinstance(subgraph.edges, list)
    assert isinstance(subgraph.subjects, list)

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
            series=False,
        )

    subgraph = repo.expand_s2s(subject_no_relations)
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject == subject_no_relations
    assert subgraph.center_character is None
    assert subgraph.center_person is None
    assert subgraph.edges == []
    assert len(subgraph.subjects) == 1  # Only the starting subject


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

    subgraph = repo.expand_sc(subject)
    assert subgraph is not None
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject == subject
    assert subgraph.center_character is None
    assert subgraph.center_person is None
    assert isinstance(subgraph.edges, list)
    assert isinstance(subgraph.subjects, list)
    assert isinstance(subgraph.characters, list)

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
            series=False,
        )

    subgraph = repo.expand_sc(subject_no_relations)
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject == subject_no_relations
    assert subgraph.center_character is None
    assert subgraph.center_person is None
    assert subgraph.edges == []
    assert len(subgraph.subjects) == 1  # Only the starting subject
    assert subgraph.characters == []


def test_expand_s2p():
    """Test expand_s2p (subject to person) method."""
    # Test valid subject ID
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")

    subgraph = repo.expand_sp(subject)
    assert subgraph is not None
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject == subject
    assert subgraph.center_character is None
    assert subgraph.center_person is None
    assert isinstance(subgraph.edges, list)
    assert isinstance(subgraph.subjects, list)
    assert isinstance(subgraph.persons, list)

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
            series=False,
        )

    subgraph = repo.expand_sp(subject_no_relations)
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject == subject_no_relations
    assert subgraph.center_character is None
    assert subgraph.center_person is None
    assert subgraph.edges == []
    assert len(subgraph.subjects) == 1  # Only the starting subject
    assert subgraph.persons == []


def test_expand_s2p_invalid_input():
    """Test expand_s2p with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_sp(0)

    with pytest.raises(AssertionError):
        repo.expand_sp(-1)

    with pytest.raises(AssertionError):
        repo.expand_sp("invalid")


def test_expand_s2e():
    """Test expand_s2e (subject to engagement) method."""
    # Test valid subject ID
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")

    subgraph = repo.expand_se(subject)
    assert subgraph is not None
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject == subject
    assert subgraph.center_character is None
    assert subgraph.center_person is None
    assert isinstance(subgraph.edges, list)
    assert isinstance(subgraph.subjects, list)
    assert isinstance(subgraph.persons, list)
    assert isinstance(subgraph.characters, list)

    # Test with subject that has no engagement relations
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
            series=False,
        )

    subgraph = repo.expand_se(subject_no_relations)
    assert isinstance(subgraph, Subgraph)
    assert subgraph.edges == []
    assert len(subgraph.subjects) == 1  # Only the starting subject
    assert subgraph.persons == []
    assert subgraph.characters == []


def test_expand_s2e_invalid_input():
    """Test expand_s2e with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_se(0)

    with pytest.raises(AssertionError):
        repo.expand_se(-1)

    with pytest.raises(AssertionError):
        repo.expand_se("invalid")


def test_expand_c2s():
    """Test expand_c2s (character to subject) method."""
    # Test valid character ID
    character = _rdb_repo.find_character_by_id(1)
    if character is None:
        pytest.skip("Character with ID 1 not found in test database")

    subgraph = repo.expand_cs(character)
    assert subgraph is not None
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject is None
    assert subgraph.center_character == character
    assert subgraph.center_person is None
    assert isinstance(subgraph.edges, list)
    assert isinstance(subgraph.subjects, list)
    assert isinstance(subgraph.characters, list)

    # Test with character that has no subject relations
    character_no_relations = _rdb_repo.find_character_by_id(999999)
    if character_no_relations is None:
        # Create a dummy character for testing
        import bgm_archive.loader.model as m

        character_no_relations = m.Character(
            id=999999,
            name="Test Character",
            infobox="",
            summary="",
            comments=0,
            collects=0,
        )

    subgraph = repo.expand_cs(character_no_relations)
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject is None
    assert subgraph.center_character == character_no_relations
    assert subgraph.center_person is None
    assert subgraph.edges == []
    assert subgraph.subjects == []
    assert len(subgraph.characters) == 1  # Only the starting character


def test_expand_c2s_invalid_input():
    """Test expand_c2s with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_cs(0)

    with pytest.raises(AssertionError):
        repo.expand_cs(-1)

    with pytest.raises(AssertionError):
        repo.expand_cs("invalid")


def test_expand_p2s():
    """Test expand_p2s (person to subject) method."""
    # Test valid person ID
    person = _rdb_repo.find_person_by_id(1)
    if person is None:
        pytest.skip("Person with ID 1 not found in test database")

    subgraph = repo.expand_ps(person)
    assert subgraph is not None
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject is None
    assert subgraph.center_character is None
    assert subgraph.center_person == person
    assert isinstance(subgraph.edges, list)
    assert isinstance(subgraph.subjects, list)
    assert isinstance(subgraph.persons, list)

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
            collects=0,
        )

    subgraph = repo.expand_ps(person_no_relations)
    assert isinstance(subgraph, Subgraph)
    assert subgraph.center_subject is None
    assert subgraph.center_character is None
    assert subgraph.center_person == person_no_relations
    assert subgraph.edges == []
    assert subgraph.subjects == []
    assert len(subgraph.persons) == 1  # Only the starting person


def test_expand_p2s_invalid_input():
    """Test expand_p2s with invalid input."""
    with pytest.raises(AssertionError):
        repo.expand_ps(0)

    with pytest.raises(AssertionError):
        repo.expand_ps(-1)

    with pytest.raises(AssertionError):
        repo.expand_ps("invalid")


def test_graph_edge_structure():
    """Test that returned edges have the correct structure."""
    # Test s2s edges
    subject = _rdb_repo.find_subject_by_id(1)
    if subject is None:
        pytest.skip("Subject with ID 1 not found in test database")

    subgraph = repo.expand_s2s(subject)
    if subgraph.edges:
        edge = subgraph.edges[0]
        assert isinstance(edge, GraphEdgeSimple)
        assert hasattr(edge, "s2s_relation_type")

    # Test s2c edges
    subgraph = repo.expand_sc(subject)
    if subgraph.edges:
        edge = subgraph.edges[0]
        assert isinstance(edge, GraphEdgeSimple)
        assert hasattr(edge, "sc_type")

    # Test s2p edges
    subgraph = repo.expand_sp(subject)
    if subgraph.edges:
        edge = subgraph.edges[0]
        assert isinstance(edge, GraphEdgeSimple)
        assert hasattr(edge, "sp_position")

    # Test s2e edges
    subgraph = repo.expand_se(subject)
    if subgraph.edges:
        edge = subgraph.edges[0]
        assert isinstance(edge, GraphEdgeSimple)
        assert hasattr(edge, "engagement_summary")

    # Test c2s edges
    character = _rdb_repo.find_character_by_id(1)
    if character is None:
        pytest.skip("Character with ID 1 not found in test database")

    subgraph = repo.expand_cs(character)
    if subgraph.edges:
        edge = subgraph.edges[0]
        assert isinstance(edge, GraphEdgeSimple)
        assert hasattr(edge, "sc_type")

    # Test p2s edges
    person = _rdb_repo.find_person_by_id(1)
    if person is None:
        pytest.skip("Person with ID 1 not found in test database")

    subgraph = repo.expand_ps(person)
    if subgraph.edges:
        edge = subgraph.edges[0]
        assert isinstance(edge, GraphEdgeSimple)
        assert hasattr(edge, "sp_position")


def test_empty_results():
    """Test that methods return empty subgraphs for non-existent IDs."""
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
        series=False,
    )

    non_existent_character = m.Character(
        id=999999,
        name="Test Character",
        infobox="",
        summary="",
        comments=0,
        collects=0,
    )

    non_existent_person = m.Person(
        id=999999,
        name="Test Person",
        type=m.PersonType.INDIVIDUAL,
        career=[],
        infobox="",
        summary="",
        comments=0,
        collects=0,
    )

    # Test that all methods return Subgraph objects with empty edges
    s2s_subgraph = repo.expand_s2s(non_existent_subject)
    assert isinstance(s2s_subgraph, Subgraph)
    assert s2s_subgraph.center_subject == non_existent_subject
    assert s2s_subgraph.center_character is None
    assert s2s_subgraph.center_person is None
    assert s2s_subgraph.edges == []
    assert len(s2s_subgraph.subjects) == 1  # Only the starting subject

    sc_subgraph = repo.expand_sc(non_existent_subject)
    assert isinstance(sc_subgraph, Subgraph)
    assert sc_subgraph.center_subject == non_existent_subject
    assert sc_subgraph.center_character is None
    assert sc_subgraph.center_person is None
    assert sc_subgraph.edges == []
    assert len(sc_subgraph.subjects) == 1  # Only the starting subject
    assert sc_subgraph.characters == []

    sp_subgraph = repo.expand_sp(non_existent_subject)
    assert isinstance(sp_subgraph, Subgraph)
    assert sp_subgraph.center_subject == non_existent_subject
    assert sp_subgraph.center_character is None
    assert sp_subgraph.center_person is None
    assert sp_subgraph.edges == []
    assert len(sp_subgraph.subjects) == 1  # Only the starting subject
    assert sp_subgraph.persons == []

    se_subgraph = repo.expand_se(non_existent_subject)
    assert isinstance(se_subgraph, Subgraph)
    assert se_subgraph.center_subject == non_existent_subject
    assert se_subgraph.center_character is None
    assert se_subgraph.center_person is None
    assert se_subgraph.edges == []
    assert len(se_subgraph.subjects) == 1  # Only the starting subject
    assert se_subgraph.persons == []
    assert se_subgraph.characters == []

    cs_subgraph = repo.expand_cs(non_existent_character)
    assert isinstance(cs_subgraph, Subgraph)
    assert cs_subgraph.center_subject is None
    assert cs_subgraph.center_character == non_existent_character
    assert cs_subgraph.center_person is None
    assert cs_subgraph.edges == []
    assert cs_subgraph.subjects == []
    assert len(cs_subgraph.characters) == 1  # Only the starting character

    ps_subgraph = repo.expand_ps(non_existent_person)
    assert isinstance(ps_subgraph, Subgraph)
    assert ps_subgraph.center_subject is None
    assert ps_subgraph.center_character is None
    assert ps_subgraph.center_person == non_existent_person
    assert ps_subgraph.edges == []
    assert ps_subgraph.subjects == []
    assert len(ps_subgraph.persons) == 1  # Only the starting person
