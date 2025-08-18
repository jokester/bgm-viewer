import { GraphBuilder } from './graph-builder';
import { Subject, Character, Person, GraphEdgeSimple, Subgraph } from './api';
import { List as IList, Map as IMap, Set as ISet } from 'immutable';

describe('GraphBuilder', () => {
  let emptyBuilder: GraphBuilder;
  let sampleBuilder: GraphBuilder;

  beforeEach(() => {
    // Create an empty builder
    emptyBuilder = new GraphBuilder(
      IMap<number, Subject>(),
      IMap<number, Character>(),
      IMap<number, Person>(),
      ISet<number>(),
      ISet<number>(),
      ISet<number>(),
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

    // Create a builder with some initial data
    const subject1: Subject = { id: 1, name: 'Test Subject 1', type: 'anime' } as Subject;
    const character1: Character = { id: 101, name: 'Test Character 1' } as Character;
    const person1: Person = { id: 201, name: 'Test Person 1' } as Person;

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
      const subject2: Subject = { id: 2, name: 'Test Subject 2', type: 'manga' } as Subject;
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
      const character2: Character = { id: 102, name: 'Test Character 2' } as Character;
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
      const person2: Person = { id: 202, name: 'Test Person 2' } as Person;
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
      const subject1Updated: Subject = { id: 1, name: 'Updated Subject 1', type: 'anime' } as Subject;
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

      // Should keep the original subject, not the updated one
      expect(result.subjects.get(1)?.name).toBe('Test Subject 1');
    });

    it('should add center entity IDs to expanded sets', () => {
      const subject2: Subject = { id: 2, name: 'Test Subject 2', type: 'manga' } as Subject;
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

      expect(result.expandedSubjectIds.has(2)).toBe(true);
      expect(result.expandedSubjectIds.size).toBe(1);
    });

    it('should handle engagement edges (scp)', () => {
      const engagementEdge: GraphEdgeSimple = {
        subject1_id: 1,
        character_id: 101,
        person_id: 201,
        engagement_summary: 'Test engagement',
      };

      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges: [engagementEdge],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      expect(result.engagements.size).toBe(1);
      expect(result.engagements.get(0)).toEqual(engagementEdge);
      
      // Check that it's indexed in all three edge collections
      expect(result.seEdges.get(1)?.size).toBe(1);
      expect(result.ceEdges.get(101)?.size).toBe(1);
      expect(result.peEdges.get(201)?.size).toBe(1);
    });

    it('should handle subject-subject edges (directed)', () => {
      const s2sEdge: GraphEdgeSimple = {
        subject1_id: 1,
        subject2_id: 2,
        s2s_relation_type: 'sequel',
      };

      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges: [s2sEdge],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      // Should only be in ssEdges from source to target
      expect(result.ssEdges.get(1)?.get(2)?.size).toBe(1);
      expect(result.ssEdges.get(1)?.get(2)?.get(0)).toEqual(s2sEdge);
      
      // Should NOT be in the reverse direction
      expect(result.ssEdges.get(2)).toBeUndefined();
    });

    it('should handle subject-character edges (undirected)', () => {
      const scEdge: GraphEdgeSimple = {
        subject1_id: 1,
        character_id: 101,
        sc_type: 'main',
      };

      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges: [scEdge],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      // Should be in both directions
      expect(result.scEdges.get(1)?.get(101)?.size).toBe(1);
      expect(result.csEdges.get(101)?.get(1)?.size).toBe(1);
      
      // Both should reference the same edge object
      expect(result.scEdges.get(1)?.get(101)?.get(0)).toBe(scEdge);
      expect(result.csEdges.get(101)?.get(1)?.get(0)).toBe(scEdge);
    });

    it('should handle subject-person edges (undirected)', () => {
      const spEdge: GraphEdgeSimple = {
        subject1_id: 1,
        person_id: 201,
        sp_position: 'director',
      };

      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges: [spEdge],
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      // Should be in both directions
      expect(result.spEdges.get(1)?.get(201)?.size).toBe(1);
      expect(result.psEdges.get(201)?.get(1)?.size).toBe(1);
      
      // Both should reference the same edge object
      expect(result.spEdges.get(1)?.get(201)?.get(0)).toBe(spEdge);
      expect(result.psEdges.get(201)?.get(1)?.get(0)).toBe(spEdge);
    });

    it('should handle multiple edges of different types', () => {
      const edges: GraphEdgeSimple[] = [
        // Engagement edge
        { subject1_id: 1, character_id: 101, person_id: 201, engagement_summary: 'Engagement 1' },
        // Subject-subject edge
        { subject1_id: 1, subject2_id: 2, s2s_relation_type: 'sequel' },
        // Subject-character edge
        { subject1_id: 1, character_id: 102, sc_type: 'main' },
        // Subject-person edge
        { subject1_id: 1, person_id: 202, sp_position: 'director' },
      ];

      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges,
      };

      const result = emptyBuilder.mergeSubgraph(subgraph);

      // Check engagement
      expect(result.engagements.size).toBe(1);
      expect(result.seEdges.get(1)?.size).toBe(1);
      expect(result.ceEdges.get(101)?.size).toBe(1);
      expect(result.peEdges.get(201)?.size).toBe(1);

      // Check subject-subject
      expect(result.ssEdges.get(1)?.get(2)?.size).toBe(1);

      // Check subject-character (both directions)
      expect(result.scEdges.get(1)?.get(102)?.size).toBe(1);
      expect(result.csEdges.get(102)?.get(1)?.size).toBe(1);

      // Check subject-person (both directions)
      expect(result.spEdges.get(1)?.get(202)?.size).toBe(1);
      expect(result.psEdges.get(202)?.get(1)?.size).toBe(1);
    });

    it('should handle edges with existing data in collections', () => {
      // Add some existing edges to the sample builder
      const existingEdge: GraphEdgeSimple = {
        subject1_id: 1,
        character_id: 101,
        sc_type: 'main',
      };

      const builderWithEdges = new GraphBuilder(
        sampleBuilder.subjects,
        sampleBuilder.characters,
        sampleBuilder.persons,
        sampleBuilder.expandedSubjectIds,
        sampleBuilder.expandedCharacterIds,
        sampleBuilder.expandedPersonIds,
        sampleBuilder.engagements,
        IMap([[1, IList([existingEdge])]]),
        IMap([[101, IList([existingEdge])]]),
        IMap<number, IList<GraphEdgeSimple>>(),
        IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
        IMap([[1, IMap([[101, IList([existingEdge])]])]]),
        IMap([[101, IMap([[1, IList([existingEdge])]])]]),
        IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
        IMap<number, IMap<number, IList<GraphEdgeSimple>>>(),
      );

      const newEdge: GraphEdgeSimple = {
        subject1_id: 1,
        character_id: 102,
        sc_type: 'supporting',
      };

      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges: [newEdge],
      };

      const result = builderWithEdges.mergeSubgraph(subgraph);

      // Should have both old and new edges
      expect(result.scEdges.get(1)?.get(101)?.size).toBe(1);
      expect(result.scEdges.get(1)?.get(102)?.size).toBe(1);
      expect(result.csEdges.get(101)?.get(1)?.size).toBe(1);
      expect(result.csEdges.get(102)?.get(1)?.size).toBe(1);
    });

    it('should return a new GraphBuilder instance', () => {
      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges: [],
      };

      const result = sampleBuilder.mergeSubgraph(subgraph);

      expect(result).not.toBe(sampleBuilder);
      expect(result).toBeInstanceOf(GraphBuilder);
    });

    it('should preserve existing data when merging empty subgraph', () => {
      const subgraph: Subgraph = {
        center_subject: null,
        center_character: null,
        center_person: null,
        subjects: [],
        characters: [],
        persons: [],
        edges: [],
      };

      const result = sampleBuilder.mergeSubgraph(subgraph);

      expect(result.subjects.size).toBe(1);
      expect(result.characters.size).toBe(1);
      expect(result.persons.size).toBe(1);
      expect(result.expandedSubjectIds.has(1)).toBe(true);
      expect(result.expandedCharacterIds.has(101)).toBe(true);
      expect(result.expandedPersonIds.has(201)).toBe(true);
    });
  });
});
