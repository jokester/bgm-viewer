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

export enum CharacterRole {
  MAIN = 1,
  SUPPORTING = 2,
  MINOR = 3,
  GUEST = 4,
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
  role: CharacterRole;
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
  role?: number;
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
    options: RequestInit = {}
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
    this.config = { ...this.config, ...newConfig };
  }
}

// Default API client instance
export const defaultAPI = new BGMArchiveAPI({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
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
  getCharacter,
  getCharactersMultiple,
  getPerson,
  getPeopleMultiple,
} = defaultAPI;
