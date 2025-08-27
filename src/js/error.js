// Simulación de distintos errores posibles
const errorTypes = {
    camera: "No se pudo acceder a la cámara. Verifica permisos.",
    notFound: "El producto no está registrado en el sistema.",
    unreadable: "El código no pudo ser leído. Intenta nuevamente."
  };
  
  // Mostrar mensaje dinámico
  document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const errorKey = params.get("type") || "unreadable";
  
    const container = document.getElementById("error-container");
    const message = container.querySelector("p");
  
    message.textContent = errorTypes[errorKey] || errorTypes.unreadable;
  });
  