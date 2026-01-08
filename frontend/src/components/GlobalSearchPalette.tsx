import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, User, ArrowRightLeft, Loader2 } from 'lucide-react';
import { searchService, SearchResult } from '@/services/searchService';

interface GlobalSearchPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function GlobalSearchPalette({ isOpen, onClose }: GlobalSearchPaletteProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const buscar = async () => {
      if (query.length < 2) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const data = await searchService.buscar(query);
        const allResults = [...data.pacientes, ...data.interconsultas];
        setResults(allResults);
        setSelectedIndex(0);
      } catch (error) {
        console.error('Error en búsqueda:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(buscar, 300);
    return () => clearTimeout(debounce);
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      handleSelect(results[selectedIndex]);
    }
  };

  const handleSelect = (result: SearchResult) => {
    navigate(result.url);
    onClose();
    setQuery('');
  };

  const getIcon = (iconName: string) => {
    if (iconName === 'user') return <User size={18} />;
    if (iconName === 'arrow-right-left') return <ArrowRightLeft size={18} />;
    return <Search size={18} />;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black bg-opacity-50">
      <div className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-lg shadow-2xl">
        <div className="flex items-center border-b border-gray-200 dark:border-gray-700 p-4">
          <Search className="text-gray-400 mr-3" size={20} />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Buscar pacientes, interconsultas..."
            className="flex-1 bg-transparent outline-none text-gray-900 dark:text-gray-100 placeholder-gray-400"
          />
          {loading && <Loader2 className="animate-spin text-gray-400 mr-2" size={18} />}
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            aria-label="Cerrar búsqueda"
          >
            <X size={18} className="text-gray-400" />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto">
          {results.length === 0 && query.length >= 2 && !loading && (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              No se encontraron resultados
            </div>
          )}
          
          {results.length === 0 && query.length < 2 && (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              Escribe al menos 2 caracteres para buscar
            </div>
          )}

          {results.map((result, index) => (
            <button
              key={result.id}
              onClick={() => handleSelect(result)}
              className={`w-full flex items-center p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                index === selectedIndex ? 'bg-gray-50 dark:bg-gray-700' : ''
              }`}
            >
              <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-primary-100 dark:bg-primary-900/30 rounded-lg mr-3">
                {getIcon(result.icono)}
              </div>
              <div className="flex-1 text-left">
                <div className="font-medium text-gray-900 dark:text-gray-100">{result.titulo}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{result.subtitulo}</div>
              </div>
              <div className="text-xs text-gray-400 dark:text-gray-500 uppercase">
                {result.tipo}
              </div>
            </button>
          ))}
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900 text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
          <div className="flex gap-4">
            <span><kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded">↑↓</kbd> Navegar</span>
            <span><kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded">Enter</kbd> Seleccionar</span>
            <span><kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded">Esc</kbd> Cerrar</span>
          </div>
          <div>
            <span>Atajos: <kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded">g d</kbd> Dashboard, <kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded">g i</kbd> Interconsultas</span>
          </div>
        </div>
      </div>
    </div>
  );
}