import React, { useCallback, useState } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
  NodeSelectionChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Bot, Play, Square, GitBranch, Zap, FileText, Globe, Database, Bell, Clock, Repeat, Workflow, Users } from 'lucide-react';
import CollaborationPanel from './CollaborationPanel';

// Tipos de nodos personalizados
import StartNode from './nodes/StartNode';
import EndNode from './nodes/EndNode';
import AgentNode from './nodes/AgentNode';
import ConditionNode from './nodes/ConditionNode';
import ActionNode from './nodes/ActionNode';
import LoopNode from './nodes/LoopNode';
import SubworkflowNode from './nodes/SubworkflowNode';
import NodePropertiesPanel from './NodePropertiesPanel';

const nodeTypes = {
  start: StartNode,
  end: EndNode,
  agent: AgentNode,
  condition: ConditionNode,
  action: ActionNode,
  loop: LoopNode,
  subworkflow: SubworkflowNode,
};

interface WorkflowBuilderProps {
  workflowId?: string;
  initialNodes?: Node[];
  initialEdges?: Edge[];
  onSave?: (nodes: Node[], edges: Edge[]) => void;
}

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  workflowId,
  initialNodes = [],
  initialEdges = [],
  onSave,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [showCollaboration, setShowCollaboration] = useState(false);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (!type) return;

      const position = {
        x: event.clientX,
        y: event.clientY,
      };

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: { label: `${type} node` },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleSave = () => {
    if (onSave) {
      onSave(nodes, edges);
    }
  };

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const handleCloseProperties = () => {
    setSelectedNode(null);
  };

  const handleUpdateNodeData = (nodeId: string, data: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return { ...node, data: { ...node.data, ...data } };
        }
        return node;
      })
    );
  };

  const handleDeleteNode = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
    setSelectedNode(null);
  }, [setNodes, setEdges]);

  // Eliminar nodo con tecla Delete o Backspace
  const onKeyDown = useCallback((event: KeyboardEvent) => {
    if ((event.key === 'Delete' || event.key === 'Backspace') && selectedNode) {
      event.preventDefault();
      handleDeleteNode(selectedNode.id);
    }
  }, [selectedNode, handleDeleteNode]);

  React.useEffect(() => {
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [onKeyDown]);

  const nodeTypesList = [
    { type: 'start', label: 'Inicio', icon: Play, color: '#10b981' },
    { type: 'end', label: 'Fin', icon: Square, color: '#ef4444' },
    { type: 'agent', label: 'Agente IA', icon: Bot, color: '#3b82f6' },
    { type: 'condition', label: 'Condición', icon: GitBranch, color: '#f59e0b' },
    { type: 'action', label: 'Acción', icon: Zap, color: '#8b5cf6' },
    { type: 'loop', label: 'Loop', icon: Repeat, color: '#9333ea' },
    { type: 'subworkflow', label: 'Subworkflow', icon: Workflow, color: '#0891b2' },
    { type: 'form', label: 'Formulario', icon: FileText, color: '#06b6d4' },
    { type: 'api_call', label: 'API Call', icon: Globe, color: '#ec4899' },
    { type: 'database', label: 'Base de Datos', icon: Database, color: '#14b8a6' },
    { type: 'notification', label: 'Notificación', icon: Bell, color: '#f97316' },
    { type: 'delay', label: 'Espera', icon: Clock, color: '#6366f1' },
  ];

  return (
    <div className="flex h-screen">
      {/* Sidebar con tipos de nodos */}
      <div className="w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">Componentes</h3>
        
        <div className="space-y-2">
          {nodeTypesList.map((nodeType) => {
            const Icon = nodeType.icon;
            return (
              <div
                key={nodeType.type}
                className="flex items-center gap-3 p-3 rounded-lg border-2 border-gray-200 cursor-move hover:border-blue-400 hover:bg-blue-50 transition-colors"
                draggable
                onDragStart={(e) => onDragStart(e, nodeType.type)}
              >
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: nodeType.color + '20' }}
                >
                  <Icon size={20} style={{ color: nodeType.color }} />
                </div>
                <span className="font-medium text-sm">{nodeType.label}</span>
              </div>
            );
          })}
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200 space-y-2">
          <button
            onClick={handleSave}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Guardar Workflow
          </button>
          
          <button
            onClick={() => setShowCollaboration(true)}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center justify-center gap-2"
          >
            <Users size={20} />
            Colaborar en Tiempo Real
          </button>
        </div>
      </div>

      {/* Canvas de React Flow */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>

      {/* Panel de Propiedades */}
      <NodePropertiesPanel
        selectedNode={selectedNode}
        onClose={handleCloseProperties}
        onUpdate={handleUpdateNodeData}
        onDelete={handleDeleteNode}
      />

      {/* Panel de Colaboración */}
      {showCollaboration && workflowId && (
        <CollaborationPanel
          workflowId={workflowId}
          onClose={() => setShowCollaboration(false)}
        />
      )}
    </div>
  );
};

export default WorkflowBuilder;
