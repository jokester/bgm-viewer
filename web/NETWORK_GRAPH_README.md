# NetworkGraph Component

A React component for rendering interactive network graphs using React Sigma, designed to work with the Bangumi Archive GraphBuilder data structure.

## Features

- **Interactive Network Visualization**: Renders complex graph data with nodes and edges
- **Node Types**: Supports three main entity types:
  - **Subjects** (Anime, Manga, Games, etc.) - Blue nodes
  - **Characters** - Orange nodes  
  - **People** (Staff, Voice Actors, etc.) - Green nodes
- **Edge Types**: Multiple relationship types with different colors and labels
- **ForceAtlas2 Layout**: Automatic graph layout with interactive controls
- **Click Interactions**: Handle clicks on different node types
- **Responsive Design**: Full-width/height container with Tailwind CSS styling

## Installation

The component uses the following packages (already installed in this project):

```bash
@react-sigma/core
@react-sigma/layout-forceatlas2
graphology
sigma
```

## Usage

### Basic Usage

```tsx
import { NetworkGraph } from './network-graph';
import { Character, Subject, Person } from './data/api';

const MyComponent = () => {
  const handleSubjectClick = (subject: Subject) => {
    console.log('Subject clicked:', subject);
  };

  const handleCharacterClick = (character: Character) => {
    console.log('Character clicked:', character);
  };

  const handlePersonClick = (person: Person) => {
    console.log('Person clicked:', person);
  };

  return (
    <div className="w-full h-[600px]">
      <NetworkGraph
        onSubjectClick={handleSubjectClick}
        onCharacterClick={handleCharacterClick}
        onPersonClick={handlePersonClick}
      />
    </div>
  );
};
```

### Props

The `NetworkGraph` component accepts the following props:

- `onSubjectClick: (subject: Subject) => void` - Callback when a subject node is clicked
- `onCharacterClick: (character: Character) => void` - Callback when a character node is clicked  
- `onPersonClick: (person: Person) => void` - Callback when a person node is clicked

### Data Structure

The component works with the `GraphBuilder` class which manages:

- **Nodes**: Subjects, Characters, and People with their attributes
- **Edges**: Various relationship types between entities
- **State**: Expanded entity tracking and graph metadata

## Architecture

### Components

1. **NetworkGraph**: Main component that renders the Sigma container
2. **GraphLoader**: Loads graph data from GraphBuilder into Sigma
3. **NodeClickHandler**: Manages node click events and callbacks

### Data Flow

1. `GraphBuilder` manages the graph state (nodes, edges, metadata)
2. `buildSigmaGraph()` converts GraphBuilder data to a graphology Graph
3. Sigma renders the graph with React Sigma components
4. User interactions trigger callbacks through the click handlers

### Styling

- **Nodes**: Different colors and sizes based on type and expansion state
- **Edges**: Color-coded by relationship type with labels
- **Layout**: ForceAtlas2 algorithm with interactive controls
- **Responsive**: Full container dimensions with minimum height

## Customization

### Node Styling

Nodes are styled through the `nodeReducer` setting:

```tsx
settings={{
  nodeReducer: (node, data) => ({
    ...data,
    size: data.expanded ? data.size * 1.5 : data.size,
    color: data.expanded ? '#FF6B6B' : data.color,
    borderColor: data.expanded ? '#FF0000' : undefined,
    borderWidth: data.expanded ? 2 : 0
  })
}}
```

### Edge Styling

Edges are styled through the `edgeReducer` setting:

```tsx
settings={{
  edgeReducer: (edge, data) => ({
    ...data,
    size: data.size,
    color: data.color,
    label: data.label
  })
}}
```

## Event Handling

The component listens for `clickNode` events from Sigma.js and:

1. Extracts the clicked node ID
2. Determines the node type (subject/character/person)
3. Retrieves the node data from the graph
4. Calls the appropriate callback function

## Layout Controls

The `LayoutForceAtlas2Control` component provides:

- **Start/Stop**: Control the ForceAtlas2 layout algorithm
- **Settings**: Adjust layout parameters
- **Reset**: Return to initial positions

## Performance Considerations

- **Graph Updates**: The graph is rebuilt when GraphBuilder state changes
- **Event Handling**: Click handlers are properly cleaned up on unmount
- **Rendering**: Sigma.js handles efficient WebGL rendering for large graphs

## Troubleshooting

### Common Issues

1. **Container Height Error**: Ensure the container has explicit height/width
2. **Event Handling**: Check that click callbacks are properly defined
3. **Data Loading**: Verify GraphBuilder contains valid data

### Debug Tips

- Check browser console for Sigma.js errors
- Verify node/edge data in the GraphBuilder
- Test with simple demo data first

## Examples

See `network-graph-demo.tsx` for a complete working example with demo data and click handlers.

## Dependencies

- **React Sigma Core**: Main graph rendering components
- **ForceAtlas2 Layout**: Automatic graph layout algorithm
- **Graphology**: Graph data structure and algorithms
- **Sigma.js**: WebGL-based graph rendering engine
- **Tailwind CSS**: Utility-first CSS framework for styling
