import React, { useState, useEffect } from 'react';
import { Node } from '@xyflow/react';
import { X, Settings, Bot, Zap, GitBranch, FileText, Globe, Database, Bell, Clock, Repeat, Workflow } from 'lucide-react';
import LLMSelector from './LLMSelector';

interface NodePropertiesPanelProps {
  selectedNode: Node | null;
  onClose: () => void;
  onUpdate: (nodeId: string, data: any) => void;
  onDelete?: (nodeId: string) => void;
}

const NodePropertiesPanel: React.FC<NodePropertiesPanelProps> = ({
  selectedNode,
  onClose,
  onUpdate,
  onDelete,
}) => {
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    if (selectedNode) {
      setFormData(selectedNode.data || {});
    }
  }, [selectedNode]);

  if (!selectedNode) {
    return (
      <div className="w-80 bg-gray-50 border-l border-gray-200 p-6 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <Settings className="mx-auto mb-2" size={48} />
          <p>Selecciona un nodo para configurar sus propiedades</p>
        </div>
      </div>
    );
  }

  const handleChange = (field: string, value: any) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    onUpdate(selectedNode.id, newData);
  };

  const renderAgentProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre del Agente
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: Agente de Diagnóstico"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Configuración de IA
        </label>
        <LLMSelector
          selectedProvider={formData.llmProvider || 'openai'}
          selectedModel={formData.llmModel || 'gpt-4'}
          onProviderChange={(provider) => handleChange('llmProvider', provider)}
          onModelChange={(model) => handleChange('llmModel', model)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Prompt del Sistema
        </label>
        <textarea
          value={formData.systemPrompt || ''}
          onChange={(e) => handleChange('systemPrompt', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Instrucciones para el agente..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Temperatura
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={formData.temperature || 0.7}
          onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="text-sm text-gray-600 text-center">{formData.temperature || 0.7}</div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Max Tokens
        </label>
        <input
          type="number"
          value={formData.maxTokens || 2000}
          onChange={(e) => handleChange('maxTokens', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </div>
  );

  const renderConditionProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre de la Condición
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: ¿Resultado positivo?"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Variable a Evaluar
        </label>
        <input
          type="text"
          value={formData.variable || ''}
          onChange={(e) => handleChange('variable', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: resultado.valor"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Operador
        </label>
        <select
          value={formData.operator || '=='}
          onChange={(e) => handleChange('operator', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="==">Igual a (==)</option>
          <option value="!=">Diferente de (!=)</option>
          <option value=">">Mayor que (&gt;)</option>
          <option value="<">Menor que (&lt;)</option>
          <option value=">=">Mayor o igual (≥)</option>
          <option value="<=">Menor o igual (≤)</option>
          <option value="contains">Contiene</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Valor de Comparación
        </label>
        <input
          type="text"
          value={formData.value || ''}
          onChange={(e) => handleChange('value', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Valor a comparar"
        />
      </div>
    </div>
  );

  const renderActionProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre de la Acción
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: Enviar notificación"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tipo de Acción
        </label>
        <select
          value={formData.actionType || 'custom'}
          onChange={(e) => handleChange('actionType', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="custom">Acción Personalizada</option>
          <option value="email">Enviar Email</option>
          <option value="notification">Enviar Notificación</option>
          <option value="database">Guardar en BD</option>
          <option value="api">Llamar API</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Configuración (JSON)
        </label>
        <textarea
          value={formData.config || '{}'}
          onChange={(e) => handleChange('config', e.target.value)}
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          placeholder='{"key": "value"}'
        />
      </div>
    </div>
  );

  const renderApiCallProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre del Endpoint
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: Obtener datos del paciente"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          URL
        </label>
        <input
          type="text"
          value={formData.url || ''}
          onChange={(e) => handleChange('url', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="https://api.example.com/endpoint"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Método HTTP
        </label>
        <select
          value={formData.method || 'GET'}
          onChange={(e) => handleChange('method', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
          <option value="PATCH">PATCH</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Headers (JSON)
        </label>
        <textarea
          value={formData.headers || '{}'}
          onChange={(e) => handleChange('headers', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          placeholder='{"Authorization": "Bearer token"}'
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Body (JSON)
        </label>
        <textarea
          value={formData.body || '{}'}
          onChange={(e) => handleChange('body', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          placeholder='{"key": "value"}'
        />
      </div>
    </div>
  );

  const renderFormProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre del Formulario
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: Datos del Paciente"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Campos del Formulario (JSON)
        </label>
        <textarea
          value={formData.fields || '[]'}
          onChange={(e) => handleChange('fields', e.target.value)}
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          placeholder={`[
  {
    "name": "nombre",
    "label": "Nombre",
    "type": "text",
    "required": true
  }
]`}
        />
      </div>
    </div>
  );

  const renderLoopProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre del Loop
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: Procesar pacientes"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tipo de Loop
        </label>
        <select
          value={formData.loopType || 'for_each'}
          onChange={(e) => handleChange('loopType', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="for_each">For Each (Iterar sobre lista)</option>
          <option value="while">While (Mientras condición)</option>
          <option value="count">Count (N iteraciones)</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Variable de Iteración
        </label>
        <input
          type="text"
          value={formData.iterationVariable || ''}
          onChange={(e) => handleChange('iterationVariable', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: paciente, item, i"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Colección/Condición
        </label>
        <input
          type="text"
          value={formData.collection || ''}
          onChange={(e) => handleChange('collection', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: pacientes, count < 10"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Máximo de Iteraciones
        </label>
        <input
          type="number"
          value={formData.maxIterations || 100}
          onChange={(e) => handleChange('maxIterations', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="parallel"
          checked={formData.parallel || false}
          onChange={(e) => handleChange('parallel', e.target.checked)}
          className="mr-2"
        />
        <label htmlFor="parallel" className="text-sm text-gray-700">
          Ejecutar en paralelo
        </label>
      </div>
    </div>
  );

  const renderSubworkflowProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre del Subworkflow
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: Análisis de laboratorio"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Workflow a Ejecutar
        </label>
        <input
          type="text"
          value={formData.subworkflowId || ''}
          onChange={(e) => handleChange('subworkflowId', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="ID del workflow"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nombre del Workflow
        </label>
        <input
          type="text"
          value={formData.subworkflowName || ''}
          onChange={(e) => handleChange('subworkflowName', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Nombre descriptivo"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Variables de Entrada (JSON)
        </label>
        <textarea
          value={formData.inputMapping || '{}'}
          onChange={(e) => handleChange('inputMapping', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          placeholder='{"pacienteId": "{{context.pacienteId}}"}'
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Variables de Salida (JSON)
        </label>
        <textarea
          value={formData.outputMapping || '{}'}
          onChange={(e) => handleChange('outputMapping', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          placeholder='{"resultado": "{{output.resultado}}"}'
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="waitForCompletion"
          checked={formData.waitForCompletion !== false}
          onChange={(e) => handleChange('waitForCompletion', e.target.checked)}
          className="mr-2"
        />
        <label htmlFor="waitForCompletion" className="text-sm text-gray-700">
          Esperar a que termine
        </label>
      </div>
    </div>
  );

  const renderDefaultProperties = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Etiqueta
        </label>
        <input
          type="text"
          value={formData.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Nombre del nodo"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Descripción
        </label>
        <textarea
          value={formData.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Descripción del nodo..."
        />
      </div>
    </div>
  );

  const renderPropertiesForm = () => {
    switch (selectedNode.type) {
      case 'agent':
        return renderAgentProperties();
      case 'condition':
        return renderConditionProperties();
      case 'action':
        return renderActionProperties();
      case 'api_call':
        return renderApiCallProperties();
      case 'form':
        return renderFormProperties();
      case 'loop':
        return renderLoopProperties();
      case 'subworkflow':
        return renderSubworkflowProperties();
      default:
        return renderDefaultProperties();
    }
  };

  const getNodeIcon = () => {
    const icons: Record<string, any> = {
      agent: Bot,
      condition: GitBranch,
      action: Zap,
      form: FileText,
      api_call: Globe,
      database: Database,
      notification: Bell,
      delay: Clock,
      loop: Repeat,
      subworkflow: Workflow,
    };
    return icons[selectedNode.type || 'action'] || Settings;
  };

  const Icon = getNodeIcon();

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon size={20} className="text-blue-600" />
          <h3 className="font-semibold text-gray-900">Propiedades</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
        >
          <X size={20} className="text-gray-500" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="text-xs font-medium text-blue-900 mb-1">Tipo de Nodo</div>
          <div className="text-sm text-blue-700 capitalize">{selectedNode.type}</div>
        </div>

        {renderPropertiesForm()}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-3">
        <div className="text-xs text-gray-500">
          ID: <span className="font-mono">{selectedNode.id}</span>
        </div>
        {onDelete && (
          <button
            onClick={() => {
              if (window.confirm('¿Estás seguro de que deseas eliminar este nodo?')) {
                onDelete(selectedNode.id);
              }
            }}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors font-medium text-sm flex items-center justify-center gap-2"
          >
            <X size={16} />
            Eliminar Nodo
          </button>
        )}
        <div className="text-xs text-gray-400 text-center">
          Presiona Delete o Backspace para eliminar
        </div>
      </div>
    </div>
  );
};

export default NodePropertiesPanel;
