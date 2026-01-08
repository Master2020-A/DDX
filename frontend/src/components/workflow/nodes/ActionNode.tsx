import { Handle, Position } from '@xyflow/react';
import { Zap } from 'lucide-react';

const ActionNode = ({ data }: any) => {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-white border-2 border-purple-500 min-w-[180px]">
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-purple-500" />
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
          <Zap className="text-purple-600" size={18} />
        </div>
        <div className="font-semibold text-gray-800">{data.label || 'Acción'}</div>
      </div>
      {data.action_type && (
        <div className="text-xs text-gray-500 mt-1">
          {data.action_type}
        </div>
      )}
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-purple-500" />
    </div>
  );
};

export default ActionNode;
