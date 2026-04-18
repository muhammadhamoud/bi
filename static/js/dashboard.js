window.HorizonBI = window.HorizonBI || {};
window.HorizonBI.renderChartFromScript = function (canvasId, scriptId) {
  const canvas = document.getElementById(canvasId);
  const script = document.getElementById(scriptId);
  if (!canvas || !script || !window.Chart) return;
  let config;
  try {
    config = JSON.parse(script.textContent);
  } catch (error) {
    console.error('Invalid chart config', error);
    return;
  }
  const context = canvas.getContext('2d');
  return new Chart(context, config);
};
