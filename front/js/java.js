
const API = "http://localhost:8000/api";

let chartMedia, chartCategoria;

async function carregarOpcoes() {
  const res = await fetch(`${API}/options`);
  const data = await res.json();
  popularSelect("curso", data.curso);
  popularSelect("periodo", data.periodo_atual);
}

function popularSelect(id, options) {
  const sel = document.getElementById(id);
  sel.innerHTML = "";
  options.forEach(opt => {
    const o = document.createElement("option");
    o.textContent = opt; o.value = opt;
    sel.appendChild(o);
  });
}

async function carregarDados() {
  const curso = document.getElementById("curso").value;
  const periodo = document.getElementById("periodo").value;
  const risco = document.getElementById("risco").value;
  const page = parseInt(document.getElementById("page").value || "1");
  const pageSize = parseInt(document.getElementById("page-size").value || "100");

  const params = new URLSearchParams({
    curso, periodo, risco, page, page_size: pageSize
  });
  const res = await fetch(`${API}/alunos?` + params.toString());
  const data = await res.json();

  document.getElementById("kpi-total").textContent = data.kpi.total_alunos;
  document.getElementById("kpi-media").textContent = data.kpi.media_geral.toFixed(2);
  document.getElementById("kpi-alto").textContent = `${data.kpi.perc_alto.toFixed(1)}%`;
  document.getElementById("kpi-medio").textContent = `${data.kpi.perc_medio.toFixed(1)}%`;

  const tbody = document.getElementById("tbody");
  tbody.innerHTML = "";
  data.items.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.matricula || ""}</td>
      <td>${item.nome || ""}</td>
      <td>${item.curso || ""}</td>
      <td>${item.periodo_atual || ""}</td>
      <td>${item.status || ""}</td>
      <td>${Number(item.media_geral || 0).toFixed(2)}</td>
      <td>${Number(item.risco_ml_evasao || 0).toFixed(2)}</td>
      <td>${item.categoria_risco || ""}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("pagination-info").textContent =
    `Página ${data.page} de ${data.pages} — mostrando ${data.items.length} de ${data.total}`;

  document.getElementById("prev").onclick = () => {
    const p = Math.max(1, data.page - 1);
    document.getElementById("page").value = p;
    carregarDados();
  };
  document.getElementById("next").onclick = () => {
    const p = Math.min(data.pages, data.page + 1);
    document.getElementById("page").value = p;
    carregarDados();
  };

  desenharGraficos(data);
}

function desenharGraficos(data) {
  const medias = data.items.map(x => Number(x.media_geral || 0));
  const counts = data.counts || {Baixo:0, Médio:0, Alto:0};

  const mediaCtx = document.getElementById("chart-media");
  const catCtx = document.getElementById("chart-categoria");

  if (chartMedia) chartMedia.destroy();
  if (chartCategoria) chartCategoria.destroy();

  chartMedia = new Chart(mediaCtx, {
    type: "bar",
    data: {
      labels: medias.map((_, i) => `Aluno ${i+1}`),
      datasets: [{ label: "Média Geral", data: medias, backgroundColor: "#4e79a7" }]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 10 } } }
  });

  chartCategoria = new Chart(catCtx, {
    type: "bar",
    data: {
      labels: ["Baixo", "Médio", "Alto"],
      datasets: [{ label: "Qtde", data: [counts.Baixo, counts.Médio, counts.Alto], backgroundColor: ["#59a14f", "#f1c40f", "#e15759"] }]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
  });
}

async function carregarAltoRisco() {
  const res = await fetch(`${API}/alto_risco?limit=100`);
  const data = await res.json();
  const tbody = document.getElementById("tbody-alto");
  tbody.innerHTML = "";
  data.items.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.matricula || ""}</td>
      <td>${item.nome || ""}</td>
      <td>${item.curso || ""}</td>
      <td>${item.periodo_atual || ""}</td>
      <td>${Number(item.media_geral || 0).toFixed(2)}</td>
      <td>${Number(item.risco_ml_evasao || 0).toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.getElementById("btn-aplicar").onclick = carregarDados;
document.getElementById("btn-reset").onclick = async () => {
  document.getElementById("curso").selectedIndex = 0;
  document.getElementById("periodo").selectedIndex = 0;
  document.getElementById("risco").selectedIndex = 0;
  document.getElementById("page").value = 1;
  await carregarDados();
};

(async function init() {
  await carregarOpcoes();
  await carregarDados();
  await carregarAltoRisco();
})();
