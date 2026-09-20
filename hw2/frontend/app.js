const { createApp, ref, onMounted } = Vue;
const { ElMessage } = ElementPlus;

createApp({
  setup() {
    const keyword = ref("");
    const loading = ref(false);
    const terms = ref([]);

    const loadTerms = async () => {
      loading.value = true;
      try {
        const response = await fetch(`/api/terms?q=${encodeURIComponent(keyword.value)}`);
        if (!response.ok) {
          throw new Error("無法取得熱詞資料");
        }
        terms.value = await response.json();
      } catch (error) {
        ElMessage.error(error.message);
      } finally {
        loading.value = false;
      }
    };

    const trendLabel = (trend) => ({ up: "上升", down: "下降", stable: "穩定" }[trend] || "穩定");
    const trendType = (trend) => ({ up: "danger", down: "success", stable: "info" }[trend] || "info");

    onMounted(loadTerms);
    return { keyword, loading, terms, loadTerms, trendLabel, trendType };
  },
}).use(ElementPlus).mount("#app");
