import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isAdmin: false,

      setAuth: (token, user) => set({
        token,
        user,
        isAuthenticated: true,
        isAdmin: user?.role === 'admin'
      }),

      logout: () => set({
        token: null,
        user: null,
        isAuthenticated: false,
        isAdmin: false
      }),

      updateUser: (user) => set({ user })
    }),
    {
      name: 'auth-storage',
    }
  )
);
