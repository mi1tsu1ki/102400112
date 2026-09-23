const API_BASE = "";


async function requestJson(path, options = {}) {
    const response = await fetch(API_BASE + path, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "請求失敗");
    }

    return data;
}


function searchPaper() {
    const keyword = document.getElementById("keyword").value;

    requestJson("/search?q=" + encodeURIComponent(keyword))
        .then(data => {
            document.getElementById("info").textContent =
                "找到 " + data.count + " 篇論文";

            const html = data.results.map(paper => `
                <div class="paper">
                    <h3>${paper.title}</h3>
                    <div class="paper-actions">
                        <a href="${paper.url}" target="_blank" rel="noopener noreferrer">
                            查看論文
                        </a>
                        <button class="detail-button" type="button">
                            查看詳細資料
                        </button>
                    </div>
                </div>
            `).join("");

            document.getElementById("result").innerHTML = html;
            document.getElementById("paper-detail").hidden = true;

            document.querySelectorAll(".detail-button").forEach((button, index) => {
                button.addEventListener("click", () => {
                    showPaperDetail(data.results[index].title);
                });
            });
        })
        .catch(error => {
            document.getElementById("info").textContent = error.message;
            document.getElementById("result").innerHTML = "";
        });
}


function showPaperDetail(title) {
    const detailSection = document.getElementById("paper-detail");
    const detailContent = document.getElementById("detail-content");

    detailSection.hidden = false;
    detailContent.innerHTML = "<p>正在載入詳細資料...</p>";

    requestJson("/paper/" + encodeURIComponent(title))
        .then(paper => {
            const authors = paper.authors.length > 0
                ? paper.authors.join(", ")
                : "無作者資料";

            detailContent.innerHTML = `
                <h3>${paper.title}</h3>
                <dl>
                    <dt>Authors</dt>
                    <dd>${authors}</dd>
                    <dt>Year</dt>
                    <dd>${paper.year}</dd>
                    <dt>Conference</dt>
                    <dd>${paper.conference}</dd>
                    <dt>PDF</dt>
                    <dd><a href="${paper.pdf}" target="_blank" rel="noopener noreferrer">${paper.pdf || "無"}</a></dd>
                    <dt>URL</dt>
                    <dd><a href="${paper.url}" target="_blank" rel="noopener noreferrer">${paper.url}</a></dd>
                </dl>
            `;

            detailSection.scrollIntoView({ behavior: "smooth", block: "start" });
        })
        .catch(error => {
            detailContent.innerHTML = `<p class="detail-error">${error.message}</p>`;
        });
}


function loadTopics() {
    requestJson("/topics")
        .then(data => {
            const html = data.topics.map(topic => `
                <div class="topic" onclick="searchTopic('${topic.keyword}')">
                    ${topic.keyword} (${topic.count})
                </div>
            `).join("");

            document.getElementById("topics").innerHTML = html;
        })
        .catch(error => {
            document.getElementById("topics").textContent = error.message;
        });
}


function searchTopic(keyword) {
    document.getElementById("keyword").value = keyword;
    searchPaper();
}


function loadKeywordNetwork() {
    requestJson("/keyword-network")
        .then(data => {
            const networkChart = echarts.init(
                document.getElementById("keyword-network")
            );

            networkChart.on("click", params => {
                if (params.dataType === "node" && params.data.name) {
                    searchTopic(params.data.name);
                }
            });

            networkChart.setOption({
                tooltip: {
                    formatter: params => params.dataType === "node"
                        ? "Keyword: " + params.data.name +
                          "<br>Count: " + params.data.value
                        : ""
                },
                series: [{
                    type: "graph",
                    layout: "force",
                    roam: true,
                    data: data.nodes.map(node => ({
                        name: node.id,
                        value: node.count,
                        symbolSize: Math.min(node.count / 5 + 10, 50)
                    })),
                    links: data.links,
                    lineStyle: { opacity: 0.3 },
                    label: {
                        show: true,
                        formatter: params => params.data.value >= 30
                            ? params.data.name
                            : ""
                    },
                    emphasis: { focus: "adjacency" },
                    force: { repulsion: 200, edgeLength: 120 }
                }]
            });
        })
        .catch(error => {
            document.getElementById("keyword-network").textContent = error.message;
        });
}


function loadTrendChart() {
    requestJson("/trend?top=10")
        .then(data => {
            const trendChart = echarts.init(
                document.getElementById("trend-chart")
            );

            trendChart.setOption({
                tooltip: { trigger: "axis" },
                legend: {
                    type: "scroll",
                    data: data.series.map(item => item.name)
                },
                xAxis: {
                    type: "category",
                    data: data.years
                },
                yAxis: { type: "value" },
                series: data.series
            });
        })
        .catch(error => {
            document.getElementById("trend-chart").textContent = error.message;
        });
}


function addPaper() {
    const data = {
        title: document.getElementById("crud-title").value,
        authors: [document.getElementById("crud-author").value],
        year: Number(document.getElementById("crud-year").value),
        conference: document.getElementById("crud-conference").value,
        pdf: "",
        url: ""
    };

    requestJson("/paper", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(() => {
            alert("新增成功");
            document.getElementById("crud-title").value = "";
        })
        .catch(error => alert(error.message));
}


function updatePaper() {
    const title = document.getElementById("crud-title").value;
    const data = {
        authors: [document.getElementById("crud-author").value],
        year: Number(document.getElementById("crud-year").value),
        conference: document.getElementById("crud-conference").value
    };

    requestJson("/paper/" + encodeURIComponent(title), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(() => alert("修改成功"))
        .catch(error => alert(error.message));
}


function deletePaper() {
    const title = document.getElementById("crud-title").value;

    requestJson("/paper/" + encodeURIComponent(title), {
        method: "DELETE"
    })
        .then(() => {
            alert("刪除成功");
            searchPaper();
        })
        .catch(error => alert(error.message));
}


loadTopics();
loadKeywordNetwork();
setTimeout(loadTrendChart, 500);

function loadAnnualTrendChart() {
    requestJson("/trend?top=5")
        .then(data => {
            const annualTrendChart = echarts.init(
                document.getElementById("annual-trend-chart")
            );

            annualTrendChart.setOption({
                title: { text: '歷年 Top 5 熱點領域變化' },
                tooltip: { trigger: "axis", axisPointer: { type: 'shadow' } },
                legend: {
                    type: "scroll",
                    top: 30,
                    data: data.series.map(item => item.name)
                },
                xAxis: {
                    type: "category",
                    data: data.years
                },
                yAxis: { type: "value" },
                series: data.series.map(s => ({
                    name: s.name,
                    type: "bar",
                    stack: "total",
                    data: s.data
                }))
            });
        })
        .catch(error => {
            const el = document.getElementById("annual-trend-chart");
            if(el) el.textContent = error.message;
        });
}

setTimeout(loadAnnualTrendChart, 800);
