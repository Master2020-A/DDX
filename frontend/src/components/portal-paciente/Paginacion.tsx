import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

interface PaginacionProps {
  paginaActual: number;
  totalPaginas: number;
  totalItems: number;
  itemsPorPagina: number;
  onPaginaChange: (pagina: number) => void;
  onItemsPorPaginaChange: (items: number) => void;
}

export default function Paginacion({
  paginaActual,
  totalPaginas,
  totalItems,
  itemsPorPagina,
  onPaginaChange,
  onItemsPorPaginaChange,
}: PaginacionProps) {
  const inicio = (paginaActual - 1) * itemsPorPagina + 1;
  const fin = Math.min(paginaActual * itemsPorPagina, totalItems);

  const irAPagina = (pagina: number) => {
    if (pagina >= 1 && pagina <= totalPaginas) {
      onPaginaChange(pagina);
    }
  };

  return (
    <div className="flex items-center justify-between px-2 py-4">
      <div className="flex items-center gap-2">
        <p className="text-sm text-muted-foreground">
          Mostrando <span className="font-medium">{inicio}</span> a{' '}
          <span className="font-medium">{fin}</span> de{' '}
          <span className="font-medium">{totalItems}</span> resultados
        </p>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <p className="text-sm text-muted-foreground">Filas por página:</p>
          <Select
            value={itemsPorPagina.toString()}
            onValueChange={(value) => onItemsPorPaginaChange(parseInt(value))}
          >
            <SelectTrigger className="h-8 w-[70px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="20">20</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => irAPagina(1)}
            disabled={paginaActual === 1}
          >
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => irAPagina(paginaActual - 1)}
            disabled={paginaActual === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          <div className="flex items-center gap-1 mx-2">
            <p className="text-sm text-muted-foreground">
              Página <span className="font-medium">{paginaActual}</span> de{' '}
              <span className="font-medium">{totalPaginas}</span>
            </p>
          </div>

          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => irAPagina(paginaActual + 1)}
            disabled={paginaActual === totalPaginas}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => irAPagina(totalPaginas)}
            disabled={paginaActual === totalPaginas}
          >
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
