// src/hooks/usePywebviewApi.ts
import { useEffect, useState } from "react";

export function usePywebviewApi<T extends keyof typeof window.pywebview.api>(
  method?: T,
  intervalMs: number = 500
) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const checkReady = () => {
      if (window.pywebview?.api) {
        if (method && !(method in window.pywebview.api)) {
          return false;
        }
        setReady(true);
        return true;
      }
      return false;
    };

    if (!checkReady()) {
      interval = setInterval(() => {
        if (checkReady()) clearInterval(interval);
      }, intervalMs);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [method, intervalMs]);

  return ready ? window.pywebview.api : null;
}
