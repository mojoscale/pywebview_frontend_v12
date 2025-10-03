import React, { createContext, useContext, useEffect, useState } from 'react';

interface SerialContextType {
  serialConnected: boolean;
  toggleMonitoring: () => Promise<void>;
  monitoring: boolean;
  serialOutput: string[];
  clearOutput: () => void;
  error: string | null;
  checkConnection: () => Promise<void>;
  terminalLogs: string[];  // ✅ compiler/terminal logs
  clearTerminal: () => void;
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

if (typeof window.__appendTerminalLog !== 'function') {
  window.__appendTerminalLog = (line: string) => {
    console.warn('[Default __appendTerminalLog] Called before React initialized. Line:', line);
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
  terminalLogs: [],
  clearTerminal: () => {},
});

export const useSerial = () => useContext(SerialContext);

export const SerialProvider = ({ children }: { children: React.ReactNode }) => {
  const [serialConnected, setSerialConnected] = useState(false);
  const [monitoring, setMonitoring] = useState(false);
  const [serialOutput, setSerialOutput] = useState<string[]>([]);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isApiReady, setIsApiReady] = useState(false);

  // ✅ Wait for pywebview API to be ready
  useEffect(() => {
    const checkApiReady = () => {
      if (window.pywebview?.api) {
        setIsApiReady(true);
        return true;
      }
      return false;
    };

    if (checkApiReady()) {
      return;
    }

    const handleReady = () => {
      if (checkApiReady()) {
        console.log("pywebview API ready in SerialContext");
      }
    };

    window.addEventListener('pywebviewready', handleReady);

    const interval = setInterval(() => {
      if (checkApiReady()) {
        clearInterval(interval);
      }
    }, 100);

    const timeoutId = setTimeout(() => {
      clearInterval(interval);
      console.warn("pywebview API not available in SerialContext");
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeoutId);
      window.removeEventListener('pywebviewready', handleReady);
    };
  }, []);

  const checkConnection = async (): Promise<void> => {
    try {
      setError(null);
      
      if (!isApiReady || !window.pywebview?.api) {
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
    if (!isApiReady || !window.pywebview?.api) {
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

  const clearTerminal = () => {
    setTerminalLogs([]);
  };

  // 🔁 Initialize and register handlers
  useEffect(() => {
    if (!isApiReady) return;

    // Serial line output
    window.onSerialLine = (line: string) => {
      if (monitoring) {
        setSerialOutput(prev => [...prev, line]);
      }
    };

    // Serial connection status
    window.onSerialStatusUpdate = (connected: boolean) => {
      setSerialConnected(connected);
      if (!connected && monitoring) {
        setMonitoring(false);
      }
    };

    // Compiler logs
    window.__appendTerminalLog = (line: string) => {
      setTerminalLogs(prev => [...prev, line]);
    };

    // Check initial connection status
    checkConnection();
  }, [isApiReady, monitoring]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      // Stop monitoring on unmount if active
      if (isApiReady && window.pywebview?.api && monitoring) {
        window.pywebview.api.stop_serial_monitor().catch(console.error);
      }

      // ✅ Cleanup global handlers to prevent stale closures
      window.onSerialLine = undefined;
      window.onSerialStatusUpdate = undefined;
      window.__appendTerminalLog = undefined;
    };
  }, [isApiReady, monitoring]);

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
        terminalLogs,
        clearTerminal,
      }}
    >
      {children}
    </SerialContext.Provider>
  );
};
