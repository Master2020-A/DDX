import React, { useState, useEffect } from 'react';
import { Brain, Zap, DollarSign, CheckCircle } from 'lucide-react';
import api from '@/services/api';

interface LLMProvider {
  name: string;
  available: boolean;
  models: string[];
}

interface LLMSelectorProps {
  selectedProvider?: string;
  selectedModel?: string;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string) => void;
}

const LLMSelector: React.FC<LLMSelectorProps> = ({
  selectedProvider = 'openai',
  selectedModel = 'gpt-4',
  onProviderChange,
  onModelChange,
}) => {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');

  useEffect(() => {
    loadProviders();
  }, []);

  useEffect(() => {
    if (selectedProvider) {
      loadModels(selectedProvider);
    }
  }, [selectedProvider]);

  const getDefaultProviders = (): LLMProvider[] => [
    { name: 'OpenAI', available: true, models: ['gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo'] },
    { name: 'Anthropic (Claude)', available: true, models: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'] },
    { name: 'Google (Gemini)', available: true, models: ['gemini-pro', 'gemini-1.5-pro'] },
    { name: 'Cohere', available: true, models: ['command', 'command-light'] },
    { name: 'Groq', available: true, models: ['llama-3.1-70b-versatile', 'mixtral-8x7b-32768'] },
  ];

  const getDefaultModels = (provider: string): string[] => {
    const defaults: { [key: string]: string[] } = {
      'openai': ['gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo'],
      'anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
      'google': ['gemini-pro', 'gemini-1.5-pro'],
      'cohere': ['command', 'command-light'],
      'groq': ['llama-3.1-70b-versatile', 'mixtral-8x7b-32768'],
    };
    return defaults[provider] || [];
  };

  const loadProviders = async () => {
    try {
      const response = await api.get('/llm/providers');
      setProviders(response.data);
    } catch (error) {
      console.error('Error loading providers:', error);
      // Usar proveedores por defecto si falla la carga
      setProviders(getDefaultProviders());
    }
  };

  const loadModels = async (provider: string) => {
    try {
      const response = await api.get(`/llm/providers/${provider}/models`);
      setModels(response.data);
    } catch (error) {
      console.error('Error loading models:', error);
      // Usar modelos por defecto si falla la carga
      setModels(getDefaultModels(provider));
    }
  };

  const testConnection = async () => {
    setTestingConnection(true);
    setConnectionStatus('idle');

    try {
      const response = await api.post('/llm/test-connection', {
        provider: selectedProvider,
        model: selectedModel,
        prompt: 'Hola, ¿cómo estás?'
      });

      if (response.data.success) {
        setConnectionStatus('success');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      console.error('Error testing connection:', error);
      setConnectionStatus('error');
    } finally {
      setTestingConnection(false);
    }
  };

  const getProviderIcon = (providerName: string) => {
    const icons: { [key: string]: string } = {
      'OpenAI': '🤖',
      'Anthropic (Claude)': '🧠',
      'Google (Gemini)': '✨',
      'Cohere': '🔮',
    };
    return icons[providerName] || '🤖';
  };

  const getModelInfo = (model: string) => {
    const info: { [key: string]: { speed: string; cost: string; quality: string } } = {
      'gpt-4': { speed: 'Medio', cost: '$$$$', quality: 'Excelente' },
      'gpt-4-turbo': { speed: 'Rápido', cost: '$$$', quality: 'Excelente' },
      'gpt-4o': { speed: 'Muy Rápido', cost: '$$', quality: 'Excelente' },
      'gpt-3.5-turbo': { speed: 'Muy Rápido', cost: '$', quality: 'Buena' },
      'claude-3-opus-20240229': { speed: 'Medio', cost: '$$$$', quality: 'Excelente' },
      'claude-3-sonnet-20240229': { speed: 'Rápido', cost: '$$$', quality: 'Muy Buena' },
      'claude-3-haiku-20240307': { speed: 'Muy Rápido', cost: '$', quality: 'Buena' },
      'gemini-pro': { speed: 'Rápido', cost: 'Gratis', quality: 'Buena' },
      'command': { speed: 'Rápido', cost: 'Gratis', quality: 'Buena' },
    };
    return info[model] || { speed: 'N/A', cost: 'N/A', quality: 'N/A' };
  };

  return (
    <div className="space-y-4">
      {/* Provider Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Proveedor de IA
        </label>
        <div className="grid grid-cols-2 gap-2">
          {providers.map((provider) => (
            <button
              key={provider.name}
              onClick={() => {
                if (provider.available) {
                  onProviderChange(provider.name.toLowerCase().split(' ')[0]);
                }
              }}
              disabled={!provider.available}
              className={`p-3 rounded-lg border-2 transition-all ${
                selectedProvider === provider.name.toLowerCase().split(' ')[0]
                  ? 'border-blue-600 bg-blue-50'
                  : provider.available
                  ? 'border-gray-300 hover:border-blue-400'
                  : 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-2xl">{getProviderIcon(provider.name)}</span>
                <div className="text-left flex-1">
                  <p className="font-medium text-sm">{provider.name}</p>
                  <p className="text-xs text-gray-500">
                    {provider.available ? `${provider.models.length} modelos` : 'No disponible'}
                  </p>
                </div>
                {provider.available && selectedProvider === provider.name.toLowerCase().split(' ')[0] && (
                  <CheckCircle size={16} className="text-blue-600" />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Model Selection */}
      {models.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Modelo
          </label>
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>

          {/* Model Info */}
          {selectedModel && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <div className="flex items-center gap-1 text-gray-600 mb-1">
                    <Zap size={12} />
                    <span>Velocidad</span>
                  </div>
                  <p className="font-medium">{getModelInfo(selectedModel).speed}</p>
                </div>
                <div>
                  <div className="flex items-center gap-1 text-gray-600 mb-1">
                    <DollarSign size={12} />
                    <span>Costo</span>
                  </div>
                  <p className="font-medium">{getModelInfo(selectedModel).cost}</p>
                </div>
                <div>
                  <div className="flex items-center gap-1 text-gray-600 mb-1">
                    <Brain size={12} />
                    <span>Calidad</span>
                  </div>
                  <p className="font-medium">{getModelInfo(selectedModel).quality}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Test Connection */}
      <div>
        <button
          onClick={testConnection}
          disabled={testingConnection || !selectedProvider || !selectedModel}
          className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {testingConnection ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700"></div>
              <span>Probando conexión...</span>
            </>
          ) : (
            <>
              <Zap size={16} />
              <span>Probar Conexión</span>
            </>
          )}
        </button>

        {connectionStatus === 'success' && (
          <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-800 flex items-center gap-2">
              <CheckCircle size={16} />
              Conexión exitosa
            </p>
          </div>
        )}

        {connectionStatus === 'error' && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-800">
              Error al conectar. Verifica tu API key en la configuración.
            </p>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-xs text-blue-800">
          💡 <strong>Tip:</strong> Configura tus API keys en el archivo .env del backend para usar estos proveedores.
        </p>
      </div>
    </div>
  );
};

export default LLMSelector;
