// Where the ChemCheck API lives, and the functions the website uses to talk to it.
// Set VITE_API_URL in web/.env.local to point at a local server instead, when testing.
export const API_URL = import.meta.env.VITE_API_URL || "https://chemcheck-api-crwd.onrender.com";

export async function askModels(elements, sample = 0) {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ elements, sample }),
  });
  if (!res.ok) throw new Error(`the server responded with status ${res.status}`);
  return res.json();
}

export function wakeServer() {
  return fetch(`${API_URL}/health`).catch(() => {});
}