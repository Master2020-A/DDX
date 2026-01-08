"""
Servicio de extracción automática de datos desde archivos (PDF/imágenes)
para Estudios Especiales: EKG, EEG, Ecografías

Utiliza OCR (Tesseract) para extraer texto de archivos y patrones regex
para identificar parámetros médicos.
"""
import re
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# OCR y procesamiento de imágenes
try:
    import pytesseract
    from PIL import Image
    import PyPDF2
    from pdf2image import convert_from_path
    OCR_DISPONIBLE = True
except ImportError:
    OCR_DISPONIBLE = False
    print("⚠️ Advertencia: pytesseract, Pillow, PyPDF2 o pdf2image no están instalados")


class ExtractorEstudiosEspeciales:
    """
    Extrae automáticamente datos de estudios especiales desde archivos PDF o imágenes
    """
    
    def __init__(self):
        if not OCR_DISPONIBLE:
            raise ImportError(
                "Las librerías de OCR no están instaladas. "
                "Ejecuta: pip install pytesseract Pillow PyPDF2 pdf2image"
            )
    
    # ==================== PATRONES REGEX ====================
    
    # Patrones para EKG
    PATRONES_EKG = {
        'frecuencia_cardiaca': [
            r'(?:FC|Frecuencia\s+Card[ií]aca|Heart\s+Rate)[:\s]*(\d+)\s*(?:lpm|bpm|lat)',
            r'(\d+)\s*(?:lpm|bpm)\s*(?:FC)?',
        ],
        'intervalo_pr': [
            r'(?:PR|Intervalo\s+PR)[:\s]*(\d+)\s*ms',
            r'PR[:\s]*(\d+)',
        ],
        'duracion_qrs': [
            r'(?:QRS|Duraci[oó]n\s+QRS)[:\s]*(\d+)\s*ms',
            r'QRS[:\s]*(\d+)',
        ],
        'intervalo_qt': [
            r'(?:QT|Intervalo\s+QT)[:\s]*(\d+)\s*ms',
            r'QT[:\s]*(\d+)',
        ],
        'intervalo_qtc': [
            r'(?:QTc|QT\s+corregido)[:\s]*(\d+)\s*ms',
            r'QTc[:\s]*(\d+)',
        ],
        'eje_qrs': [
            r'(?:Eje|Eje\s+QRS|Axis)[:\s]*([+-]?\d+)\s*[°º]?',
        ],
        'presion_arterial': [
            r'(?:PA|Presi[oó]n\s+Arterial|BP)[:\s]*(\d+/\d+)',
            r'(\d{2,3}/\d{2,3})\s*mmHg',
        ],
    }
    
    # Patrones para EEG
    PATRONES_EEG = {
        'duracion_minutos': [
            r'(?:Duraci[oó]n|Duration)[:\s]*(\d+)\s*(?:min|minutos)',
        ],
        'frecuencia_dominante': [
            r'(?:Frecuencia\s+dominante|Dominant\s+frequency)[:\s]*(\d+\.?\d*)\s*Hz',
        ],
    }
    
    # Patrones para Ecografías
    PATRONES_ECO = {
        'profundidad_cm': [
            r'(?:Profundidad|Depth)[:\s]*(\d+\.?\d*)\s*cm',
        ],
        'frecuencia_mhz': [
            r'(?:Frecuencia|Frequency)[:\s]*(\d+\.?\d*)\s*MHz',
        ],
    }
    
    # Palabras clave para detectar tipo de estudio
    PALABRAS_CLAVE = {
        'ekg': ['electrocardiograma', 'ekg', 'ecg', 'cardiaco', 'corazón', 'ritmo sinusal'],
        'eeg': ['electroencefalograma', 'eeg', 'cerebral', 'ondas cerebrales', 'epilepsia', 'convulsiones'],
        'ecografia': ['ecografía', 'ultrasonido', 'doppler', 'transductor', 'gel', 'sonda'],
    }
    
    # ==================== MÉTODOS PRINCIPALES ====================
    
    def extraer_desde_archivo(self, archivo_path: str) -> Dict[str, Any]:
        """
        Extrae datos de un archivo (PDF o imagen)
        
        Returns:
            Dict con tipo_estudio y datos extraídos
        """
        # Determinar tipo de archivo
        extension = Path(archivo_path).suffix.lower()
        
        # Extraer texto
        if extension == '.pdf':
            texto = self._extraer_texto_pdf(archivo_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            texto = self._extraer_texto_imagen(archivo_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")
        
        # Detectar tipo de estudio
        tipo_estudio = self._detectar_tipo_estudio(texto)
        
        # Extraer datos según tipo
        if tipo_estudio == 'ekg':
            datos = self._extraer_datos_ekg(texto)
        elif tipo_estudio == 'eeg':
            datos = self._extraer_datos_eeg(texto)
        elif tipo_estudio == 'ecografia':
            datos = self._extraer_datos_ecografia(texto)
        else:
            datos = {}
        
        return {
            'tipo_estudio': tipo_estudio,
            'texto_extraido': texto[:500],  # Primeros 500 caracteres
            'datos': datos,
            'confianza': self._calcular_confianza(datos)
        }
    
    # ==================== EXTRACCIÓN DE TEXTO ====================
    
    def _extraer_texto_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un PDF (con OCR si es necesario)"""
        texto = ""
        
        try:
            # Intentar extraer texto directo
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    texto += page.extract_text() + "\n"
            
            # Si no hay texto, usar OCR
            if len(texto.strip()) < 50:
                texto = self._ocr_pdf(pdf_path)
        
        except Exception as e:
            print(f"Error extrayendo texto de PDF: {e}")
            # Intentar OCR como fallback
            texto = self._ocr_pdf(pdf_path)
        
        return texto
    
    def _ocr_pdf(self, pdf_path: str) -> str:
        """Aplica OCR a un PDF convirtiéndolo a imágenes"""
        texto = ""
        try:
            # Convertir PDF a imágenes
            imagenes = convert_from_path(pdf_path, dpi=300)
            
            # OCR a cada página
            for imagen in imagenes:
                texto += pytesseract.image_to_string(imagen, lang='spa') + "\n"
        
        except Exception as e:
            print(f"Error en OCR de PDF: {e}")
        
        return texto
    
    def _extraer_texto_imagen(self, imagen_path: str) -> str:
        """Extrae texto de una imagen usando OCR"""
        try:
            imagen = Image.open(imagen_path)
            texto = pytesseract.image_to_string(imagen, lang='spa')
            return texto
        except Exception as e:
            print(f"Error en OCR de imagen: {e}")
            return ""
    
    # ==================== DETECCIÓN DE TIPO ====================
    
    def _detectar_tipo_estudio(self, texto: str) -> str:
        """Detecta el tipo de estudio basado en palabras clave"""
        texto_lower = texto.lower()
        
        puntuaciones = {
            'ekg': 0,
            'eeg': 0,
            'ecografia': 0
        }
        
        # Contar palabras clave
        for tipo, palabras in self.PALABRAS_CLAVE.items():
            for palabra in palabras:
                if palabra in texto_lower:
                    puntuaciones[tipo] += 1
        
        # Retornar el tipo con mayor puntuación
        tipo_detectado = max(puntuaciones, key=puntuaciones.get)
        
        # Si no hay puntuación, retornar desconocido
        if puntuaciones[tipo_detectado] == 0:
            return 'desconocido'
        
        return tipo_detectado
    
    # ==================== EXTRACCIÓN POR TIPO ====================
    
    def _extraer_datos_ekg(self, texto: str) -> Dict[str, Any]:
        """Extrae datos específicos de EKG"""
        datos = {}
        
        for campo, patrones in self.PATRONES_EKG.items():
            valor = self._buscar_patron(texto, patrones)
            if valor:
                datos[campo] = valor
        
        # Extraer datos del paciente
        datos.update(self._extraer_datos_paciente(texto))
        
        # Extraer motivo/indicación
        datos['motivo'] = self._extraer_motivo(texto)
        
        return datos
    
    def _extraer_datos_eeg(self, texto: str) -> Dict[str, Any]:
        """Extrae datos específicos de EEG"""
        datos = {}
        
        for campo, patrones in self.PATRONES_EEG.items():
            valor = self._buscar_patron(texto, patrones)
            if valor:
                datos[campo] = valor
        
        # Detectar tipo de estudio
        if 'basal' in texto.lower():
            datos['tipo_estudio'] = 'basal'
        elif 'sueño' in texto.lower() or 'sleep' in texto.lower():
            datos['tipo_estudio'] = 'sueno'
        elif 'vigilia' in texto.lower():
            datos['tipo_estudio'] = 'vigilia'
        
        # Detectar hallazgos anormales
        hallazgos = []
        if 'espiga' in texto.lower() or 'spike' in texto.lower():
            hallazgos.append('espigas')
        if 'onda aguda' in texto.lower() or 'sharp wave' in texto.lower():
            hallazgos.append('ondas_agudas')
        if 'punta-onda' in texto.lower():
            hallazgos.append('punta_onda')
        
        if hallazgos:
            datos['hallazgos_anormales'] = hallazgos
        
        # Extraer datos del paciente
        datos.update(self._extraer_datos_paciente(texto))
        
        # Extraer motivo
        datos['motivo'] = self._extraer_motivo(texto)
        
        return datos
    
    def _extraer_datos_ecografia(self, texto: str) -> Dict[str, Any]:
        """Extrae datos específicos de Ecografía"""
        datos = {}
        
        for campo, patrones in self.PATRONES_ECO.items():
            valor = self._buscar_patron(texto, patrones)
            if valor:
                datos[campo] = valor
        
        # Detectar tipo de ecografía
        texto_lower = texto.lower()
        if 'abdominal' in texto_lower:
            datos['tipo_ecografia'] = 'abdominal'
        elif 'obstétrica' in texto_lower or 'obstetrica' in texto_lower:
            datos['tipo_ecografia'] = 'obstetrica'
        elif 'pélvica' in texto_lower or 'pelvica' in texto_lower:
            datos['tipo_ecografia'] = 'pelvica'
        elif 'mamaria' in texto_lower or 'mama' in texto_lower:
            datos['tipo_ecografia'] = 'mamaria'
        elif 'tiroidea' in texto_lower or 'tiroides' in texto_lower:
            datos['tipo_ecografia'] = 'tiroidea'
        
        # Detectar hallazgos
        hallazgos = []
        if 'masa' in texto_lower or 'tumor' in texto_lower:
            hallazgos.append('masa')
        if 'líquido libre' in texto_lower or 'liquido libre' in texto_lower:
            hallazgos.append('liquido_libre')
        if 'quiste' in texto_lower or 'cyst' in texto_lower:
            hallazgos.append('quiste')
        
        if hallazgos:
            datos['hallazgos'] = hallazgos
        
        # Detectar Doppler
        if 'doppler' in texto_lower:
            datos['estudio_doppler'] = True
        
        # Extraer datos del paciente
        datos.update(self._extraer_datos_paciente(texto))
        
        # Extraer motivo
        datos['motivo'] = self._extraer_motivo(texto)
        
        return datos
    
    # ==================== UTILIDADES ====================
    
    def _buscar_patron(self, texto: str, patrones: List[str]) -> Optional[str]:
        """Busca un patrón en el texto"""
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extraer_datos_paciente(self, texto: str) -> Dict[str, Any]:
        """Extrae datos del paciente (edad, peso, altura)"""
        datos = {}
        
        # Edad
        patron_edad = r'(?:Edad|Age)[:\s]*(\d+)\s*(?:años|years|a)'
        match = re.search(patron_edad, texto, re.IGNORECASE)
        if match:
            datos['edad_paciente'] = int(match.group(1))
        
        # Peso
        patron_peso = r'(?:Peso|Weight)[:\s]*(\d+\.?\d*)\s*kg'
        match = re.search(patron_peso, texto, re.IGNORECASE)
        if match:
            datos['peso_paciente'] = float(match.group(1))
        
        # Altura
        patron_altura = r'(?:Altura|Talla|Height)[:\s]*(\d+\.?\d*)\s*(?:cm|m)'
        match = re.search(patron_altura, texto, re.IGNORECASE)
        if match:
            altura = float(match.group(1))
            # Convertir a cm si está en metros
            if altura < 3:
                altura *= 100
            datos['altura_paciente'] = int(altura)
        
        return datos
    
    def _extraer_motivo(self, texto: str) -> Optional[str]:
        """Extrae el motivo o indicación del estudio"""
        patrones = [
            r'(?:Motivo|Indicaci[oó]n|Reason)[:\s]*([^\n]{10,100})',
            r'(?:Solicita|Requested\s+by)[:\s]*([^\n]{10,100})',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _calcular_confianza(self, datos: Dict[str, Any]) -> float:
        """Calcula un score de confianza basado en datos extraídos"""
        if not datos:
            return 0.0
        
        # Contar campos extraídos
        campos_extraidos = len([v for v in datos.values() if v is not None and v != ''])
        
        # Score simple: más campos = más confianza
        if campos_extraidos == 0:
            return 0.0
        elif campos_extraidos <= 2:
            return 0.3
        elif campos_extraidos <= 4:
            return 0.6
        elif campos_extraidos <= 6:
            return 0.8
        else:
            return 0.95
