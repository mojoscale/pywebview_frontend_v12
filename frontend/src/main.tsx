// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter } from "react-router-dom";
import "./index.css";
import App from "./App.tsx";

import { UpdateProvider } from "./contexts/UpdateContext";
import { SerialProvider } from "./contexts/SerialContext"; // 👈 import it

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <UpdateProvider>
      <SerialProvider>   {/* 👈 wrap your whole app in this */}
        <HashRouter>
          <App />
        </HashRouter>
      </SerialProvider>
    </UpdateProvider>
  </StrictMode>
);
