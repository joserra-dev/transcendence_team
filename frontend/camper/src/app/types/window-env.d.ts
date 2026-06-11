declare global {
  interface Window {
    env: {
      URL_FRONT: string;
      URL_BACK: string;
    };
  }
}

export {};