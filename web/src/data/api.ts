// API client for Bangumi Archive
// Based on OpenAPI specification

// Enums from the API specification
export enum SubjectType {
  ANIME = 1,
  COMIC = 2,
  GAME = 3,
  MUSIC = 4,
  REAL = 6,
}

export enum EpisodeType {
  NORMAL = 0,
  SPECIAL = 1,
  OPENING = 2,
  ENDING = 3,
  PREVIEW = 4,
  MAD = 5,
  OTHER = 6,
}

export enum PersonType {
  INDIVIDUAL = 0,
  COMPANY = 1,
  ASSOCIATION = 2,
  UNIT = 3,
}

// Additional types from OpenAPI spec
export type AnimeStuff =
  | 1
  | 74
  | 2
  | 72
  | 3
  | 4
  | 89
  | 5
  | 91
  | 6
  | 7
  | 8
  | 9
  | 10
  | 11
  | 71
  | 13
  | 16
  | 19
  | 14
  | 15
  | 90
  | 70
  | 77
  | 17
  | 69
  | 86
  | 18
  | 20
  | 21
  | 92
  | 22
  | 67
  | 73
  | 82
  | 65
  | 85
  | 55
  | 24
  | 25
  | 26
  | 27
  | 75
  | 37
  | 28
  | 29
  | 30
  | 31
  | 32
  | 33
  | 34
  | 35
  | 36
  | 38
  | 39
  | 40
  | 41
  | 42
  | 63
  | 43
  | 84
  | 44
  | 45
  | 46
  | 88
  | 47
  | 48
  | 49
  | 50
  | 51
  | 58
  | 59
  | 54
  | 52
  | 53
  | 23
  | 87
  | 80
  | 56
  | 83
  | 57
  | 60
  | 61
  | 62
  | 64
  | 76
  | 66
  | 81;

export type BookStaff = 2007 | 2001 | 2002 | 2003 | 2010 | 2004 | 2005 | 2006 | 2008 | 2009 | 2011 | 2012 | 2013;

export type GameStaff =
  | 1001
  | 1002
  | 1003
  | 1015
  | 1016
  | 1032
  | 1028
  | 1026
  | 1004
  | 1027
  | 1031
  | 1013
  | 1008
  | 1029
  | 1005
  | 1023
  | 1024
  | 1025
  | 1030
  | 1006
  | 1021
  | 1014
  | 1017
  | 1020
  | 1018
  | 1019
  | 1007
  | 1009
  | 1010
  | 1011
  | 1012
  | 1022;

export type MusicStaff =
  | 3001
  | 3002
  | 3004
  | 3003
  | 3006
  | 3008
  | 3014
  | 3015
  | 3007
  | 3013
  | 3012
  | 3009
  | 3005
  | 3010
  | 3011;

export type RealStaff =
  | 4001
  | 4002
  | 4013
  | 4003
  | 4004
  | 4005
  | 4006
  | 4007
  | 4008
  | 4009
  | 4010
  | 4011
  | 4012
  | 4014
  | 4015
  | 4016
  | 4017
  | 4018
  | 4019;

export type SubjectRelationType =
  | 1
  | 2
  | 3
  | 4
  | 5
  | 6
  | 7
  | 8
  | 9
  | 10
  | 11
  | 12
  | 14
  | 99
  | 1002
  | 1003
  | 1004
  | 1005
  | 1006
  | 1007
  | 1008
  | 1010
  | 1011
  | 1012
  | 1013
  | 1014
  | 1015
  | 1099
  | 3001
  | 3002
  | 3003
  | 3004
  | 3005
  | 3006
  | 3007
  | 3099
  | 4002
  | 4003
  | 4006
  | 4007
  | 4008
  | 4009
  | 4010
  | 4012
  | 4014
  | 4015
  | 4016
  | 4017
  | 4018
  | 4099;

export enum SubjectCharacterType {
  // Subject character types - values from OpenAPI spec
  MAIN = 1,
  SUPPORTING = 2,
  CAMEOS = 3,
  OTHER = 4,
  UNKNOWN = 5,
}

// Data types from the API specification
export interface Tag {
  name: string;
  count: number;
}

export interface ScoreDetails {
  1: number;
  2: number;
  3: number;
  4: number;
  5: number;
  6: number;
  7: number;
  8: number;
  9: number;
  10: number;
}

export interface Favorite {
  wish: number;
  done: number;
  doing: number;
  on_hold: number;
  dropped: number;
}

export interface Subject {
  id: number;
  type: SubjectType;
  name: string;
  name_cn: string;
  infobox: string;
  platform: number;
  summary: string;
  nsfw: boolean;
  tags: Tag[];
  score: number;
  score_details: ScoreDetails | null;
  rank: number;
  date: string | null;
  favorite: Favorite;
  series: boolean;
  meta_tags: string[] | null;
}

export interface Episode {
  id: number;
  name: string;
  name_cn: string;
  description: string;
  airdate: string | null;
  disc: number;
  duration: string;
  subject_id: number;
  sort: number;
  type: EpisodeType;
}

export interface Character {
  id: number;
  name: string;
  infobox: string;
  summary: string;
  comments: number;
  collects: number;
}

export interface Person {
  id: number;
  name: string;
  type: PersonType;
  career: string[];
  infobox: string;
  summary: string;
  comments: number;
  collects: number;
}

// New types from OpenAPI spec
export interface GraphEdgeSimple {
  subject1_id: number | null;
  subject2_id: number | null;
  character_id: number | null;
  person_id: number | null;
  s2s_relation_type: SubjectRelationType | null;
  sp_position: AnimeStuff | BookStaff | GameStaff | MusicStaff | RealStaff | null;
  sc_type: SubjectCharacterType | null;
  sc_order_idx: number | null;
  engagement_summary: string | null;
}

