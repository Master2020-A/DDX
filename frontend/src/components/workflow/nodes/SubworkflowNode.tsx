import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { GitBranch } from 'lucide-react';

export default function SubworkflowNode({ data, selected }: NodeProps) {
  return (
    <div
      style={{
        padding: '12px 20px',
        borderRadius: '8px',
        border: selected ? '2px solid #0891b2' : '2px solid #06b6d4',
        background: 'linear-gradient(135deg, #ecfeff 0%, #cffafe 100%)',
        minWidth: '180px',
        boxShadow: selected ? '0 4px 12px rgba(8, 145, 178, 0.3)' : '0 2px 8px rgba(6, 182, 212, 0.2)',
      }}
    >
      <Handle type="target" position={Position.Left} />
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
        <GitBranch size={18} color="#0891b2" />
        <strong style={{ color: '#164e63', fontSize: '14px' }}>Subworkflow</strong>
      </div>
      
      <div style={{ fontSize: '12px', color: '#155e75' }}>
        {data.label || 'Workflow anidado'}
      </div>
      
      {data.subworkflowName && (
        <div style={{ fontSize: '11px', color: '#0e7490', marginTop: '4px' }}>
          {data.subworkflowName}
        </div>
      )}
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
