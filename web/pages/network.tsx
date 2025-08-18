import { useState, useRef } from 'react';
import { Layout } from './_layout';
import { PageProps } from './_shared';
import { SearchSubject } from '../src/search/search-subject';
import { SearchCharacter } from '../src/search/search-character';
import { SearchPerson } from '../src/search/search-person';
import { NetworkGraph, NetworkGraphHandle } from '../src/network-graph';
import { Subject, Character, Person, Subgraph } from '../src/data/api';
import { Dropdown } from 'primereact/dropdown';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { useBgmApi } from '../src/data';

type SearchType = 'subject' | 'character' | 'person';

export function NetworkPage(props: PageProps) {
  const [selectedSearchType, setSelectedSearchType] = useState<SearchType>('subject');
  const [graphKey, setGraphKey] = useState<number>(0);
  const networkGraphRef = useRef<NetworkGraphHandle>(null!);
  const bgmApi = useBgmApi()
  const apiInFlight = useRef(false);

  const searchTypeOptions = [
    { label: '作品 (Subject)', value: 'subject' },
    { label: '角色 (Character)', value: 'character' },
    { label: '人物 (Person)', value: 'person' },
  ];

  const handleSubjectClick = async (subject: Subject) => {
    console.log('Subject clicked:', subject);
    
    try {
      // Call API to expand subject and get related entities
      const subgraph = await bgmApi.getSubjectEdges(subject.id);
      
      // Add the expanded subgraph to the network graph
      if (networkGraphRef.current) {
        networkGraphRef.current.addSubgraph(subgraph);
      }
    } catch (error) {
      console.error('Failed to expand subject:', error);
    }
  };

  const handleCharacterClick = async (character: Character) => {
    console.log('Character clicked:', character);
    
    try {
      // Call API to expand character and get related entities
      const subgraph = await bgmApi.getCharacterEdges(character.id);
      
      // Add the expanded subgraph to the network graph
      if (networkGraphRef.current) {
        networkGraphRef.current.addSubgraph(subgraph);
      }
    } catch (error) {
      console.error('Failed to expand character:', error);
    }
  };

  const handlePersonClick = async (person: Person) => {
    console.log('Person clicked:', person);
    
    try {
      // Call API to expand person and get related entities
      const subgraph = await bgmApi.getPersonEdges(person.id);
      
      // Add the expanded subgraph to the network graph
      if (networkGraphRef.current) {
        networkGraphRef.current.addSubgraph(subgraph);
      }
    } catch (error) {
      console.error('Failed to expand person:', error);
    }
  };

  const clearGraph = () => {
    // Force a re-render of the NetworkGraph component by changing the key
    setGraphKey(prev => prev + 1);
  };

  const renderSearchComponent = () => {
    switch (selectedSearchType) {
      case 'subject':
        return <SearchSubject onResultClick={handleSubjectClick} />;
      case 'character':
        return <SearchCharacter onResultClick={handleCharacterClick} />;
      case 'person':
        return <SearchPerson onResultClick={handlePersonClick} />;
      default:
        return null;
    }
  };

  return (
    <Layout path={props.path}>
      <div className="flex h-screen bg-gray-50">
        {/* Left Sidebar */}
        <div className="w-96 bg-white border-r border-gray-200 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <h1 className="text-xl font-semibold text-gray-800 mb-3">网络图构建器</h1>
            <p className="text-sm text-gray-600 mb-4">
              搜索并添加作品、角色和人物到网络图中，探索它们之间的关系
            </p>
            
            {/* Search Type Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                搜索类型
              </label>
              <Dropdown
                value={selectedSearchType}
                onChange={(e) => setSelectedSearchType(e.value)}
                options={searchTypeOptions}
                optionLabel="label"
                optionValue="value"
                placeholder="选择搜索类型"
                className="w-full"
              />
            </div>

            {/* Graph Controls */}
            <div className="flex gap-2">
              <Button
                label="清空图表"
                icon="pi pi-trash"
                severity="secondary"
                size="small"
                onClick={clearGraph}
                className="flex-1"
              />
              <Button
                label="导出"
                icon="pi pi-download"
                size="small"
                className="flex-1"
                disabled
                tooltip="功能开发中"
              />
            </div>
          </div>

          {/* Search Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-4">
              {renderSearchComponent()}
            </div>
          </div>
        </div>

        {/* Main Content - Network Graph */}
        <div className="flex-1 flex flex-col">
          {/* Graph Header */}
          <div className="p-4 border-b border-gray-200 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-800">网络关系图</h2>
                <p className="text-sm text-gray-600">
                  点击节点查看详情，使用右侧控制面板调整布局
                </p>
              </div>
              <div className="text-sm text-gray-500">
                <span className="inline-flex items-center px-2 py-1 rounded-full bg-blue-100 text-blue-800 mr-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-1"></span>
                  作品
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-full bg-orange-100 text-orange-800 mr-2">
                  <span className="w-2 h-2 bg-orange-500 rounded-full mr-1"></span>
                  角色
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-full bg-green-100 text-green-800">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                  人物
                </span>
              </div>
            </div>
          </div>

          {/* Graph Canvas */}
          <div className="flex-1 p-4">
            <Card className="h-full">
              <NetworkGraph
                key={graphKey} // Force re-render when clearing the graph
                ref={networkGraphRef}
                graphBuilder={undefined} // Pass undefined as graphBuilder state is removed
                onSubjectClick={handleSubjectClick}
                onCharacterClick={handleCharacterClick}
                onPersonClick={handlePersonClick}
              />
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
}
