export const environment = {
  production: false,
  urlFront: (window as any).env?.URL_FRONT || 'http://localhost:4200',
  urlBack: ((window as any).env?.URL_BACK || 'http://localhost:5000').replace(/\/$/, '')
};
