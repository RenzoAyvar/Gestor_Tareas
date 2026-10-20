export class AuthError extends Error {
  constructor(message, status = null) {
    super(message)
    this.name = 'AuthError'
    this.status = status
  }
}

export async function loginApi({ correo, password }) {
  let response
  try {
    response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, password }),
    })
  } catch {
    throw new AuthError('No se pudo conectar con el servidor.')
  }
  if (!response.ok) {
    if ([400, 401].includes(response.status)) {
      throw new AuthError('Correo o contraseña incorrectos.', response.status)
    }
    throw new AuthError('No se pudo iniciar sesión. Intentá de nuevo.', response.status)
  }
  let payload
  try {
    payload = await response.json()
  } catch {
    throw new AuthError('No se pudo iniciar sesión. Intentá de nuevo.', response.status)
  }
  if (!payload?.token || !payload?.correo || payload?.token_type !== 'bearer') {
    throw new AuthError('No se pudo iniciar sesión. Intentá de nuevo.', response.status)
  }
  return { correo: payload.correo, token: payload.token }
}
