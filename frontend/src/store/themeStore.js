import create from 'zustand';
import { persist } from 'zustand/middleware';

const useThemeStore = create(
  persist(
    (set) => ({
      isDarkMode: false,
      toggleTheme: () => {
        set((state) => {
          const newIsDarkMode = !state.isDarkMode;
          // Update the class on the html element
          if (newIsDarkMode) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { isDarkMode: newIsDarkMode };
        });
      },
    }),
    {
      name: 'theme-storage',
    }
  )
);

// Initialize theme from storage on page load
if (typeof window !== 'undefined') {
  const theme = localStorage.getItem('theme-storage');
  if (theme) {
    const { state } = JSON.parse(theme);
    if (state.isDarkMode) {
      document.documentElement.classList.add('dark');
    }
  }
}

export default useThemeStore;
