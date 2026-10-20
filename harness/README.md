# Harness Engineering — Evaluación 2

El Harness no es solo esta carpeta. Es el conjunto compuesto por:
- Instrucciones: `AGENTS.md` y configuraciones de `.codex/agents/`.
- Políticas: `harness/policies/quality-gates.md`.
- Ejecución determinista: `harness/scripts/verify.py`.
- Reglas de colaboración: `CODEOWNERS`, PR reviews y protecciones de rama.
- CI: `.github/workflows/ci.yml` (ejecuta gates en ambiente limpio), CD controlado.

## Comandos

```bash
python harness/scripts/verify.py --scope spec
python harness/scripts/verify.py --scope frontend
python harness/scripts/verify.py --scope backend
python harness/scripts/verify.py --scope all
```

`--scope spec` valida archivos/IDs/referencias sin dependencias. `backend` requiere Python+deps+PostgreSQL; `frontend` requiere npm packages. `all` requiere ambos. La salida guarda `harness/reports/last-run.json`, ignorado por Git. El Harness no sustituye la revisión humana de ambigüedades, seguridad ni cobertura semántica de requisitos.

**Evitar falsos positivos:** no marcar la tarea completada cuando faltan dependencias o no existe base de datos; reportar `BLOQUEADO`.
