// Consumos a backend
const API_URL = "https://api.midominio.com/productos";

async function getProductByCode(code) {
  try {
    const res = await fetch(`${API_URL}/${code}`);
    if (!res.ok) throw new Error("Error al obtener producto");
    return await res.json();
  } catch (err) {
    console.error(err);
    return null;
  }
}
