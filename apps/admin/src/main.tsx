import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { StackProvider, StackTheme } from "@stackframe/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";
import { App } from "./App";
import { stackClientApp } from "./auth/stack";

const queryClient = new QueryClient();
const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

createRoot(root).render(
  <StrictMode>
    <StackProvider app={stackClientApp}>
      <StackTheme>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </StackTheme>
    </StackProvider>
  </StrictMode>,
);
