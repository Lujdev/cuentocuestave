import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { NeonAuthUIProvider } from "@neondatabase/neon-js/auth/react";
import "@neondatabase/neon-js/ui/css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";
import { App } from "./App";
import { authClient } from "./auth/stack";

const queryClient = new QueryClient();
const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

function navigate(path: string) {
  window.location.href = path;
}

function Link({ href, children }: { href: string; children: React.ReactNode }) {
  return <a href={href}>{children}</a>;
}

createRoot(root).render(
  <StrictMode>
    <NeonAuthUIProvider
      authClient={authClient}
      navigate={navigate}
      redirectTo="/"
      Link={Link}
    >
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </NeonAuthUIProvider>
  </StrictMode>,
);
