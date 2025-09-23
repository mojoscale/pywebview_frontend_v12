import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

interface UpdateInfo {
  version: string;
  url: string;
  changelog?: string;
}

interface UpdateContextType {
  updateInfo: UpdateInfo | null;
  setUpdateInfo: (info: UpdateInfo | null) => void;
}

const UpdateContext = createContext<UpdateContextType | null>(null);

interface UpdateProviderProps {
  children: ReactNode;
}

// Extend the Window interface so TypeScript knows about our custom global
declare global {
  interface Window {
    onUpdateAvailable?: (info: UpdateInfo) => void;
  }
}

export const UpdateProvider = ({ children }: UpdateProviderProps) => {
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);

  useEffect(() => {
    window.onUpdateAvailable = (info: UpdateInfo) => {
      console.log('🔔 Update available:', info);
      setUpdateInfo(info);
    };
  }, []);

  const contextValue: UpdateContextType = {
    updateInfo,
    setUpdateInfo,
  };

  return (
    <UpdateContext.Provider value={contextValue}>
      {children}
    </UpdateContext.Provider>
  );
};

export const useUpdate = () => {
  const context = useContext(UpdateContext);
  if (!context) {
    throw new Error('useUpdate must be used within an UpdateProvider');
  }
  return context;
};
