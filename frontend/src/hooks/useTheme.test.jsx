import { expect, it } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useTheme } from './useTheme.js'

it('persiste el tema', () => {
  const { result } = renderHook(() => useTheme())
  const old = result.current.theme
  act(() => result.current.toggleTheme())
  expect(result.current.theme).not.toBe(old)
  expect(localStorage.getItem('practica-1:theme')).toBe(result.current.theme)
  expect(document.documentElement.dataset.theme).toBe(result.current.theme)
})
