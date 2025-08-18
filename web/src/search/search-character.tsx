import { useState, useEffect, useCallback } from 'react';
import { Character, CharactersIndexQuery, CharacterSearchResult } from '../data/api';
import { useBgmApi } from '../data';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Card } from 'primereact/card';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Paginator } from 'primereact/paginator';

export const SearchCharacter = () => {
  const api = useBgmApi();
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [results, setResults] = useState<Character[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(0);
  const [totalResults, setTotalResults] = useState<number>(0);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  const pageSize = 20;

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
      setError('请输入搜索关键词');
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
      };

      const searchResults = await api.searchCharacters(searchParams);
      setResults(searchResults.items);
      setTotalResults(searchResults.total);
      
      setHasSearched(true);
    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : '搜索失败，请重试。');
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

  const truncateText = (text: string, maxLength: number = 150): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">角色搜索</h1>
      
      {/* Search Form */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">搜索条件</h2>
        <p className="text-sm text-gray-600 mb-3">
          搜索角色名称、简介和资料框信息。输入至少2个字符开始搜索。
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <label htmlFor="searchQuery" className="block text-sm font-medium text-gray-700 mb-2">
              搜索关键词
            </label>
            <div className="relative">
              <InputText
                id="searchQuery"
                value={searchQuery}
                onChange={(e) => handleQueryChange(e.target.value)}
                onKeyUp={handleKeyPress}
                placeholder="按角色名称、简介、资料框搜索..."
                className="w-full"
              />
              {loading && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <i className="pi pi-spinner text-gray-400 text-sm"></i>
                </div>
              )}
              {searchQuery.trim().length >= 2 && !loading && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <i className="pi pi-clock text-gray-400 text-sm"></i>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex justify-center gap-3">
          <Button
            label={loading ? "搜索中..." : "搜索"}
            icon={loading ? "pi pi-spinner" : "pi pi-search"}
            onClick={handleSearch}
            disabled={loading || !searchQuery.trim()}
            className="px-6"
            loading={loading}
          />
          {hasSearched && (
            <Button
              label="清除"
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
      </div>

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
          <span className="ml-3 text-gray-600">搜索中...</span>
        </div>
      )}

      {/* Results */}
      {!loading && hasSearched && (
        <div>
          {/* Search Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-blue-800">搜索关键词: "{searchQuery}"</h3>
              </div>
              <Button
                label="修改搜索"
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
                搜索结果
              </h2>
              <p className="text-sm text-gray-600">
                显示第 {currentPage * pageSize + 1}-{Math.min((currentPage + 1) * pageSize, totalResults)} 条，共约 {totalResults} 条结果
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
              <p>未找到 "{searchQuery}" 的相关结果</p>
              <p className="text-sm">请尝试调整搜索关键词或筛选条件</p>
              <div className="mt-4">
                <Button
                  label="尝试其他搜索"
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
                <Card key={character.id} className="character-card">
                  <div className="flex items-center mb-3">
                    <div className="w-16 h-16 rounded-full mr-3 bg-gray-200 flex items-center justify-center">
                      <i className="pi pi-user text-2xl text-gray-400"></i>
                    </div>
                    <h3 className="text-lg font-bold text-gray-800">{character.name}</h3>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{character.summary}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                    <span>评论: {character.comments}</span>
                    <span>收藏: {character.collects}</span>
                  </div>
                  {character.infobox && (
                    <details className="text-xs">
                      <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                        显示详细资料
                      </summary>
                      <div className="mt-2 p-2 bg-gray-50 rounded text-gray-700 whitespace-pre-wrap">
                        {truncateText(character.infobox, 200)}
                      </div>
                    </details>
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
          <h2 className="text-xl font-semibold mb-2">开始角色搜索</h2>
          <p>在上方输入搜索关键词，在Bangumi档案中查找角色</p>
        </div>
      )}
    </div>
  );
};
