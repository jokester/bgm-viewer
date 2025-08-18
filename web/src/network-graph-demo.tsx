import React from 'react';
import { NetworkGraph } from './network-graph';
import { Character, Subject, Person } from './data/api';

// Demo data
const demoSubject: Subject = {
  id: 1,
  type: 1, // ANIME
  name: "Demo Anime",
  name_cn: "演示动画",
  infobox: "",
  platform: 1,
  summary: "A demo anime for testing",
  nsfw: false,
  tags: [],
  score: 8.5,
  rank: 100,
  wish: 50,
  done: 200,
  doing: 30,
  dropped: 5,
  on_hold: 10,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z"
};

const demoCharacter: Character = {
  id: 101,
  name: "Demo Character",
  name_cn: "演示角色",
  infobox: "",
  summary: "A demo character for testing",
  nsfw: false,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z"
};

const demoPerson: Person = {
  id: 201,
  name: "Demo Person",
  name_cn: "演示人员",
  infobox: "",
  summary: "A demo person for testing",
  nsfw: false,
  type: 0, // INDIVIDUAL
  career: "Director",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z"
};

export const NetworkGraphDemo: React.FC = () => {
  const handleSubjectClick = (subject: Subject) => {
    console.log('Subject clicked:', subject);
    alert(`Subject clicked: ${subject.name}`);
  };

  const handleCharacterClick = (character: Character) => {
    console.log('Character clicked:', character);
    alert(`Character clicked: ${character.name}`);
  };

  const handlePersonClick = (person: Person) => {
    console.log('Person clicked:', person);
    alert(`Person clicked: ${person.name}`);
  };

  return (
    <div className="w-full h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">Network Graph Demo</h1>
      <p className="mb-4">Click on nodes to see interactions. Use ForceAtlas2 controls to adjust layout.</p>
      
      <div className="w-full h-[600px] border border-gray-300 rounded-lg">
        <NetworkGraph
          onSubjectClick={handleSubjectClick}
          onCharacterClick={handleCharacterClick}
          onPersonClick={handlePersonClick}
        />
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        <p>• Blue nodes: Subjects (Anime, Manga, etc.)</p>
        <p>• Orange nodes: Characters</p>
        <p>• Green nodes: People (Staff, Voice Actors, etc.)</p>
        <p>• Purple edges: Engagements (Character + Person + Subject)</p>
        <p>• Red edges: Subject relationships</p>
        <p>• Blue edges: Subject-Character relationships</p>
        <p>• Green edges: Subject-Person relationships</p>
      </div>
    </div>
  );
};
