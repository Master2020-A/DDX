import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Square } from 'lucide-react';

const EndNode = ({ data }: any) => {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-gradient-to-r from-red-500 to-red-600 border-2 border-red-700 min-w-[150px]">
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-red-700" />
      <div className="flex items-center gap-2">
        <Square className="text-white" size={20} />
        <div className="text-white font-semibold">Fin</div>
      </div>
    </div>
  );
};

export default EndNode;
