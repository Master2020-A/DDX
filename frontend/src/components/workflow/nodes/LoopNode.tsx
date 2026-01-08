import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Repeat } from 'lucide-react';

export default function LoopNode({ data, selected }: NodeProps) {
  return (
    <div
      style={{
        padding: '12px 20px',
        borderRadius: '8px',
        border: selected ? '2px solid #9333ea' : '2px solid #a855f7',
        background: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
        minWidth: '180px',
        boxShadow: selected ? '0 4px 12px rgba(147, 51, 234, 0.3)' : '0 2px 8px rgba(168, 85, 247, 0.2)',
      }}
    >
      <Handle type="target" position={Position.Left} />
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
        <Repeat size={18} color="#9333ea" />
        <strong style={{ color: '#581c87', fontSize: '14px' }}>Loop</strong>
      </div>
      
      <div style={{ fontSize: '12px', color: '#6b21a8' }}>
        {data.label || 'Iteración'}
      </div>
      
      {data.loopType && (
        <div style={{ fontSize: '11px', color: '#7e22ce', marginTop: '4px' }}>
          Tipo: {data.loopType}
        </div>
      )}
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
