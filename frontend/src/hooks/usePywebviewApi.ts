// src/hooks/usePywebviewApi.ts
import { useEffect, useState } from "react";

declare global {
  interface Window {
    pywebview?: {
      api: any;
    };
  }
}

export function usePywebviewApi() {
  const [api, setApi] = useState<any>(() => {
    // Initialize with current value if available
    return window.pywebview?.api || null;
  });

  useEffect(() => {
    // If already available, we're done
    if (window.pywebview?.api) {
      setApi(window.pywebview.api);
      return;
    }

    // Listen for pywebview ready event if it exists
    const handleReady = () => {
      if (window.pywebview?.api) {
        setApi(window.pywebview.api);
      }
    };

    // Some pywebview versions fire a ready event
    window.addEventListener('pywebviewready', handleReady);

    // Fallback: poll for a short time
    const interval = setInterval(() => {
      if (window.pywebview?.api) {
        setApi(window.pywebview.api);
        clearInterval(interval);
      }
    }, 100);

    // Stop polling after 3 seconds
    setTimeout(() => {
      clearInterval(interval);
    }, 3000);

    return () => {
      clearInterval(interval);
      window.removeEventListener('pywebviewready', handleReady);
    };
  }, []);

  return api;
}