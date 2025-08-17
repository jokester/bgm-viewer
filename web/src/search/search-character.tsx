import { useState, useEffect, useCallback } from 'react';
import { Character, CharacterRole, CharactersIndexQuery, CharacterSearchResult } from '../data/api';
import { useBgmApi } from '../data';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Card } from 'primereact/card';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Paginator } from 'primereact/paginator';

export const SearchCharacter = () => {
  const api = useBgmApi();
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<number | null>(null);
  const [results, setResults] = useState<Character[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(0);
  const [totalResults, setTotalResults] = useState<number>(0);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  const pageSize = 20;

  const characterRoleOptions = [
    { label: 'All Roles', value: null },
    { label: 'Main Character', value: CharacterRole.MAIN },
    { label: 'Supporting Character', value: CharacterRole.SUPPORTING },
    { label: 'Minor Character', value: CharacterRole.MINOR },
    { label: 'Guest Character', value: CharacterRole.GUEST },
  ];

  // Debounced search function
  const debouncedSearch = useCallback((query: string) => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    if (query.trim().length >= 2) {
      const timeout = setTimeout(() => {
        performSearch(0);
      }, 500);
      setSearchTimeout(timeout);
    }
  }, [searchTimeout]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchTimeout]);

  const performSearch = async (page: number = 0) => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentPage(page);

    try {
      const searchParams: CharactersIndexQuery = {
        query: searchQuery.trim(),
        limit: pageSize,
        offset: page * pageSize,
        role: selectedRole || undefined,
      };

      const searchResults = await api.searchCharacters(searchParams);
      setResults(searchResults.characters);
      setTotalResults(searchResults.total);
      
      setHasSearched(true);
    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : 'Search failed. Please try again.');
      setResults([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    performSearch(0);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleQueryChange = (value: string) => {
    setSearchQuery(value);
    if (value.trim().length >= 2) {
      debouncedSearch(value);
    } else {
      setResults([]);
      setHasSearched(false);
      setTotalResults(0);
    }
  };

  const handlePageChange = (event: { page: number }) => {
    performSearch(event.page);
  };

  const handleFilterChange = () => {
    // Reset to first page when filters change
    performSearch(0);
  };

  const formatCharacterRole = (role: number): string => {
    switch (role) {
      case CharacterRole.MAIN: return 'Main Character';
      case CharacterRole.SUPPORTING: return 'Supporting Character';
      case CharacterRole.MINOR: return 'Minor Character';
      case CharacterRole.GUEST: return 'Guest Character';
      default: return 'Unknown';
    }
  };

  const truncateText = (text: string, maxLength: number = 150): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Search Characters</h1>
      
      {/* Search Form */}
      <Card className="mb-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Search Criteria</h2>
          <p className="text-sm text-gray-600 mb-3">
            Search across character names, summaries, and infobox information. Type at least 2 characters to start searching.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2">
              <label htmlFor="searchQuery" className="block text-sm font-medium text-gray-700 mb-2">
                Search Query
              </label>
              <div className="relative">
                <InputText
                  id="searchQuery"
                  value={searchQuery}
                  onChange={(e) => handleQueryChange(e.target.value)}
                  onKeyUp={handleKeyPress}
                  placeholder="Search by character name, summary, infobox..."
                  className="w-full"
                />
                {loading && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <ProgressSpinner style={{ width: '16px', height: '16px' }} />
                  </div>
                )}
                {searchQuery.trim().length >= 2 && !loading && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <i className="pi pi-clock text-gray-400 text-sm"></i>
                  </div>
                )}
              </div>
            </div>
            
            <div>
              <label htmlFor="characterRole" className="block text-sm font-medium text-gray-700 mb-2">
                Character Role
              </label>
              <Dropdown
                id="characterRole"
                value={selectedRole}
                onChange={(e) => {
                  setSelectedRole(e.value);
                  handleFilterChange();
                }}
                options={characterRoleOptions}
                optionLabel="label"
                optionValue="value"
                placeholder="Select role"
                className="w-full"
              />
            </div>
          </div>
        </div>
        
        <div className="flex justify-center gap-3">
          <Button
            label={loading ? "Searching..." : "Search"}
            icon={loading ? "pi pi-spinner" : "pi pi-search"}
            onClick={handleSearch}
            disabled={loading || !searchQuery.trim()}
            className="px-6"
            loading={loading}
          />
          {hasSearched && (
            <Button
              label="Clear"
              icon="pi pi-times"
              onClick={() => {
                setSearchQuery('');
                setResults([]);
                setHasSearched(false);
                setTotalResults(0);
                setCurrentPage(0);
                setError(null);
              }}
              severity="secondary"
              className="px-6"
            />
          )}
        </div>
      </Card>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <ProgressSpinner />
          <span className="ml-3 text-gray-600">Searching...</span>
        </div>
      )}

      {/* Results */}
      {!loading && hasSearched && (
        <div>
          {/* Search Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-blue-800">Search Query: "{searchQuery}"</h3>
                <div className="flex items-center gap-4 mt-1 text-xs text-blue-600">
                  {selectedRole !== null && (
                    <span>Role: {characterRoleOptions.find(opt => opt.value === selectedRole)?.label}</span>
                  )}
                </div>
              </div>
              <Button
                label="Modify Search"
                icon="pi pi-pencil"
                size="small"
                severity="secondary"
                onClick={() => {
                  setResults([]);
                  setHasSearched(false);
                  setTotalResults(0);
                  setCurrentPage(0);
                }}
              />
            </div>
          </div>
          
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-800">
                Search Results
              </h2>
              <p className="text-sm text-gray-600">
                Showing {currentPage * pageSize + 1}-{Math.min((currentPage + 1) * pageSize, totalResults)} of approximately {totalResults} results
              </p>
            </div>
            {totalResults > pageSize && (
              <Paginator
                first={currentPage * pageSize}
                rows={pageSize}
                totalRecords={totalResults}
                onPageChange={handlePageChange}
                className="border-0"
                template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
              />
            )}
          </div>

          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <i className="pi pi-search text-4xl mb-4 block"></i>
              <p>No results found for "{searchQuery}"</p>
              <p className="text-sm">Try adjusting your search terms or filters</p>
              <div className="mt-4">
                <Button
                  label="Try Different Search"
                  icon="pi pi-refresh"
                  onClick={() => {
                    setSearchQuery('');
                    setResults([]);
                    setHasSearched(false);
                    setTotalResults(0);
                    setCurrentPage(0);
                    setError(null);
                  }}
                  severity="secondary"
                  size="small"
                />
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((character) => (
                <Card key={character.id} className="hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {formatCharacterRole(character.role)}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-800 mb-2 overflow-hidden">
                    {character.name}
                  </h3>
                  
                  {character.summary && (
                    <p className="text-sm text-gray-700 mb-3 overflow-hidden">
                      {truncateText(character.summary)}
                    </p>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center">
                      <i className="pi pi-comment text-blue-500 mr-1"></i>
                      <span>{character.comments}</span>
                    </div>
                    <div className="flex items-center">
                      <i className="pi pi-heart text-red-500 mr-1"></i>
                      <span>{character.collects}</span>
                    </div>
                  </div>
                  
                  {character.infobox && (
                    <div className="mt-3">
                      <details className="text-xs">
                        <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                          Show infobox details
                        </summary>
                        <div className="mt-2 p-2 bg-gray-50 rounded text-gray-700 whitespace-pre-wrap">
                          {truncateText(character.infobox, 200)}
                        </div>
                      </details>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Initial State */}
      {!loading && !hasSearched && (
        <div className="text-center py-12 text-gray-500">
          <i className="pi pi-user text-6xl mb-4 block"></i>
          <h2 className="text-xl font-semibold mb-2">Start Your Character Search</h2>
          <p>Enter a search query above to find characters in the Bangumi archive</p>
        </div>
      )}
    </div>
  );
};
