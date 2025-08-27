// Manejo de UI para mostrar productos
function renderProduct(product) {
    const result = document.getElementById("product-result");
    result.innerHTML = `
      <h2 class="text-lg font-semibold text-gray-800">Producto Detectado</h2>
      <div class="flex items-center mt-3">
        <img src="${product.img}" alt="Producto" class="w-20 h-20 rounded-xl object-cover">
        <div class="ml-4">
          <p class="text-gray-700 font-semibold">${product.name}</p>
          <p class="text-gray-500 text-sm">Categoría: ${product.category}</p>
          <p class="text-gray-500 text-sm">Caducidad: ${product.expiry}</p>
        </div>
      </div>
    `;
    result.classList.remove("hidden");
  }
  