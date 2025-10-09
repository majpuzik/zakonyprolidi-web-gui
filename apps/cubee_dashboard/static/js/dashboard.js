// ---------- Helpery ----------
async function fetchJSON(url, method = "GET", body = null) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ---------- UI aktualizace ----------
async function loadState() {
  try {
    const state = await fetchJSON("/api/state");
    document.getElementById("soc").textContent = state.battery_soc.toFixed(1);
    document.getElementById("pv").textContent = state.pv_power.toFixed(2);
    document.getElementById("load").textContent = state.load_power.toFixed(2);
    document.getElementById("price").textContent = state.grid_price.toFixed(2);
    document.getElementById("timestamp").textContent = new Date(state.timestamp).toLocaleString('cs-CZ');
    return state;
  } catch (err) {
    console.error("Chyba při načítání stavu:", err);
    return null;
  }
}

async function loadPrices() {
  try {
    const prices = await fetchJSON("/api/prices");
    return prices.map(p => p.finalni_cena);
  } catch (err) {
    console.error("Chyba při načítání cen:", err);
    return Array(24).fill(6.0);
  }
}

async function loadCurrentAction() {
  try {
    const resp = await fetchJSON("/api/action");
    document.getElementById("cubee-action").textContent = resp.action;
  } catch (err) {
    console.error("Chyba při načítání akce:", err);
    document.getElementById("cubee-action").textContent = "error";
  }
}

// ---------- Optimizer ----------
async function computeAction(state, prices) {
  if (!state || !prices) {
    return { action: "monitor", amount_kwh: 0, reason: "Chybějící data", benefit_czk: 0 };
  }

  const soc = state.battery_soc;
  const pv = state.pv_power;
  const load = state.load_power;
  const price = state.grid_price;

  // Jednoduchá logika (zjednodušená verze z SelfConsumptionOptimizer)
  if (pv > load && pv > 2 && soc < 90) {
    const excess = pv - load;
    return {
      action: "store_solar_excess",
      amount_kwh: excess,
      reason: `Solární přebytek ${excess.toFixed(1)} kW → baterie`,
      benefit_czk: price * excess
    };
  }

  if (price < 0 && soc < 90) {
    return {
      action: "buy_negative_price",
      amount_kwh: 5,
      reason: `Záporná cena ${price.toFixed(2)} CZK/kWh`,
      benefit_czk: Math.abs(price) * 5
    };
  }

  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
  if (price > avgPrice * 1.2 && soc > 30) {
    const amount = Math.min(load, 8);
    return {
      action: "use_battery_high_price",
      amount_kwh: amount,
      reason: `Vysoká cena ${price.toFixed(1)} CZK/kWh → použij baterii`,
      benefit_czk: price * amount
    };
  }

  if (pv > 0 && load > 0) {
    const direct = Math.min(pv, load);
    return {
      action: "direct_self_consumption",
      amount_kwh: direct,
      reason: "Přímá spotřeba ze solár",
      benefit_czk: price * direct
    };
  }

  return {
    action: "monitor",
    amount_kwh: 0,
    reason: "Monitorování – žádná optimalizace potřebná",
    benefit_czk: 0
  };
}

