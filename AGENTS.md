# Instrucciones compartidas para Codex (Evaluación 2)

1. **Antes de editar**, leer `specs/001-login/spec.md`, `specs/001-login/contract.md`, `specs/001-login/plan.md`, `specs/001-login/tasks.md` y `harness/policies/quality-gates.md`.
2. Respetar rutas autorizadas de la SPEC para cambios **de funcionalidad de login**. Para cambios de infraestructura/scaffolding hacer PR separado y justificar rutas adicionales.
3. Coordinar roles `frontend`, `backend`, `qa`, `devops`. En trabajos en paralelo, evitar que subagentes editen el mismo archivo simultáneamente.
4. Seguir contrato: `POST /auth/login`; body `{correo,password}`; éxito `{correo,token,token_type}`; 401 genérico; 422 esquema FastAPI.
5. Backend: router delgado, servicio asíncrono, SQLAlchemy/asyncpg, bcrypt y JWT con secreto de entorno. No filtrar `password_hash` ni secretos.
6. Frontend: JSX + Fetch API, token **solo en estado React**, validaciones y mensajes exactos de la SPEC. Tema es lo único persistido en localStorage.
7. Ejecutar `python harness/scripts/verify.py --scope spec` y comprobaciones de implementación. Si fallan, explicar cuál fue la causa; nunca inventar evidencia, saltar tests ni alterar asserts para hacerlos pasar.
8. Mantener la trazabilidad SPEC → escenario → prueba. La SPEC aprobada no cambia como efecto secundario de errores de implementación.
9. No cambiar `harness/`, CI, secretos o restricciones de ramas sin PR revisado por equipo responsable.
10. Entrega: describir archivos cambiados, decisiones, riesgos, comandos ejecutados, pruebas aprobadas/fallidas/bloqueadas.
