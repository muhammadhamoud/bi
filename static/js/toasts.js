document.addEventListener('DOMContentLoaded', () => {
  const dismissToast = (toast) => {
    if (!toast || toast.dataset.state === 'closing') return;
    toast.dataset.state = 'closing';
    toast.classList.add('translate-x-4', 'opacity-0');
    window.setTimeout(() => toast.remove(), 220);
  };

  document.querySelectorAll('[data-toast]').forEach((toast) => {
    const timeout = Number(toast.dataset.timeout || 5000);
    const progress = toast.querySelector('.toast-progress');
    if (progress) {
      progress.style.transition = `transform ${timeout}ms linear`;
      requestAnimationFrame(() => {
        progress.style.transform = 'scaleX(0)';
      });
    }
    const closeButton = toast.querySelector('.toast-dismiss');
    if (closeButton) {
      closeButton.addEventListener('click', () => dismissToast(toast));
    }
    window.setTimeout(() => dismissToast(toast), timeout);
  });
});
