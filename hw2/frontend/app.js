const { createApp, computed, nextTick, onBeforeUnmount, onMounted, ref } = Vue;
const { ElMessage } = ElementPlus;

const raceData = {
  2022: { Transformer: 92, "Object Detection": 78, "Self-Supervised": 64, Diffusion: 48, "Neural Rendering": 35 },
  2023: { Diffusion: 96, Transformer: 88, "Neural Rendering": 76, "Object Detection": 69, "Self-Supervised": 52 },
  2024: { "Neural Rendering": 108, Diffusion: 101, "Multimodal LLM": 94, Transformer: 83, "Object Detection": 72 },
};

createApp({
  setup() {
    const activeTab = ref("papers");
    const keyword = ref("");
    const loading = ref(false);
    const papers = ref([]);
    const crawlDialogVisible = ref(false);
    const crawlLoading = ref(false);
    const crawlFormRef = ref(null);
    const crawlForm = ref({ conference: "", year: null });
    const availableYears = [2022, 2023, 2024, 2025, 2026];
    const crawlRules = {
      conference: [{ required: true, message: "請選擇會議名稱", trigger: "change" }],
      year: [{ required: true, message: "請選擇年份", trigger: "change" }],
    };
    const graphContainer = ref(null);
    const racingContainer = ref(null);
    let graphChart = null;
    let racingChart = null;
    let raceTimer = null;

    const filteredPapers = computed(() => {
      const query = keyword.value.trim().toLowerCase();
      if (!query) return papers.value;
      return papers.value.filter((paper) =>
        `${paper.title} ${paper.authors}`.toLowerCase().includes(query),
      );
    });

    const loadPapers = async () => {
      loading.value = true;
      try {
        const response = await fetch("/api/papers");
        if (!response.ok) throw new Error("無法取得論文資料");
        papers.value = await response.json();
      } catch (error) {
        ElMessage.error(error.message);
      } finally {
        loading.value = false;
      }
    };

    const submitCrawl = async () => {
      if (!crawlFormRef.value) return;
      const valid = await crawlFormRef.value.validate().catch(() => false);
      if (!valid) return;

      crawlLoading.value = true;
      try {
        const response = await fetch("/api/crawl", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(crawlForm.value),
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "爬取資料失敗");
        ElMessage.success(
          `完成：取得 ${result.fetched_count} 篇，寫入 ${result.saved_count} 筆`,
        );
        crawlDialogVisible.value = false;
        await loadPapers();
      } catch (error) {
        ElMessage.error(error.message);
      } finally {
        crawlLoading.value = false;
      }
    };

    const loadKeywordGraph = async () => {
      await nextTick();
      if (!graphContainer.value) return;
      if (!graphChart) graphChart = echarts.init(graphContainer.value);
      try {
        const response = await fetch("/api/keyword-graph");
        if (!response.ok) throw new Error("無法取得關鍵詞圖譜");
        const graph = await response.json();
        graphChart.setOption({
          tooltip: {},
          animationDuration: 900,
          series: [{
            type: "graph",
            layout: "force",
            roam: true,
            data: graph.nodes,
            links: graph.links,
            label: { show: true, position: "right" },
            force: { repulsion: 260, edgeLength: [80, 180] },
            lineStyle: { color: "#94a3b8", opacity: 0.65 },
          }],
        });
      } catch (error) {
        ElMessage.error(error.message);
      }
    };

    const renderRace = (year) => {
      if (!racingChart) return;
      const values = Object.entries(raceData[year])
        .sort(([, first], [, second]) => second - first);
      racingChart.setOption({
        title: { text: `${year} 年熱門研究詞彙`, left: "center" },
        grid: { top: 55, right: 32, bottom: 28, left: 145 },
        xAxis: { max: "dataMax", splitLine: { show: false } },
        yAxis: {
          type: "category",
          inverse: true,
          data: values.map(([name]) => name),
          animationDuration: 300,
          animationDurationUpdate: 500,
        },
        series: [{
          type: "bar",
          realtimeSort: true,
          data: values.map(([, value]) => value),
          label: { show: true, position: "right", valueAnimation: true },
          itemStyle: { color: "#409eff", borderRadius: [0, 5, 5, 0] },
        }],
        animationDuration: 0,
        animationDurationUpdate: 1000,
      });
    };

    const startRace = () => {
      if (!racingContainer.value) return;
      if (!racingChart) racingChart = echarts.init(racingContainer.value);
      clearInterval(raceTimer);
      const years = Object.keys(raceData);
      let index = 0;
      renderRace(years[index]);
      raceTimer = setInterval(() => {
        index = (index + 1) % years.length;
        renderRace(years[index]);
      }, 2400);
    };

    const restartRace = () => {
      startRace();
    };

    const handleTabChange = (tabName) => {
      if (tabName === "graph") loadKeywordGraph();
      if (tabName === "racing") nextTick(startRace);
    };

    const resizeCharts = () => {
      graphChart?.resize();
      racingChart?.resize();
    };

    onMounted(() => {
      loadPapers();
      window.addEventListener("resize", resizeCharts);
    });
    onBeforeUnmount(() => {
      clearInterval(raceTimer);
      window.removeEventListener("resize", resizeCharts);
      graphChart?.dispose();
      racingChart?.dispose();
    });

    return {
      activeTab,
      keyword,
      loading,
      filteredPapers,
      crawlDialogVisible,
      crawlLoading,
      crawlFormRef,
      crawlForm,
      crawlRules,
      availableYears,
      graphContainer,
      racingContainer,
      loadPapers,
      submitCrawl,
      loadKeywordGraph,
      restartRace,
      handleTabChange,
    };
  },
}).use(ElementPlus).mount("#app");
