window.HorizonBI = window.HorizonBI || {};
window.HorizonBI.embedPowerBI = function (containerId, scriptId) {
  const container = document.getElementById(containerId);
  const script = document.getElementById(scriptId);
  if (!container || !script || !window['powerbi-client']) return;
  let config;
  try {
    config = JSON.parse(script.textContent);
  } catch (error) {
    console.error('Invalid Power BI config', error);
    return;
  }
  const models = window['powerbi-client'].models;
  const embedConfig = {
    type: config.type,
    tokenType: models.TokenType.Embed,
    accessToken: config.accessToken,
    embedUrl: config.embedUrl,
    id: config.reportId,
    settings: {
      panes: {
        filters: { visible: false },
        pageNavigation: { visible: true },
      },
      background: models.BackgroundType.Transparent,
    },
  };
  window.powerbi.embed(container, embedConfig);
};
