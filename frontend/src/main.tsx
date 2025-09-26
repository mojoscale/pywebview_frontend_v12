// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter } from "react-router-dom"; // 👈 use HashRouter
import "./index.css";
import App from "./App.tsx";

import { UpdateProvider } from "./contexts/UpdateContext";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <UpdateProvider>
      <HashRouter>   {/* 👈 wrap App with router */}
        <App />
      </HashRouter>
    </UpdateProvider>
  </StrictMode>
);
