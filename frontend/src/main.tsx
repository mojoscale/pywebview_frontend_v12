import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

import { UpdateProvider } from './contexts/UpdateContext';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
   <UpdateProvider>
     <App />
   </UpdateProvider>
    
  </StrictMode>,
)