// ---------- Graf ----------
async function renderChart(state = null, prices = null) {
  try {
    // Pokud data nejsou předána, načti je
    if (!state) state = await loadState();
    if (!prices) prices = await loadPrices();

    if (!state || !prices) {
      console.warn("⚠️ Chybí data pro graf");
      return;
    }

    const now = new Date();
    const hour = now.getHours();

    // Plánovaná akce
    const planned = new Array(24).fill(0);
    const action = await computeAction(state, prices);
    if (action) {
      planned[hour] = action.amount_kwh;
    }

    // Skutečná spotřeba = grid import (nákup ze sítě)
    // Pro každou hodinu: import ze sítě * nákupní cena
    const actualImport = new Array(24).fill(0);
    const actualExport = new Array(24).fill(0);

    // Aktuální hodina - skutečná data
    actualImport[hour] = state.grid_import || 0;
    actualExport[hour] = state.grid_export || 0;

    // Ostatní hodiny - průměr z aktuálního stavu (pro vizualizaci)
    for (let i = 0; i < 24; i++) {
      if (i !== hour) {
        actualImport[i] = (state.grid_import || 0) * (0.8 + Math.random() * 0.4);
        actualExport[i] = (state.grid_export || 0) * (0.8 + Math.random() * 0.4);
      }
    }

    const hourLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`);

  // Nákupní ceny (spot + poplatky)
  const buyPrices = prices.map(p => p + 0.85 + 0.30);  // spot + CEZ + import

  // Prodejní ceny (feed-in tariff)
  const sellPrices = new Array(24).fill(0.55);

  // Naše optimalizace - kdy nakupovat/prodávat
  const avgBuyPrice = buyPrices.reduce((a, b) => a + b, 0) / buyPrices.length;
  const recommendations = new Array(24).fill(null);
  const recommendColors = new Array(24).fill('rgba(0,0,0,0)');

  for (let i = 0; i < 24; i++) {
    if (buyPrices[i] < avgBuyPrice * 0.85) {
      // Levná hodina - doporučujeme NÁKUP/nabíjení
      recommendations[i] = buyPrices[i];
      recommendColors[i] = 'rgba(255, 100, 100, 0.4)';  // Červená
    } else if (buyPrices[i] > avgBuyPrice * 1.15) {
      // Drahá hodina - doporučujeme PRODEJ/vybíjení
      recommendations[i] = buyPrices[i];
      recommendColors[i] = 'rgba(100, 255, 100, 0.4)';  // Zelená
    }
  }

  // Trace 1: Cena za nákup (černá, horní)
  const trace1 = {
    x: hourLabels,
    y: buyPrices,
    name: "Cena za nákup v Kč",
    type: "scatter",
    mode: "lines",
    line: {
      width: 2,
      shape: 'hv',
      color: 'rgba(50, 50, 50, 1)'  // Černá
    },
    fill: 'tonexty',
    fillcolor: 'rgba(180, 220, 180, 0.3)'  // Světle zelená výplň
  };

  // Trace 2: Cena za prodej (modrá, dolní)
  const trace2 = {
    x: hourLabels,
    y: sellPrices,
    name: "Cena za prodej v Kč",
    type: "scatter",
    mode: "lines",
    line: {
      width: 2,
      shape: 'hv',
      color: 'rgba(100, 150, 255, 1)'  // Modrá
    },
    fill: 'tozeroy',
    fillcolor: 'rgba(200, 220, 255, 0.3)'  // Světle modrá výplň
  };

  // Trace 3: Aktuální čas (svislá čára)
  const trace3 = {
    x: [hourLabels[hour], hourLabels[hour]],
    y: [0, Math.max(...buyPrices)],
    name: "Aktuální čas",
    type: "scatter",
    mode: "lines",
    line: {
      width: 2,
      color: 'rgba(0, 0, 0, 0.5)',
      dash: 'dash'
    },
    showlegend: true
  };

  // Trace 4: Naše doporučení (červená = nakup, zelená = prodej)
  const trace4 = {
    x: hourLabels,
    y: recommendations,
    name: "Doporučení",
    type: "bar",
    marker: {
      color: recommendColors,
      line: { width: 0 }
    },
    opacity: 0.5,
    showlegend: true
  };

    const layout = {
      title: "Ceny elektřiny (24h)",
      xaxis: {
        title: "",
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)'
      },
      yaxis: {
        title: "CZK/kWh",
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)',
        range: [0, Math.max(...buyPrices) * 1.1]
      },
      legend: {
        x: 0.5,
        y: -0.15,
        xanchor: 'center',
        orientation: 'h'
      },
      margin: { l: 60, r: 40, t: 60, b: 80 },
      height: 400,
      hovermode: 'x unified',
      plot_bgcolor: 'rgba(250, 250, 250, 1)',
      paper_bgcolor: 'white'
    };

    Plotly.newPlot("plotly-chart", [trace2, trace1, trace4, trace3], layout, {responsive: true});
  } catch (err) {
    console.error("❌ Chyba při vykreslování grafu:", err);
  }
}

// ---------- Odeslání akce ----------
async function sendAction(action, amount) {
  try {
    const result = await fetchJSON("/api/send_action", "POST", { action, amount_kwh: amount });
    alert(`✅ Akce odeslána do systému Cubee.cz\n${JSON.stringify(result, null, 2)}`);
  } catch (err) {
    alert(`❌ Chyba při odesílání: ${err.message}`);
  }
}

// ---------- Export ----------
function downloadCSV(data, filename) {
  const csv = "action,amount_kwh,benefit_czk\n" +
    `${data.action},${data.amount_kwh},${data.benefit_czk}\n`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function downloadPNG() {
  Plotly.downloadImage("plotly-chart", {
    format: "png",
    filename: "cubee_chart",
    width: 1200,
    height: 600
  });
}

// ---------- Metriky ----------
async function loadMetrics() {
  try {
    const strategy = await fetchJSON("/api/strategy?mode=passive");
    const metrics = strategy.metrics;

    document.getElementById("metric-ote").textContent = metrics.ote_price_avg;
    document.getElementById("metric-our-profit").textContent = metrics.our_profit;
    document.getElementById("metric-cubee-profit").textContent = metrics.cubee_profit;
    document.getElementById("metric-import").textContent = metrics.total_import_kwh;
    document.getElementById("metric-export").textContent = metrics.total_export_kwh;
  } catch (err) {
    console.error("Chyba při načítání metrik:", err);
  }
}

// ---------- Trend chart ----------
async function renderTrend() {
  try {
    const hist = await fetchJSON("/api/history");
    if (!hist.length) {
      document.getElementById("trend-chart").innerHTML = "<p>Zatím nejsou k dispozici historická data</p>";
      return;
    }

    const dates = hist.map(r => r.date).reverse();
    const our = hist.map(r => r.our_profit).reverse();
    const cubee = hist.map(r => r.cubee_profit).reverse();

    const trace1 = {
      x: dates,
      y: our,
      name: "Náš zisk",
      type: "scatter",
      mode: "lines+markers",
      line: { color: "gold", width: 2 },
      marker: { size: 6 }
    };

    const trace2 = {
      x: dates,
      y: cubee,
      name: "Cubee zisk",
      type: "scatter",
      mode: "lines+markers",
      line: { color: "blue", width: 2 },
      marker: { size: 6 }
    };

    const layout = {
      title: "Denní zisk – trend",
      xaxis: { title: "Datum" },
      yaxis: { title: "Zisk (CZK)" },
      height: 400,
      hovermode: "x unified"
    };

    Plotly.newPlot("trend-chart", [trace1, trace2], layout, {responsive: true});
  } catch (err) {
    console.error("Chyba při vykreslování trendu:", err);
  }
}

// ---------- Init ----------
let currentAction = null;

async function init() {
  console.log("🚀 Inicializace dashboardu...");

  try {
    // Načti data
    console.log("1️⃣ Načítám state...");
    const state = await loadState();
    console.log("2️⃣ Načítám prices...");
    const prices = await loadPrices();
    console.log("3️⃣ Načítám current action...");
    await loadCurrentAction();
    console.log("4️⃣ Renderuji chart...");
    await renderChart(state, prices);  // Předáme data přímo
    console.log("5️⃣ Načítám metrics...");
    await loadMetrics();
    console.log("6️⃣ Renderuji trend...");
    await renderTrend();

    console.log("7️⃣ Počítám action...");
    // Vypočítej naší akci
    currentAction = await computeAction(state, prices);
    if (currentAction) {
      document.getElementById("our-action").textContent =
        `${currentAction.action} (${currentAction.amount_kwh.toFixed(2)} kWh) - ${currentAction.reason} - Benefit: ${currentAction.benefit_czk.toFixed(2)} CZK`;
    }

    // Footer datum
    document.getElementById("footer-date").textContent = new Date().toLocaleDateString('cs-CZ');

    console.log("✅ Dashboard inicializován");
  } catch (err) {
    console.error("❌ Chyba při inicializaci:", err);
    document.getElementById("our-action").textContent = "Chyba při načítání dat";
    document.getElementById("cubee-action").textContent = "Chyba při načítání dat";
  }
}

// ---------- Event listeners ----------
document.addEventListener("DOMContentLoaded", () => {
  init();

  // Přepínač režimu
  const radios = document.querySelectorAll('input[name="mode"]');
  radios.forEach(r => r.addEventListener("change", () => {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    document.getElementById("send-btn").disabled = (mode !== "active");
  }));

  // Aktualizovat
  document.getElementById("refresh-btn").addEventListener("click", async () => {
    await init();
  });

  // Odeslat akci
  document.getElementById("send-btn").addEventListener("click", async () => {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    if (mode !== "active") return;
    if (!currentAction) {
      alert("Nejprve vypočítej akci pomocí tlačítka Aktualizovat");
      return;
    }
    await sendAction(currentAction.action, currentAction.amount_kwh);
  });

  // Export CSV
  document.getElementById("download-csv").addEventListener("click", (e) => {
    e.preventDefault();
    if (!currentAction) {
      alert("Nejprve vypočítej akci pomocí tlačítka Aktualizovat");
      return;
    }
    downloadCSV(currentAction, "cubee_action.csv");
  });

  // Export PNG
  document.getElementById("download-png").addEventListener("click", (e) => {
    e.preventDefault();
    downloadPNG();
  });

  // Auto-refresh každých 60 sekund
  setInterval(() => {
    console.log("🔄 Auto-refresh...");
    init();
  }, 60000);
});
