export function validateLogin({ correo = '', password = '' } = {}) {
  const errors = {}
  if (!correo) {
    errors.correo = 'El correo es obligatorio.'
  } else if (/\s/.test(correo)) {
    errors.correo = 'El correo no debe contener espacios en blanco.'
  } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(correo)) {
    errors.correo = 'Ingresá un correo válido.'
  }
  if (!password) errors.password = 'La contraseña es obligatoria.'
  return errors
}
