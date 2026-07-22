const form = document.getElementById("optimizer-form");
const resultsContainer = document.getElementById("results");
const emptyState = document.getElementById("results-empty");
const submitButton = document.getElementById("submit-button");
const formError = document.getElementById("form-error");

let scoreChart;
let tradeoffChart;

const weightIds = ["quality", "cost", "latency", "context", "privacy"];

function updateWeightLabels() {
  let total = 0;
  weightIds.forEach((name) => {
    const value = Number(document.getElementById(`${name}-weight`).value);
    document.getElementById(`${name}-value`).textContent = `${value}%`;
    total += value;
  });
  const totalElement = document.getElementById("weight-total");
  totalElement.textContent = `${total}%`;
  totalElement.style.color = total === 100 ? "#63e6be" : "#fb7185";
}

document.querySelectorAll(".weight-input").forEach((input) => {
  input.addEventListener("input", updateWeightLabels);
});
updateWeightLabels();

function getPayload() {
  const weights = {};
  let total = 0;

  weightIds.forEach((name) => {
    const value = Number(document.getElementById(`${name}-weight`).value) / 100;
    weights[name] = value;
    total += value;
  });

  if (Math.abs(total - 1) > 0.0001) {
    throw new Error("Optimization weights must total exactly 100%.");
  }

  return {
    use_case: document.getElementById("use-case").value,
    max_cost_per_million_tokens: Number(document.getElementById("max-cost").value),
    max_latency_ms: Number(document.getElementById("max-latency").value),
    minimum_context_tokens: Number(document.getElementById("min-context").value),
    deployment: document.getElementById("deployment").value,
    privacy_required: document.getElementById("privacy-required").checked,
    top_n: Number(document.getElementById("top-n").value),
    weights,
  };
}

function formatContext(tokens) {
  return tokens >= 1000 ? `${Math.round(tokens / 1000)}K` : String(tokens);
}

function renderResults(data) {
  document.getElementById("evaluated-count").textContent = data.evaluated_models;
  document.getElementById("eligible-count").textContent = data.eligible_models;

  const best = data.recommendations[0];
  document.getElementById("best-score").textContent = best
    ? `${Math.round(best.total_score * 100)}%`
    : "—";

  if (!data.recommendations.length) {
    resultsContainer.innerHTML = "";
    emptyState.style.display = "block";
    emptyState.textContent = "No models satisfy all selected constraints. Increase budget, latency, or reduce privacy/context requirements.";
    renderCharts([]);
    return;
  }

  emptyState.style.display = "none";
  resultsContainer.innerHTML = data.recommendations.map((model) => `
    <article class="result-card">
      <div class="result-top">
        <div>
          <div class="rank">RANK #${model.rank}</div>
          <h4>${model.name}</h4>
          <div class="provider">${model.provider}</div>
        </div>
        <div class="score">${Math.round(model.total_score * 100)}<small>/100</small></div>
      </div>

      <div class="metric-list">
        <div class="mini-metric">
          <span>Cost / 1M</span>
          <strong>$${Number(model.metrics.cost_per_million_tokens).toFixed(2)}</strong>
        </div>
        <div class="mini-metric">
          <span>Latency</span>
          <strong>${model.metrics.latency_ms} ms</strong>
        </div>
        <div class="mini-metric">
          <span>Context</span>
          <strong>${formatContext(model.metrics.context_tokens)}</strong>
        </div>
        <div class="mini-metric">
          <span>Deployment</span>
          <strong>${model.metrics.deployment}</strong>
        </div>
      </div>

      <ul class="reason-list">
        ${model.explanation.map((line) => `<li>${line}</li>`).join("")}
      </ul>
    </article>
  `).join("");

  renderCharts(data.recommendations);
}

function renderCharts(models) {
  const labels = models.map((model) => model.name);
  const scores = models.map((model) => Math.round(model.total_score * 100));

  if (scoreChart) scoreChart.destroy();
  scoreChart = new Chart(document.getElementById("score-chart"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Overall score",
        data: scores,
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, max: 100, ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,.12)" } },
        x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
      },
      plugins: { legend: { labels: { color: "#e8eef8" } } },
    },
  });

  if (tradeoffChart) tradeoffChart.destroy();
  tradeoffChart = new Chart(document.getElementById("tradeoff-chart"), {
    type: "scatter",
    data: {
      datasets: models.map((model) => ({
        label: model.name,
        data: [{
          x: Number(model.metrics.cost_per_million_tokens),
          y: Number(model.metrics.latency_ms),
        }],
        pointRadius: 8,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: "Cost per 1M tokens", color: "#94a3b8" },
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(148,163,184,.12)" },
        },
        y: {
          title: { display: true, text: "Latency (ms)", color: "#94a3b8" },
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(148,163,184,.12)" },
        },
      },
      plugins: { legend: { labels: { color: "#e8eef8" } } },
    },
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.textContent = "";
  submitButton.disabled = true;
  submitButton.textContent = "Optimizing...";

  try {
    const response = await fetch("/api/v1/select-model", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload()),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail?.[0]?.msg || data.detail || "Optimization request failed.");
    }

    renderResults(data);
  } catch (error) {
    formError.textContent = error.message;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Recommend Best Models";
  }
});

form.dispatchEvent(new Event("submit"));
