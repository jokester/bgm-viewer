import { GraphBuilder } from "./graph-builder";
import Graph from "graphology";
import { Character, Subject, Person, GraphEdgeSimple } from "./api";

export function buildSigmaGraph(graphBuilder: GraphBuilder): Graph {
  const graph = new Graph();
  
  // Add subject nodes
  graphBuilder.subjects.forEach((subject, id) => {
    graph.addNode(`subject_${id}`, {
      x: Math.random() * 1000,
      y: Math.random() * 1000,
      size: 20,
      label: subject.name,
      color: "#4A90E2",
      type: "subject",
      data: subject,
      expanded: graphBuilder.expandedSubjectIds.has(id)
    });
  });

  // Add character nodes
  graphBuilder.characters.forEach((character, id) => {
    graph.addNode(`character_${id}`, {
      x: Math.random() * 1000,
      y: Math.random() * 1000,
      size: 15,
      label: character.name,
      color: "#F5A623",
      type: "character",
      data: character,
      expanded: graphBuilder.expandedCharacterIds.has(id)
    });
  });

  // Add person nodes
  graphBuilder.persons.forEach((person, id) => {
    graph.addNode(`person_${id}`, {
      x: Math.random() * 1000,
      y: Math.random() * 1000,
      size: 18,
      label: person.name,
      color: "#7ED321",
      type: "person",
      data: person,
      expanded: graphBuilder.expandedPersonIds.has(id)
    });
  });

  // Add engagement edges (hypergraph edges connecting 3 entities)
  graphBuilder.engagements.forEach((edge, index) => {
    if (edge.subject1_id && edge.character_id && edge.person_id) {
      const edgeKey = `engagement_${index}`;
      graph.addEdgeWithKey(edgeKey, `subject_${edge.subject1_id}`, `character_${edge.character_id}`, {
        type: "engagement",
        label: edge.engagement_summary || "Engagement",
        color: "#9B59B6",
        size: 3,
        data: edge
      });
      
      // Add edge from character to person
      graph.addEdgeWithKey(`${edgeKey}_cp`, `character_${edge.character_id}`, `person_${edge.person_id}`, {
        type: "engagement",
        label: edge.engagement_summary || "Engagement",
        color: "#9B59B6",
        size: 3,
        data: edge
      });
      
      // Add edge from person to subject
      graph.addEdgeWithKey(`${edgeKey}_ps`, `person_${edge.person_id}`, `subject_${edge.subject1_id}`, {
        type: "engagement",
        label: edge.engagement_summary || "Engagement",
        color: "#9B59B6",
        size: 3,
        data: edge
      });
    }
  });

  // Add subject-subject edges
  graphBuilder.ssEdges.forEach((targetMap, sourceId) => {
    targetMap.forEach((edges, targetId) => {
      edges.forEach((edge, edgeIndex) => {
        const edgeKey = `ss_${sourceId}_${targetId}_${edgeIndex}`;
        graph.addEdgeWithKey(edgeKey, `subject_${sourceId}`, `subject_${targetId}`, {
          type: "subject_subject",
          label: edge.s2s_relation_type ? String(edge.s2s_relation_type) : "Related",
          color: "#E74C3C",
          size: 2,
          data: edge
        });
      });
    });
  });

  // Add subject-character edges
  graphBuilder.scEdges.forEach((targetMap, sourceId) => {
    targetMap.forEach((edges, targetId) => {
      edges.forEach((edge, edgeIndex) => {
        const edgeKey = `sc_${sourceId}_${targetId}_${edgeIndex}`;
        graph.addEdgeWithKey(edgeKey, `subject_${sourceId}`, `character_${targetId}`, {
          type: "subject_character",
          label: edge.sc_type ? String(edge.sc_type) : "Features",
          color: "#3498DB",
          size: 2,
          data: edge
        });
      });
    });
  });

  // Add subject-person edges
  graphBuilder.spEdges.forEach((targetMap, sourceId) => {
    targetMap.forEach((edges, targetId) => {
      edges.forEach((edge, edgeIndex) => {
        const edgeKey = `sp_${sourceId}_${targetId}_${edgeIndex}`;
        graph.addEdgeWithKey(edgeKey, `subject_${sourceId}`, `person_${targetId}`, {
          type: "subject_person",
          label: edge.sp_position ? String(edge.sp_position) : "Staff",
          color: "#2ECC71",
          size: 2,
          data: edge
        });
      });
    });
  });

  return graph;
}

export function getNodeType(nodeId: string): "subject" | "character" | "person" | null {
  if (nodeId.startsWith("subject_")) return "subject";
  if (nodeId.startsWith("character_")) return "character";
  if (nodeId.startsWith("person_")) return "person";
  return null;
}

export function getNodeId(nodeId: string): number | null {
  const match = nodeId.match(/^(\w+)_(\d+)$/);
  return match && match[2] ? parseInt(match[2]) : null;
}