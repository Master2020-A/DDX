import { Handle, Position } from '@xyflow/react';
import { GitBranch } from 'lucide-react';

const ConditionNode = ({ data }: any) => {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-white border-2 border-orange-500 min-w-[180px]">
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-orange-500" />
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center">
          <GitBranch className="text-orange-600" size={18} />
        </div>
        <div className="font-semibold text-gray-800">{data.label || 'Condición'}</div>
      </div>
      {data.condition && (
        <div className="text-xs text-gray-500 mt-1">
          {data.condition}
        </div>
      )}
      <Handle type="source" position={Position.Right} id="true" className="w-3 h-3 bg-green-500" style={{ top: '30%' }} />
      <Handle type="source" position={Position.Right} id="false" className="w-3 h-3 bg-red-500" style={{ top: '70%' }} />
    </div>
  );
};

export default ConditionNode;
