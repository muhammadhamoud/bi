(function () {
  const stored = localStorage.getItem('theme');
  const preferred = stored || window.__themePreference || 'system';
  const shouldDark = preferred === 'dark' || (preferred === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  if (shouldDark) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (button) {
      button.addEventListener('click', function () {
        const currentlyDark = document.documentElement.classList.contains('dark');
        const nextTheme = currentlyDark ? 'light' : 'dark';
        localStorage.setItem('theme', nextTheme);
        document.documentElement.classList.toggle('dark', nextTheme === 'dark');
      });
    });
  });
})();
