import React from 'react';
import { NetworkGraph } from './network-graph';
import { Character, Person, PersonType, Subject, SubjectType } from './data/api';

// Demo data
const demoSubject: Subject = {
  id: 1,
  type: SubjectType.ANIME,
  name: 'Demo Anime',
  name_cn: '演示动画',
  infobox: '',
  platform: 1,
  summary: 'A demo anime for testing',
  nsfw: false,
  tags: [],
  score: 8.5,
  score_details: null,
  rank: 100,
  date: '2024-01-01',
  favorite: {
    wish: 50,
    done: 200,
    doing: 30,
    dropped: 5,
    on_hold: 10,
  },
  series: false,
  meta_tags: null,
};

const demoCharacter: Character = {
  id: 101,
  name: 'Demo Character',
  infobox: '',
  summary: 'A demo character for testing',
  comments: 10,
  collects: 100,
};

const demoPerson: Person = {
  id: 201,
  name: 'Demo Person',
  type: PersonType.INDIVIDUAL,
  career: ['Director'],
  infobox: '',
  summary: 'A demo person for testing',
  comments: 15,
  collects: 200,
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
    <div className='w-full h-screen p-4'>
      <h1 className='text-2xl font-bold mb-4'>Network Graph Demo</h1>
      <p className='mb-4'>Click on nodes to see interactions. Use ForceAtlas2 controls to adjust layout.</p>

      <div className='w-full h-[600px] border border-gray-300 rounded-lg'>
        <NetworkGraph
          onSubjectClick={handleSubjectClick}
          onCharacterClick={handleCharacterClick}
          onPersonClick={handlePersonClick}
        />
      </div>

      <div className='mt-4 text-sm text-gray-600'>
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
