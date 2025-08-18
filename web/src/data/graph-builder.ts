import { Character, GraphEdgeSimple, Person, Subgraph, Subject } from './api';
import { List as IList, Map as IMap, Set as ISet } from 'immutable';

/**
 * A data-only graph builder.
 * Keeps "known" vertices and edges.
 * And can be expanded by taking in a new subgraph.
 * The fields are immutable. Merging with a new subgraph will return a new GraphBuilder.
 * To save memory, updating of its state should try to reuse objects.
 */
export class GraphBuilder {
  static empty() {
    return new GraphBuilder(
      // subjects
      IMap(),
      // characters
      IMap(),
      // persons
      IMap(),
      // expanded subject ids
      ISet(),
      // expanded character ids
      ISet(),
      // expanded person ids
      ISet(),
      // engagements
      IList(),
      // subject_id -> engagement edges
      IMap(),
      // character_id -> engagement edges
      IMap(),
      // character_id -> engagement edges
      IMap(),
      // person_id -> engagement edges
      IMap(),
      // subject_id -> subject_id -> edges
      IMap(),
      // subject_id -> character_id -> edges
      IMap(),
      // character_id -> subject_id -> edges
      IMap(),
      // person_id -> subject_id -> edges
      IMap(),
    );
  }
  constructor(
    // vertex objects
    readonly subjects: IMap<number, Subject>,
    readonly characters: IMap<number, Character>,
    readonly persons: IMap<number, Person>,
    // expanded entity ids
    readonly expandedSubjectIds: ISet<number>,
    readonly expandedCharacterIds: ISet<number>,
    readonly expandedPersonIds: ISet<number>,
    // hyperedges connecting 3 vertices each
    readonly engagements: IList<GraphEdgeSimple>,
    // subject_id -> engagement edges
    readonly seEdges: IMap<number, IList<GraphEdgeSimple>>,
    readonly ceEdges: IMap<number, IList<GraphEdgeSimple>>,
    readonly peEdges: IMap<number, IList<GraphEdgeSimple>>,
    // binary edges
    // subject_id -> subject_id -> edges
    readonly ssEdges: IMap<number, IMap<number, IList<GraphEdgeSimple>>>,
    // subject_id -> character_id -> edges
    readonly scEdges: IMap<number, IMap<number, IList<GraphEdgeSimple>>>,
    // character_id -> subject_id -> edges
    readonly csEdges: IMap<number, IMap<number, IList<GraphEdgeSimple>>>,
    // subject_id -> person_id -> edges
    readonly spEdges: IMap<number, IMap<number, IList<GraphEdgeSimple>>>,
    // person_id -> subject_id -> edges
    readonly psEdges: IMap<number, IMap<number, IList<GraphEdgeSimple>>>,
  ) {
  }

