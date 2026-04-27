import { StackClientApp } from "@stackframe/react";

export const stackClientApp = new StackClientApp({
  tokenStore: "cookie",
  projectId: import.meta.env.VITE_STACK_AUTH_PROJECT_ID ?? "",
  publishableClientKey: import.meta.env.VITE_STACK_AUTH_PUBLISHABLE_CLIENT_KEY ?? "",
  urls: {
    signIn: "/login",
    afterSignIn: "/",
  },
});
