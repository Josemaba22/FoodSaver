// Simulación de datos recibidos desde backend
const productData = {
    name: "Yogurt Natural",
    category: "Lácteos",
    expiry: "15/01/2026",
    img: "https://via.placeholder.com/80"
  };
  
  document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("confirmation-container");
  
    // Renderizar los datos del producto
    const productCard = container.querySelector("div.flex.items-center");
    productCard.innerHTML = `
      <img src="${productData.img}" alt="Producto" class="w-20 h-20 rounded-lg object-cover">
      <div class="ml-4 text-left">
        <p class="text-gray-700 font-semibold">Nombre: ${productData.name}</p>
        <p class="text-gray-500 text-sm">Categoría: ${productData.category}</p>
        <p class="text-gray-500 text-sm">Caducidad: ${productData.expiry}</p>
      </div>
    `;
  });
  