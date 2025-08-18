import { GraphBuilder } from './graph-builder';
import {
  Character,
  GraphEdgeSimple,
  Person,
  PersonType,
  Subgraph,
  Subject,
  SubjectCharacterType,
  SubjectType,
} from './api';
import { List as IList, Map as IMap, Set as ISet } from 'immutable';

// Helper functions to create valid test data matching OpenAPI specification
function createTestSubject(id: number, name: string, type: SubjectType = SubjectType.ANIME): Subject {
  return {
    id,
    type,
    name,
    name_cn: `${name} (CN)`,
    infobox: `Infobox for ${name}`,
    platform: 1,
    summary: `Summary for ${name}`,
    nsfw: false,
    tags: [],
    score: 7.5,
    score_details: null,
    rank: 1000,
    date: '2023-01-01',
    favorite: {wish: 10, done: 50, doing: 20, on_hold: 5, dropped: 15},
    series: false,
    meta_tags: null,
  };
}

function createTestCharacter(id: number, name: string): Character {
  return {
    id,
    name,
    infobox: `Infobox for ${name}`,
    summary: `Summary for ${name}`,
    comments: 10,
    collects: 100,
  };
}

function createTestPerson(id: number, name: string, type: PersonType = PersonType.INDIVIDUAL): Person {
  return {
    id,
    name,
    type,
    career: ['Director'],
    infobox: `Infobox for ${name}`,
    summary: `Summary for ${name}`,
    comments: 15,
    collects: 200,
  };
}

function createTestGraphEdge(
  subject1_id: number | null = null,
  subject2_id: number | null = null,
  character_id: number | null = null,
  person_id: number | null = null,
  s2s_relation_type: number | null = null,
  sp_position: number | null = null,
  sc_type: SubjectCharacterType | null = null,
  sc_order_idx: number | null = null,
  engagement_summary: string | null = null,
): GraphEdgeSimple {
  return {
    subject1_id,
    subject2_id,
    character_id,
    person_id,
    s2s_relation_type: s2s_relation_type as any,
    sp_position: sp_position as any,
    sc_type,
    sc_order_idx,
    engagement_summary,
  };
}

describe('GraphBuilder', () => {
  let emptyBuilder: GraphBuilder;
  let sampleBuilder: GraphBuilder;

  beforeEach(() => {
    // Create an empty builder
    emptyBuilder = GraphBuilder.empty();

    // Create a builder with some initial data
    const subject1 = createTestSubject(1, 'Test Subject 1');
    const character1 = createTestCharacter(101, 'Test Character 1');
    const person1 = createTestPerson(201, 'Test Person 1');

    sampleBuilder = new GraphBuilder(
      IMap([[1, subject1]]),
      IMap([[101, character1]]),
      IMap([[201, person1]]),
      ISet([1]),
      ISet([101]),
      ISet([201]),
      IList<GraphEdgeSimple>(),
      IMap<number, IList<GraphEdgeSimple>>(),
      IMap<number, IList<GraphEdgeSimple>>(),
      IMap<number, IList<GraphEdgeSimple>>(),
      IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
      IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
      IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
      IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
      IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
    );
  });

  describe('mergeSubgraph', () => {
    it('should merge subjects from subgraph', () => {
      const subject2 = createTestSubject(2, 'Test Subject 2', SubjectType.COMIC);
      const subgraph: Subgraph = {
        center_subject: subject2,
        center_character: null,
        center_person: null,
        subjects: [subject2],
        characters: [],
        persons: [],
        edges: [],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      expect(result.subjects.get(2)).toEqual(subject2);
      expect(result.subjects.size).toBe(1);
    });

    it('should merge characters from subgraph', () => {
      const character2 = createTestCharacter(102, 'Test Character 2');
      const subgraph: Subgraph = {
        center_subject: null,
        center_character: character2,
        center_person: null,
        subjects: [],
        characters: [character2],
        persons: [],
        edges: [],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      expect(result.characters.get(102)).toEqual(character2);
      expect(result.characters.size).toBe(1);
    });

    it('should merge persons from subgraph', () => {
      const person2 = createTestPerson(202, 'Test Person 2');
      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: person2,
        subjects: [],
        characters: [],
        persons: [person2],
        edges: [],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      expect(result.persons.get(202)).toEqual(person2);
      expect(result.persons.size).toBe(1);
    });

    it('should not overwrite existing entities', () => {
      const subject1Updated = createTestSubject(1, 'Updated Subject 1');
      const subgraph: Subgraph = {
        center_subject: subject1Updated,
        center_character: null,
        center_person: null,
        subjects: [subject1Updated],
        characters: [],
        persons: [],
        edges: [],
      };

      const result = sampleBuilder.mergeSubgraph(subgraph);

      // Should not overwrite existing subject - should keep the original
      expect(result.subjects.get(1)).toEqual(sampleBuilder.subjects.get(1));
      expect(result.subjects.get(1)).not.toEqual(subject1Updated);
    });

    it('should merge edges from subgraph', () => {
      const subject2 = createTestSubject(2, 'Test Subject 2');
      const engagementEdge = createTestGraphEdge(
        1,
        null,
        101,
        201,
        null,
        null,
        null,
        null,
        'Engagement 1',
      );

      const subgraph: Subgraph = {
        center_subject: subject2,
        center_character: null,
        center_person: null,
        subjects: [subject2],
        characters: [],
        persons: [],
        edges: [engagementEdge],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      expect(result.engagements.size).toBe(1);
      expect(result.engagements.get(0)).toEqual(engagementEdge);
    });
  });

  describe('empty', () => {
    it('should create empty builder', () => {
      const builder = GraphBuilder.empty();

      expect(builder.subjects.size).toBe(0);
      expect(builder.characters.size).toBe(0);
      expect(builder.persons.size).toBe(0);
      expect(builder.engagements.size).toBe(0);
    });
  });
});
