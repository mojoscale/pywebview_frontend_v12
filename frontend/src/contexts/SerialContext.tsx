import React, { createContext, useContext, useEffect, useState } from 'react';

interface SerialContextType {
  serialConnected: boolean;
  toggleMonitoring: () => Promise<void>;
  monitoring: boolean;
  serialOutput: string[];
  clearOutput: () => void;
  error: string | null;
  checkConnection: () => Promise<void>;
}

// ✅ Ensure window handlers exist early to prevent Python-side errors
if (typeof window.onSerialStatusUpdate !== 'function') {
  window.onSerialStatusUpdate = () => {
    console.warn('[Default onSerialStatusUpdate] Called before React initialized.');
  };
}

if (typeof window.onSerialLine !== 'function') {
  window.onSerialLine = () => {
    console.warn('[Default onSerialLine] Called before React initialized.');
  };
}

const SerialContext = createContext<SerialContextType>({
  serialConnected: false,
  toggleMonitoring: async () => {},
  monitoring: false,
  serialOutput: [],
  clearOutput: () => {},
  error: null,
  checkConnection: async () => {},
});

export const useSerial = () => useContext(SerialContext);

export const SerialProvider = ({ children }: { children: React.ReactNode }) => {
  const [serialConnected, setSerialConnected] = useState(false);
  const [monitoring, setMonitoring] = useState(false);
  const [serialOutput, setSerialOutput] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [apiReady, setApiReady] = useState(false);

  const waitForApi = async (maxRetries = 5, interval = 500): Promise<boolean> => {
    let retries = 0;
    
    const checkApi = () => {
      return typeof window.pywebview?.api?.serial_port_available === 'function';
    };

    if (checkApi()) return true;

    return new Promise((resolve) => {
      const timer = setInterval(() => {
        retries++;
        if (checkApi()) {
          clearInterval(timer);
          resolve(true);
        } else if (retries >= maxRetries) {
          clearInterval(timer);
          console.warn(`API not available after ${maxRetries} retries`);
          resolve(false);
        }
      }, interval);
    });
  };

  const checkConnection = async (): Promise<void> => {
    try {
      setError(null);
      const isApiReady = await waitForApi();
      
      if (!isApiReady) {
        throw new Error('Python backend API is not available');
      }

      const result = await window.pywebview.api.serial_port_available();
      setSerialConnected(result?.available === true);
      console.log('Serial connection status:', result);
    } catch (err) {
      console.error('Error checking serial connection:', err);
      setError(err instanceof Error ? err.message : String(err));
      setSerialConnected(false);
    }
  };

  const toggleMonitoring = async (): Promise<void> => {
    if (!apiReady) {
      setError('Backend API is not ready');
      return;
    }

    const newState = !monitoring;
    setMonitoring(newState);

    try {
      if (newState) {
        await window.pywebview.api.start_serial_monitor();
      } else {
        await window.pywebview.api.stop_serial_monitor();
      }
      console.log(`Serial monitoring ${newState ? 'started' : 'stopped'}`);
    } catch (err) {
      console.error('Error toggling serial monitor:', err);
      setError(err instanceof Error ? err.message : String(err));
      setMonitoring(!newState); // Revert state on error
    }
  };

  const clearOutput = () => {
    setSerialOutput([]);
  };

  // 🔁 Initialize and register handlers
  useEffect(() => {
    const initialize = async () => {
      try {
        if (!window.pywebview) {
          await new Promise<void>((resolve) => {
            const handler = () => {
              window.removeEventListener('pywebviewready', handler);
              resolve();
            };
            window.addEventListener('pywebviewready', handler);
          });
        }

        const isReady = await waitForApi();
        setApiReady(isReady);

        if (isReady) {
          // 🔁 Overwrite handlers after React mount
          window.onSerialLine = (line: string) => {
            if (monitoring) {
              setSerialOutput(prev => [...prev, line]);
            }
          };

          window.onSerialStatusUpdate = (connected: boolean) => {
            setSerialConnected(connected);
            if (!connected && monitoring) {
              setMonitoring(false);
            }
          };

          await checkConnection();
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setError(err instanceof Error ? err.message : String(err));
      }
    };

    initialize();

    return () => {
      if (window.pywebview?.api?.stop_serial_monitor && monitoring) {
        window.pywebview.api.stop_serial_monitor().catch(console.error);
      }

      // ✅ Cleanup global handlers to prevent stale closures
      window.onSerialLine = undefined;
      window.onSerialStatusUpdate = undefined;
    };
  }, []);

  return (
    <SerialContext.Provider
      value={{
        serialConnected,
        toggleMonitoring,
        monitoring,
        serialOutput,
        clearOutput,
        error,
        checkConnection,
      }}
    >
      {children}
    </SerialContext.Provider>
  );
};