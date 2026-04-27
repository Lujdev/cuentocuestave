import { authClient } from "./auth/stack";

export function App() {
  const { data: session, isPending } = authClient.useSession();

  if (isPending) return null;

  if (!session?.user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">cuantocuestave — Admin</h1>
          <button
            onClick={() =>
              authClient.signIn.magicLink({
                email: import.meta.env.VITE_ADMIN_EMAIL ?? "",
                callbackURL: "/",
              })
            }
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Sign in
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-4 py-3 flex justify-between items-center">
        <span className="font-bold">cuantocuestave admin</span>
        <span className="text-sm text-gray-500">{session.user.email}</span>
      </header>
      <main className="p-4">
        <p className="text-gray-500">Dashboard — Fase 5</p>
      </main>
    </div>
  );
}
