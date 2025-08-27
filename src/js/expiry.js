// Simulación de un producto perecedero recibido desde backend
const product = {
    name: "Leche Entera",
    category: "Lácteos",
    expiry: "2025-09-02", // Fecha de caducidad (formato ISO)
    img: "https://via.placeholder.com/80"
  };
  
  document.addEventListener("DOMContentLoaded", () => {
    const today = new Date();
    const expiryDate = new Date(product.expiry);
  
    const diffTime = expiryDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
    const title = document.getElementById("expiry-title");
    const message = document.getElementById("expiry-message");
  
    // Mostrar datos del producto
    document.getElementById("product-img").src = product.img;
    document.getElementById("product-name").textContent = "Nombre: " + product.name;
    document.getElementById("product-category").textContent = "Categoría: " + product.category;
    document.getElementById("product-expiry").textContent = "Caducidad: " + expiryDate.toLocaleDateString();
  
    // Validación de caducidad
    if (diffDays < 0) {
      title.textContent = "⚠ Producto vencido";
      message.textContent = "Este alimento ya caducó. No se recomienda su consumo.";
      message.classList.add("text-red-600", "font-semibold");
    } else if (diffDays <= 3) {
      title.textContent = "⚠ Caducidad próxima";
      message.textContent = `Este alimento vence en ${diffDays} día(s). Consúmelo pronto.`;
      message.classList.add("text-yellow-600", "font-semibold");
    } else {
      title.textContent = "✔ Producto en buen estado";
      message.textContent = `Este alimento vence en ${diffDays} días.`;
      message.classList.add("text-green-600", "font-semibold");
    }
  });
  