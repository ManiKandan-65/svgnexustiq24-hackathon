/**
 * NEXUS RETAIL COMMAND CENTER — Interactive Web Application
 * Zero external JS dependencies. Standard Browser Web APIs only.
 */

document.addEventListener('DOMContentLoaded', () => {
  // GLOBAL STATE
  let currentStoreId = 'ALL';
  let productsCache = [];
  let alertsCache = [];
  let matrixCache = [];
  let forecastCache = [];

  // DOM ELEMENTS — Navigation & Topbar
  const sidebarNavBtns = document.querySelectorAll('.sidebar-nav .nav-item');
  const views = document.querySelectorAll('.nexus-view');
  const nexusStoreSelect = document.getElementById('nexusStoreSelect');
  const topNavSearch = document.getElementById('topNavSearch');
  const sidebarAlertBadge = document.getElementById('sidebarAlertBadge');
  const nexusDataQualityBanner = document.getElementById('nexusDataQualityBanner');
  const nexusDataQualityMessage = document.getElementById('nexusDataQualityMessage');

  // KPI Elements
  const kpiTotalProducts = document.getElementById('kpiTotalProducts');
  const kpiCriticalStock = document.getElementById('kpiCriticalStock');
  const kpiAtRiskProducts = document.getElementById('kpiAtRiskProducts');
  const kpiStableProducts = document.getElementById('kpiStableProducts');
  const kpiEstimatedCoverage = document.getElementById('kpiEstimatedCoverage');

  // Matrix & Overview
  const inventoryMatrixBody = document.getElementById('inventoryMatrixBody');
  const overviewStoresBody = document.getElementById('overviewStoresBody');

  // Catalogue
  const catalogueSearch = document.getElementById('catalogueSearch');
  const catalogueRiskFilter = document.getElementById('catalogueRiskFilter');
  const catalogueTbody = document.querySelector('#viewInventory .nexus-table tbody');

  // Alerts
  const nexusAlertsGrid = document.getElementById('nexusAlertsGrid');

  // Forecast
  const forecastGrid = document.getElementById('forecastGrid');

  // Reorders & Transfers
  const reordersTbody = document.getElementById('reordersTbody');
  const transfersGrid = document.getElementById('transfersGrid');

  // Simulator
  const simStoreSelect = document.getElementById('simStoreSelect');
  const simProductSelect = document.getElementById('simProductSelect');
  const simSalesChangeSlider = document.getElementById('simSalesChangeSlider');
  const simSalesChangeVal = document.getElementById('simSalesChangeVal');
  const simIncomingStockInput = document.getElementById('simIncomingStockInput');
  const simTargetDaysInput = document.getElementById('simTargetDaysInput');

  const simBaseStockVal = document.getElementById('simBaseStockVal');
  const simSalesVal = document.getElementById('simSalesVal');
  const simTotalStockVal = document.getElementById('simTotalStockVal');
  const simCoverageVal = document.getElementById('simCoverageVal');
  const simStockoutDateVal = document.getElementById('simStockoutDateVal');
  const simRiskVal = document.getElementById('simRiskVal');
  const simRecommendationText = document.getElementById('simRecommendationText');

  // Evidence Copilot
  const nexusCopilotQuery = document.getElementById('nexusCopilotQuery');
  const nexusSendQueryBtn = document.getElementById('nexusSendQueryBtn');
  const nexusBtnText = document.getElementById('nexusBtnText');
  const nexusCopilotResponsePanel = document.getElementById('nexusCopilotResponsePanel');
  const nexusResponseSourceBadge = document.getElementById('nexusResponseSourceBadge');
  const resQueryText = document.getElementById('resQueryText');
  const nexusResAnswer = document.getElementById('nexusResAnswer');
  const nexusResKeyNumbers = document.getElementById('nexusResKeyNumbers');
  const nexusResEvidence = document.getElementById('nexusResEvidence');
  const nexusResRecommendation = document.getElementById('nexusResRecommendation');
  const nexusResLimitations = document.getElementById('nexusResLimitations');

  // Why Modal
  const whyModal = document.getElementById('whyModal');
  const closeWhyModalBtn = document.getElementById('closeWhyModalBtn');
  const whyProdName = document.getElementById('whyProdName');
  const whyStoreName = document.getElementById('whyStoreName');
  const whyCurrentStock = document.getElementById('whyCurrentStock');
  const whyAvgSales = document.getElementById('whyAvgSales');
  const whyCoverage = document.getElementById('whyCoverage');
  const whyRiskBadge = document.getElementById('whyRiskBadge');
  const whyExplanationText = document.getElementById('whyExplanationText');

  // Product Drawer
  const productDrawer = document.getElementById('productDrawer');
  const closeDrawerBtn = document.getElementById('closeDrawerBtn');
  const drawerProductName = document.getElementById('drawerProductName');
  const drawerCategory = document.getElementById('drawerCategory');
  const drawerStoreName = document.getElementById('drawerStoreName');
  const drawerStock = document.getElementById('drawerStock');
  const drawerReorderLevel = document.getElementById('drawerReorderLevel');
  const drawerAvgSales = document.getElementById('drawerAvgSales');
  const drawerCoverage = document.getElementById('drawerCoverage');
  const drawerRiskBadge = document.getElementById('drawerRiskBadge');
  const drawer7dDemand = document.getElementById('drawer7dDemand');
  const drawer14dDemand = document.getElementById('drawer14dDemand');
  const drawerStockoutDate = document.getElementById('drawerStockoutDate');
  const drawerActionText = document.getElementById('drawerActionText');
  const drawerTransferText = document.getElementById('drawerTransferText');
  const drawerSvgChartWrapper = document.getElementById('drawerSvgChartWrapper');

  // INITIALIZATION
  init();

  function init() {
    setupEventListeners();
    loadAllCommandCenterData();
  }

  function setupEventListeners() {
    // Navigation router
    sidebarNavBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sidebarNavBtns.forEach(b => b.classList.remove('active'));
        views.forEach(v => v.classList.remove('active'));

        btn.classList.add('active');
        const targetViewId = btn.getAttribute('data-view');
        document.getElementById(targetViewId).classList.add('active');
      });
    });

    // Store filter change
    nexusStoreSelect.addEventListener('change', (e) => {
      currentStoreId = e.target.value;
      loadAllCommandCenterData();
    });

    // Top Search Bar (Triggers Evidence Copilot)
    topNavSearch.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && topNavSearch.value.trim()) {
        const query = topNavSearch.value.trim();
        switchView('viewEvidence');
        nexusCopilotQuery.value = query;
        executeCopilotQuery(query);
      }
    });

    // Catalogue filters
    catalogueSearch.addEventListener('input', renderCatalogueTable);
    catalogueRiskFilter.addEventListener('change', renderCatalogueTable);

    // Simulator inputs
    simSalesChangeSlider.addEventListener('input', (e) => {
      const val = e.target.value;
      simSalesChangeVal.textContent = `${val >= 0 ? '+' : ''}${val}%`;
      runSimulation();
    });
    simIncomingStockInput.addEventListener('input', runSimulation);
    simTargetDaysInput.addEventListener('input', runSimulation);
    simStoreSelect.addEventListener('change', runSimulation);
    simProductSelect.addEventListener('change', runSimulation);

    // Evidence Copilot query send
    nexusSendQueryBtn.addEventListener('click', () => {
      executeCopilotQuery(nexusCopilotQuery.value);
    });
    nexusCopilotQuery.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') executeCopilotQuery(nexusCopilotQuery.value);
    });

    // Suggested Chips
    document.querySelectorAll('.nexus-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const queryText = chip.getAttribute('data-query');
        nexusCopilotQuery.value = queryText;
        executeCopilotQuery(queryText);
      });
    });

    // Modal Close events
    closeWhyModalBtn.addEventListener('click', () => whyModal.classList.add('hidden'));
    whyModal.addEventListener('click', (e) => { if (e.target === whyModal) whyModal.classList.add('hidden'); });

    closeDrawerBtn.addEventListener('click', () => productDrawer.classList.add('hidden'));
    productDrawer.addEventListener('click', (e) => { if (e.target === productDrawer) productDrawer.classList.add('hidden'); });
  }

  function switchView(viewId) {
    sidebarNavBtns.forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-view') === viewId);
    });
    views.forEach(v => {
      v.classList.toggle('active', v.id === viewId);
    });
  }

  // DATA LOADERS
  async function loadAllCommandCenterData() {
    await fetchDashboardKPIs();
    await fetchInventoryMatrix();
    await fetchAlerts();
    await fetchCatalogue();
    await fetchStores();
    await fetchForecast();
    await fetchReordersAndTransfers();
    populateSimulatorProducts();
  }

  async function fetchDashboardKPIs() {
    try {
      const res = await fetch(`/api/dashboard?store_id=${currentStoreId}`);
      if (!res.ok) throw new Error('KPI fetch failed');
      const data = await res.json();

      kpiTotalProducts.textContent = data.total_products || 0;
      kpiCriticalStock.textContent = data.critical_stock_count || 0;
      kpiAtRiskProducts.textContent = data.at_risk_count || 0;
      kpiStableProducts.textContent = data.stable_count || 0;
      kpiEstimatedCoverage.textContent = `${data.avg_coverage_days || 0}d`;

      sidebarAlertBadge.textContent = data.critical_stock_count || 0;

      if (data.data_quality_warnings && data.data_quality_warnings.length > 0) {
        nexusDataQualityMessage.textContent = data.data_quality_warnings.join(' | ');
        nexusDataQualityBanner.classList.remove('hidden');
      } else {
        nexusDataQualityBanner.classList.add('hidden');
      }
    } catch (err) {
      console.error('[KPIs] Error:', err);
    }
  }

  async function fetchInventoryMatrix() {
    try {
      const res = await fetch('/api/matrix');
      if (!res.ok) throw new Error('Matrix fetch failed');
      matrixCache = await res.json();
      renderInventoryMatrix(matrixCache);
    } catch (err) {
      console.error('[Matrix] Error:', err);
      inventoryMatrixBody.innerHTML = `<tr><td colspan="5" class="text-center">Error loading matrix.</td></tr>`;
    }
  }

  function renderInventoryMatrix(matrix) {
    inventoryMatrixBody.innerHTML = matrix.map(m => {
      const st1 = m.stores['ST01'] || { status: 'N/A' };
      const st2 = m.stores['ST02'] || { status: 'N/A' };
      const st3 = m.stores['ST03'] || { status: 'N/A' };

      return `
        <tr>
          <td><strong>${escapeHtml(m.product_name)}</strong></td>
          <td>${escapeHtml(m.category)}</td>
          <td>${renderHealthPill(st1)}</td>
          <td>${renderHealthPill(st2)}</td>
          <td>${renderHealthPill(st3)}</td>
        </tr>
      `;
    }).join('');
  }

  function renderHealthPill(storeData) {
    if (!storeData || storeData.status === 'N/A') return `<span class="health-pill">N/A</span>`;
    const statusClass = storeData.status.toLowerCase();
    const covStr = storeData.coverage_days !== null ? `${storeData.coverage_days}d` : 'Inf';
    return `<span class="health-pill ${statusClass}">${storeData.status} (${covStr})</span>`;
  }

  async function fetchAlerts() {
    try {
      const res = await fetch(`/api/alerts?store_id=${currentStoreId}`);
      if (!res.ok) throw new Error('Alerts fetch failed');
      alertsCache = await res.json();
      renderStockAlerts(alertsCache);
    } catch (err) {
      console.error('[Alerts] Error:', err);
      nexusAlertsGrid.innerHTML = `<div class="text-center">Error loading stock alerts.</div>`;
    }
  }

  function renderStockAlerts(alerts) {
    if (!alerts || alerts.length === 0) {
      nexusAlertsGrid.innerHTML = `<div style="grid-column: 1/-1;" class="text-center">No active stock alerts for current store filter.</div>`;
      return;
    }

    nexusAlertsGrid.innerHTML = alerts.map(a => {
      let severityClass = 'info';
      let badgeClass = 'badge-info';

      if (a.alert_type.includes('CRITICAL')) {
        severityClass = 'critical';
        badgeClass = 'badge-stockout';
      } else if (a.alert_type.includes('WARNING') || a.alert_type.includes('OVERSTOCK')) {
        severityClass = 'warning';
        badgeClass = 'badge-overstock';
      }

      return `
        <div class="nexus-alert-card ${severityClass}" data-product-id="${a.product_id}" data-store-id="${a.store_id}">
          <div class="alert-top">
            <div>
              <div class="alert-prod">${escapeHtml(a.product_name)}</div>
              <div class="alert-sub">${escapeHtml(a.store_name)} &bull; ${escapeHtml(a.category)}</div>
            </div>
            <span class="risk-badge ${badgeClass}">${escapeHtml(a.severity)}</span>
          </div>

          <div class="alert-stats-box">
            Stock: <strong>${a.current_stock}</strong> | Velocity: <strong>${a.avg_daily_sales}/day</strong> | Coverage: <strong class="color-cyan">${a.metric_value}</strong>
          </div>

          <div class="why-matters">
            ${escapeHtml(a.why_it_matters)}
          </div>

          <div class="alert-action-line">
            ${escapeHtml(a.recommended_action)}
          </div>

          <div class="alert-footer-nexus">
            <span style="font-size: 10px; color: var(--text-muted);">Verified Python Audit</span>
            <button class="why-btn" onclick="openWhyModal('${a.product_id}', '${a.store_id}')">WHY?</button>
          </div>
        </div>
      `;
    }).join('');

    // Attach click events to open drawer
    document.querySelectorAll('.nexus-alert-card').forEach(card => {
      card.addEventListener('click', (e) => {
        if (e.target.classList.contains('why-btn')) return;
        const pid = card.getAttribute('data-product-id');
        const sid = card.getAttribute('data-store-id');
        openProductDrawer(pid, sid);
      });
    });
  }

  async function fetchCatalogue() {
    try {
      const res = await fetch(`/api/products?store_id=${currentStoreId}`);
      if (!res.ok) throw new Error('Catalogue fetch failed');
      productsCache = await res.json();
      renderCatalogueTable();
    } catch (err) {
      console.error('[Catalogue] Error:', err);
      catalogueTbody.innerHTML = `<tr><td colspan="9" class="text-center">Error loading catalogue.</td></tr>`;
    }
  }

  function renderCatalogueTable() {
    const search = catalogueSearch.value.toLowerCase().trim();
    const risk = catalogueRiskFilter.value;

    const filtered = productsCache.filter(p => {
      const matchSearch = p.product_name.toLowerCase().includes(search) || p.category.toLowerCase().includes(search);
      const matchRisk = risk === 'ALL' || p.risk_level.includes(risk);
      return matchSearch && matchRisk;
    });

    if (filtered.length === 0) {
      catalogueTbody.innerHTML = `<tr><td colspan="9" class="text-center">No products match filter criteria.</td></tr>`;
      return;
    }

    catalogueTbody.innerHTML = filtered.map(p => {
      let badgeClass = 'badge-stable';
      if (p.risk_level.includes('CRITICAL')) badgeClass = 'badge-stockout';
      else if (p.risk_level.includes('WARNING')) badgeClass = 'badge-overstock';

      const covStr = p.days_remaining !== null ? `${p.days_remaining}d` : 'Inf';
      const growthSign = p.growth_pct >= 0 ? '+' : '';
      const growthStyle = p.growth_pct >= 0 ? 'color: var(--accent-emerald)' : 'color: var(--accent-rose)';

      return `
        <tr data-product-id="${p.product_id}" data-store-id="${p.store_id}">
          <td><strong>${escapeHtml(p.product_name)}</strong></td>
          <td>${escapeHtml(p.category)}</td>
          <td>${escapeHtml(p.store_name)}</td>
          <td style="font-family: var(--font-mono);">${p.current_stock} units</td>
          <td style="font-family: var(--font-mono);">${p.avg_daily_sales}/day</td>
          <td style="font-family: var(--font-mono); font-weight: 700;">${covStr}</td>
          <td style="${growthStyle}; font-weight: 700; font-family: var(--font-mono);">${growthSign}${p.growth_pct}%</td>
          <td><span class="risk-badge ${badgeClass}">${escapeHtml(p.risk_level)}</span></td>
          <td><button class="nexus-chip">View Details</button></td>
        </tr>
      `;
    }).join('');

    document.querySelectorAll('#catalogueTbody tr').forEach(row => {
      row.addEventListener('click', () => {
        const pid = row.getAttribute('data-product-id');
        const sid = row.getAttribute('data-store-id');
        openProductDrawer(pid, sid);
      });
    });
  }

  async function fetchStores() {
    try {
      const res = await fetch('/api/stores');
      if (!res.ok) throw new Error('Stores fetch failed');
      const stores = await res.json();
      overviewStoresBody.innerHTML = stores.map((s, i) => `
        <tr>
          <td><strong>#${i + 1}</strong></td>
          <td><strong>${escapeHtml(s.store_name)}</strong></td>
          <td>${escapeHtml(s.city)}, ${escapeHtml(s.region)}</td>
          <td style="font-family: var(--font-mono); font-weight: 700; color: var(--accent-cyan-glow);">₹${s.revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
          <td style="font-family: var(--font-mono);">${s.units_sold.toLocaleString('en-IN')} units</td>
          <td style="font-family: var(--font-mono); font-weight: 700;">${s.sales_growth_pct >= 0 ? '+' : ''}${s.sales_growth_pct}%</td>
          <td><span class="risk-badge ${s.low_stock_count > 0 ? 'badge-stockout' : 'badge-stable'}">${s.low_stock_count} items</span></td>
        </tr>
      `).join('');
    } catch (err) {
      console.error('[Stores] Error:', err);
    }
  }

  async function fetchForecast() {
    try {
      const res = await fetch(`/api/forecast?store_id=${currentStoreId}`);
      if (!res.ok) throw new Error('Forecast fetch failed');
      forecastCache = await res.json();

      forecastGrid.innerHTML = forecastCache.map(f => `
        <div class="forecast-card" data-product-id="${f.product_id}" data-store-id="${f.store_id}">
          <div style="font-weight: 800; font-size: 15px;">${escapeHtml(f.product_name)}</div>
          <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(f.store_name)} &bull; ${escapeHtml(f.category)}</div>
          
          <div class="fc-stat-row"><span>Current Stock:</span><span class="fc-val">${f.current_stock} units</span></div>
          <div class="fc-stat-row"><span>Avg Daily Demand:</span><span class="fc-val">${f.avg_daily_sales} units/day</span></div>
          <div class="fc-stat-row"><span>7-Day Demand Forecast:</span><span class="fc-val color-cyan">${f.demand_7d} units</span></div>
          <div class="fc-stat-row"><span>14-Day Demand Forecast:</span><span class="fc-val color-violet">${f.demand_14d} units</span></div>
          <div class="fc-stat-row"><span>Estimated Stockout Date:</span><span class="fc-val color-amber">${f.estimated_stockout_date}</span></div>
          
          <div class="kpi-indicator ${f.projected_status.includes('CRITICAL') ? 'red' : 'green'}">${f.projected_status}</div>
        </div>
      `).join('');

      document.querySelectorAll('.forecast-card').forEach(card => {
        card.addEventListener('click', () => {
          const pid = card.getAttribute('data-product-id');
          const sid = card.getAttribute('data-store-id');
          openProductDrawer(pid, sid);
        });
      });
    } catch (err) {
      console.error('[Forecast] Error:', err);
    }
  }

  async function fetchReordersAndTransfers() {
    try {
      const resR = await fetch(`/api/reorder?store_id=${currentStoreId}`);
      const reorders = await resR.json();
      
      reordersTbody.innerHTML = reorders.map(r => `
        <tr>
          <td><strong>${escapeHtml(r.product_name)}</strong></td>
          <td>${escapeHtml(r.store_name)}</td>
          <td style="font-family: var(--font-mono);">${r.current_stock} units</td>
          <td style="font-family: var(--font-mono);">${r.avg_daily_sales}/day</td>
          <td style="font-family: var(--font-mono);">${r.target_stock} units</td>
          <td style="font-family: var(--font-mono); font-weight: 800; color: var(--accent-cyan-glow);">${r.recommended_reorder} units</td>
          <td><span class="risk-badge ${r.urgency === 'CRITICAL' ? 'badge-stockout' : 'badge-overstock'}">${escapeHtml(r.action_timeline)}</span></td>
          <td style="font-size: 11px; color: var(--text-muted);">${escapeHtml(r.formula_explanation)}</td>
        </tr>
      `).join('');

      const resT = await fetch('/api/transfers');
      const transfers = await resT.json();

      if (transfers.length === 0) {
        transfersGrid.innerHTML = `<div class="text-center" style="grid-column: 1/-1;">No inter-store inventory transfers required currently.</div>`;
      } else {
        transfersGrid.innerHTML = transfers.map(t => `
          <div class="transfer-card">
            <div style="font-weight: 800; font-size: 15px;">${escapeHtml(t.product_name)}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(t.category)}</div>

            <div class="transfer-flow">
              <div class="t-node">
                <span style="font-size: 10px; color: var(--text-muted);">SOURCE STORE</span>
                <strong>${escapeHtml(t.from_store_name)}</strong>
                <span style="font-size: 11px; color: var(--accent-emerald);">${t.from_stock} units (${t.from_coverage}d)</span>
              </div>
              <div class="t-arrow">&rarr; ${t.recommended_transfer_qty} units &rarr;</div>
              <div class="t-node">
                <span style="font-size: 10px; color: var(--text-muted);">DESTINATION STORE</span>
                <strong>${escapeHtml(t.to_store_name)}</strong>
                <span style="font-size: 11px; color: var(--accent-rose);">${t.to_stock} units (${t.to_coverage}d)</span>
              </div>
            </div>

            <div style="font-size: 12px; color: var(--text-sub);">
              <strong>Transfer Reason:</strong> ${escapeHtml(t.reason)}
            </div>
          </div>
        `).join('');
      }

    } catch (err) {
      console.error('[Reorder/Transfers] Error:', err);
    }
  }

  // SIMULATOR
  function populateSimulatorProducts() {
    if (productsCache.length === 0) return;
    const uniqueProds = Array.from(new Set(productsCache.map(p => p.product_id)))
      .map(id => productsCache.find(p => p.product_id === id));

    simProductSelect.innerHTML = uniqueProds.map(p => `
      <option value="${p.product_id}">${p.product_name} (${p.category})</option>
    `).join('');

    runSimulation();
  }

  async function runSimulation() {
    const store_id = simStoreSelect.value;
    const product_id = simProductSelect.value;
    const sales_change_pct = parseFloat(simSalesChangeSlider.value);
    const incoming_stock = parseInt(simIncomingStockInput.value || 0);
    const target_days = parseInt(simTargetDaysInput.value || 14);

    if (!product_id) return;

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          store_id, product_id, sales_change_pct, incoming_stock, target_coverage_days: target_days
        })
      });

      const sim = await res.json();
      if (sim.error) return;

      simBaseStockVal.textContent = `${sim.baseline.current_stock} units (${sim.baseline.avg_daily_sales}/day)`;
      simSalesVal.textContent = `${sim.simulated_results.simulated_daily_sales} units/day`;
      simTotalStockVal.textContent = `${sim.simulated_results.simulated_total_stock} units`;
      simCoverageVal.textContent = `${sim.simulated_results.simulated_coverage_days} days`;
      simStockoutDateVal.textContent = sim.simulated_results.estimated_stockout_date;

      simRiskVal.textContent = sim.simulated_results.risk_level;
      simRiskVal.className = `sim-val ${sim.simulated_results.risk_level.includes('CRITICAL') ? 'color-red' : 'color-green'}`;
      simRecommendationText.textContent = sim.simulated_results.recommended_action;

    } catch (err) {
      console.error('[Simulator] Error:', err);
    }
  }

  // EVIDENCE COPILOT
  async function executeCopilotQuery(queryText) {
    if (!queryText || !queryText.trim()) return;

    nexusSendQueryBtn.disabled = true;
    nexusBtnText.textContent = "Analyzing data...";

    nexusCopilotResponsePanel.classList.remove('hidden');
    resQueryText.textContent = queryText;
    nexusResAnswer.innerHTML = `<div class="loading-spinner" style="color: var(--accent-cyan-glow);">Analyzing your retail data...</div>`;
    nexusResKeyNumbers.innerHTML = '';
    nexusResEvidence.textContent = '';
    nexusResRecommendation.textContent = '';
    nexusResLimitations.textContent = '';

    try {
      const res = await fetch('/api/copilot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryText, store_id: currentStoreId })
      });

      const data = await res.json();

      nexusResAnswer.textContent = data.answer || 'No response generated.';

      if (data.is_fallback) {
        nexusResponseSourceBadge.textContent = 'Deterministic Python Engine';
        nexusResponseSourceBadge.style.color = '#f59e0b';
      } else {
        nexusResponseSourceBadge.textContent = 'Gemini 1.5 Flash + Verified Python Facts';
        nexusResponseSourceBadge.style.color = '#06b6d4';
      }

      if (data.key_numbers && data.key_numbers.length > 0) {
        nexusResKeyNumbers.innerHTML = data.key_numbers.map(n => `
          <div class="sim-stat-box">
            <span class="sim-label">${escapeHtml(n.label)}</span>
            <span class="sim-val">${escapeHtml(String(n.value))}</span>
          </div>
        `).join('');
      } else {
        nexusResKeyNumbers.innerHTML = `<div style="color: var(--text-muted); font-size: 12px;">No key numbers applicable.</div>`;
      }

      nexusResEvidence.textContent = data.evidence || 'N/A';
      nexusResRecommendation.textContent = data.recommendation || 'N/A';
      nexusResLimitations.textContent = data.assumptions_limitations || 'N/A';

    } catch (err) {
      console.error('[Copilot] Error:', err);
      nexusResAnswer.textContent = 'Error connecting to copilot backend engine.';
    } finally {
      nexusSendQueryBtn.disabled = false;
      nexusBtnText.textContent = "Ask Nexus";
    }
  }

  // EXPLAINABLE DECISION MODAL ("WHY?")
  window.openWhyModal = function(productId, storeId) {
    const alertItem = alertsCache.find(a => a.product_id === productId && a.store_id === storeId);
    if (!alertItem) return;

    whyProdName.textContent = alertItem.product_name;
    whyStoreName.textContent = alertItem.store_name;
    whyCurrentStock.textContent = `${alertItem.current_stock} units`;
    whyAvgSales.textContent = `${alertItem.avg_daily_sales} units/day`;
    whyCoverage.textContent = `${alertItem.days_remaining} days`;
    whyRiskBadge.textContent = alertItem.alert_type;

    whyExplanationText.textContent = `Mathematical Audit: Current stock of ${alertItem.current_stock} units divided by 30-day average sales velocity of ${alertItem.avg_daily_sales} units/day yields ${alertItem.days_remaining} days of supply. Because ${alertItem.days_remaining} days is below the safe threshold of 7.0 days, the deterministic engine flags this SKU for immediate replenishment.`;

    whyModal.classList.remove('hidden');
  };

  // PRODUCT SIDE DRAWER
  async function openProductDrawer(productId, storeId) {
    try {
      const sid = storeId || currentStoreId;
      const res = await fetch(`/api/product?id=${productId}&store_id=${sid}`);
      if (!res.ok) throw new Error('Product not found');
      const prod = await res.json();

      drawerProductName.textContent = prod.product_name;
      drawerCategory.textContent = `${prod.category} (${prod.product_id})`;
      drawerStoreName.textContent = prod.store_name || 'All Stores';
      drawerStock.textContent = `${prod.current_stock} units`;
      drawerReorderLevel.textContent = `${prod.reorder_level} units`;
      drawerAvgSales.textContent = `${prod.avg_daily_sales}/day`;
      drawerCoverage.textContent = prod.days_remaining !== null ? `${prod.days_remaining} days` : 'Infinite';
      drawerRiskBadge.textContent = prod.risk_level;

      if (prod.demand_forecast) {
        drawer7dDemand.textContent = `${prod.demand_forecast.demand_7d} units`;
        drawer14dDemand.textContent = `${prod.demand_forecast.demand_14d} units`;
        drawerStockoutDate.textContent = prod.demand_forecast.estimated_stockout_date;
      }

      drawerActionText.textContent = prod.recommended_action;

      if (prod.transfer_opportunities && prod.transfer_opportunities.length > 0) {
        const t = prod.transfer_opportunities[0];
        drawerTransferText.textContent = `Recommended Transfer: Move ${t.recommended_transfer_qty} units from ${t.from_store_name} (${t.from_stock} units) to ${t.to_store_name} (${t.to_stock} units).`;
      } else {
        drawerTransferText.textContent = 'No active inter-store transfer required.';
      }

      renderSvgSalesTrendChart(prod.sales_trend || []);
      productDrawer.classList.remove('hidden');

    } catch (err) {
      console.error('[Drawer] Error:', err);
      alert('Could not load product details.');
    }
  }

  function renderSvgSalesTrendChart(trendData) {
    if (!trendData || trendData.length === 0) {
      drawerSvgChartWrapper.innerHTML = `<div style="color: var(--text-muted); font-size: 12px;">No historical daily sales trend available.</div>`;
      return;
    }

    const svgWidth = 380;
    const svgHeight = 150;
    const pad = 20;

    const values = trendData.map(d => d.quantity_sold);
    const maxVal = Math.max(...values, 5);
    const minVal = 0;

    const dx = (svgWidth - pad * 2) / (trendData.length - 1 || 1);
    const points = trendData.map((d, i) => {
      const x = pad + i * dx;
      const y = svgHeight - pad - ((d.quantity_sold - minVal) / (maxVal - minVal)) * (svgHeight - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');

    const polylineSvg = `<polyline fill="none" stroke="#06b6d4" stroke-width="2" points="${points}" />`;

    const startDateStr = trendData[0].date;
    const endDateStr = trendData[trendData.length - 1].date;

    const svgHtml = `
      <svg width="100%" height="100%" viewBox="0 0 ${svgWidth} ${svgHeight}" preserveAspectRatio="none" style="overflow: visible;">
        <line x1="${pad}" y1="${svgHeight - pad}" x2="${svgWidth - pad}" y2="${svgHeight - pad}" stroke="#1f2937" stroke-width="1" />
        ${polylineSvg}
        <text x="${pad}" y="${svgHeight - 4}" fill="#6b7280" font-size="9">${startDateStr}</text>
        <text x="${svgWidth - pad}" y="${svgHeight - 4}" fill="#6b7280" font-size="9" text-anchor="end">${endDateStr}</text>
      </svg>
    `;

    drawerSvgChartWrapper.innerHTML = svgHtml;
  }

  function escapeHtml(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }
});
