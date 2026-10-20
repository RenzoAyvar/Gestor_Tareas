# Quality Gates (v1)

## G0 — Contrato y trazabilidad
- Deben existir `spec.md`, `plan.md`, `tasks.md`, `contract.md` y trazabilidad AC-001...AC-007.
- Cada criterio de aceptación debe enlazar a uno o más archivos de prueba existentes.
- El agente debe leer SPEC antes de programar. Cambios al contrato requieren PR explícito.

## G1 — Backend
- Pruebas de integración HTTP con PostgreSQL real: 200, 401 usuario desconocido, 401 contraseña incorrecta, 422 inválidos.
- Contraseña usando bcrypt; no filtrar `password_hash`; JWT HS256, expiración y secreto de entorno.
- Pruebas fallidas no se silencian.

## G2 — Frontend
- Tests Vitest para validaciones, error mapping, navegación, sesión en memoria y tema persistente.
- `npm run build` exitoso.
- No se debe llamar al backend con campos inválidos.

## G3 — Integración
- Pipeline CI ejecuta G0, G1 y G2 en cada PR contra main.
- Revisar impactos compartidos frontend/backend. PR requiere revisión humana según políticas del repo.

## G4 — Despliegue
- Secretos fuera de Git. Imagen publicada en GHCR no equivale a servidor desplegado.
- Producción requiere servidor preconfigurado, secretos, revisión/aprobación del entorno y despliegue explícito.

## Resultados
APROBADO = comando devuelve 0 y evidencia disponible. RECHAZADO = test fallido. BLOQUEADO = infraestructura/dependencias no disponibles.
