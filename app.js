(() => {
  "use strict";

  const aShareDataset = window.IC_DATA;
  if (!aShareDataset || !Array.isArray(aShareDataset.companies)) {
    document.body.innerHTML =
      '<div style="padding:48px;font-family:sans-serif;color:#0c1729">数据文件 data.js 未加载，请确认文件与本页面位于同一目录。</div>';
    return;
  }

  const globalDataset = window.IC_GLOBAL_DATA || { companies: [] };
  const meta = aShareDataset.meta || {};
  const XHS_MODE = document.body.classList.contains("xhs-mode");
  const companies = [
    ...aShareDataset.companies,
    ...(globalDataset.companies || []),
  ];
  const companyById = new Map(companies.map((company) => [company.id, company]));
  const sourceOrder = new Map(companies.map((company, index) => [company.id, index]));
  const MAX_COMPARE = 20;
  const MAX_METRICS = 3;
  const STORAGE_KEY = "ic-analog-compare-v2";

  const DEFAULT_IDS = [
    "sheng-bang",
    "si-rui-pu",
    "na-xin-wei",
    "ai-wei",
    "di-ao",
  ];

  const QUICK_PRIORITY = [
    "sheng-bang",
    "si-rui-pu",
    "na-xin-wei",
    "ai-wei",
    "di-ao",
    "zhuo-sheng",
    "nan-xin",
    "jing-feng",
  ];

  const SERIES_COLORS = [
    { line: "#2563eb", soft: "#eaf0ff" },
    { line: "#df604f", soft: "#fff0ed" },
    { line: "#0e9f7a", soft: "#e5f8f2" },
    { line: "#8059dc", soft: "#f2ecff" },
    { line: "#d99a17", soft: "#fff5df" },
    { line: "#078ea8", soft: "#e6f8fb" },
    { line: "#d44d82", soft: "#fff0f6" },
    { line: "#5d6b80", soft: "#f0f3f6" },
    { line: "#3d7a3a", soft: "#eaf7e7" },
    { line: "#b25f16", soft: "#fff1e4" },
    { line: "#0b7a5c", soft: "#e4f7f0" },
    { line: "#9a4fbf", soft: "#f7ecff" },
    { line: "#c2493a", soft: "#ffefeb" },
    { line: "#2b6b9a", soft: "#e9f4fb" },
    { line: "#7a7a10", soft: "#f7f7df" },
    { line: "#a34767", soft: "#fbeef3" },
    { line: "#4f5bd5", soft: "#edeeff" },
    { line: "#b06c00", soft: "#fff4dc" },
    { line: "#127a84", soft: "#e5f8f9" },
    { line: "#6d5b45", soft: "#f5f0e9" },
  ];

  const CATEGORY_TONES = {
    "信号链 / 通用模拟": { soft: "#eaf0ff", deep: "#2349b8" },
    "电源管理 / 驱动": { soft: "#fff4df", deep: "#946200" },
    "射频 / 混合信号": { soft: "#e6f8fb", deep: "#08768b" },
    "军工 / 特种模拟": { soft: "#fff0ed", deep: "#a53e31" },
    "IDM / 平台型": { soft: "#e5f8f2", deep: "#096e55" },
    "CPU / 处理器": { soft: "#e8ecff", deep: "#2e42a0" },
    "SoC 芯片": { soft: "#f0ecff", deep: "#5940b7" },
    "GPU / AI 算力": { soft: "#fff0ed", deep: "#a53e31" },
    "FPGA / 可编程计算": { soft: "#f3e9ff", deep: "#6a3eb5" },
    "存储芯片": { soft: "#fff0d8", deep: "#9b5b00" },
    "存储模组 / 系统": { soft: "#e6f7fb", deep: "#0b7187" },
    "存储配套": { soft: "#e7f8f1", deep: "#08735a" },
    "封装测试": { soft: "#e9eef6", deep: "#3f5877" },
    "功率半导体": { soft: "#fff1dc", deep: "#965d05" },
    "显示驱动": { soft: "#f2ecff", deep: "#6540b7" },
    "图像传感器": { soft: "#fff0ed", deep: "#a33e32" },
    "光通信 / 激光芯片": { soft: "#e7f8fb", deep: "#086f84" },
    "ASIC / 设计服务": { soft: "#eaf0ff", deep: "#29449f" },
    "网络 / 交换芯片": { soft: "#e5f8f2", deep: "#08745a" },
    "半导体材料": { soft: "#edf8df", deep: "#547a13" },
    "半导体相关": { soft: "#f1f3f5", deep: "#556171" },
    "晶圆代工 FAB": { soft: "#e3f8f1", deep: "#08745a" },
    "半导体设备": { soft: "#e8f4ff", deep: "#176a9c" },
  };

  const CATEGORY_ORDER = [
    "信号链 / 通用模拟",
    "电源管理 / 驱动",
    "射频 / 混合信号",
    "军工 / 特种模拟",
    "IDM / 平台型",
    "CPU / 处理器",
    "SoC 芯片",
    "GPU / AI 算力",
    "FPGA / 可编程计算",
    "存储芯片",
    "存储模组 / 系统",
    "存储配套",
    "封装测试",
    "功率半导体",
    "显示驱动",
    "图像传感器",
    "光通信 / 激光芯片",
    "ASIC / 设计服务",
    "网络 / 交换芯片",
    "半导体材料",
    "半导体相关",
    "晶圆代工 FAB",
    "半导体设备",
  ];

  const metricDefinitions = [
    {
      key: "revenue",
      label: "营业收入",
      unit: "亿元",
      group: "finance",
      formatKind: "money",
      hint: "单季或年度营业收入",
    },
    {
      key: "grossMargin",
      label: "毛利率",
      unit: "%",
      group: "finance",
      formatKind: "percent",
      hint: "毛利 ÷ 营业收入",
    },
    {
      key: "netProfit",
      label: "净利润",
      unit: "亿元",
      group: "finance",
      formatKind: "money",
      hint: "归母净利润",
    },
    {
      key: "ocf",
      label: "经营性现金流",
      unit: "亿元",
      group: "finance",
      formatKind: "money",
      hint: "经营活动现金流净额",
    },
    {
      key: "rdExpense",
      label: "研发费用",
      unit: "亿元",
      group: "finance",
      formatKind: "money",
      hint: "费用化研发投入",
    },
    {
      key: "rdIntensity",
      label: "研发强度",
      unit: "%",
      group: "finance",
      formatKind: "percent",
      hint: "研发费用 ÷ 营业收入",
    },
    {
      key: "cash",
      label: "账上现金",
      unit: "亿元",
      group: "finance",
      formatKind: "money",
      hint: "货币资金 + 交易性金融资产",
    },
    {
      key: "headcount",
      label: "员工数量",
      unit: "人",
      group: "people",
      formatKind: "integer",
      hint: "期末员工总数",
      annualOnly: true,
    },
    {
      key: "avgPay",
      label: "人均薪酬",
      unit: "万元 / 年",
      group: "people",
      formatKind: "pay",
      hint: "支付给职工的现金 ÷ 员工人数",
      annualOnly: true,
    },
    {
      key: "rdStaff",
      label: "研发人员数量",
      unit: "人",
      group: "people",
      formatKind: "integer",
      hint: "期末研发人员数量",
      annualOnly: true,
    },
    {
      key: "rdStaffRatio",
      label: "研发人员占比",
      unit: "%",
      group: "people",
      formatKind: "percent",
      hint: "研发人员 ÷ 员工总数",
      annualOnly: true,
    },
    {
      key: "rdComp",
      label: "研发薪酬（估算）",
      unit: "亿元",
      group: "people",
      formatKind: "money",
      hint: "按研发人员占比分摊现金薪酬",
      annualOnly: true,
    },
    {
      key: "rdExpensePerStaff",
      label: "研发人员人均投入",
      unit: "万元 / 年",
      group: "people",
      formatKind: "pay",
      hint: "研发费用 ÷ 研发人员数量",
      annualOnly: true,
    },
    {
      key: "revenueGrowth",
      label: "营业收入增速",
      unit: "%",
      group: "finance",
      formatKind: "percent",
      hint: "同比对比上年同期；环比对比上一季度；负基数按绝对值计算",
      baseKey: "revenue",
      growth: true,
      historyOnly: true,
    },
    {
      key: "ocfGrowth",
      label: "经营性现金流增速",
      unit: "%",
      group: "finance",
      formatKind: "percent",
      hint: "同比对比上年同期；环比对比上一季度；负基数按绝对值计算",
      baseKey: "ocf",
      growth: true,
      historyOnly: true,
    },
    {
      key: "netProfitGrowth",
      label: "净利润增速",
      unit: "%",
      group: "finance",
      formatKind: "percent",
      hint: "同比对比上年同期；环比对比上一季度；负基数按绝对值计算",
      baseKey: "netProfit",
      growth: true,
      historyOnly: true,
    },
  ];

  const metricByKey = new Map(metricDefinitions.map((metric) => [metric.key, metric]));

  const elements = {
    search: document.querySelector("#companySearch"),
    searchShell: document.querySelector("#searchShell"),
    searchResults: document.querySelector("#searchResults"),
    quickPicks: document.querySelector("#quickPicks"),
    companyCards: document.querySelector("#companyCards"),
    emptyState: document.querySelector("#emptyState"),
    emptyAddBtn: document.querySelector("#emptyAddBtn"),
    selectionCount: document.querySelector("#selectionCount"),
    companyTotal: document.querySelector("#companyTotal"),
    headerPeriod: document.querySelector("#headerPeriod"),
    shareBtn: document.querySelector("#shareBtn"),
    clearBtn: document.querySelector("#clearBtn"),
    exportBtn: document.querySelector("#exportBtn"),
    tableFrequency: document.querySelector("#tableFrequency"),
    tablePeriod: document.querySelector("#tablePeriod"),
    tablePeriodNote: document.querySelector("#tablePeriodNote"),
    metricsTable: document.querySelector("#metricsTable"),
    chartTypeToggle: document.querySelector("#chartTypeToggle"),
    frequencyToggle: document.querySelector("#frequencyToggle"),
    metricPicker: document.querySelector("#metricPicker"),
    metricSelectedCount: document.querySelector("#metricSelectedCount"),
    historyRange: document.querySelector("#historyRange"),
    historyModeNote: document.querySelector("#historyModeNote"),
    chartGrid: document.querySelector("#chartGrid"),
    chartEmpty: document.querySelector("#chartEmpty"),
    toast: document.querySelector("#toast"),
    navLinks: Array.from(document.querySelectorAll("[data-nav]")),
  };

  const state = {
    selected: [],
    searchOpen: false,
    query: "",
    activeIndex: -1,
    searchResults: [],
    tableFrequency: "annual",
    tablePeriod: null,
    chartType: "line",
    historyFrequency: "quarter",
    historyMetrics: ["revenue", "grossMargin", "rdExpense"],
    hiddenByMetric: new Map(),
    growthBasisByMetric: new Map(),
    companyColors: new Map(),
    charts: new Map(),
    chartTooltips: [],
    resizeObserver: null,
    toastTimer: null,
  };

  const annualPeriods = Array.from(
    new Set(companies.flatMap((company) => company.annual.map((row) => row.period)))
  ).sort();
  const quarterPeriods = generateQuarters(
    meta.startPeriod || "2021Q1",
    meta.latestQuarter || "2026Q3"
  );
  const latestAnnual = meta.latestAnnual || annualPeriods.at(-1) || "2025";
  const latestQuarter = meta.latestQuarter || quarterPeriods.at(-1) || "2026Q3";

  companies.forEach((company) => {
    company.annualMap = new Map(company.annual.map((row) => [row.period, row]));
    company.quarterMap = new Map(company.quarterly.map((row) => [row.period, row]));
  });

  function generateQuarters(start, end) {
    const startYear = Number(start.slice(0, 4));
    const startQuarter = Number(start.slice(5));
    const endYear = Number(end.slice(0, 4));
    const endQuarter = Number(end.slice(5));
    const result = [];
    let year = startYear;
    let quarter = startQuarter;

    while (year < endYear || (year === endYear && quarter <= endQuarter)) {
      result.push(`${year}Q${quarter}`);
      quarter += 1;
      if (quarter > 4) {
        quarter = 1;
        year += 1;
      }
    }
    return result;
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => {
      const replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      };
      return replacements[character];
    });
  }

  function normalize(value) {
    return String(value ?? "")
      .toLowerCase()
      .replace(/[\s·•,，/\\|()（）-]+/g, "");
  }

  function getCompany(id) {
    return companyById.get(id);
  }

  function sanitizeIds(value) {
    const candidate = Array.isArray(value) ? value : [];
    const unique = [];
    candidate.forEach((id) => {
      if (companyById.has(id) && !unique.includes(id)) unique.push(id);
    });
    return unique.slice(0, MAX_COMPARE);
  }

  function readInitialSelection() {
    const params = new URLSearchParams(window.location.search);
    if (params.has("compare")) {
      return sanitizeIds(params.get("compare").split(","));
    }

    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored !== null) return sanitizeIds(JSON.parse(stored));
    } catch (error) {
      // localStorage may be unavailable when the file is opened directly.
    }

    return sanitizeIds(DEFAULT_IDS);
  }

  function persistSelection() {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state.selected));
    } catch (error) {
      // The interface remains fully usable without persistence.
    }

    try {
      const url = new URL(window.location.href);
      if (state.selected.length) {
        url.searchParams.set("compare", state.selected.join(","));
      } else {
        url.searchParams.delete("compare");
      }
      window.history.replaceState(null, "", url);
    } catch (error) {
      // Some embedded browsers restrict history changes.
    }
  }

  function getRow(company, frequency, period) {
    return frequency === "annual"
      ? company.annualMap.get(period)
      : company.quarterMap.get(period);
  }

  function previousPeriod(period, frequency, basis) {
    if (frequency === "annual") {
      return String(Number(period) - 1);
    }
    const year = Number(period.slice(0, 4));
    const quarter = Number(period.slice(-1));
    if (basis === "yoy") {
      return `${year - 1}Q${quarter}`;
    }
    return quarter === 1 ? `${year - 1}Q4` : `${year}Q${quarter - 1}`;
  }

  function growthValue(company, metric, frequency, period, basis) {
    const currentRow = getRow(company, frequency, period);
    const previousRow = getRow(
      company,
      frequency,
      previousPeriod(period, frequency, basis)
    );
    const current = currentRow?.[metric.baseKey];
    const previous = previousRow?.[metric.baseKey];
    if (
      !Number.isFinite(current) ||
      !Number.isFinite(previous) ||
      previous === 0
    ) {
      return null;
    }
    return ((current - previous) / Math.abs(previous)) * 100;
  }

  function chartMetricValue(
    company,
    metric,
    frequency,
    period,
    growthBasis
  ) {
    if (metric.growth) {
      return growthValue(company, metric, frequency, period, growthBasis);
    }
    const row = getRow(company, frequency, period);
    return row && Number.isFinite(row[metric.key]) ? row[metric.key] : null;
  }

  function formatValue(metric, value) {
    if (!Number.isFinite(value)) return "—";

    if (metric.formatKind === "percent") {
      return value.toFixed(1);
    }

    if (metric.formatKind === "integer") {
      return new Intl.NumberFormat("zh-CN", {
        maximumFractionDigits: 0,
      }).format(value);
    }

    if (metric.formatKind === "pay") {
      return value.toFixed(1);
    }

    const absolute = Math.abs(value);
    const digits = absolute >= 100 ? 1 : 2;
    return new Intl.NumberFormat("zh-CN", {
      maximumFractionDigits: digits,
      minimumFractionDigits: 0,
    }).format(value);
  }

  function formatAxisValue(metric, value) {
    if (!Number.isFinite(value)) return "";

    if (metric.formatKind === "percent") {
      return `${Math.round(value)}%`;
    }

    if (metric.formatKind === "integer") {
      if (Math.abs(value) >= 10000) {
        return `${(value / 10000).toFixed(1)}万`;
      }
      if (Math.abs(value) >= 1000) {
        return `${(value / 1000).toFixed(1)}k`;
      }
      return String(Math.round(value));
    }

    if (Math.abs(value) >= 1000) {
      return `${(value / 1000).toFixed(1)}k`;
    }

    return Number.isInteger(value) ? String(value) : value.toFixed(1);
  }

  function mean(values) {
    if (!values.length) return 0;
    return values.reduce((sum, value) => sum + value, 0) / values.length;
  }

  function getSearchResults(query) {
    const normalizedQuery = normalize(query);
    const categoryRank = new Map(
      CATEGORY_ORDER.map((category, index) => [category, index])
    );

    if (!normalizedQuery) {
      return [...companies]
        .sort((a, b) => {
          const aCategory = categoryRank.has(a.category)
            ? categoryRank.get(a.category)
            : 99;
          const bCategory = categoryRank.has(b.category)
            ? categoryRank.get(b.category)
            : 99;
          if (aCategory !== bCategory) return aCategory - bCategory;
          return (sourceOrder.get(a.id) || 0) - (sourceOrder.get(b.id) || 0);
        });
    }

    return companies
      .map((company) => {
        const name = normalize(company.name);
        const code = normalize(company.code);
        const category = normalize(company.category);
        const products = company.products.map(normalize);
        const haystack = normalize(
          [
            company.name,
            company.code,
            company.market,
            company.category,
            company.location,
            company.region,
            company.fxPair,
            company.description,
            ...(company.aliases || []),
            ...company.products,
          ].join(" ")
        );

        if (!haystack.includes(normalizedQuery)) return null;

        let rank = 7;
        if (name.startsWith(normalizedQuery)) rank = 0;
        else if (name.includes(normalizedQuery)) rank = 1;
        else if (code.includes(normalizedQuery)) rank = 2;
        else if (products.some((product) => product.includes(normalizedQuery))) rank = 3;
        else if (category.includes(normalizedQuery)) rank = 4;
        else if (normalize(company.location).includes(normalizedQuery)) rank = 5;

        return { company, rank };
      })
      .filter(Boolean)
      .sort((a, b) => {
        const aCategory = categoryRank.has(a.company.category)
          ? categoryRank.get(a.company.category)
          : 99;
        const bCategory = categoryRank.has(b.company.category)
          ? categoryRank.get(b.company.category)
          : 99;
        if (aCategory !== bCategory) return aCategory - bCategory;
        if (a.rank !== b.rank) return a.rank - b.rank;
        return (
          (sourceOrder.get(a.company.id) || 0) -
          (sourceOrder.get(b.company.id) || 0)
        );
      })
      .map((entry) => entry.company);
  }

  function isSelected(id) {
    return state.selected.includes(id);
  }

  function rebuildCompanyColors() {
    state.companyColors = new Map(
      state.selected.map((id, index) => [
        id,
        SERIES_COLORS[index % SERIES_COLORS.length],
      ])
    );
  }

  function pruneHiddenSeries() {
    state.hiddenByMetric.forEach((hidden, metricKey) => {
      hidden.forEach((companyId) => {
        if (!state.selected.includes(companyId)) hidden.delete(companyId);
      });
      if (!metricByKey.has(metricKey)) state.hiddenByMetric.delete(metricKey);
    });
  }

  function visibleCompaniesForMetric(metricKey, selectedCompanies) {
    const hidden = state.hiddenByMetric.get(metricKey) || new Set();
    return selectedCompanies.filter((company) => !hidden.has(company.id));
  }

  function renderSearch() {
    state.searchResults = getSearchResults(state.query);
    const label = state.query.trim()
      ? `搜索结果 · ${state.searchResults.length}`
      : `全部公司 · ${state.searchResults.length}`;

    if (!state.searchResults.length) {
      elements.searchResults.innerHTML = `
        <div class="search-empty">
          <strong>没有找到匹配公司</strong>
          试试公司简称、股票代码，或「电源管理 / 射频 / 车规」等产品词。
        </div>
      `;
      return;
    }

    const groups = new Map();
    state.searchResults.forEach((company) => {
      if (!groups.has(company.category)) groups.set(company.category, []);
      groups.get(company.category).push(company);
    });
    const searchIndex = new Map(
      state.searchResults.map((company, index) => [company.id, index])
    );

    elements.searchResults.innerHTML = `
      <div class="search-results-label">
        <span>${label}</span>
        <span>共 ${companies.length} 家</span>
      </div>
      ${Array.from(groups.entries())
        .sort(
          ([a], [b]) =>
            CATEGORY_ORDER.indexOf(a) - CATEGORY_ORDER.indexOf(b)
        )
        .map(
          ([category, groupCompanies]) => `
            <div class="search-category">
              <span>${escapeHtml(category)}</span>
              <span class="search-category-count">${groupCompanies.length}</span>
            </div>
            ${groupCompanies
              .map((company) => {
                const selected = isSelected(company.id);
                const tone =
                  CATEGORY_TONES[company.category] ||
                  CATEGORY_TONES["信号链 / 通用模拟"];
                const index = searchIndex.get(company.id) ?? -1;
                return `
                  <button
                    class="search-result${selected ? " is-added" : ""}${index === state.activeIndex ? " is-active" : ""}"
                    type="button"
                    role="option"
                    aria-selected="${selected}"
                    data-company-id="${escapeHtml(company.id)}"
                  >
                    <span
                      class="result-mark"
                      style="--tone-soft:${tone.soft};--tone-deep:${tone.deep}"
                      aria-hidden="true"
                    >${escapeHtml(company.mark)}</span>
                    <span class="result-main">
                      <span class="result-title">
                        <strong>${escapeHtml(company.name)}</strong>
                        <em>${escapeHtml(company.code)}</em>
                      </span>
                      <small>${escapeHtml(company.products.slice(0, 3).join(" / "))}</small>
                    </span>
                    <span class="result-action">${selected ? "已加入" : "加入 +"}</span>
                  </button>
                `;
              })
              .join("")}
          `
        )
        .join("")}
    `;
  }

  function setSearchOpen(open) {
    state.searchOpen = open;
    elements.searchResults.classList.toggle("is-open", open);
    elements.search.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("xhs-search-open", XHS_MODE && open);
    if (open) {
      renderSearch();
    } else {
      state.activeIndex = -1;
      updateActiveSearchResult();
    }
  }

  function updateActiveSearchResult() {
    elements.searchResults.querySelectorAll(".search-result").forEach((button, index) => {
      const active = index === state.activeIndex;
      button.classList.toggle("is-active", active);
      if (active) button.scrollIntoView({ block: "nearest" });
    });
  }

  function renderQuickPicks() {
    const priority = new Map(QUICK_PRIORITY.map((id, index) => [id, index]));
    const candidates = companies
      .filter((company) => !isSelected(company.id))
      .sort((a, b) => {
        const aRank = priority.has(a.id) ? priority.get(a.id) : 100;
        const bRank = priority.has(b.id) ? priority.get(b.id) : 100;
        return aRank - bRank;
      })
      .slice(0, 6);

    elements.quickPicks.innerHTML = candidates
      .map(
        (company) => `
          <button class="quick-pick" type="button" data-quick-id="${escapeHtml(company.id)}">
            <span aria-hidden="true">＋</span>
            ${escapeHtml(company.name)}
          </button>
        `
      )
      .join("");
  }

  function renderCompanyCards() {
    const selectedCompanies = state.selected.map(getCompany).filter(Boolean);

    elements.companyCards.innerHTML = selectedCompanies
      .map((company, index) => {
        const annual = company.annualMap.get(latestAnnual) || company.annual.at(-1) || {};
        const color = state.companyColors.get(company.id) || SERIES_COLORS[0];
        const products = company.products.slice(0, 5);
        const remaining = company.products.length - products.length;

        return `
          <article
            class="company-card"
            style="--company-color:${color.line};--company-soft:${color.soft};animation-delay:${index * 35}ms"
          >
            <div class="card-head">
              <div class="card-identity">
                <span class="company-mark" aria-hidden="true">${escapeHtml(company.mark)}</span>
                <div class="card-name">
                  <h3>${escapeHtml(company.name)}</h3>
                  <div class="card-subline">
                    <span>${escapeHtml(company.code)}</span>
                    <span class="dot" aria-hidden="true"></span>
                    <span>${escapeHtml(company.market)}</span>
                  </div>
                </div>
              </div>
              <button
                class="remove-button"
                type="button"
                data-remove-id="${escapeHtml(company.id)}"
                aria-label="移除 ${escapeHtml(company.name)}"
                title="移除公司"
              >
                <svg viewBox="0 0 16 16" aria-hidden="true">
                  <path d="m4 4 8 8M12 4l-8 8" />
                </svg>
              </button>
            </div>

            <span class="category-pill">${escapeHtml(company.category)}</span>

            <div class="product-block">
              <span class="product-label">PRODUCT MATRIX / 产品矩阵</span>
              <div class="product-tags">
                ${products
                  .map((product) => `<span class="product-tag">${escapeHtml(product)}</span>`)
                  .join("")}
                ${remaining > 0 ? `<span class="product-tag is-more">+${remaining}</span>` : ""}
              </div>
            </div>

            <div class="card-snapshot">
              <div class="snapshot-item">
                <span>${latestAnnual} 营收</span>
                <strong>${formatValue(metricByKey.get("revenue"), annual.revenue)}<small>亿</small></strong>
              </div>
              <div class="snapshot-item">
                <span>${latestAnnual} 净利</span>
                <strong class="${Number(annual.netProfit) < 0 ? "is-negative" : ""}">
                  ${formatValue(metricByKey.get("netProfit"), annual.netProfit)}<small>亿</small>
                </strong>
              </div>
              <div class="snapshot-item">
                <span>研发强度</span>
                <strong>${formatValue(metricByKey.get("rdIntensity"), annual.rdIntensity)}<small>%</small></strong>
              </div>
            </div>
          </article>
        `;
      })
      .join("");

    elements.emptyState.hidden = selectedCompanies.length > 0;
  }

  function getVisibleTableMetrics() {
    if (state.tableFrequency === "quarter") {
      return metricDefinitions.filter(
        (metric) => !metric.annualOnly && !metric.historyOnly
      );
    }
    return metricDefinitions.filter((metric) => !metric.historyOnly);
  }

  function renderTable() {
    const selectedCompanies = state.selected.map(getCompany).filter(Boolean);
    const period = state.tablePeriod;
    const frequency = state.tableFrequency;
    const visibleMetrics = getVisibleTableMetrics();

    if (!selectedCompanies.length) {
      elements.metricsTable.innerHTML = `
        <tbody>
          <tr>
            <td class="table-empty-cell">请先在对比清单中添加公司。</td>
          </tr>
        </tbody>
      `;
      return;
    }

    const header = `
      <thead>
        <tr>
          <th scope="col">
            <div class="table-corner">
              <span>METRIC / COMPANY</span>
              <strong>指标 / 公司</strong>
            </div>
          </th>
          ${selectedCompanies
            .map((company) => {
              const color = state.companyColors.get(company.id) || SERIES_COLORS[0];
              return `
                <th scope="col">
                  <div class="table-company">
                    <span class="table-company-dot" style="--company-color:${color.line}" aria-hidden="true"></span>
                    <div>
                      <strong>${escapeHtml(company.name)}</strong>
                      <span>${escapeHtml(company.code)}</span>
                    </div>
                  </div>
                </th>
              `;
            })
            .join("")}
        </tr>
      </thead>
    `;

    let currentGroup = null;
    const bodyRows = visibleMetrics
      .map((metric) => {
        const rows = selectedCompanies.map((company) =>
          getRow(company, frequency, period)
        );
        const values = rows.map((row) => (row ? row[metric.key] : null));
        const finiteValues = values.filter(Number.isFinite);
        const maxAbs = Math.max(0, ...finiteValues.map((value) => Math.abs(value)));
        const maxValue = finiteValues.length ? Math.max(...finiteValues) : null;
        const groupChanged = metric.group !== currentGroup;
        currentGroup = metric.group;

        const groupRow = groupChanged
          ? `
            <tr class="metric-group-row">
              <td colspan="${selectedCompanies.length + 1}">
                ${metric.group === "finance" ? "FINANCIALS / 财务表现" : "PEOPLE & R&D / 人员与研发"}
              </td>
            </tr>
          `
          : "";

        const valueCells = values
          .map((value, index) => {
            const company = selectedCompanies[index];
            if (!Number.isFinite(value)) {
              return `
                <td class="metric-cell missing" title="${escapeHtml(company.name)} · ${escapeHtml(metric.label)}：未披露">
                  <div class="metric-value-line">
                    <strong>—</strong>
                    <span>${escapeHtml(metric.unit)}</span>
                  </div>
                  <div class="metric-mini-bar"><i style="width:0%"></i></div>
                </td>
              `;
            }

            const width = maxAbs > 0 ? Math.max(3, (Math.abs(value) / maxAbs) * 100) : 0;
            const isLeader =
              selectedCompanies.length > 1 &&
              maxValue !== null &&
              maxValue > 0 &&
              Math.abs(value - maxValue) < 1e-9;

            return `
              <td
                class="metric-cell${isLeader ? " is-leader" : ""}"
                title="${escapeHtml(company.name)} · ${escapeHtml(metric.label)}（${escapeHtml(period)}）：${escapeHtml(formatValue(metric, value))} ${escapeHtml(metric.unit)}"
              >
                <div class="metric-value-line">
                  <strong class="${value < 0 ? "is-negative" : ""}">${escapeHtml(formatValue(metric, value))}</strong>
                  <span>${escapeHtml(metric.unit)}</span>
                </div>
                <div class="metric-mini-bar" aria-hidden="true">
                  <i
                    class="${value < 0 ? "is-negative" : ""}"
                    style="width:${width.toFixed(1)}%"
                  ></i>
                </div>
              </td>
            `;
          })
          .join("");

        return `
          ${groupRow}
          <tr>
            <th scope="row" class="metric-label" title="${escapeHtml(metric.hint)}">
              <strong>${escapeHtml(metric.label)}</strong>
              <span>${escapeHtml(metric.hint)}</span>
            </th>
            ${valueCells}
          </tr>
        `;
      })
      .join("");

    elements.metricsTable.innerHTML = `${header}<tbody>${bodyRows}</tbody>`;
  }

  function renderMetricPicker() {
    const quarterMode = state.historyFrequency === "quarter";
    elements.metricPicker.innerHTML = metricDefinitions
      .map((metric) => {
        const active = state.historyMetrics.includes(metric.key);
        const disabled = quarterMode && metric.annualOnly;
        return `
          <button
            class="metric-chip${active ? " is-active" : ""}"
            type="button"
            data-metric="${escapeHtml(metric.key)}"
            aria-pressed="${active}"
            ${disabled ? "disabled" : ""}
            title="${escapeHtml(disabled ? `${metric.label}仅年度披露` : metric.hint)}"
          >
            <span>${escapeHtml(metric.label)}</span>
            <em class="metric-badge">${
              metric.growth
                ? "增速"
                : metric.annualOnly
                  ? "年度"
                  : escapeHtml(metric.unit)
            }</em>
          </button>
        `;
      })
      .join("");
    elements.metricSelectedCount.textContent = String(state.historyMetrics.length);
  }

  function disposeCharts() {
    state.chartTooltips.forEach((tooltip) => {
      tooltip._cleanup?.();
      tooltip.remove();
    });
    state.chartTooltips = [];
    state.charts.forEach((chart) => chart.dispose());
    state.charts.clear();
    if (state.resizeObserver) {
      state.resizeObserver.disconnect();
      state.resizeObserver = null;
    }
  }

  function renderCharts() {
    disposeCharts();
    const selectedCompanies = state.selected.map(getCompany).filter(Boolean);
    const visibleMetrics = state.historyMetrics
      .map((key) => metricByKey.get(key))
      .filter(Boolean);

    if (!selectedCompanies.length || !visibleMetrics.length) {
      elements.chartGrid.innerHTML = "";
      elements.chartEmpty.hidden = false;
      return;
    }

    elements.chartEmpty.hidden = true;
    elements.chartGrid.innerHTML = visibleMetrics
      .map((metric) => {
        const hidden = state.hiddenByMetric.get(metric.key) || new Set();
        const growthBasis =
          state.historyFrequency === "annual"
            ? "yoy"
            : state.growthBasisByMetric.get(metric.key) || "yoy";
        const visibleCompanies = selectedCompanies.filter(
          (company) => !hidden.has(company.id)
        );
        const toggles = selectedCompanies
          .map((company) => {
            const color = state.companyColors.get(company.id) || SERIES_COLORS[0];
            const isOff = hidden.has(company.id);
            return `
              <button
                class="series-toggle${isOff ? " is-off" : ""}"
                type="button"
                data-toggle-series
                data-metric="${escapeHtml(metric.key)}"
                data-company-id="${escapeHtml(company.id)}"
                aria-pressed="${!isOff}"
                title="${isOff ? "显示" : "隐藏"} ${escapeHtml(company.name)}"
              >
                <i style="background:${color.line}" aria-hidden="true"></i>
                <span>${escapeHtml(company.name)}</span>
              </button>
            `;
          })
          .join("");

        return `
          <article class="chart-panel">
            <div class="chart-panel-head">
              <div class="chart-panel-title">
                <h3>${escapeHtml(metric.label)}</h3>
                <span>${escapeHtml(metric.unit)}</span>
              </div>
              <div class="chart-panel-meta">
                ${
                  metric.growth
                    ? `
                      <div class="growth-basis-toggle" role="group" aria-label="选择增速计算方式">
                        <button
                          type="button"
                          data-growth-basis="yoy"
                          data-metric="${escapeHtml(metric.key)}"
                          class="${growthBasis === "yoy" ? "is-active" : ""}"
                        >同比</button>
                        <button
                          type="button"
                          data-growth-basis="qoq"
                          data-metric="${escapeHtml(metric.key)}"
                          class="${growthBasis === "qoq" ? "is-active" : ""}"
                          ${state.historyFrequency === "annual" ? "disabled" : ""}
                          title="${state.historyFrequency === "annual" ? "年度数据没有环比" : "与上一季度比较"}"
                        >环比</button>
                      </div>
                    `
                    : ""
                }
                <span class="chart-panel-period">${escapeHtml(
                  state.historyFrequency === "annual"
                    ? `${annualPeriods[0]} – ${annualPeriods.at(-1)}`
                    : `${quarterPeriods[0]} – ${quarterPeriods.at(-1)}`
                )}</span>
              </div>
            </div>
            <div
              class="chart-series-toggles"
              role="group"
              aria-label="${escapeHtml(metric.label)}公司显示开关"
            >
              ${toggles}
              ${
                hidden.size
                  ? `<button class="series-reset" type="button" data-reset-series="${escapeHtml(metric.key)}">全部显示</button>`
                  : ""
              }
            </div>
            <div
              class="chart-canvas"
              id="chart-${escapeHtml(metric.key)}"
              role="img"
              aria-label="${escapeHtml(metric.label)}历史${state.chartType === "bar" ? "柱状图" : "曲线"}"
            >${
              visibleCompanies.length
                ? ""
                : '<div class="chart-all-hidden">该指标下的公司已全部关闭</div>'
            }</div>
          </article>
        `;
      })
      .join("");

    if (!window.echarts) {
      elements.chartGrid.innerHTML =
        '<div class="chart-empty"><h3>图表库未加载</h3><p>请检查 vendor/echarts.min.js 是否存在。</p></div>';
      elements.chartEmpty.hidden = true;
      return;
    }

    const periods =
      state.historyFrequency === "annual" ? annualPeriods : quarterPeriods;

    visibleMetrics.forEach((metric) => {
      const growthBasis =
        state.historyFrequency === "annual"
          ? "yoy"
          : state.growthBasisByMetric.get(metric.key) || "yoy";
      const visibleCompanies = visibleCompaniesForMetric(
        metric.key,
        selectedCompanies
      );
      if (!visibleCompanies.length) return;
      const container = document.getElementById(`chart-${metric.key}`);
      if (!container) return;
      const chart = window.echarts.init(container, null, { renderer: "canvas" });
      state.charts.set(metric.key, chart);
      chart.setOption(
        buildChartOption(
          metric,
          visibleCompanies,
          periods,
          state.historyFrequency,
          state.chartType,
          growthBasis
        )
      );
      attachChartHover(
        chart,
        metric,
        visibleCompanies,
        periods,
        state.historyFrequency,
        growthBasis
      );
    });

    if ("ResizeObserver" in window) {
      state.resizeObserver = new ResizeObserver(() => {
        state.charts.forEach((chart) => chart.resize());
      });
      elements.chartGrid
        .querySelectorAll(".chart-canvas")
        .forEach((container) => state.resizeObserver.observe(container));
    }
  }

  function buildChartOption(
    metric,
    selectedCompanies,
    periods,
    frequency,
    chartType,
    growthBasis
  ) {
    const isBar = chartType === "bar";
    const series = selectedCompanies.map((company) => {
      const color = state.companyColors.get(company.id) || SERIES_COLORS[0];
      const data = periods.map((period) =>
        chartMetricValue(company, metric, frequency, period, growthBasis)
      );
      if (isBar) {
        return {
          name: company.name,
          type: "bar",
          data,
          barMaxWidth: 18,
          barGap: "12%",
          itemStyle: {
            color: color.line,
            borderRadius: [3, 3, 0, 0],
          },
          emphasis: {
            focus: "series",
            itemStyle: { opacity: 1 },
          },
          blur: {
            itemStyle: { opacity: 0.15 },
          },
        };
      }
      return {
        name: company.name,
        type: "line",
        data,
        smooth: 0.22,
        connectNulls: false,
        showSymbol: true,
        symbol: "circle",
        symbolSize: XHS_MODE ? 5 : 4.5,
        lineStyle: {
          width: 2.1,
          color: color.line,
        },
        itemStyle: {
          color: color.line,
          borderColor: "#fff",
          borderWidth: 1,
        },
        emphasis: {
          focus: "series",
          lineStyle: { width: 3 },
          itemStyle: { symbolSize: 7 },
        },
        blur: {
          lineStyle: { opacity: 0.14 },
          itemStyle: { opacity: 0.14 },
        },
      };
    });

    const useZoom = isBar && periods.length > 8;
    return {
      animationDuration: 480,
      color: selectedCompanies.map(
        (company) =>
          (state.companyColors.get(company.id) || SERIES_COLORS[0]).line
      ),
      grid: {
        top: 18,
        right: 22,
        bottom: useZoom ? 50 : 30,
        left: 56,
        containLabel: false,
      },
      tooltip: {
        show: false,
      },
      xAxis: {
        type: "category",
        boundaryGap: isBar,
        data: periods,
        axisTick: { show: false },
        axisLine: { lineStyle: { color: "#dfe4e9" } },
        axisLabel: {
          color: "#8791a1",
          fontSize: XHS_MODE ? 10 : 8,
          margin: 11,
          hideOverlap: true,
          interval: frequency === "annual" ? 0 : "auto",
          rotate: isBar && frequency === "quarter" ? 30 : 0,
          fontFamily: "Bahnschrift, Segoe UI, Microsoft YaHei, sans-serif",
        },
      },
      yAxis: {
        type: "value",
        scale: ["netProfit", "ocf"].includes(metric.key),
        splitNumber: 4,
        axisLabel: {
          color: "#8c95a4",
          fontSize: XHS_MODE ? 10 : 8,
          formatter: (value) => formatAxisValue(metric, value),
        },
        splitLine: {
          lineStyle: { color: "#eef1f4", type: "dashed" },
        },
      },
      dataZoom: useZoom
        ? [
            { type: "inside", xAxisIndex: 0 },
            {
              type: "slider",
              xAxisIndex: 0,
              height: 14,
              bottom: 8,
              borderColor: "transparent",
              backgroundColor: "#f3f5f8",
              fillerColor: "rgba(37, 99, 235, 0.12)",
              handleStyle: { color: "#2563eb" },
              textStyle: {
                color: "#8c95a4",
                fontSize: XHS_MODE ? 9 : 8,
              },
            },
          ]
        : undefined,
      series: isBar
        ? series
        : series.map((item) => ({
            ...item,
            markLine: {
              silent: true,
              symbol: "none",
              lineStyle: { color: "#cbd2db", type: "dashed", width: 1 },
              label: { show: false },
              data: [{ yAxis: 0 }],
            },
          })),
    };
  }

  function attachChartHover(
    chart,
    metric,
    selectedCompanies,
    periods,
    frequency,
    growthBasis
  ) {
    const dom = chart.getDom();
    const tooltip = document.createElement("div");
    tooltip.className = "chart-floating-tip";
    document.body.appendChild(tooltip);
    state.chartTooltips.push(tooltip);

    const dataBySeries = selectedCompanies.map((company) => {
      return periods.map((period) =>
        chartMetricValue(company, metric, frequency, period, growthBasis)
      );
    });

    let focusedSeriesIndex = -1;

    const resetSeriesStyles = () => {
      if (focusedSeriesIndex === -1) return;
      chart.setOption(
        {
          series: selectedCompanies.map(() => ({
            lineStyle: { opacity: 1, width: 2.1 },
            itemStyle: { opacity: 1 },
            symbolSize: 4.5,
          })),
        },
        { lazyUpdate: true }
      );
      focusedSeriesIndex = -1;
    };

    const focusSeries = (index) => {
      if (focusedSeriesIndex === index) return;
      chart.setOption(
        {
          series: selectedCompanies.map((_, seriesIndex) => ({
            lineStyle: {
              opacity: seriesIndex === index ? 1 : 0.13,
              width: seriesIndex === index ? 2.9 : 1.6,
            },
            itemStyle: {
              opacity: seriesIndex === index ? 1 : 0.13,
            },
            symbolSize: seriesIndex === index ? 6.5 : 3.2,
          })),
        },
        { lazyUpdate: true }
      );
      focusedSeriesIndex = index;
    };

    const hide = () => {
      tooltip.classList.remove("is-visible");
      resetSeriesStyles();
    };

    const handleMove = (event) => {
      const offsetX = event.offsetX;
      const offsetY = event.offsetY;
      if (
        offsetX < 50 ||
        offsetX > chart.getWidth() - 18 ||
        offsetY < 46 ||
        offsetY > chart.getHeight() - 30
      ) {
        hide();
        return;
      }

      let periodIndex = -1;
      let nearestX = Number.POSITIVE_INFINITY;
      periods.forEach((_, index) => {
        let periodPixel = null;
        try {
          const converted = chart.convertToPixel({ xAxisIndex: 0 }, index);
          periodPixel = Array.isArray(converted) ? converted[0] : converted;
        } catch (error) {
          periodPixel = null;
        }
        if (Number.isFinite(periodPixel)) {
          const distance = Math.abs(periodPixel - offsetX);
          if (distance < nearestX) {
            nearestX = distance;
            periodIndex = index;
          }
          return;
        }
        for (let seriesIndex = 0; seriesIndex < dataBySeries.length; seriesIndex += 1) {
          const value = dataBySeries[seriesIndex][index];
          if (!Number.isFinite(value)) continue;
          const pixel = chart.convertToPixel(
            { seriesIndex },
            [index, value]
          );
          if (!pixel) break;
          const distance = Math.abs(pixel[0] - offsetX);
          if (distance < nearestX) {
            nearestX = distance;
            periodIndex = index;
          }
          break;
        }
      });

      if (periodIndex < 0 || nearestX > 38) {
        hide();
        return;
      }

      let seriesIndex = -1;
      let nearestY = Number.POSITIVE_INFINITY;
      dataBySeries.forEach((values, index) => {
        const value = values[periodIndex];
        if (!Number.isFinite(value)) return;
        const pixel = chart.convertToPixel(
          { seriesIndex: index },
          [periodIndex, value]
        );
        if (!pixel) return;
        const distance = Math.abs(pixel[1] - offsetY);
        if (distance < nearestY) {
          nearestY = distance;
          seriesIndex = index;
        }
      });

      if (seriesIndex < 0) {
        hide();
        return;
      }

      const period = periods[periodIndex];
      const rows = selectedCompanies
        .map((company, index) => ({
          name: company.name,
          value: dataBySeries[index][periodIndex],
          color:
            (state.companyColors.get(company.id) || SERIES_COLORS[0]).line,
          active: index === seriesIndex,
        }))
        .filter((row) => Number.isFinite(row.value));

      if (!rows.length) {
        hide();
        return;
      }

      tooltip.innerHTML = `
        <div class="chart-tip-period">${escapeHtml(period)}</div>
        ${rows
          .map(
            (row) => `
              <div class="chart-tip-row ${row.active ? "is-active" : "is-dim"}">
                <span class="chart-tip-company">
                  <i style="background:${row.color}" aria-hidden="true"></i>
                  ${escapeHtml(row.name)}
                </span>
                <strong class="chart-tip-value">
                  ${escapeHtml(formatValue(metric, row.value))}
                  <small>${escapeHtml(metric.unit)}</small>
                </strong>
              </div>
            `
          )
          .join("")}
      `;

      focusSeries(seriesIndex);

      const rect = dom.getBoundingClientRect();
      const margin = 10;
      const tooltipWidth = tooltip.offsetWidth;
      const tooltipHeight = tooltip.offsetHeight;
      let left = rect.left + offsetX + 16;
      let top = rect.top + offsetY + 16;

      if (left + tooltipWidth > window.innerWidth - margin) {
        left = rect.left + offsetX - tooltipWidth - 16;
      }
      if (top + tooltipHeight > window.innerHeight - margin) {
        top = window.innerHeight - tooltipHeight - margin;
      }

      tooltip.style.left = `${Math.max(margin, left)}px`;
      tooltip.style.top = `${Math.max(margin, top)}px`;
      tooltip.classList.add("is-visible");
    };

    const handleScroll = () => hide();
    chart.getZr().on("mousemove", handleMove);
    chart.getZr().on("globalout", hide);
    window.addEventListener("scroll", handleScroll, { passive: true });

    tooltip._cleanup = () => {
      window.removeEventListener("scroll", handleScroll);
      chart.getZr().off("mousemove", handleMove);
      chart.getZr().off("globalout", hide);
    };
  }

  function updateChrome() {
    const count = state.selected.length;
    elements.selectionCount.textContent = `${count} / ${MAX_COMPARE}`;
    elements.companyTotal.textContent = String(companies.length);
    elements.headerPeriod.textContent = latestQuarter.replace("Q", " Q");
    elements.exportBtn.disabled = count === 0;
    elements.shareBtn.disabled = count === 0;
    elements.clearBtn.disabled = count === 0;

    const periods =
      state.tableFrequency === "annual" ? annualPeriods : quarterPeriods;
    if (!periods.includes(state.tablePeriod)) {
      state.tablePeriod = periods.at(-1);
    }
    elements.tableFrequency.value = state.tableFrequency;
    elements.tablePeriod.innerHTML = periods
      .map(
        (period) =>
          `<option value="${escapeHtml(period)}">${escapeHtml(period)}${state.tableFrequency === "quarter" ? " 单季" : " 年报"}</option>`
      )
      .join("");
    elements.tablePeriod.value = state.tablePeriod;

    elements.tablePeriodNote.textContent =
      state.tableFrequency === "annual"
        ? `年度口径：${state.tablePeriod} 年报 · 财务单位：亿元 · 薪酬单位：万元 / 年`
        : `单季口径：${state.tablePeriod} · 财务单位：亿元 · 人员与薪酬指标仅在年度视图提供`;

    elements.historyRange.textContent =
      state.historyFrequency === "annual"
        ? `${annualPeriods[0]} – ${annualPeriods.at(-1)}`
        : `${quarterPeriods[0]} – ${latestQuarter}`;
    elements.historyModeNote.textContent =
      state.historyFrequency === "annual"
        ? `${state.chartType === "bar" ? "柱状图" : "折线图"} · 年度视图包含人员、薪酬与研发人员数据`
        : `${state.chartType === "bar" ? "柱状图" : "折线图"} · 单季视图仅展示财务指标`;
  }

  function renderAll() {
    rebuildCompanyColors();
    pruneHiddenSeries();
    updateChrome();
    renderQuickPicks();
    renderCompanyCards();
    renderTable();
    renderMetricPicker();
    renderCharts();
    if (state.searchOpen) renderSearch();
  }

  function applySelection(nextSelected) {
    state.selected = sanitizeIds(nextSelected);
    persistSelection();
    renderAll();
  }

  function addCompany(id) {
    const company = getCompany(id);
    if (!company) return;
    if (isSelected(id)) {
      showToast(`${company.name} 已在对比清单中`);
      return;
    }
    if (state.selected.length >= MAX_COMPARE) {
      showToast(`最多同时对比 ${MAX_COMPARE} 家公司`);
      return;
    }

    applySelection([...state.selected, id]);
    showToast(`${company.name} 已加入对比`);
    elements.search.value = "";
    state.query = "";
    state.activeIndex = -1;
    setSearchOpen(false);
  }

  function removeCompany(id) {
    const company = getCompany(id);
    if (!company) return;
    applySelection(state.selected.filter((selectedId) => selectedId !== id));
    showToast(`${company.name} 已移出对比`);
  }

  function showToast(message) {
    window.clearTimeout(state.toastTimer);
    elements.toast.textContent = message;
    elements.toast.classList.add("is-visible");
    state.toastTimer = window.setTimeout(() => {
      elements.toast.classList.remove("is-visible");
    }, 2200);
  }

  function focusSearch() {
    elements.search.focus();
    elements.search.select();
    setSearchOpen(true);
  }

  function exportCsv() {
    const selectedCompanies = state.selected.map(getCompany).filter(Boolean);
    if (!selectedCompanies.length) {
      showToast("请先添加公司");
      return;
    }

    const period = state.tablePeriod;
    const frequency = state.tableFrequency;
    const visibleMetrics = getVisibleTableMetrics();
    const rows = [
      ["A 股模拟芯片公司对比", period, "财务单位：亿元", "薪酬单位：万元 / 年"],
      [],
      ["指标", "单位", ...selectedCompanies.map((company) => company.name)],
    ];

    visibleMetrics.forEach((metric) => {
      rows.push([
        metric.label,
        metric.unit,
        ...selectedCompanies.map((company) => {
          const row = getRow(company, frequency, period);
          return row && Number.isFinite(row[metric.key])
            ? formatValue(metric, row[metric.key])
            : "";
        }),
      ]);
    });

    rows.push([]);
    rows.push([
      "数据说明",
      "数据来源：东方财富公开财务数据接口；研发薪酬为按研发人员占比分摊的估算值。",
    ]);

    const csv = rows
      .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\r\n");
    const blob = new Blob([`\ufeff${csv}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    const date = new Date().toISOString().slice(0, 10);
    anchor.href = url;
    anchor.download = `模拟芯片公司对比_${period}_${date}.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast("CSV 已导出");
  }

  async function copyShareLink() {
    persistSelection();
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      showToast("对比链接已复制");
      return;
    } catch (error) {
      // Fall back for file:// and older browsers.
    }

    const temporaryInput = document.createElement("textarea");
    temporaryInput.value = url;
    temporaryInput.style.position = "fixed";
    temporaryInput.style.opacity = "0";
    document.body.appendChild(temporaryInput);
    temporaryInput.select();
    try {
      const copied = document.execCommand("copy");
      showToast(copied ? "对比链接已复制" : "复制失败，请手动复制地址栏");
    } catch (error) {
      showToast("复制失败，请手动复制地址栏");
    } finally {
      temporaryInput.remove();
    }
  }

  function bindEvents() {
    elements.search.addEventListener("focus", () => setSearchOpen(true));
    elements.search.addEventListener("input", (event) => {
      state.query = event.target.value;
      state.activeIndex = -1;
      setSearchOpen(true);
    });

    elements.search.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        if (!state.searchOpen) setSearchOpen(true);
        state.activeIndex = Math.min(
          state.activeIndex + 1,
          state.searchResults.length - 1
        );
        updateActiveSearchResult();
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        state.activeIndex = Math.max(state.activeIndex - 1, 0);
        updateActiveSearchResult();
      }

      if (event.key === "Enter" && state.activeIndex >= 0) {
        const company = state.searchResults[state.activeIndex];
        if (company) {
          event.preventDefault();
          addCompany(company.id);
        }
      }

      if (event.key === "Escape") {
        setSearchOpen(false);
        elements.search.blur();
      }
    });

    elements.searchResults.addEventListener("click", (event) => {
      const result = event.target.closest("[data-company-id]");
      if (result) addCompany(result.dataset.companyId);
    });

    elements.searchShell.addEventListener("click", (event) => {
      event.stopPropagation();
    });

    document.addEventListener("pointerdown", (event) => {
      if (!elements.searchShell.contains(event.target)) setSearchOpen(false);
    });

    document.addEventListener("keydown", (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        focusSearch();
      }
    });

    elements.quickPicks.addEventListener("click", (event) => {
      const button = event.target.closest("[data-quick-id]");
      if (button) addCompany(button.dataset.quickId);
    });

    elements.companyCards.addEventListener("click", (event) => {
      const button = event.target.closest("[data-remove-id]");
      if (button) removeCompany(button.dataset.removeId);
    });

    elements.emptyAddBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
      window.setTimeout(focusSearch, 360);
    });

    elements.clearBtn.addEventListener("click", () => {
      if (!state.selected.length) return;
      applySelection([]);
      showToast("对比清单已清空");
    });

    elements.shareBtn.addEventListener("click", copyShareLink);
    elements.exportBtn.addEventListener("click", exportCsv);

    elements.tableFrequency.addEventListener("change", (event) => {
      state.tableFrequency = event.target.value;
      state.tablePeriod =
        state.tableFrequency === "annual" ? latestAnnual : latestQuarter;
      updateChrome();
      renderTable();
    });

    elements.tablePeriod.addEventListener("change", (event) => {
      state.tablePeriod = event.target.value;
      updateChrome();
      renderTable();
    });

    elements.frequencyToggle.addEventListener("click", (event) => {
      const button = event.target.closest("[data-frequency]");
      if (!button || button.dataset.frequency === state.historyFrequency) return;
      state.historyFrequency = button.dataset.frequency;
      elements.frequencyToggle.querySelectorAll("[data-frequency]").forEach((item) => {
        item.classList.toggle(
          "is-active",
          item.dataset.frequency === state.historyFrequency
        );
      });

      if (state.historyFrequency === "quarter") {
        const removed = state.historyMetrics.filter(
          (key) => metricByKey.get(key)?.annualOnly
        );
        state.historyMetrics = state.historyMetrics.filter(
          (key) => !metricByKey.get(key)?.annualOnly
        );
        if (!state.historyMetrics.length) state.historyMetrics = ["revenue"];
        if (removed.length) showToast("人员与薪酬指标仅提供年度数据");
      }

      updateChrome();
      renderMetricPicker();
      renderCharts();
    });

    elements.metricPicker.addEventListener("click", (event) => {
      const button = event.target.closest("[data-metric]");
      if (!button || button.disabled) return;
      const key = button.dataset.metric;
      if (state.historyMetrics.includes(key)) {
        state.historyMetrics = state.historyMetrics.filter((item) => item !== key);
      } else {
        if (state.historyMetrics.length >= MAX_METRICS) {
          showToast(`最多同时展示 ${MAX_METRICS} 个指标`);
          return;
        }
        state.historyMetrics.push(key);
      }
      renderMetricPicker();
      renderCharts();
    });

    elements.chartTypeToggle.addEventListener("click", (event) => {
      const button = event.target.closest("[data-chart-type]");
      if (!button || button.dataset.chartType === state.chartType) return;
      state.chartType = button.dataset.chartType;
      elements.chartTypeToggle
        .querySelectorAll("[data-chart-type]")
        .forEach((item) => {
          item.classList.toggle(
            "is-active",
            item.dataset.chartType === state.chartType
          );
        });
      updateChrome();
      renderCharts();
    });

    elements.chartGrid.addEventListener("click", (event) => {
      const basisButton = event.target.closest("[data-growth-basis]");
      if (basisButton && !basisButton.disabled) {
        state.growthBasisByMetric.set(
          basisButton.dataset.metric,
          basisButton.dataset.growthBasis
        );
        renderCharts();
        return;
      }

      const toggle = event.target.closest("[data-toggle-series]");
      if (toggle) {
        const metricKey = toggle.dataset.metric;
        const companyId = toggle.dataset.companyId;
        const hidden = state.hiddenByMetric.get(metricKey) || new Set();
        if (hidden.has(companyId)) {
          hidden.delete(companyId);
        } else {
          hidden.add(companyId);
        }
        state.hiddenByMetric.set(metricKey, hidden);
        renderCharts();
        return;
      }

      const reset = event.target.closest("[data-reset-series]");
      if (reset) {
        state.hiddenByMetric.delete(reset.dataset.resetSeries);
        renderCharts();
      }
    });

    window.addEventListener("resize", () => {
      state.charts.forEach((chart) => chart.resize());
    });

    if ("IntersectionObserver" in window) {
      const linkBySection = new Map(
        elements.navLinks.map((link) => [link.dataset.nav, link])
      );
      const observer = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
          if (!visible) return;
          const link = linkBySection.get(visible.target.id);
          if (!link) return;
          elements.navLinks.forEach((item) => {
            item.classList.toggle("is-active", item === link);
          });
        },
        { rootMargin: "-20% 0px -55% 0px", threshold: [0.08, 0.25, 0.5] }
      );

      ["compare", "metrics", "history"].forEach((id) => {
        const section = document.getElementById(id);
        if (section) observer.observe(section);
      });
    }
  }

  function init() {
    state.selected = readInitialSelection();
    bindEvents();
    renderAll();
  }

  init();
})();