export interface Subgraph {
  center_subject: Subject | null;
  center_character: Character | null;
  center_person: Person | null;
  subjects: Subject[];
  characters: Character[];
  persons: Person[];
  edges: GraphEdgeSimple[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface HTTPValidationError {
  detail: ValidationError[];
}

// Search query interfaces - matching OpenAPI spec exactly
export interface SubjectsIndexQuery {
  query: string;
  limit?: number;
  offset?: number;
  type?: number;
  subject_type?: number;
  nsfw?: boolean;
}

export interface CharactersIndexQuery {
  query: string;
  limit?: number;
  offset?: number;
}

export interface PersonsIndexQuery {
  query: string;
  limit?: number;
  offset?: number;
  type?: number;
  career?: string;
}

export interface EpisodesIndexQuery {
  query: string;
  limit?: number;
  offset?: number;
  type?: number;
  subject_id?: number;
}

// API Response types - matching OpenAPI spec exactly
export interface SubjectSearchResult {
  items: Subject[];
  total: number;
  query: string;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface CharacterSearchResult {
  items: Character[];
  total: number;
  query: string;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface PersonSearchResult {
  items: Person[];
  total: number;
  query: string;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface EpisodeSearchResult {
  items: Episode[];
  total: number;
  query: string;
  limit: number;
  offset: number;
  has_more: boolean;
}

// Type aliases for backward compatibility
export type SubjectsResponse = SubjectSearchResult;
export type CharactersResponse = CharacterSearchResult;
export type PeopleResponse = PersonSearchResult;
export type EpisodesResponse = EpisodeSearchResult;

// API Client Configuration
export interface APIClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

// API Client Class
export class BGMArchiveAPI {
  private config: APIClientConfig;

  constructor(config: APIClientConfig) {
    this.config = {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
      ...config,
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`;

    const requestOptions: RequestInit = {
      ...options,
      headers: {
        ...this.config.headers,
        ...options.headers,
      },
    };

    if (this.config.timeout) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      try {
        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        clearTimeout(timeoutId);
        throw error;
      }
    } else {
      const response = await fetch(url, requestOptions);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    }
  }

  // Subject endpoints
  async getSubject(subjectId: number): Promise<Subject> {
    return this.request<Subject>(`/subjects/${subjectId}`);
  }

  async searchSubjects(searchQuery: SubjectsIndexQuery): Promise<SubjectSearchResult> {
    return this.request<SubjectSearchResult>('/subjects/search', {
      method: 'POST',
      body: JSON.stringify(searchQuery),
    });
  }

  async getSubjectsMultiple(ids?: string): Promise<Subject[]> {
    const params = ids ? `?ids=${encodeURIComponent(ids)}` : '';
    return this.request<Subject[]>(`/subjects/multiple${params}`);
  }

  async getSubjectEpisodes(subjectId: number): Promise<Episode[]> {
    return this.request<Episode[]>(`/subjects/${subjectId}/episodes`);
  }

  async getSubjectEdges(subjectId: number): Promise<Subgraph> {
    return this.request<Subgraph>(`/subjects/${subjectId}/edges`);
  }

  // Character endpoints
  async getCharacter(characterId: number): Promise<Character> {
    return this.request<Character>(`/characters/${characterId}`);
  }

  async searchCharacters(searchQuery: CharactersIndexQuery): Promise<CharacterSearchResult> {
    return this.request<CharacterSearchResult>('/characters/search', {
      method: 'POST',
      body: JSON.stringify(searchQuery),
    });
  }

  async getCharactersMultiple(ids?: string): Promise<Character[]> {
    const params = ids ? `?ids=${encodeURIComponent(ids)}` : '';
    return this.request<Character[]>(`/characters/multiple${params}`);
  }

  async getCharacterEdges(characterId: number): Promise<Subgraph> {
    return this.request<Subgraph>(`/characters/${characterId}/edges`);
  }

  // Person endpoints
  async getPerson(personId: number): Promise<Person> {
    return this.request<Person>(`/people/${personId}`);
  }

  async searchPeople(searchQuery: PersonsIndexQuery): Promise<PersonSearchResult> {
    return this.request<PersonSearchResult>('/people/search', {
      method: 'POST',
      body: JSON.stringify(searchQuery),
    });
  }

  async getPeopleMultiple(ids?: string): Promise<Person[]> {
    const params = ids ? `?ids=${encodeURIComponent(ids)}` : '';
    return this.request<Person[]>(`/people/multiple${params}`);
  }

  async getPersonEdges(personId: number): Promise<Subgraph> {
    return this.request<Subgraph>(`/people/${personId}/edges`);
  }

  // Episode endpoints
  async searchEpisodes(searchQuery: EpisodesIndexQuery): Promise<EpisodeSearchResult> {
    return this.request<EpisodeSearchResult>('/episodes/search', {
      method: 'POST',
      body: JSON.stringify(searchQuery),
    });
  }

  // Utility methods
  getBaseURL(): string {
    return this.config.baseURL;
  }

  updateConfig(newConfig: Partial<APIClientConfig>): void {
    this.config = {...this.config, ...newConfig};
  }
}

// Default API client instance
export const defaultAPI = new BGMArchiveAPI({
  baseURL: 'http://localhost:8000',
});

// Export individual methods for convenience
export const {
  getSubject,
  searchSubjects,
  searchPeople,
  searchCharacters,
  searchEpisodes,
  getSubjectsMultiple,
  getSubjectEpisodes,
  getSubjectEdges,
  getCharacter,
  getCharactersMultiple,
  getCharacterEdges,
  getPerson,
  getPeopleMultiple,
  getPersonEdges,
} = defaultAPI;
