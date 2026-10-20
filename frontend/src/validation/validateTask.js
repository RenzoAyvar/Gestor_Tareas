const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/

function isRealDate(value) {
  if (!DATE_PATTERN.test(value)) return false
  const [year, month, day] = value.split('-').map(Number)
  const date = new Date(Date.UTC(year, month - 1, day))
  return date.getUTCFullYear() === year
    && date.getUTCMonth() === month - 1
    && date.getUTCDate() === day
}

export function validateTask({ titulo = '', descripcion = '', fecha_limite = '' } = {}) {
  const errors = {}
  if (!titulo.trim()) errors.titulo = 'El título es obligatorio.'
  else if (titulo.length > 120) errors.titulo = 'El título no puede superar los 120 caracteres.'

  if (!descripcion.trim()) errors.descripcion = 'La descripción es obligatoria.'
  else if (descripcion.length > 1000) errors.descripcion = 'La descripción no puede superar los 1000 caracteres.'

  if (fecha_limite && !isRealDate(fecha_limite)) {
    errors.fecha_limite = 'Ingresá una fecha límite válida.'
  }
  return errors
}
