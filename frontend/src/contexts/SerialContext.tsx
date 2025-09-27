import React, { createContext, useContext, useEffect, useState } from 'react';
import { usePywebviewApi } from '../hooks/usePywebviewApi';

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
  
  // Use the hook for all pywebview API interactions
  const pywebviewApi = usePywebviewApi();

  const checkConnection = async (): Promise<void> => {
    try {
      setError(null);
      
      if (!pywebviewApi) {
        throw new Error('Python backend API is not available');
      }

      const result = await pywebviewApi.serial_port_available();
      setSerialConnected(result?.available === true);
      console.log('Serial connection status:', result);
    } catch (err) {
      console.error('Error checking serial connection:', err);
      setError(err instanceof Error ? err.message : String(err));
      setSerialConnected(false);
    }
  };

  const toggleMonitoring = async (): Promise<void> => {
    if (!pywebviewApi) {
      setError('Backend API is not ready');
      return;
    }

    const newState = !monitoring;
    setMonitoring(newState);

    try {
      if (newState) {
        await pywebviewApi.start_serial_monitor();
      } else {
        await pywebviewApi.stop_serial_monitor();
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
    if (!pywebviewApi) return;

    // 🔁 Overwrite handlers when API is ready
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

    // Check initial connection status
    checkConnection();
  }, [pywebviewApi, monitoring]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      // Stop monitoring on unmount if active
      if (pywebviewApi && monitoring) {
        pywebviewApi.stop_serial_monitor().catch(console.error);
      }

      // ✅ Cleanup global handlers to prevent stale closures
      window.onSerialLine = undefined;
      window.onSerialStatusUpdate = undefined;
    };
  }, [pywebviewApi, monitoring]);

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