import { Handle, Position } from '@xyflow/react';
import { Bot } from 'lucide-react';

const AgentNode = ({ data }: any) => {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-white border-2 border-blue-500 min-w-[180px]">
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-blue-500" />
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
          <Bot className="text-blue-600" size={18} />
        </div>
        <div className="font-semibold text-gray-800">{data.label || 'Agente IA'}</div>
      </div>
      {data.model && (
        <div className="text-xs text-gray-500 mt-1">
          Modelo: {data.model}
        </div>
      )}
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-blue-500" />
    </div>
  );
};

export default AgentNode;