  mergeSubgraph(subgraph: Subgraph) {
    let {
      subjects,
      characters,
      persons,
      expandedSubjectIds,
      expandedCharacterIds,
      expandedPersonIds,
      engagements,
      seEdges,
      ceEdges,
      peEdges,
      ssEdges,
      scEdges,
      csEdges,
      spEdges,
      psEdges,
    } = this;

    // Merge subjects
    subjects = subjects.withMutations(map => {
      for (const subject of subgraph.subjects) {
        if (!map.has(subject.id)) map.set(subject.id, subject);
      }
    });

    // Merge characters
    characters = characters.withMutations(map => {
      for (const character of subgraph.characters) {
        if (!map.has(character.id)) map.set(character.id, character);
      }
    });

    // Merge persons
    persons = persons.withMutations(map => {
      for (const person of subgraph.persons) {
        if (!map.has(person.id)) map.set(person.id, person);
      }
    });

    // Merge expanded subject IDs
    if (subgraph.center_subject) {
      expandedSubjectIds = expandedSubjectIds.add(subgraph.center_subject.id);
    }

    // Merge expanded character IDs
    if (subgraph.center_character) {
      expandedCharacterIds = expandedCharacterIds.add(subgraph.center_character.id);
    }

    // Merge expanded person IDs
    if (subgraph.center_person) {
      expandedPersonIds = expandedPersonIds.add(subgraph.center_person.id);
    }

    // Process edges from subgraph and merge them into existing collections
    for (const edge of subgraph.edges) {
      // Handle engagement edges (edges with all three entity types)
      if (edge.subject1_id && edge.character_id && edge.person_id) {
        engagements = engagements.push(edge);

        // Add to seEdges
        const existingSeEdges = seEdges.get(edge.subject1_id) || IList<GraphEdgeSimple>();
        seEdges = seEdges.set(edge.subject1_id, existingSeEdges.push(edge));

        // Add to ceEdges
        const existingCeEdges = ceEdges.get(edge.character_id) || IList<GraphEdgeSimple>();
        ceEdges = ceEdges.set(edge.character_id, existingCeEdges.push(edge));

        // Add to peEdges
        const existingPeEdges = peEdges.get(edge.person_id) || IList<GraphEdgeSimple>();
        peEdges = peEdges.set(edge.person_id, existingPeEdges.push(edge));
      } // Handle subject-subject edges (directed)
      else if (edge.subject1_id && edge.subject2_id) {
        const existingTargetMap = ssEdges.get(edge.subject1_id) || IMap<number, IList<GraphEdgeSimple>>();
        const existingEdges = existingTargetMap.get(edge.subject2_id) || IList<GraphEdgeSimple>();
        const updatedTargetMap = existingTargetMap.set(edge.subject2_id, existingEdges.push(edge));
        ssEdges = ssEdges.set(edge.subject1_id, updatedTargetMap);
      } // Handle subject-character edges (undirected - update both directions)
      else if (edge.subject1_id && edge.character_id) {
        // Add to scEdges (subject -> character)
        const existingScTargetMap = scEdges.get(edge.subject1_id) || IMap<number, IList<GraphEdgeSimple>>();
        const existingScEdges = existingScTargetMap.get(edge.character_id) || IList<GraphEdgeSimple>();
        const updatedScTargetMap = existingScTargetMap.set(edge.character_id, existingScEdges.push(edge));
        scEdges = scEdges.set(edge.subject1_id, updatedScTargetMap);

        // Add to csEdges (character -> subject) - same edge, undirected
        const existingCsTargetMap = csEdges.get(edge.character_id) || IMap<number, IList<GraphEdgeSimple>>();
        const existingCsEdges = existingCsTargetMap.get(edge.subject1_id) || IList<GraphEdgeSimple>();
        const updatedCsTargetMap = existingCsTargetMap.set(edge.subject1_id, existingCsEdges.push(edge));
        csEdges = csEdges.set(edge.character_id, updatedCsTargetMap);
      } // Handle subject-person edges (undirected - update both directions)
      else if (edge.subject1_id && edge.person_id) {
        // Add to spEdges (subject -> person)
        const existingSpTargetMap = spEdges.get(edge.subject1_id) || IMap<number, IList<GraphEdgeSimple>>();
        const existingSpEdges = existingSpTargetMap.get(edge.person_id) || IList<GraphEdgeSimple>();
        const updatedSpTargetMap = existingSpTargetMap.set(edge.person_id, existingSpEdges.push(edge));
        spEdges = spEdges.set(edge.subject1_id, updatedSpTargetMap);

        // Add to psEdges (person -> subject) - same edge, undirected
        const existingPsTargetMap = psEdges.get(edge.person_id) || IMap<number, IList<GraphEdgeSimple>>();
        const existingPsEdges = existingPsTargetMap.get(edge.subject1_id) || IList<GraphEdgeSimple>();
        const updatedPsTargetMap = existingPsTargetMap.set(edge.subject1_id, existingPsEdges.push(edge));
        psEdges = psEdges.set(edge.person_id, updatedPsTargetMap);
      }
    }

    return new GraphBuilder(
      subjects,
      characters,
      persons,
      expandedSubjectIds,
      expandedCharacterIds,
      expandedPersonIds,
      engagements,
      seEdges,
      ceEdges,
      peEdges,
      ssEdges,
      scEdges,
      csEdges,
      spEdges,
      psEdges,
    );
  }
}
