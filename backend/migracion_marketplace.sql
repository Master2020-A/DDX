-- ============================================================
-- MIGRACION DEL MARKETPLACE DE TEMPLATES
-- ============================================================

-- 1. Crear tabla workflow_templates_marketplace
CREATE TABLE IF NOT EXISTS workflow_templates_marketplace (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Informacion basica
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tags TEXT[],
    
    -- Autor
    author_id UUID NOT NULL REFERENCES usuarios(id),
    author_name VARCHAR(200),
    organization VARCHAR(200),
    
    -- Contenido del template
    workflow_data JSONB NOT NULL,
    thumbnail_url VARCHAR(500),
    screenshots TEXT[],
    
    -- Version y compatibilidad
    version VARCHAR(20) DEFAULT '1.0.0',
    min_system_version VARCHAR(20),
    dependencies JSONB DEFAULT '{}'::jsonb,
    
    -- Metricas de uso
    downloads_count INTEGER DEFAULT 0,
    installs_count INTEGER DEFAULT 0,
    rating_average FLOAT DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    
    -- Estado y moderacion
    status VARCHAR(20) DEFAULT 'draft',
    is_featured BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_free BOOLEAN DEFAULT TRUE,
    price FLOAT DEFAULT 0.0,
    
    -- Documentacion
    readme TEXT,
    changelog TEXT,
    usage_instructions TEXT,
    
    -- Metadatos
    created_at VARCHAR(50) DEFAULT NOW()::TEXT,
    updated_at VARCHAR(50) DEFAULT NOW()::TEXT,
    published_at VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_templates_name ON workflow_templates_marketplace(name);
CREATE INDEX IF NOT EXISTS idx_templates_category ON workflow_templates_marketplace(category);
CREATE INDEX IF NOT EXISTS idx_templates_author ON workflow_templates_marketplace(author_id);
CREATE INDEX IF NOT EXISTS idx_templates_status ON workflow_templates_marketplace(status);

-- 2. Crear tabla template_reviews
CREATE TABLE IF NOT EXISTS template_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES workflow_templates_marketplace(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    
    -- Calificacion
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    comment TEXT,
    
    -- Utilidad
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    
    -- Estado
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_moderated BOOLEAN DEFAULT FALSE,
    
    -- Metadatos
    created_at VARCHAR(50) DEFAULT NOW()::TEXT,
    updated_at VARCHAR(50) DEFAULT NOW()::TEXT
);

CREATE INDEX IF NOT EXISTS idx_reviews_template ON template_reviews(template_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON template_reviews(user_id);

-- 3. Crear tabla template_installations
CREATE TABLE IF NOT EXISTS template_installations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES workflow_templates_marketplace(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    workflow_id UUID REFERENCES workflows(id),
    
    -- Informacion de instalacion
    installed_version VARCHAR(20),
    customizations JSONB DEFAULT '{}'::jsonb,
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at VARCHAR(50),
    
    -- Metadatos
    installed_at VARCHAR(50) DEFAULT NOW()::TEXT
);

CREATE INDEX IF NOT EXISTS idx_installations_template ON template_installations(template_id);
CREATE INDEX IF NOT EXISTS idx_installations_user ON template_installations(user_id);
CREATE INDEX IF NOT EXISTS idx_installations_workflow ON template_installations(workflow_id);

-- 4. Crear tabla template_categories
CREATE TABLE IF NOT EXISTS template_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    
    -- Orden y visibilidad
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Contador
    templates_count INTEGER DEFAULT 0,
    
    -- Metadatos
    created_at VARCHAR(50) DEFAULT NOW()::TEXT
);

CREATE INDEX IF NOT EXISTS idx_categories_slug ON template_categories(slug);

-- 5. Crear tabla template_collections
CREATE TABLE IF NOT EXISTS template_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    slug VARCHAR(200) UNIQUE,
    
    -- Curador
    curator_id UUID REFERENCES usuarios(id),
    curator_name VARCHAR(200),
    
    -- Contenido
    template_ids UUID[],
    cover_image_url VARCHAR(500),
    
    -- Estado
    is_featured BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- Metricas
    views_count INTEGER DEFAULT 0,
    
    -- Metadatos
    created_at VARCHAR(50) DEFAULT NOW()::TEXT,
    updated_at VARCHAR(50) DEFAULT NOW()::TEXT
);

CREATE INDEX IF NOT EXISTS idx_collections_slug ON template_collections(slug);
CREATE INDEX IF NOT EXISTS idx_collections_curator ON template_collections(curator_id);

-- 6. Insertar categorias iniciales
INSERT INTO template_categories (name, slug, description, icon, color, display_order) VALUES
('Diagnostico Medico', 'diagnostico-medico', 'Templates para diagnostico y analisis clinico', 'Stethoscope', '#3b82f6', 1),
('Administrativo', 'administrativo', 'Flujos administrativos y gestion', 'FileText', '#10b981', 2),
('Laboratorio', 'laboratorio', 'Procesamiento de resultados de laboratorio', 'TestTube', '#8b5cf6', 3),
('Imagenologia', 'imagenologia', 'Analisis de imagenes medicas', 'Image', '#f59e0b', 4),
('Atencion al Paciente', 'atencion-paciente', 'Flujos de atencion y seguimiento', 'Heart', '#ef4444', 5),
('Reportes', 'reportes', 'Generacion de reportes e informes', 'FileBarChart', '#06b6d4', 6)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================
-- MIGRACION COMPLETADA
-- ============================================================
