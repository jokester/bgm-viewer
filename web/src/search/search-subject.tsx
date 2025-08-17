import { useState, useEffect, useCallback } from 'react';
import { Subject, SubjectType, SubjectsIndexQuery, SubjectSearchResult } from '../data/api';
import { useBgmApi } from '../data';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Checkbox } from 'primereact/checkbox';
import { Card } from 'primereact/card';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Paginator } from 'primereact/paginator';

export const SearchSubject = () => {
  const api = useBgmApi();
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedType, setSelectedType] = useState<number | null>(null);
  const [nsfwFilter, setNsfwFilter] = useState<boolean | null>(null);
  const [results, setResults] = useState<Subject[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(0);
  const [totalResults, setTotalResults] = useState<number>(0);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  const pageSize = 20;

  const subjectTypeOptions = [
    { label: '所有类型', value: null },
    { label: '动画', value: SubjectType.ANIME },
    { label: '漫画', value: SubjectType.COMIC },
    { label: '游戏', value: SubjectType.GAME },
    { label: '音乐', value: SubjectType.MUSIC },
    { label: '三次元', value: SubjectType.REAL },
  ];

  const nsfwOptions = [
    { label: '所有内容', value: null },
    { label: '仅安全内容', value: false },
    { label: '仅NSFW内容', value: true },
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
      setError('请输入搜索查询');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentPage(page);

    try {
      const searchParams: SubjectsIndexQuery = {
        query: searchQuery.trim(),
        limit: pageSize,
        offset: page * pageSize,
        subject_type: selectedType || undefined,
        nsfw: nsfwFilter !== null ? nsfwFilter : undefined,
      };

      const searchResults = await api.searchSubjects(searchParams);
      setResults(searchResults.subjects);
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

  const formatSubjectType = (type: number): string => {
    switch (type) {
      case SubjectType.ANIME: return '动画';
      case SubjectType.COMIC: return '漫画';
      case SubjectType.GAME: return '游戏';
      case SubjectType.MUSIC: return '音乐';
      case SubjectType.REAL: return '三次元';
      default: return '未知';
    }
  };

  const truncateText = (text: string, maxLength: number = 150): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">搜索作品</h1>
      
      {/* Search Form */}
      <Card className="mb-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">搜索条件</h2>
          <p className="text-sm text-gray-600 mb-3">
            搜索作品名称、简介和标签。输入至少2个字符开始搜索。
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="lg:col-span-2">
            <label htmlFor="searchQuery" className="block text-sm font-medium text-gray-700 mb-2">
              搜索查询
            </label>
            <div className="relative">
              <InputText
                id="searchQuery"
                value={searchQuery}
                onChange={(e) => handleQueryChange(e.target.value)}
                onKeyUp={handleKeyPress}
                placeholder="按名称、简介、标签搜索..."
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
            <label htmlFor="subjectType" className="block text-sm font-medium text-gray-700 mb-2">
              作品类型
            </label>
            <Dropdown
              id="subjectType"
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.value);
                handleFilterChange();
              }}
              options={subjectTypeOptions}
              optionLabel="label"
              optionValue="value"
              placeholder="选择类型"
              className="w-full"
            />
          </div>
          
          <div>
            <label htmlFor="nsfwFilter" className="block text-sm font-medium text-gray-700 mb-2">
              内容筛选
            </label>
            <Dropdown
              id="nsfwFilter"
              value={nsfwFilter}
              onChange={(e) => {
                setNsfwFilter(e.value);
                handleFilterChange();
              }}
              options={nsfwOptions}
              optionLabel="label"
              optionValue="value"
              placeholder="选择筛选"
              className="w-full"
            />
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
                <h3 className="text-sm font-medium text-blue-800">搜索查询: "{searchQuery}"</h3>
                <div className="flex items-center gap-4 mt-1 text-xs text-blue-600">
                  {selectedType !== null && (
                    <span>类型: {subjectTypeOptions.find(opt => opt.value === selectedType)?.label}</span>
                  )}
                  {nsfwFilter !== null && (
                    <span>内容: {nsfwFilter ? '仅NSFW内容' : '仅安全内容'}</span>
                  )}
                </div>
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
              <p>未找到 "{searchQuery}" 的结果</p>
              <p className="text-sm">请尝试调整搜索词或筛选条件</p>
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
              {results.map((subject) => (
                <Card key={subject.id} className="hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {formatSubjectType(subject.type)}
                    </span>
                    {subject.nsfw && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        NSFW
                      </span>
                    )}
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
                    {subject.name}
                  </h3>
                  
                  {subject.name_cn && subject.name_cn !== subject.name && (
                    <p className="text-sm text-gray-600 mb-2">{subject.name_cn}</p>
                  )}
                  
                  {subject.summary && (
                    <p className="text-sm text-gray-700 mb-3 line-clamp-3">
                      {truncateText(subject.summary)}
                    </p>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center">
                      <i className="pi pi-star text-yellow-500 mr-1"></i>
                      <span>{subject.score.toFixed(1)}</span>
                    </div>
                    <div className="flex items-center">
                      <i className="pi pi-heart text-red-500 mr-1"></i>
                      <span>{subject.favorite.done + subject.favorite.doing}</span>
                    </div>
                  </div>
                  
                  {subject.tags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {subject.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {tag.name}
                        </span>
                      ))}
                      {subject.tags.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{subject.tags.length - 3} 更多
                        </span>
                      )}
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
          <i className="pi pi-search text-6xl mb-4 block"></i>
          <h2 className="text-xl font-semibold mb-2">开始搜索</h2>
          <p>在上方输入搜索查询以在Bangumi档案中查找作品</p>
        </div>
      )}
    </div>
  );
};