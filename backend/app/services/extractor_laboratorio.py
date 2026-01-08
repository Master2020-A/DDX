"""
Servicio para extracción de datos de laboratorio desde PDF e imágenes
Utiliza OCR (Tesseract) y procesamiento de texto con expresiones regulares
"""
import re
import io
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import tempfile

try:
    import pytesseract
    from PIL import Image
    import platform
    import os
    
    # Configurar ruta de Tesseract en Windows
    if platform.system() == 'Windows':
        # Intentar rutas comunes de instalación
        posibles_rutas = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Tesseract-OCR\tesseract.exe'
        ]
        for ruta in posibles_rutas:
            if Path(ruta).exists():
                pytesseract.pytesseract.tesseract_cmd = ruta
                # Configurar TESSDATA_PREFIX
                tessdata_dir = str(Path(ruta).parent / 'tessdata')
                if Path(tessdata_dir).exists():
                    os.environ['TESSDATA_PREFIX'] = tessdata_dir
                break
    
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract no disponible. Instalar con: pip install pytesseract pillow")

try:
    import PyPDF2
    import pdf2image
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2/pdf2image no disponibles. Instalar con: pip install PyPDF2 pdf2image")

logger = logging.getLogger(__name__)


class ExtractorLaboratorio:
    """
    Extrae datos de laboratorio desde PDFs e imágenes usando OCR
    """
    
    # Patrones de parámetros comunes en español
    PARAMETROS_PATTERNS = {
        # Hematología
        'hemoglobina': [
            r'hemoglobina[:\s]+(\d+\.?\d*)',
            r'hb[:\s]+(\d+\.?\d*)',
            r'hgb[:\s]+(\d+\.?\d*)'
        ],
        'hematocrito': [
            r'hematocrito[:\s]+(\d+\.?\d*)',
            r'hto[:\s]+(\d+\.?\d*)',
            r'hct[:\s]+(\d+\.?\d*)'
        ],
        'leucocitos': [
            r'leucocitos[:\s]+(\d+\.?\d*)',
            r'globulos\s+blancos[:\s]+(\d+\.?\d*)',
            r'wbc[:\s]+(\d+\.?\d*)'
        ],
        'plaquetas': [
            r'plaquetas[:\s]+(\d+\.?\d*)',
            r'plt[:\s]+(\d+\.?\d*)'
        ],
        'eritrocitos': [
            r'eritrocitos[:\s]+(\d+\.?\d*)',
            r'globulos\s+rojos[:\s]+(\d+\.?\d*)',
            r'rbc[:\s]+(\d+\.?\d*)',
            r'hematies[:\s]+(\d+\.?\d*)'
        ],
        'neutrofilos': [
            r'neutrofilos[:\s]+(\d+\.?\d*)',
            r'neu[:\s]+(\d+\.?\d*)',
            r'neutrofilos\s+segmentados[:\s]+(\d+\.?\d*)'
        ],
        'linfocitos': [
            r'linfocitos[:\s]+(\d+\.?\d*)',
            r'linf[:\s]+(\d+\.?\d*)',
            r'lym[:\s]+(\d+\.?\d*)'
        ],
        'monocitos': [
            r'monocitos[:\s]+(\d+\.?\d*)',
            r'mono[:\s]+(\d+\.?\d*)'
        ],
        'eosinofilos': [
            r'eosinofilos[:\s]+(\d+\.?\d*)',
            r'eos[:\s]+(\d+\.?\d*)'
        ],
        'basofilos': [
            r'basofilos[:\s]+(\d+\.?\d*)',
            r'baso[:\s]+(\d+\.?\d*)'
        ],
        'vcm': [
            r'volumen\s+corpuscular\s+medio[:\s]+(\d+\.?\d*)',
            r'vcm[:\s]+(\d+\.?\d*)',
            r'mcv[:\s]+(\d+\.?\d*)'
        ],
        'hcm': [
            r'hgb\.?\s*corpuscular\s+media[:\s]+(\d+\.?\d*)',
            r'hemoglobina\s+corpuscular\s+media[:\s]+(\d+\.?\d*)',
            r'hcm[:\s]+(\d+\.?\d*)',
            r'mch[:\s]+(\d+\.?\d*)'
        ],
        'chcm': [
            r'cont\.?\s*med\.?\s*hgb\.?\s*corpuscular[:\s]+(\d+\.?\d*)',
            r'concentracion\s+media\s+hemoglobina\s+corpuscular[:\s]+(\d+\.?\d*)',
            r'chcm[:\s]+(\d+\.?\d*)',
            r'mchc[:\s]+(\d+\.?\d*)'
        ],
        'rdw': [
            r'amplitud\s+de\s+distribucion[:\s]+(\d+\.?\d*)',
            r'rdw[:\s]+(\d+\.?\d*)',
            r'rdw-cv[:\s]+(\d+\.?\d*)',
            r'rdw-sd[:\s]+(\d+\.?\d*)',
            r'ancho\s+distribucion\s+eritrocitaria[:\s]+(\d+\.?\d*)'
        ],
        'neutrofilos_abs': [
            r'neutrofilos\s+\(abs\)[:\s]+(\d+\.?\d*)',
            r'neutrofilos\s+absolutos[:\s]+(\d+\.?\d*)',
            r'neu\s+abs[:\s]+(\d+\.?\d*)',
            r'neutrofilos\s+\(10\^?3[:/]',
            r'neutrofilos.*?(\d+\.?\d*)\s*x\s*10'
        ],
        'linfocitos_abs': [
            r'linfocitos\s+\(abs\)[:\s]+(\d+\.?\d*)',
            r'linfocitos\s+absolutos[:\s]+(\d+\.?\d*)',
            r'linf\s+abs[:\s]+(\d+\.?\d*)',
            r'linfocitos\s+\(10\^?3[:/]',
            r'linfocitos.*?(\d+\.?\d*)\s*x\s*10'
        ],
        'monocitos_abs': [
            r'monocitos\s+\(abs\)[:\s]+(\d+\.?\d*)',
            r'monocitos\s+absolutos[:\s]+(\d+\.?\d*)',
            r'mono\s+abs[:\s]+(\d+\.?\d*)',
            r'monocitos\s+\(10\^?3[:/]',
            r'monocitos.*?(\d+\.?\d*)\s*x\s*10'
        ],
        'eosinofilos_abs': [
            r'eosinofilos\s+\(abs\)[:\s]+(\d+\.?\d*)',
            r'eosinofilos\s+absolutos[:\s]+(\d+\.?\d*)',
            r'eos\s+abs[:\s]+(\d+\.?\d*)',
            r'eosinofilos\s+\(10\^?3[:/]',
            r'eosinofilos.*?(\d+\.?\d*)\s*x\s*10'
        ],
        'basofilos_abs': [
            r'basofilos\s+\(abs\)[:\s]+(\d+\.?\d*)',
            r'basofilos\s+absolutos[:\s]+(\d+\.?\d*)',
            r'baso\s+abs[:\s]+(\d+\.?\d*)',
            r'basofilos\s+\(10\^?3[:/]',
            r'basofilos.*?(\d+\.?\d*)\s*x\s*10'
        ],
        'bandas': [
            r'bandas[:\s]+(\d+\.?\d*)',
            r'neutrofilos\s+en\s+banda[:\s]+(\d+\.?\d*)',
            r'band[:\s]+(\d+\.?\d*)'
        ],
        'segmentados': [
            r'segmentados[:\s]+(\d+\.?\d*)',
            r'neutrofilos\s+segmentados[:\s]+(\d+\.?\d*)',
            r'seg[:\s]+(\d+\.?\d*)'
        ],
        
        # Química Clínica
        'glucosa': [
            r'glucosa[:\s]+(\d+\.?\d*)',
            r'gluc[:\s]+(\d+\.?\d*)'
        ],
        'creatinina': [
            r'creatinina[:\s]+(\d+\.?\d*)',
            r'creat[:\s]+(\d+\.?\d*)'
        ],
        'urea': [
            r'urea[:\s]+(\d+\.?\d*)',
            r'bun[:\s]+(\d+\.?\d*)'
        ],
        'acido_urico': [
            r'acido\s+urico[:\s]+(\d+\.?\d*)',
            r'uric\s+acid[:\s]+(\d+\.?\d*)'
        ],
        'colesterol_total': [
            r'colesterol\s+total[:\s]+(\d+\.?\d*)',
            r'colesterol[:\s]+(\d+\.?\d*)',
            r'chol[:\s]+(\d+\.?\d*)'
        ],
        'trigliceridos': [
            r'trigliceridos[:\s]+(\d+\.?\d*)',
            r'trig[:\s]+(\d+\.?\d*)'
        ],
        'hdl': [
            r'hdl[:\s]+(\d+\.?\d*)',
            r'colesterol\s+hdl[:\s]+(\d+\.?\d*)'
        ],
        'ldl': [
            r'ldl[:\s]+(\d+\.?\d*)',
            r'colesterol\s+ldl[:\s]+(\d+\.?\d*)'
        ],
        'tgo': [
            r'tgo[:\s]+(\d+\.?\d*)',
            r'ast[:\s]+(\d+\.?\d*)',
            r'aspartato[:\s]+(\d+\.?\d*)'
        ],
        'tgp': [
            r'tgp[:\s]+(\d+\.?\d*)',
            r'alt[:\s]+(\d+\.?\d*)',
            r'alanina[:\s]+(\d+\.?\d*)'
        ],
        'bilirrubina_total': [
            r'bilirrubina\s+total[:\s]+(\d+\.?\d*)',
            r'bili\s+total[:\s]+(\d+\.?\d*)'
        ],
        'bilirrubina_directa': [
            r'bilirrubina\s+directa[:\s]+(\d+\.?\d*)',
            r'bili\s+directa[:\s]+(\d+\.?\d*)'
        ],
        'fosfatasa_alcalina': [
            r'fosfatasa\s+alcalina[:\s]+(\d+\.?\d*)',
            r'alp[:\s]+(\d+\.?\d*)'
        ],
        'proteinas_totales': [
            r'proteinas\s+totales[:\s]+(\d+\.?\d*)',
            r'prot\s+total[:\s]+(\d+\.?\d*)'
        ],
        'albumina': [
            r'albumina[:\s]+(\d+\.?\d*)',
            r'alb[:\s]+(\d+\.?\d*)'
        ],
        'globulinas': [
            r'globulinas[:\s]+(\d+\.?\d*)',
            r'glob[:\s]+(\d+\.?\d*)'
        ],
        'bilirrubina_indirecta': [
            r'bilirrubina\s+indirecta[:\s]+(\d+\.?\d*)',
            r'bili\s+indirecta[:\s]+(\d+\.?\d*)'
        ],
        'ggt': [
            r'gamma\s+glutamil[:\s]+(\d+\.?\d*)',
            r'ggt[:\s]+(\d+\.?\d*)',
            r'gamma\s+gt[:\s]+(\d+\.?\d*)'
        ],
        'ldh': [
            r'lactato\s+deshidrogenasa[:\s]+(\d+\.?\d*)',
            r'ldh[:\s]+(\d+\.?\d*)',
            r'dhl[:\s]+(\d+\.?\d*)'
        ],
        'amilasa': [
            r'amilasa[:\s]+(\d+\.?\d*)',
            r'amylase[:\s]+(\d+\.?\d*)'
        ],
        'lipasa': [
            r'lipasa[:\s]+(\d+\.?\d*)',
            r'lipase[:\s]+(\d+\.?\d*)'
        ],
        'ck': [
            r'creatina\s+quinasa[:\s]+(\d+\.?\d*)',
            r'ck[:\s]+(\d+\.?\d*)',
            r'cpk[:\s]+(\d+\.?\d*)'
        ],
        'ck_mb': [
            r'ck-mb[:\s]+(\d+\.?\d*)',
            r'ckmb[:\s]+(\d+\.?\d*)'
        ],
        'vldl': [
            r'vldl[:\s]+(\d+\.?\d*)',
            r'colesterol\s+vldl[:\s]+(\d+\.?\d*)'
        ],
        
        # Electrolitos
        'sodio': [
            r'sodio[:\s]+(\d+\.?\d*)',
            r'na\+?[:\s]+(\d+\.?\d*)',
            r'sodium[:\s]+(\d+\.?\d*)'
        ],
        'potasio': [
            r'potasio[:\s]+(\d+\.?\d*)',
            r'k\+?[:\s]+(\d+\.?\d*)',
            r'potassium[:\s]+(\d+\.?\d*)'
        ],
        'cloro': [
            r'cloro[:\s]+(\d+\.?\d*)',
            r'cl-?[:\s]+(\d+\.?\d*)',
            r'chloride[:\s]+(\d+\.?\d*)'
        ],
        'calcio': [
            r'calcio[:\s]+(\d+\.?\d*)',
            r'ca\+?\+?[:\s]+(\d+\.?\d*)',
            r'calcium[:\s]+(\d+\.?\d*)'
        ],
        'calcio_ionico': [
            r'calcio\s+ionico[:\s]+(\d+\.?\d*)',
            r'calcio\s+ionizado[:\s]+(\d+\.?\d*)',
            r'ca\+\+[:\s]+(\d+\.?\d*)'
        ],
        'magnesio': [
            r'magnesio[:\s]+(\d+\.?\d*)',
            r'mg\+?\+?[:\s]+(\d+\.?\d*)',
            r'magnesium[:\s]+(\d+\.?\d*)'
        ],
        'fosforo': [
            r'fosforo[:\s]+(\d+\.?\d*)',
            r'p[:\s]+(\d+\.?\d*)',
            r'phosphorus[:\s]+(\d+\.?\d*)'
        ],
        
        # Función tiroidea
        'tsh': [
            r'tsh[:\s]+(\d+\.?\d*)',
            r'tirotropina[:\s]+(\d+\.?\d*)'
        ],
        't3': [
            r't3[:\s]+(\d+\.?\d*)',
            r'triyodotironina[:\s]+(\d+\.?\d*)'
        ],
        't4': [
            r't4[:\s]+(\d+\.?\d*)',
            r'tiroxina[:\s]+(\d+\.?\d*)'
        ],
        't4_libre': [
            r't4\s+libre[:\s]+(\d+\.?\d*)',
            r'ft4[:\s]+(\d+\.?\d*)'
        ],
        
        # Hierro y metabolismo
        'hierro': [
            r'hierro[:\s]+(\d+\.?\d*)',
            r'fe[:\s]+(\d+\.?\d*)',
            r'iron[:\s]+(\d+\.?\d*)'
        ],
        'ferritina': [
            r'ferritina[:\s]+(\d+\.?\d*)',
            r'ferritin[:\s]+(\d+\.?\d*)'
        ],
        'transferrina': [
            r'transferrina[:\s]+(\d+\.?\d*)',
            r'transferrin[:\s]+(\d+\.?\d*)'
        ],
        'tibc': [
            r'tibc[:\s]+(\d+\.?\d*)',
            r'capacidad\s+total[:\s]+(\d+\.?\d*)'
        ],
        
        # Vitaminas
        'vitamina_b12': [
            r'vitamina\s+b12[:\s]+(\d+\.?\d*)',
            r'b12[:\s]+(\d+\.?\d*)',
            r'cobalamina[:\s]+(\d+\.?\d*)'
        ],
        'vitamina_d': [
            r'vitamina\s+d[:\s]+(\d+\.?\d*)',
            r'25-oh\s+vitamina\s+d[:\s]+(\d+\.?\d*)',
            r'vit\s+d[:\s]+(\d+\.?\d*)'
        ],
        'acido_folico': [
            r'acido\s+folico[:\s]+(\d+\.?\d*)',
            r'folato[:\s]+(\d+\.?\d*)',
            r'folic\s+acid[:\s]+(\d+\.?\d*)'
        ],
        
        # Otros
        'vsg': [
            r'velocidad\s+sedimentacion[:\s]+(\d+\.?\d*)',
            r'vsg[:\s]+(\d+\.?\d*)',
            r'esr[:\s]+(\d+\.?\d*)'
        ],
        'hba1c': [
            r'hemoglobina\s+glicosilada[:\s]+(\d+\.?\d*)',
            r'hba1c[:\s]+(\d+\.?\d*)',
            r'a1c[:\s]+(\d+\.?\d*)'
        ],
        'insulina': [
            r'insulina[:\s]+(\d+\.?\d*)',
            r'insulin[:\s]+(\d+\.?\d*)'
        ],
        'cortisol': [
            r'cortisol[:\s]+(\d+\.?\d*)'
        ],
        'testosterona': [
            r'testosterona[:\s]+(\d+\.?\d*)',
            r'testosterone[:\s]+(\d+\.?\d*)'
        ],
        'estradiol': [
            r'estradiol[:\s]+(\d+\.?\d*)'
        ],
        'progesterona': [
            r'progesterona[:\s]+(\d+\.?\d*)',
            r'progesterone[:\s]+(\d+\.?\d*)'
        ],
        'prolactina': [
            r'prolactina[:\s]+(\d+\.?\d*)',
            r'prolactin[:\s]+(\d+\.?\d*)'
        ],
        'psa': [
            r'psa[:\s]+(\d+\.?\d*)',
            r'antigeno\s+prostatico[:\s]+(\d+\.?\d*)'
        ],
        
        # Inmunología
        'pcr': [
            r'proteina\s+c\s+reactiva[:\s]+(\d+\.?\d*)',
            r'pcr[:\s]+(\d+\.?\d*)',
            r'crp[:\s]+(\d+\.?\d*)'
        ],
        
        # Examen General de Orina (EGO)
        'densidad_orina': [
            r'densidad[:\s]+(\d+\.?\d*)',
            r'specific\s+gravity[:\s]+(\d+\.?\d*)'
        ],
        'ph_orina': [
            r'ph[:\s]+(\d+\.?\d*)'
        ],
        'proteinas_orina': [
            r'proteinas[:\s]+([\w\s]+)',  # Puede ser NEGATIVO o valor
            r'protein[:\s]+([\w\s]+)'
        ],
        'glucosa_orina': [
            r'glucosa[:\s]+([\w\s]+)',
            r'glucose[:\s]+([\w\s]+)'
        ],
        'hemoglobina_orina': [
            r'hemoglobina[:\s]+([\w\s]+)',
            r'blood[:\s]+([\w\s]+)'
        ],
        'cetonas_orina': [
            r'cetona[:\s]+([\w\s]+)',
            r'ketones[:\s]+([\w\s]+)'
        ],
        'bilirrubina_orina': [
            r'bilirrubina[:\s]+([\w\s]+)',
            r'bilirubin[:\s]+([\w\s]+)'
        ],
        'urobilinogeno_orina': [
            r'urobilinogenos[:\s]+([\w\s]+)',
            r'urobilinogen[:\s]+([\w\s]+)'
        ],
        'nitritos_orina': [
            r'nitritos[:\s]+([\w\s]+)',
            r'nitrites[:\s]+([\w\s]+)'
        ],
        'leucocitos_orina': [
            r'leucocitos[:\s]+(\d+\.?\d*|[\w\s]+)',
            r'wbc[:\s]+(\d+\.?\d*|[\w\s]+)'
        ],
        'eritrocitos_orina': [
            r'eritrocitos[:\s]+(\d+\.?\d*|[\w\s]+)',
            r'rbc[:\s]+(\d+\.?\d*|[\w\s]+)'
        ],
        'celulas_epiteliales': [
            r'celulas\s+epiteliales[:\s]+([\w\s]+)',
            r'epithelial\s+cells[:\s]+([\w\s]+)'
        ],
        'bacterias_orina': [
            r'bacteriuria[:\s]+([\w\s]+)',
            r'bacteria[:\s]+([\w\s]+)'
        ],
        'cristales_orina': [
            r'cristales[:\s]+([\w\s]+)',
            r'crystals[:\s]+([\w\s]+)'
        ],
        'cilindros_orina': [
            r'cilindros[:\s]+([\w\s]+)',
            r'casts[:\s]+([\w\s]+)'
        ],
        'moco_orina': [
            r'filamento\s+de\s+moco[:\s]+([\w\s]+)',
            r'mucus[:\s]+([\w\s]+)'
        ]
    }
    
    # Mapeo de áreas por parámetros
    AREA_MAPPING = {
        # Hematología
        'hemoglobina': 'hematologia',
        'hematocrito': 'hematologia',
        'leucocitos': 'hematologia',
        'plaquetas': 'hematologia',
        'eritrocitos': 'hematologia',
        'neutrofilos': 'hematologia',
        'linfocitos': 'hematologia',
        'monocitos': 'hematologia',
        'eosinofilos': 'hematologia',
        'basofilos': 'hematologia',
        'vcm': 'hematologia',
        'hcm': 'hematologia',
        'chcm': 'hematologia',
        'rdw': 'hematologia',
        'bandas': 'hematologia',
        'segmentados': 'hematologia',
        'neutrofilos_abs': 'hematologia',
        'linfocitos_abs': 'hematologia',
        'monocitos_abs': 'hematologia',
        'eosinofilos_abs': 'hematologia',
        'basofilos_abs': 'hematologia',
        'vsg': 'hematologia',
        
        # Química Clínica
        'glucosa': 'quimica_clinica',
        'creatinina': 'quimica_clinica',
        'urea': 'quimica_clinica',
        'acido_urico': 'quimica_clinica',
        'colesterol_total': 'quimica_clinica',
        'trigliceridos': 'quimica_clinica',
        'hdl': 'quimica_clinica',
        'ldl': 'quimica_clinica',
        'vldl': 'quimica_clinica',
        'tgo': 'quimica_clinica',
        'tgp': 'quimica_clinica',
        'bilirrubina_total': 'quimica_clinica',
        'bilirrubina_directa': 'quimica_clinica',
        'bilirrubina_indirecta': 'quimica_clinica',
        'fosfatasa_alcalina': 'quimica_clinica',
        'proteinas_totales': 'quimica_clinica',
        'albumina': 'quimica_clinica',
        'globulinas': 'quimica_clinica',
        'ggt': 'quimica_clinica',
        'ldh': 'quimica_clinica',
        'amilasa': 'quimica_clinica',
        'lipasa': 'quimica_clinica',
        'ck': 'quimica_clinica',
        'ck_mb': 'quimica_clinica',
        'sodio': 'quimica_clinica',
        'potasio': 'quimica_clinica',
        'cloro': 'quimica_clinica',
        'calcio': 'quimica_clinica',
        'calcio_ionico': 'quimica_clinica',
        'magnesio': 'quimica_clinica',
        'fosforo': 'quimica_clinica',
        'hierro': 'quimica_clinica',
        'ferritina': 'quimica_clinica',
        'transferrina': 'quimica_clinica',
        'tibc': 'quimica_clinica',
        'vitamina_b12': 'quimica_clinica',
        'vitamina_d': 'quimica_clinica',
        'acido_folico': 'quimica_clinica',
        'hba1c': 'quimica_clinica',
        'insulina': 'quimica_clinica',
        'tsh': 'quimica_clinica',
        't3': 'quimica_clinica',
        't4': 'quimica_clinica',
        't4_libre': 'quimica_clinica',
        'cortisol': 'quimica_clinica',
        'testosterona': 'quimica_clinica',
        'estradiol': 'quimica_clinica',
        'progesterona': 'quimica_clinica',
        'prolactina': 'quimica_clinica',
        'psa': 'quimica_clinica',
        
        # Inmunología
        'pcr': 'inmunologia',
        
        # Uroanálisis
        'densidad_orina': 'uroanalisis',
        'ph_orina': 'uroanalisis',
        'proteinas_orina': 'uroanalisis',
        'glucosa_orina': 'uroanalisis',
        'hemoglobina_orina': 'uroanalisis',
        'cetonas_orina': 'uroanalisis',
        'bilirrubina_orina': 'uroanalisis',
        'urobilinogeno_orina': 'uroanalisis',
        'nitritos_orina': 'uroanalisis',
        'leucocitos_orina': 'uroanalisis',
        'eritrocitos_orina': 'uroanalisis',
        'celulas_epiteliales': 'uroanalisis',
        'bacterias_orina': 'uroanalisis',
        'cristales_orina': 'uroanalisis',
        'cilindros_orina': 'uroanalisis',
        'moco_orina': 'uroanalisis'
    }
    
    def __init__(self):
        """Inicializa el extractor"""
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract OCR no disponible")
        if not PDF_AVAILABLE:
            logger.warning("Librerías PDF no disponibles")
    
    def extraer_desde_imagen(self, imagen_path: str) -> Dict[str, Any]:
        """
        Extrae datos de laboratorio desde una imagen
        
        Args:
            imagen_path: Ruta a la imagen
            
        Returns:
            Dict con resultados extraídos y metadatos
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract no está instalado. Ejecute: pip install pytesseract pillow")
        
        try:
            # Abrir imagen
            imagen = Image.open(imagen_path)
            
            # Aplicar OCR - intentar español primero, luego inglés
            texto = None
            idioma_usado = None
            
            try:
                texto = pytesseract.image_to_string(imagen, lang='spa')
                idioma_usado = 'spa'
            except Exception as e:
                logger.warning(f"No se pudo usar idioma español: {e}. Intentando con inglés...")
                try:
                    texto = pytesseract.image_to_string(imagen, lang='eng')
                    idioma_usado = 'eng'
                except Exception as e2:
                    logger.error(f"Error con ambos idiomas: {e2}")
                    raise RuntimeError(
                        "No se pudo extraer texto. Asegúrate de que Tesseract esté instalado correctamente "
                        "con al menos un idioma (español o inglés). "
                        "Ejecuta: instalar_idioma_tesseract.bat"
                    )
            
            if not texto:
                raise RuntimeError("No se pudo extraer texto de la imagen")
            
            # Extraer datos
            resultados = self._extraer_parametros(texto)
            
            return {
                'exito': True,
                'resultados': resultados,
                'texto_extraido': texto[:500],  # Primeros 500 caracteres
                'parametros_encontrados': len(resultados),
                'metodo': f'OCR_imagen_{idioma_usado}'
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo desde imagen: {e}")
            return {
                'exito': False,
                'error': str(e),
                'resultados': {},
                'parametros_encontrados': 0
            }
    
    def extraer_desde_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrae datos de laboratorio desde un PDF
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Dict con resultados extraídos y metadatos
        """
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2/pdf2image no están instalados. Ejecute: pip install PyPDF2 pdf2image")
        
        try:
            # Intentar extraer texto directamente del PDF
            texto = self._extraer_texto_pdf(pdf_path)
            
            # Si no hay texto, usar OCR en las páginas
            if not texto.strip():
                logger.info("PDF sin texto extraíble, usando OCR...")
                texto = self._extraer_texto_pdf_ocr(pdf_path)
            
            # Extraer datos
            resultados = self._extraer_parametros(texto)
            
            return {
                'exito': True,
                'resultados': resultados,
                'texto_extraido': texto,
                'parametros_encontrados': len(resultados),
                'metodo': 'PDF_texto' if texto else 'PDF_OCR'
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo desde PDF: {e}")
            return {
                'exito': False,
                'error': str(e),
                'resultados': {},
                'parametros_encontrados': 0
            }
    
    def _extraer_texto_pdf(self, pdf_path: str) -> str:
        """Extrae texto directamente del PDF"""
        texto = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    texto += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extrayendo texto de PDF: {e}")
        return texto
    
    def _extraer_texto_pdf_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR"""
        if not TESSERACT_AVAILABLE:
            return ""
        
        texto = ""
        try:
            # Convertir PDF a imágenes
            imagenes = pdf2image.convert_from_path(pdf_path)
            
            # Aplicar OCR a cada página
            for i, imagen in enumerate(imagenes):
                logger.info(f"Procesando página {i+1}/{len(imagenes)} con OCR...")
                texto += pytesseract.image_to_string(imagen, lang='spa') + "\n"
                
        except Exception as e:
            logger.error(f"Error en OCR de PDF: {e}")
        
        return texto
    
    def _extraer_parametros(self, texto: str) -> Dict[str, float]:
        """
        Extrae parámetros de laboratorio del texto usando regex
        
        Args:
            texto: Texto extraído del documento
            
        Returns:
            Dict con parámetros y valores encontrados
        """
        resultados = {}
        
        # Normalizar texto: eliminar saltos de línea múltiples y espacios extra
        texto_normalizado = re.sub(r'\s+', ' ', texto)
        texto_lower = texto_normalizado.lower()
        
        logger.info(f"🔍 Iniciando extracción de parámetros...")
        logger.info(f"📄 Longitud del texto: {len(texto)} caracteres")
        
        parametros_encontrados = 0
        
        for parametro, patterns in self.PARAMETROS_PATTERNS.items():
            for pattern in patterns:
                # Hacer el patrón más flexible con espacios
                pattern_flexible = pattern.replace(r'\s+', r'\s*')
                
                match = re.search(pattern_flexible, texto_lower, re.IGNORECASE)
                if match:
                    try:
                        valor_str = match.group(1).strip()
                        # Limpiar el valor (remover espacios, comas como separadores decimales)
                        valor_str = valor_str.replace(',', '.').replace(' ', '')
                        valor = float(valor_str)
                        
                        resultados[parametro] = valor
                        parametros_encontrados += 1
                        logger.info(f"✅ Encontrado {parametro}: {valor}")
                        break  # Ya encontramos este parámetro
                    except (ValueError, IndexError) as e:
                        logger.debug(f"⚠️ Error parseando {parametro}: {e}")
                        continue
        
        logger.info(f"📊 Total de parámetros encontrados: {parametros_encontrados}")
        
        if parametros_encontrados == 0:
            logger.warning("⚠️ No se encontraron parámetros. Mostrando muestra del texto:")
            logger.warning(f"Primeros 500 caracteres: {texto_lower[:500]}")
        
        return resultados
    
    def detectar_area_y_tipo(self, resultados: Dict[str, float]) -> Tuple[str, str]:
        """
        Detecta el área y tipo de prueba basándose en los parámetros encontrados
        
        Args:
            resultados: Dict con parámetros extraídos
            
        Returns:
            Tuple (area, tipo_prueba)
        """
        if not resultados:
            return ('quimica_clinica', 'glucosa')  # Default
        
        # Contar parámetros por área
        areas_count = {}
        for parametro in resultados.keys():
            area = self.AREA_MAPPING.get(parametro, 'quimica_clinica')
            areas_count[area] = areas_count.get(area, 0) + 1
        
        # Área más común
        area = max(areas_count, key=areas_count.get)
        
        # Determinar tipo de prueba
        tipo_prueba = self._determinar_tipo_prueba(area, resultados)
        
        return (area, tipo_prueba)
    
    def _determinar_tipo_prueba(self, area: str, resultados: Dict[str, float]) -> str:
        """Determina el tipo de prueba específico"""
        parametros = set(resultados.keys())
        
        if area == 'hematologia':
            # Si tiene hemoglobina, leucocitos y plaquetas, es biometría completa
            if {'hemoglobina', 'leucocitos', 'plaquetas'}.issubset(parametros):
                return 'biometria_hematica'
            return 'biometria_hematica'
        
        elif area == 'quimica_clinica':
            # Detectar tipo específico
            if 'glucosa' in parametros and len(parametros) == 1:
                return 'glucosa'
            elif {'creatinina', 'urea'}.intersection(parametros):
                return 'funcion_renal'
            elif {'colesterol_total', 'trigliceridos', 'hdl', 'ldl'}.intersection(parametros):
                return 'perfil_lipidico'
            elif {'tgo', 'tgp', 'bilirrubina_total'}.intersection(parametros):
                return 'funcion_hepatica'
            return 'glucosa'
        
        elif area == 'inmunologia':
            return 'marcadores_inflamatorios'
        
        return 'glucosa'
    
    def formatear_para_api(self, resultados: Dict[str, float], 
                          paciente_id: str,
                          consulta_id: Optional[str] = None,
                          laboratorio_externo: Optional[str] = None) -> Dict[str, Any]:
        """
        Formatea los resultados extraídos para el formato de la API
        
        Args:
            resultados: Dict con parámetros extraídos
            paciente_id: ID del paciente
            consulta_id: ID de la consulta (opcional)
            laboratorio_externo: Nombre del laboratorio (opcional)
            
        Returns:
            Dict en formato CrearPruebaLaboratorio
        """
        area, tipo_prueba = self.detectar_area_y_tipo(resultados)
        
        return {
            'paciente_id': paciente_id,
            'consulta_id': consulta_id,
            'area': area,
            'tipo_prueba': tipo_prueba,
            'resultados': resultados,
            'laboratorio_externo': laboratorio_externo,
            'metodo_captura': 'extraccion_automatica'
        }


# Instancia singleton
_extractor_instance = None

def obtener_extractor() -> ExtractorLaboratorio:
    """Obtiene la instancia singleton del extractor"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = ExtractorLaboratorio()
    return _extractor_instance
