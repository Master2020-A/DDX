import React, { useState, useEffect } from 'react';
import { Search, Star, Download, TrendingUp, Filter, Grid, List } from 'lucide-react';
import axios from 'axios';

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  author_name: string;
  thumbnail_url?: string;
  rating_average: number;
  rating_count: number;
  downloads_count: number;
  installs_count: number;
  is_featured: boolean;
  is_verified: boolean;
  is_free: boolean;
  price: number;
  version: string;
}

const Marketplace: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [featuredTemplates, setFeaturedTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [loading, setLoading] = useState(false);

  const categories = [
    { value: '', label: 'Todas las categorías' },
    { value: 'diagnostico-medico', label: 'Diagnóstico Médico' },
    { value: 'administrativo', label: 'Administrativo' },
    { value: 'laboratorio', label: 'Laboratorio' },
    { value: 'imagenologia', label: 'Imagenología' },
    { value: 'atencion-paciente', label: 'Atención al Paciente' },
    { value: 'reportes', label: 'Reportes' },
  ];

  useEffect(() => {
    loadFeaturedTemplates();
    searchTemplates();
  }, []);

  useEffect(() => {
    searchTemplates();
  }, [searchQuery, selectedCategory]);

  const loadFeaturedTemplates = async () => {
    try {
      const response = await axios.get('http://localhost:8612/api/marketplace/templates/featured');
      setFeaturedTemplates(response.data);
    } catch (error) {
      console.error('Error loading featured templates:', error);
    }
  };

  const searchTemplates = async () => {
    setLoading(true);
    try {
      const params: any = { page: 1, page_size: 20 };
      if (searchQuery) params.query = searchQuery;
      if (selectedCategory) params.category = selectedCategory;

      const response = await axios.get('http://localhost:8612/api/marketplace/templates', { params });
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Error searching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const installTemplate = async (templateId: string) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://localhost:8612/api/marketplace/templates/${templateId}/install`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Template instalado exitosamente');
    } catch (error) {
      console.error('Error installing template:', error);
      alert('Error al instalar el template');
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={16}
            className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
          />
        ))}
        <span className="text-sm text-gray-600 ml-1">({rating.toFixed(1)})</span>
      </div>
    );
  };

  const TemplateCard: React.FC<{ template: Template }> = ({ template }) => (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4">
      {template.thumbnail_url && (
        <img
          src={template.thumbnail_url}
          alt={template.name}
          className="w-full h-40 object-cover rounded-md mb-3"
        />
      )}
      
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-lg flex-1">{template.name}</h3>
        {template.is_verified && (
          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">✓ Verificado</span>
        )}
      </div>

      <p className="text-gray-600 text-sm mb-3 line-clamp-2">{template.description}</p>

      <div className="flex items-center gap-2 mb-3">
        {renderStars(template.rating_average)}
        <span className="text-xs text-gray-500">({template.rating_count} reseñas)</span>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
        <div className="flex items-center gap-1">
          <Download size={14} />
          <span>{template.downloads_count}</span>
        </div>
        <span className="text-xs bg-gray-100 px-2 py-1 rounded">{template.category}</span>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">por {template.author_name}</span>
        <button
          onClick={() => installTemplate(template.id)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm"
        >
          Instalar
        </button>
      </div>
    </div>
  );

  const TemplateListItem: React.FC<{ template: Template }> = ({ template }) => (
    <div className="bg-white rounded-lg shadow-md p-4 flex gap-4 hover:shadow-lg transition-shadow">
      {template.thumbnail_url && (
        <img
          src={template.thumbnail_url}
          alt={template.name}
          className="w-32 h-32 object-cover rounded-md"
        />
      )}
      
      <div className="flex-1">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-lg">{template.name}</h3>
          {template.is_verified && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">✓ Verificado</span>
          )}
        </div>

        <p className="text-gray-600 text-sm mb-2">{template.description}</p>

        <div className="flex items-center gap-4 mb-2">
          {renderStars(template.rating_average)}
          <span className="text-xs text-gray-500">({template.rating_count} reseñas)</span>
          <div className="flex items-center gap-1 text-sm text-gray-600">
            <Download size={14} />
            <span>{template.downloads_count} descargas</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs bg-gray-100 px-2 py-1 rounded">{template.category}</span>
            <span className="text-sm text-gray-600">por {template.author_name}</span>
          </div>
          <button
            onClick={() => installTemplate(template.id)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm"
          >
            Instalar
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Marketplace de Templates</h1>
          <p className="text-gray-600">Descubre y utiliza workflows predefinidos para tu práctica médica</p>
        </div>

        {/* Featured Templates */}
        {featuredTemplates.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="text-blue-600" size={24} />
              <h2 className="text-2xl font-semibold">Templates Destacados</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredTemplates.slice(0, 3).map((template) => (
                <TemplateCard key={template.id} template={template} />
              ))}
            </div>
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Buscar templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex items-center gap-2">
              <Filter size={20} className="text-gray-600" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>

              <div className="flex gap-2 ml-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                >
                  <Grid size={20} />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                >
                  <List size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Templates Grid/List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Cargando templates...</p>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
            {templates.map((template) =>
              viewMode === 'grid' ? (
                <TemplateCard key={template.id} template={template} />
              ) : (
                <TemplateListItem key={template.id} template={template} />
              )
            )}
          </div>
        )}

        {!loading && templates.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600">No se encontraron templates</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Marketplace;
