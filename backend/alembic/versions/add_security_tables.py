"""add_security_tables

Revision ID: security_001
Revises: cie10_001
Create Date: 2025-12-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "security_001"
down_revision = "cie10_001"
branch_labels = None
depends_on = None


def upgrade():
    # TwoFactorAuth
    op.create_table(
        "two_factor_auth",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("secret_key", sa.String(255), nullable=False),
        sa.Column("backup_codes", postgresql.JSONB, nullable=True),
        sa.Column("enabled", sa.Boolean, server_default="false"),
        sa.Column("verified", sa.Boolean, server_default="false"),
        sa.Column("method", sa.String(50), server_default="totp"),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id"),
    )
    op.create_index("ix_two_factor_auth_usuario_id", "two_factor_auth", ["usuario_id"])

    # AuditLog
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("accion", sa.String(100), nullable=False),
        sa.Column("recurso", sa.String(100), nullable=False),
        sa.Column("recurso_id", sa.String(255), nullable=True),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("datos_anteriores", postgresql.JSONB, nullable=True),
        sa.Column("datos_nuevos", postgresql.JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("metodo_http", sa.String(10), nullable=True),
        sa.Column("endpoint", sa.String(255), nullable=True),
        sa.Column("exitoso", sa.Boolean, server_default="true"),
        sa.Column("codigo_estado", sa.Integer, nullable=True),
        sa.Column("mensaje_error", sa.Text, nullable=True),
        sa.Column("metadata_extra", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_usuario_id", "audit_logs", ["usuario_id"])
    op.create_index("ix_audit_logs_accion", "audit_logs", ["accion"])
    op.create_index("ix_audit_logs_recurso", "audit_logs", ["recurso"])
    op.create_index("ix_audit_logs_recurso_id", "audit_logs", ["recurso_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # UserSession
    op.create_table(
        "user_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_token", sa.String(255), nullable=False),
        sa.Column("refresh_token", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("device_info", postgresql.JSONB, nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("activa", sa.Boolean, server_default="true"),
        sa.Column("revocada", sa.Boolean, server_default="false"),
        sa.Column("motivo_revocacion", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token"),
        sa.UniqueConstraint("refresh_token"),
    )
    op.create_index("ix_user_sessions_usuario_id", "user_sessions", ["usuario_id"])
    op.create_index(
        "ix_user_sessions_session_token", "user_sessions", ["session_token"]
    )
    op.create_index("ix_user_sessions_activa", "user_sessions", ["activa"])

    # Permission
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("modulo", sa.String(50), nullable=False),
        sa.Column("recurso", sa.String(50), nullable=False),
        sa.Column("accion", sa.String(50), nullable=False),
        sa.Column("activo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
        sa.UniqueConstraint("codigo"),
    )
    op.create_index("ix_permissions_nombre", "permissions", ["nombre"])
    op.create_index("ix_permissions_codigo", "permissions", ["codigo"])
    op.create_index("ix_permissions_modulo", "permissions", ["modulo"])

    # Role
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("nivel", sa.Integer, server_default="0"),
        sa.Column("rol_padre_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("activo", sa.Boolean, server_default="true"),
        sa.Column("es_sistema", sa.Boolean, server_default="false"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(["rol_padre_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
        sa.UniqueConstraint("codigo"),
    )
    op.create_index("ix_roles_nombre", "roles", ["nombre"])
    op.create_index("ix_roles_codigo", "roles", ["codigo"])

    # RolePermission
    op.create_table(
        "role_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("concedido_por_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["permissions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["concedido_por_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_role_permissions_role_id", "role_permissions", ["role_id"])
    op.create_index(
        "ix_role_permissions_permission_id", "role_permissions", ["permission_id"]
    )

    # UserRole
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asignado_por_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["asignado_por_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_roles_usuario_id", "user_roles", ["usuario_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])

    # SSOProvider
    op.create_table(
        "sso_providers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("client_id", sa.String(255), nullable=False),
        sa.Column("client_secret", sa.String(255), nullable=False),
        sa.Column("authorization_endpoint", sa.String(500), nullable=True),
        sa.Column("token_endpoint", sa.String(500), nullable=True),
        sa.Column("userinfo_endpoint", sa.String(500), nullable=True),
        sa.Column("redirect_uri", sa.String(500), nullable=False),
        sa.Column("scopes", postgresql.JSONB, nullable=True),
        sa.Column("metadata_config", postgresql.JSONB, nullable=True),
        sa.Column("activo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )

    # SSOConnection
    op.create_table(
        "sso_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("external_email", sa.String(255), nullable=True),
        sa.Column("external_username", sa.String(255), nullable=True),
        sa.Column("access_token", sa.Text, nullable=True),
        sa.Column("refresh_token", sa.Text, nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("profile_data", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["provider_id"], ["sso_providers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sso_connections_usuario_id", "sso_connections", ["usuario_id"])
    op.create_index(
        "ix_sso_connections_external_id", "sso_connections", ["external_id"]
    )

    # EncryptedData
    op.create_table(
        "encrypted_data",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recurso_tipo", sa.String(50), nullable=False),
        sa.Column("recurso_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campo", sa.String(100), nullable=False),
        sa.Column("datos_encriptados", sa.Text, nullable=False),
        sa.Column("algoritmo", sa.String(50), server_default="AES-256-GCM"),
        sa.Column("iv", sa.String(255), nullable=True),
        sa.Column("encriptado_por_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(["encriptado_por_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_encrypted_data_recurso_tipo", "encrypted_data", ["recurso_tipo"]
    )
    op.create_index("ix_encrypted_data_recurso_id", "encrypted_data", ["recurso_id"])


def downgrade():
    op.drop_table("encrypted_data")
    op.drop_table("sso_connections")
    op.drop_table("sso_providers")
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("roles")
    op.drop_table("permissions")
    op.drop_table("user_sessions")
    op.drop_table("audit_logs")
    op.drop_table("two_factor_auth")
