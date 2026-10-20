import { describe, it, expect } from 'vitest'
import { validateLogin } from './validateLogin.js'

describe('validateLogin', () => {
  it('muestra errores de obligatorios', () => {
    expect(validateLogin({ correo: '', password: '' })).toEqual({
      correo: 'El correo es obligatorio.', password: 'La contraseña es obligatoria.'
    })
  })
  it('rechaza espacios', () => {
    expect(validateLogin({ correo: ' a@b.com', password: 'pass' }).correo).toBe('El correo no debe contener espacios en blanco.')
  })
  it('rechaza formato inválido', () => {
    expect(validateLogin({ correo: 'abc', password: 'pass' }).correo).toBe('Ingresá un correo válido.')
  })
  it('acepta datos válidos', () => {
    expect(validateLogin({ correo: 'abc@b.com', password: 'pass' })).toEqual({})
  })
})
