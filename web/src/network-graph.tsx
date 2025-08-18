import { useState, useEffect, useCallback, useImperativeHandle, forwardRef } from 'react';
import { GraphBuilder } from './data/graph-builder';
import { Character, Subject, Person, Subgraph } from './data/api';
import { buildSigmaGraph, getNodeType, getNodeId } from './data/sigma_adapter';
import { SigmaContainer, useLoadGraph, useSigma } from '@react-sigma/core';
import { LayoutForceAtlas2Control } from '@react-sigma/layout-forceatlas2';
import '@react-sigma/core/lib/style.css';

interface NetworkGraphHandle {
    addSubgraph(subgraph: Subgraph): void
}

// Component that loads the graph into Sigma
const GraphLoader = ({ graphBuilder }: { graphBuilder: GraphBuilder }) => {
  const loadGraph = useLoadGraph();

  useEffect(() => {
    const graph = buildSigmaGraph(graphBuilder);
    loadGraph(graph);
  }, [graphBuilder, loadGraph]);

  return null;
};

// Component that handles node clicks
const NodeClickHandler = ({ 
  onCharacterClick, 
  onSubjectClick, 
  onPersonClick 
}: {
  onCharacterClick: (character: Character) => void;
  onSubjectClick: (subject: Subject) => void;
  onPersonClick: (person: Person) => void;
}) => {
  const sigma = useSigma();

  useEffect(() => {
    const handleClick = (event: any) => {
      const node = event.node;
      if (node) {
        const nodeType = getNodeType(node);
        const nodeId = getNodeId(node);
        
        if (nodeType && nodeId) {
          const nodeData = sigma.getGraph().getNodeAttributes(node);
          
          switch (nodeType) {
            case 'subject':
              if (nodeData.data) {
                onSubjectClick(nodeData.data as Subject);
              }
              break;
            case 'character':
              if (nodeData.data) {
                onCharacterClick(nodeData.data as Character);
              }
              break;
            case 'person':
              if (nodeData.data) {
                onPersonClick(nodeData.data as Person);
              }
              break;
          }
        }
      }
    };

    // Use the addListener method for Sigma.js events
    if (sigma && typeof sigma.addListener === 'function') {
      sigma.addListener('clickNode', handleClick);
      
      return () => {
        sigma.removeListener('clickNode', handleClick);
      };
    }
    
    return undefined;
  }, [sigma, onCharacterClick, onSubjectClick, onPersonClick]);

  return null;
};

export const NetworkGraph = forwardRef<NetworkGraphHandle, {
    onCharacterClick(character: Character): void
    onSubjectClick(subject: Subject): void
    onPersonClick(person: Person): void
    graphBuilder?: GraphBuilder
}>((props, ref) => {
    const [state, setState] = useState(() => props.graphBuilder || GraphBuilder.empty());

    // Update internal state when external graphBuilder changes
    useEffect(() => {
        if (props.graphBuilder) {
            setState(props.graphBuilder);
        }
    }, [props.graphBuilder]);

    const handleAddSubgraph = useCallback((subgraph: Subgraph) => {
        setState(prevState => prevState.mergeSubgraph(subgraph));
    }, []);

    // Expose the addSubgraph method via ref
    useImperativeHandle(ref, () => ({
        addSubgraph: handleAddSubgraph
    }), [handleAddSubgraph]);

    return (
        <div className="w-full h-full min-h-[600px]">
            <SigmaContainer 
                style={{ height: '100%', width: '100%' }}
                settings={{
                    nodeReducer: (node, data) => ({
                        ...data,
                        size: data.expanded ? data.size * 1.5 : data.size,
                        color: data.expanded ? '#FF6B6B' : data.color,
                        label: data.label,
                        borderColor: data.expanded ? '#FF0000' : undefined,
                        borderWidth: data.expanded ? 2 : 0
                    }),
                    edgeReducer: (edge, data) => ({
                        ...data,
                        size: data.size,
                        color: data.color,
                        label: data.label
                    })
                }}
            >
                <GraphLoader graphBuilder={state} />
                <NodeClickHandler 
                    onCharacterClick={props.onCharacterClick}
                    onSubjectClick={props.onSubjectClick}
                    onPersonClick={props.onPersonClick}
                />
                <LayoutForceAtlas2Control />
            </SigmaContainer>
        </div>
    );
});

// Export the handle interface for external use
export type { NetworkGraphHandle };