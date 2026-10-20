import { describe, expect, it, vi } from 'vitest'
import { loginApi } from './authApi.js'

describe('authApi', () => {
  it('mapea 401', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 401 }))
    await expect(loginApi({ correo: 'x@b.com', password: 'x' })).rejects.toThrow('Correo o contraseña incorrectos.')
  })
  it('mapea falla de red', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('raw internal error')))
    await expect(loginApi({ correo: 'x@b.com', password: 'x' })).rejects.toThrow('No se pudo conectar con el servidor.')
  })
  it('consume contrato de éxito y body', async () => {
    const stub = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({correo: 'x@b.com', token: 'jwt', token_type: 'bearer'}) })
    vi.stubGlobal('fetch', stub)
    expect(await loginApi({ correo: 'x@b.com', password: 'abc' })).toEqual({correo: 'x@b.com', token: 'jwt'})
    expect(JSON.parse(stub.mock.calls[0][1].body)).toEqual({correo: 'x@b.com', password: 'abc'})
  })
})
