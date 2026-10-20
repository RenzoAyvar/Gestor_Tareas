import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import LoginForm from './LoginForm.jsx'

describe('LoginForm', () => {
  it('no envía campos vacíos', () => {
    const onLogin = vi.fn()
    render(<LoginForm onLogin={onLogin} loading={false} error="" />)
    fireEvent.click(screen.getByRole('button', {name: 'Iniciar sesión'}))
    expect(screen.getByText('El correo es obligatorio.')).toBeInTheDocument()
    expect(screen.getByText('La contraseña es obligatoria.')).toBeInTheDocument()
    expect(onLogin).not.toHaveBeenCalled()
  })
  it('loading deshabilita botón', () => {
    render(<LoginForm onLogin={vi.fn()} loading={true} error="" />)
    expect(screen.getByRole('button', {name: 'Iniciando sesión…'})).toBeDisabled()
  })
  it('error general usa role alert', () => {
    render(<LoginForm onLogin={vi.fn()} loading={false} error="Correo o contraseña incorrectos." />)
    expect(screen.getByRole('alert')).toHaveTextContent('Correo o contraseña incorrectos.')
  })
})
