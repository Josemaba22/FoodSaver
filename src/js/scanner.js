// Lógica del escaneo con cámara
async function startScanner() {
    const container = document.getElementById("scanner-container");
  
    // Crear marco
    container.innerHTML = `
      <div class="relative w-full h-64 bg-black rounded-2xl overflow-hidden shadow-lg flex items-center justify-center">
        <video id="camera" autoplay playsinline class="w-full h-full object-cover"></video>
        <div id="scanner-frame" class="absolute w-40 h-40"></div>
      </div>
      <button id="scan-btn" class="mt-6 w-full py-3 bg-green-600 text-white font-semibold rounded-xl shadow hover:bg-green-700 transition">
        Activar Escaneo
      </button>
      <section id="product-result" class="mt-6 hidden w-full bg-white rounded-2xl shadow p-4"></section>
    `;
  
    const video = document.getElementById("camera");
    const button = document.getElementById("scan-btn");
  
    button.addEventListener("click", async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        video.srcObject = stream;
      } catch (err) {
        alert("No se pudo acceder a la cámara: " + err.message);
      }
    });
  }
  
  document.addEventListener("DOMContentLoaded", startScanner);
  