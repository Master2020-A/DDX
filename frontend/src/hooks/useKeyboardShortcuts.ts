import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const useKeyboardShortcuts = (onOpenSearch: () => void) => {
  const navigate = useNavigate();
  
  useEffect(() => {
    let keySequence = '';
    let sequenceTimeout: NodeJS.Timeout;

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        onOpenSearch();
        return;
      }

      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
        return;
      }

      clearTimeout(sequenceTimeout);
      keySequence += e.key.toLowerCase();

      sequenceTimeout = setTimeout(() => {
        keySequence = '';
      }, 1000);

      if (keySequence === 'gd') {
        navigate('/');
        keySequence = '';
      } else if (keySequence === 'gp') {
        navigate('/pacientes');
        keySequence = '';
      } else if (keySequence === 'gc') {
        navigate('/consultas');
        keySequence = '';
      } else if (keySequence === 'gh') {
        navigate('/hospitalizacion');
        keySequence = '';
      } else if (keySequence === 'gi') {
        navigate('/interconsultas');
        keySequence = '';
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      clearTimeout(sequenceTimeout);
    };
  }, [navigate, onOpenSearch]);
};