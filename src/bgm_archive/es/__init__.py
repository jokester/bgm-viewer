from .conn import get_async_client
from .base_index import SearchResult
from .subject_index import SubjectsIndex, SubjectsIndexQuery, SubjectSearchResult
from .person_index import PersonIndex, PersonsIndexQuery, PersonSearchResult
from .character_index import CharacterIndex, CharactersIndexQuery, CharacterSearchResult
from .episode_index import EpisodeIndex, EpisodesIndexQuery, EpisodeSearchResult

__all__ = [
    # Base classes
    "SearchResult",
    # Subject related
    "SubjectsIndex",
    "SubjectsIndexQuery", 
    "SubjectSearchResult",
    # Person related
    "PersonIndex",
    "PersonsIndexQuery",
    "PersonSearchResult",
    # Character related
    "CharacterIndex",
    "CharactersIndexQuery",
    "CharacterSearchResult",
    # Episode related
    "EpisodeIndex",
    "EpisodesIndexQuery",
    "EpisodeSearchResult",
    # Connection
    "get_async_client",
]
