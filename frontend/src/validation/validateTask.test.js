import { describe, expect, it } from 'vitest'
import { validateTask } from './validateTask.js'

describe('validateTask', () => {
  it('valida campos obligatorios límites y fecha', () => {
    expect(validateTask({ titulo: ' ', descripcion: '', fecha_limite: '' })).toEqual({
      titulo: 'El título es obligatorio.',
      descripcion: 'La descripción es obligatoria.',
    })
    expect(validateTask({ titulo: 'x'.repeat(121), descripcion: 'x'.repeat(1001), fecha_limite: '2026-02-30' })).toEqual({
      titulo: 'El título no puede superar los 120 caracteres.',
      descripcion: 'La descripción no puede superar los 1000 caracteres.',
      fecha_limite: 'Ingresá una fecha límite válida.',
    })
  })

  it('acepta fecha opcional y datos válidos', () => {
    expect(validateTask({ titulo: 'Parcial', descripcion: 'Estudiar unidad 2' })).toEqual({})
    expect(validateTask({ titulo: 'Parcial', descripcion: 'Estudiar', fecha_limite: '2026-10-30' })).toEqual({})
  })
})
