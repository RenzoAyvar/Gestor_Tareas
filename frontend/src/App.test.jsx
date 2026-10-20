import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from './App.jsx'
import * as api from './api/authApi.js'

vi.mock('./api/authApi.js', () => ({ loginApi: vi.fn() }))

describe('App login', () => {
  it('muestra planificador luego del login', async () => {
    api.loginApi.mockResolvedValue({ correo: 'admin@practica.com', token: 'fake-jwt' })
    render(<App />)
    fireEvent.change(screen.getByLabelText('Correo electrónico'), {target: {value: 'admin@practica.com'}})
    fireEvent.change(screen.getByLabelText('Contraseña'), {target: {value: 'admin123'}})
    fireEvent.click(screen.getByRole('button', {name: 'Iniciar sesión'}))
    await waitFor(() => expect(screen.getByText('Planificador de Visitas')).toBeInTheDocument())
    expect(screen.getByText(/Bienvenido,/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', {name: 'Cerrar sesión'}))
    expect(screen.getByRole('heading', {name:'Iniciar sesión'})).toBeInTheDocument()
  })
  it('no usa localStorage para token', async () => {
    api.loginApi.mockResolvedValue({ correo: 'admin@practica.com', token: 'sensitive-test-jwt' })
    render(<App />)
    fireEvent.change(screen.getByLabelText('Correo electrónico'), {target: {value: 'admin@practica.com'}})
    fireEvent.change(screen.getByLabelText('Contraseña'), {target: {value: 'admin123'}})
    fireEvent.click(screen.getByRole('button', {name: 'Iniciar sesión'}))
    await waitFor(() => expect(screen.getByText('Planificador de Visitas')).toBeInTheDocument())
    expect(JSON.stringify(localStorage)).not.toContain('sensitive-test-jwt')
    expect(localStorage.getItem('token')).toBeNull()
  })
})
