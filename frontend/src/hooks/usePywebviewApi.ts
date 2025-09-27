// src/hooks/usePywebviewApi.ts
import { useEffect, useState } from "react";

export function usePywebviewApi(method?: string) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let interval: number | undefined;

    const checkReady = () => {
      if (window.pywebview?.api) {
        // If a specific method is requested, check if it exists
        if (method && !(method in window.pywebview.api)) {
          return false;
        }
        setReady(true);
        return true;
      }
      return false;
    };

    if (!checkReady()) {
      interval = window.setInterval(() => {
        if (checkReady() && interval) {
          window.clearInterval(interval);
        }
      }, 500);
    }

    return () => {
      if (interval) {
        window.clearInterval(interval);
      }
    };
  }, [method]);

  // Add null safety check
  return ready && window.pywebview ? window.pywebview.api : null;
}