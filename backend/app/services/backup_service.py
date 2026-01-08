"""
Servicio para gestión de backups y recuperación de base de datos
"""

import os
import subprocess
import hashlib
import gzip
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.backups import (
    Backup,
    ProgramacionBackup,
    Restauracion,
    ReplicacionBD,
    MonitoreoSalud,
    AlertaBackup,
    PlanRecuperacion,
    TipoBackup,
    EstadoBackup,
    TipoRestauracion,
    EstadoRestauracion,
    NivelSeveridad,
)


class BackupService:
    """Servicio para gestión de backups"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== BACKUPS ====================

    async def crear_backup(
        self,
        tipo: TipoBackup,
        nombre: str,
        descripcion: Optional[str] = None,
        automatico: bool = False,
        programacion_id: Optional[str] = None,
        usuario_id: Optional[str] = None,
    ) -> Backup:
        """Crear un nuevo backup"""

        # Configuración
        base_datos = os.getenv("POSTGRES_DB", "ddx_db")
        ruta_backups = os.getenv("BACKUP_PATH", "/var/backups/ddx")

        # Crear directorio si no existe
        Path(ruta_backups).mkdir(parents=True, exist_ok=True)

        # Nombre del archivo
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{nombre}_{timestamp}.sql.gz"
        ruta_archivo = os.path.join(ruta_backups, nombre_archivo)

        # Crear registro de backup
        backup = Backup(
            tipo=tipo,
            estado=EstadoBackup.PENDIENTE,
            nombre=nombre,
            descripcion=descripcion,
            ruta_archivo=ruta_archivo,
            base_datos=base_datos,
            automatico=automatico,
            programacion_id=programacion_id,
            usuario_id=usuario_id,
            comprimido=True,
            algoritmo_compresion="gzip",
        )

        self.db.add(backup)
        await self.db.commit()
        await self.db.refresh(backup)

        return backup

    async def ejecutar_backup(self, backup_id: str) -> Backup:
        """Ejecutar un backup"""

        result = await self.db.execute(select(Backup).where(Backup.id == backup_id))
        backup = result.scalar_one_or_none()

        if not backup:
            raise ValueError("Backup no encontrado")

        try:
            # Actualizar estado
            backup.estado = EstadoBackup.EN_PROGRESO
            backup.fecha_inicio = datetime.utcnow()
            await self.db.commit()

            # Ejecutar pg_dump
            resultado = await self._ejecutar_pg_dump(backup)

            if resultado["exito"]:
                backup.estado = EstadoBackup.COMPLETADO
                backup.fecha_fin = datetime.utcnow()
                backup.duracion_segundos = int(
                    (backup.fecha_fin - backup.fecha_inicio).total_seconds()
                )
                backup.tamano_bytes = resultado["tamano_bytes"]
                backup.checksum_md5 = resultado["checksum_md5"]
                backup.checksum_sha256 = resultado["checksum_sha256"]
                backup.version_postgresql = resultado.get("version_postgresql")
            else:
                backup.estado = EstadoBackup.FALLIDO
                backup.mensaje_error = resultado.get("error")

                # Crear alerta
                await self._crear_alerta_backup_fallido(backup)

            await self.db.commit()
            await self.db.refresh(backup)

            return backup

        except Exception as e:
            backup.estado = EstadoBackup.FALLIDO
            backup.mensaje_error = str(e)
            await self.db.commit()

            await self._crear_alerta_backup_fallido(backup)

            raise

    async def _ejecutar_pg_dump(self, backup: Backup) -> Dict[str, Any]:
        """Ejecutar pg_dump para crear el backup"""

        try:
            # Configuración de PostgreSQL
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            user = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "")
            database = backup.base_datos

            # Comando pg_dump
            env = os.environ.copy()
            env["PGPASSWORD"] = password

            # Archivo temporal sin comprimir
            archivo_temp = backup.ruta_archivo.replace(".gz", "")

            cmd = [
                "pg_dump",
                "-h",
                host,
                "-p",
                port,
                "-U",
                user,
                "-F",
                "p",  # Plain text format
                "-f",
                archivo_temp,
                database,
            ]

            # Ejecutar comando
            process = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hora timeout
            )

            if process.returncode != 0:
                return {"exito": False, "error": process.stderr}

            # Comprimir archivo
            with open(archivo_temp, "rb") as f_in:
                with gzip.open(backup.ruta_archivo, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Eliminar archivo temporal
            os.remove(archivo_temp)

            # Calcular checksums
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()

            with open(backup.ruta_archivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)

            # Obtener tamaño
            tamano_bytes = os.path.getsize(backup.ruta_archivo)

            # Obtener versión de PostgreSQL
            version_cmd = [
                "psql",
                "-h",
                host,
                "-p",
                port,
                "-U",
                user,
                "-t",
                "-c",
                "SELECT version();",
            ]
            version_process = subprocess.run(
                version_cmd, env=env, capture_output=True, text=True
            )
            version_postgresql = (
                version_process.stdout.strip()
                if version_process.returncode == 0
                else None
            )

            return {
                "exito": True,
                "tamano_bytes": tamano_bytes,
                "checksum_md5": md5_hash.hexdigest(),
                "checksum_sha256": sha256_hash.hexdigest(),
                "version_postgresql": version_postgresql,
            }

        except Exception as e:
            return {"exito": False, "error": str(e)}

    async def listar_backups(
        self,
        tipo: Optional[TipoBackup] = None,
        estado: Optional[EstadoBackup] = None,
        limite: int = 50,
    ) -> List[Backup]:
        """Listar backups"""

        query = select(Backup).order_by(Backup.created_at.desc())

        if tipo:
            query = query.where(Backup.tipo == tipo)

        if estado:
            query = query.where(Backup.estado == estado)

        query = query.limit(limite)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def eliminar_backup(self, backup_id: str) -> bool:
        """Eliminar un backup"""

        result = await self.db.execute(select(Backup).where(Backup.id == backup_id))
        backup = result.scalar_one_or_none()

        if not backup:
            return False

        # Eliminar archivo físico
        if os.path.exists(backup.ruta_archivo):
            os.remove(backup.ruta_archivo)

        # Eliminar registro
        await self.db.delete(backup)
        await self.db.commit()

        return True

    async def limpiar_backups_antiguos(self, dias_retencion: int = 30) -> int:
        """Limpiar backups antiguos según política de retención"""

        fecha_limite = datetime.utcnow() - timedelta(days=dias_retencion)

        result = await self.db.execute(
            select(Backup).where(
                and_(
                    Backup.created_at < fecha_limite,
                    Backup.estado == EstadoBackup.COMPLETADO,
                )
            )
        )
        backups_antiguos = result.scalars().all()

        eliminados = 0
        for backup in backups_antiguos:
            if await self.eliminar_backup(str(backup.id)):
                eliminados += 1

        return eliminados

    # ==================== PROGRAMACIÓN DE BACKUPS ====================

    async def crear_programacion(
        self,
        nombre: str,
        tipo_backup: TipoBackup,
        cron_expresion: str,
        retencion_dias: int = 30,
        descripcion: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ProgramacionBackup:
        """Crear programación de backup automático"""

        base_datos = os.getenv("POSTGRES_DB", "ddx_db")
        ruta_destino = os.getenv("BACKUP_PATH", "/var/backups/ddx")

        programacion = ProgramacionBackup(
            nombre=nombre,
            descripcion=descripcion,
            tipo_backup=tipo_backup,
            cron_expresion=cron_expresion,
            retencion_dias=retencion_dias,
            base_datos=base_datos,
            ruta_destino=ruta_destino,
            created_by=created_by,
        )

        self.db.add(programacion)
        await self.db.commit()
        await self.db.refresh(programacion)

        return programacion

    async def listar_programaciones(
        self, activo: Optional[bool] = None
    ) -> List[ProgramacionBackup]:
        """Listar programaciones de backups"""

        query = select(ProgramacionBackup).order_by(
            ProgramacionBackup.created_at.desc()
        )

        if activo is not None:
            query = query.where(ProgramacionBackup.activo == activo)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def actualizar_programacion(
        self,
        programacion_id: str,
        activo: Optional[bool] = None,
        cron_expresion: Optional[str] = None,
        retencion_dias: Optional[int] = None,
    ) -> ProgramacionBackup:
        """Actualizar programación de backup"""

        result = await self.db.execute(
            select(ProgramacionBackup).where(ProgramacionBackup.id == programacion_id)
        )
        programacion = result.scalar_one_or_none()

        if not programacion:
            raise ValueError("Programación no encontrada")

        if activo is not None:
            programacion.activo = activo

        if cron_expresion:
            programacion.cron_expresion = cron_expresion

        if retencion_dias:
            programacion.retencion_dias = retencion_dias

        await self.db.commit()
        await self.db.refresh(programacion)

        return programacion

    # ==================== RESTAURACIÓN ====================

    async def crear_restauracion(
        self,
        backup_id: str,
        tipo: TipoRestauracion,
        nombre: str,
        motivo: str,
        usuario_id: str,
        descripcion: Optional[str] = None,
        punto_tiempo: Optional[datetime] = None,
        tablas_restaurar: Optional[List[str]] = None,
    ) -> Restauracion:
        """Crear solicitud de restauración"""

        # Verificar que el backup existe
        result = await self.db.execute(select(Backup).where(Backup.id == backup_id))
        backup = result.scalar_one_or_none()

        if not backup:
            raise ValueError("Backup no encontrado")

        if backup.estado != EstadoBackup.COMPLETADO:
            raise ValueError("El backup no está completado")

        restauracion = Restauracion(
            backup_id=backup_id,
            tipo=tipo,
            nombre=nombre,
            descripcion=descripcion,
            motivo=motivo,
            punto_tiempo=punto_tiempo,
            tablas_restaurar=tablas_restaurar,
            base_datos_destino=backup.base_datos,
            usuario_id=usuario_id,
        )

        self.db.add(restauracion)
        await self.db.commit()
        await self.db.refresh(restauracion)

        return restauracion

    async def ejecutar_restauracion(
        self, restauracion_id: str, aprobado_por: str
    ) -> Restauracion:
        """Ejecutar una restauración (requiere aprobación)"""

        result = await self.db.execute(
            select(Restauracion).where(Restauracion.id == restauracion_id)
        )
        restauracion = result.scalar_one_or_none()

        if not restauracion:
            raise ValueError("Restauración no encontrada")

        # Marcar como aprobada
        restauracion.aprobado_por = aprobado_por
        restauracion.fecha_aprobacion = datetime.utcnow()
        restauracion.estado = EstadoRestauracion.EN_PROGRESO
        restauracion.fecha_inicio = datetime.utcnow()

        await self.db.commit()

        try:
            # Obtener backup
            result_backup = await self.db.execute(
                select(Backup).where(Backup.id == restauracion.backup_id)
            )
            backup = result_backup.scalar_one()

            # Ejecutar restauración
            resultado = await self._ejecutar_pg_restore(backup, restauracion)

            if resultado["exito"]:
                restauracion.estado = EstadoRestauracion.COMPLETADO
                restauracion.validacion_exitosa = True
            else:
                restauracion.estado = EstadoRestauracion.FALLIDO
                restauracion.mensaje_error = resultado.get("error")
                restauracion.validacion_exitosa = False

            restauracion.fecha_fin = datetime.utcnow()
            restauracion.duracion_segundos = int(
                (restauracion.fecha_fin - restauracion.fecha_inicio).total_seconds()
            )

            await self.db.commit()
            await self.db.refresh(restauracion)

            return restauracion

        except Exception as e:
            restauracion.estado = EstadoRestauracion.FALLIDO
            restauracion.mensaje_error = str(e)
            await self.db.commit()
            raise

    async def _ejecutar_pg_restore(
        self, backup: Backup, restauracion: Restauracion
    ) -> Dict[str, Any]:
        """Ejecutar pg_restore para restaurar el backup"""

        try:
            # Configuración
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            user = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "")
            database = restauracion.base_datos_destino

            env = os.environ.copy()
            env["PGPASSWORD"] = password

            # Descomprimir archivo
            archivo_descomprimido = backup.ruta_archivo.replace(".gz", "")

            with gzip.open(backup.ruta_archivo, "rb") as f_in:
                with open(archivo_descomprimido, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Comando psql para restaurar
            cmd = [
                "psql",
                "-h",
                host,
                "-p",
                port,
                "-U",
                user,
                "-d",
                database,
                "-f",
                archivo_descomprimido,
            ]

            # Ejecutar comando
            process = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hora timeout
            )

            # Eliminar archivo descomprimido
            os.remove(archivo_descomprimido)

            if process.returncode != 0:
                return {"exito": False, "error": process.stderr}

            return {"exito": True}

        except Exception as e:
            return {"exito": False, "error": str(e)}

    async def listar_restauraciones(self, limite: int = 50) -> List[Restauracion]:
        """Listar restauraciones"""

        result = await self.db.execute(
            select(Restauracion).order_by(Restauracion.created_at.desc()).limit(limite)
        )
        return result.scalars().all()

    # ==================== MONITOREO ====================

    async def registrar_salud_sistema(self) -> MonitoreoSalud:
        """Registrar métricas de salud del sistema"""

        # Obtener métricas de base de datos
        metricas_bd = await self._obtener_metricas_bd()

        # Obtener métricas de sistema (simuladas por ahora)
        metricas_sistema = await self._obtener_metricas_sistema()

        monitoreo = MonitoreoSalud(
            conexiones_activas=metricas_bd.get("conexiones_activas"),
            conexiones_maximas=metricas_bd.get("conexiones_maximas"),
            tamano_bd_bytes=metricas_bd.get("tamano_bd_bytes"),
            transacciones_por_segundo=metricas_bd.get("transacciones_por_segundo"),
            uso_cpu_porcentaje=metricas_sistema.get("uso_cpu"),
            uso_memoria_porcentaje=metricas_sistema.get("uso_memoria"),
            uso_disco_porcentaje=metricas_sistema.get("uso_disco"),
            espacio_disco_libre_gb=metricas_sistema.get("espacio_libre_gb"),
            estado_sistema="healthy",
            disponibilidad_porcentaje=99,
        )

        self.db.add(monitoreo)
        await self.db.commit()
        await self.db.refresh(monitoreo)

        return monitoreo

    async def _obtener_metricas_bd(self) -> Dict[str, Any]:
        """Obtener métricas de la base de datos"""

        try:
            # Conexiones activas
            result = await self.db.execute(
                select(func.count()).select_from(func.pg_stat_activity())
            )
            conexiones_activas = result.scalar() or 0

            # Tamaño de la base de datos
            result = await self.db.execute(
                select(func.pg_database_size(func.current_database()))
            )
            tamano_bd_bytes = result.scalar() or 0

            return {
                "conexiones_activas": conexiones_activas,
                "conexiones_maximas": 100,  # Configuración típica
                "tamano_bd_bytes": tamano_bd_bytes,
                "transacciones_por_segundo": 0,  # Requiere cálculo más complejo
            }
        except:
            return {
                "conexiones_activas": 0,
                "conexiones_maximas": 100,
                "tamano_bd_bytes": 0,
                "transacciones_por_segundo": 0,
            }

    async def _obtener_metricas_sistema(self) -> Dict[str, Any]:
        """Obtener métricas del sistema (simuladas)"""

        # En producción, usar psutil o similar
        return {
            "uso_cpu": 25,
            "uso_memoria": 60,
            "uso_disco": 45,
            "espacio_libre_gb": 100,
        }

    async def obtener_estadisticas_backups(self) -> Dict[str, Any]:
        """Obtener estadísticas de backups"""

        # Total de backups
        result = await self.db.execute(select(func.count(Backup.id)))
        total_backups = result.scalar() or 0

        # Backups completados
        result = await self.db.execute(
            select(func.count(Backup.id)).where(
                Backup.estado == EstadoBackup.COMPLETADO
            )
        )
        backups_completados = result.scalar() or 0

        # Backups fallidos
        result = await self.db.execute(
            select(func.count(Backup.id)).where(Backup.estado == EstadoBackup.FALLIDO)
        )
        backups_fallidos = result.scalar() or 0

        # Último backup exitoso
        result = await self.db.execute(
            select(Backup)
            .where(Backup.estado == EstadoBackup.COMPLETADO)
            .order_by(Backup.fecha_fin.desc())
            .limit(1)
        )
        ultimo_backup = result.scalar_one_or_none()

        # Tamaño total de backups
        result = await self.db.execute(
            select(func.sum(Backup.tamano_bytes)).where(
                Backup.estado == EstadoBackup.COMPLETADO
            )
        )
        tamano_total_bytes = result.scalar() or 0

        # Programaciones activas
        result = await self.db.execute(
            select(func.count(ProgramacionBackup.id)).where(
                ProgramacionBackup.activo == True
            )
        )
        programaciones_activas = result.scalar() or 0

        return {
            "total_backups": total_backups,
            "backups_completados": backups_completados,
            "backups_fallidos": backups_fallidos,
            "ultimo_backup": {
                "fecha": (
                    ultimo_backup.fecha_fin.isoformat()
                    if ultimo_backup and ultimo_backup.fecha_fin
                    else None
                ),
                "nombre": ultimo_backup.nombre if ultimo_backup else None,
                "tamano_mb": (
                    round(ultimo_backup.tamano_bytes / 1024 / 1024, 2)
                    if ultimo_backup and ultimo_backup.tamano_bytes
                    else 0
                ),
            },
            "tamano_total_gb": round(tamano_total_bytes / 1024 / 1024 / 1024, 2),
            "programaciones_activas": programaciones_activas,
        }

    # ==================== ALERTAS ====================

    async def _crear_alerta_backup_fallido(self, backup: Backup):
        """Crear alerta cuando un backup falla"""

        alerta = AlertaBackup(
            severidad=NivelSeveridad.ERROR,
            tipo="backup_fallido",
            titulo=f"Backup fallido: {backup.nombre}",
            mensaje=f"El backup '{backup.nombre}' ha fallado. Error: {backup.mensaje_error}",
            backup_id=backup.id,
        )

        self.db.add(alerta)
        await self.db.commit()

    async def listar_alertas(
        self, activas_solo: bool = True, limite: int = 50
    ) -> List[AlertaBackup]:
        """Listar alertas"""

        query = select(AlertaBackup).order_by(AlertaBackup.created_at.desc())

        if activas_solo:
            query = query.where(AlertaBackup.activa == True)

        query = query.limit(limite)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def resolver_alerta(
        self, alerta_id: str, resuelto_por: str, notas: str
    ) -> AlertaBackup:
        """Resolver una alerta"""

        result = await self.db.execute(
            select(AlertaBackup).where(AlertaBackup.id == alerta_id)
        )
        alerta = result.scalar_one_or_none()

        if not alerta:
            raise ValueError("Alerta no encontrada")

        alerta.activa = False
        alerta.fecha_resolucion = datetime.utcnow()
        alerta.resuelto_por = resuelto_por
        alerta.notas_resolucion = notas

        await self.db.commit()
        await self.db.refresh(alerta)

        return alerta
