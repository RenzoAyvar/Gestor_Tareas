# Guía: SDD + Harness + Subagentes + PR

Ejemplo de prompt al agente principal desde el root del proyecto:

> Lee AGENTS.md y la SPEC modular aplicable, por ejemplo `specs/auth/login.scps`. Primero delega análisis de contrato a backend y frontend; identifica dependencias entre ambos. Luego implementa por responsabilidades, sin edición simultánea del mismo archivo. Pide a QA pruebas contractuales y a DevOps verificar Harness y Docker/CI. Ejecuta `python harness/scripts/verify.py --scope spec` y los comandos completos disponibles; no declares tests aprobados sin ejecución real. Resume resultados y prepara PR.

## Ciclo de cambios posterior

1. Crear `specs/<módulo>/<nombre>.scps` con máximo 150 líneas o aprobar un cambio a una SPEC existente.
2. Crear o actualizar `specs/<módulo>/traceability.json`; compartir cambios de contrato antes de codificar.
3. Rama Git propia. La IA usa el mismo `AGENTS.md` y subagentes versionados.
4. Ejecutar Harness local, luego PR CI, revisión humana y merge.
5. Actualizar ramas de otros colaboradores; volver a ejecutar regresión al resolver conflictos.

## Restricción de archivos

La lista permitida de SPEC 001 aplica **durante tareas de modificación del login**. El armazón creado aquí necesitó otros archivos: se distingue explícitamente para no violar el alcance de cambios futuros. Pedir autorización para tocar infraestructura, Harness o contratos de otros módulos.
