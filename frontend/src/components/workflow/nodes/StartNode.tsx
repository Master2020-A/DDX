import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Play } from 'lucide-react';

const StartNode = ({ data }: any) => {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-gradient-to-r from-green-500 to-green-600 border-2 border-green-700 min-w-[150px]">
      <div className="flex items-center gap-2">
        <Play className="text-white" size={20} />
        <div className="text-white font-semibold">Inicio</div>
      </div>
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-green-700" />
    </div>
  );
};

export default StartNode;
