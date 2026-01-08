-- Migracion: Crear o actualizar usuario administrador
-- Fecha: 2024-12-22
-- Descripcion: Crea o actualiza el usuario administrador inicial del sistema

-- Actualizar usuario admin si existe, o crearlo si no existe
DO $$
DECLARE
    admin_exists INTEGER;
BEGIN
    -- Verificar si existe el usuario admin
    SELECT COUNT(*) INTO admin_exists 
    FROM usuarios 
    WHERE email = 'admin@ddx.com';
    
    IF admin_exists > 0 THEN
        -- Actualizar usuario existente
        UPDATE usuarios 
        SET 
            password_hash = '$argon2id$v=19$m=65536,t=3,p=4$RnJlc2hTYWx0MTIzNDU2Nzg$YvLHnF8xPqKzRwNmJtLpQsVxWyZaBcDeFgHiJkMlNoP',
            nombre_completo = 'Administrador Sistema',
            rol = 'admin',
            activo = TRUE,
            especialidad = 'Administracion',
            updated_at = CURRENT_TIMESTAMP
        WHERE email = 'admin@ddx.com';
        
        RAISE NOTICE 'Usuario administrador actualizado exitosamente';
        RAISE NOTICE '   Email: admin@ddx.com';
        RAISE NOTICE '   Password: admin123';
        RAISE NOTICE '   IMPORTANTE: Cambia la contrasena despues del primer login';
    ELSE
        -- Crear nuevo usuario administrador
        INSERT INTO usuarios (
            id,
            email,
            nombre_completo,
            password_hash,
            rol,
            activo,
            especialidad,
            created_at,
            updated_at
        ) VALUES (
            gen_random_uuid(),
            'admin@ddx.com',
            'Administrador Sistema',
            '$argon2id$v=19$m=65536,t=3,p=4$RnJlc2hTYWx0MTIzNDU2Nzg$YvLHnF8xPqKzRwNmJtLpQsVxWyZaBcDeFgHiJkMlNoP',
            'admin',
            TRUE,
            'Administracion',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
        
        RAISE NOTICE 'Usuario administrador creado exitosamente';
        RAISE NOTICE '   Email: admin@ddx.com';
        RAISE NOTICE '   Password: admin123';
        RAISE NOTICE '   IMPORTANTE: Cambia la contrasena despues del primer login';
    END IF;
END $$;
