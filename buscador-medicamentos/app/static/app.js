"use strict";

const form = document.getElementById("form-busqueda");
const input = document.getElementById("input-consulta");
const tabla = document.getElementById("tabla");
const tbody = document.getElementById("tbody");
const estado = document.getElementById("estado");
const info = document.getElementById("info");
const erroresDiv = document.getElementById("errores");
const configInfo = document.getElementById("config-info");

// Muestra la configuracion activa al cargar (moneda comun, tasa, sitios).
async function cargarSalud() {
  try {
    const resp = await fetch("/api/salud");
    const data = await resp.json();
    configInfo.textContent =
      `Moneda de comparación: ${data.moneda_comun} · ` +
      `Tasa: 1 USD = ${data.tasa_bs_por_usd} Bs · ` +
      `Sitios: ${data.sitios.join(", ")}`;
  } catch (e) {
    configInfo.textContent = "No se pudo cargar la configuración.";
  }
}

function fmt(valor) {
  return typeof valor === "number" ? valor.toFixed(2) : "-";
}

function render(data) {
  tbody.innerHTML = "";
  erroresDiv.innerHTML = "";

  info.textContent =
    `${data.total} resultado(s) para "${data.consulta}". ` +
    `Ordenados por precio en ${data.moneda_comun} (más barato primero).`;

  if (data.total === 0) {
    tabla.hidden = true;
  } else {
    tabla.hidden = false;
    data.resultados.forEach((r, i) => {
      const tr = document.createElement("tr");
      if (i === 0) tr.classList.add("mas-barato");
      const simbolo = r.moneda === "USD" ? "$us " : "Bs. ";
      tr.innerHTML = `
        <td>${escape(r.nombre)}</td>
        <td>${escape(r.presentacion || "-")}</td>
        <td class="precio">${simbolo}${fmt(r.precio)}</td>
        <td class="precio">${fmt(r.precio_bs)}</td>
        <td class="precio ${data.moneda_comun === "USD" ? "comparacion" : ""}">${fmt(r.precio_usd)}</td>
        <td>${escape(r.fuente)}</td>
        <td>${r.url ? `<a href="${escape(r.url)}" target="_blank" rel="noopener">ver</a>` : ""}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  const errores = Object.entries(data.errores || {});
  if (errores.length) {
    erroresDiv.innerHTML =
      "<strong>Sitios con problemas:</strong><ul>" +
      errores.map(([sitio, motivo]) => `<li>${escape(sitio)}: ${escape(motivo)}</li>`).join("") +
      "</ul>";
  }
}

function escape(txt) {
  const div = document.createElement("div");
  div.textContent = txt;
  return div.innerHTML;
}

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const q = input.value.trim();
  if (!q) return;

  estado.textContent = "Buscando...";
  tabla.hidden = true;
  info.textContent = "";
  erroresDiv.innerHTML = "";

  try {
    const resp = await fetch(`/api/buscar?q=${encodeURIComponent(q)}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    render(data);
  } catch (e) {
    info.textContent = `Error al buscar: ${e.message}`;
  } finally {
    estado.textContent = "";
  }
});

cargarSalud();
