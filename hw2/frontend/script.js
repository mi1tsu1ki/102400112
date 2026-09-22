function searchPaper() {

    let keyword = document.getElementById("keyword").value;

    fetch("http://127.0.0.1:5000/search?q=" + keyword)
        .then(response => response.json())
        .then(data => {

            document.getElementById("info").innerHTML =
                "找到 " + data.count + " 篇論文";

            let html = "";

            data.results.forEach(paper => {

                html += `
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
                `;

            });

            document.getElementById("result").innerHTML = html;
            document.getElementById("paper-detail").hidden = true;

            document.querySelectorAll(".detail-button").forEach((button, index) => {
                button.addEventListener("click", () => {
                    showPaperDetail(data.results[index].title);
                });
            });

        });

}


function showPaperDetail(title) {

    const detailSection = document.getElementById("paper-detail");
    const detailContent = document.getElementById("detail-content");

    detailSection.hidden = false;
    detailContent.innerHTML = "<p>正在載入詳細資料...</p>";

    fetch("http://127.0.0.1:5000/paper/" + encodeURIComponent(title))
        .then(response => {
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error("目前沒有這篇論文的詳細資料。");
                }

                throw new Error("讀取詳細資料失敗。");
            }

            return response.json();
        })
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
                    <dd><a href="${paper.pdf}" target="_blank" rel="noopener noreferrer">${paper.pdf}</a></dd>
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

    fetch("http://127.0.0.1:5000/topics")
        .then(response => response.json())
        .then(data => {

            let html = "";

            data.topics.forEach(topic => {

                html += `
                <div class="topic" onclick="searchTopic('${topic.keyword}')">
                    ${topic.keyword}
                    (${topic.count})
                </div>
                `;

            });

            document.getElementById("topics").innerHTML = html;

        });

}

loadTopics();


function searchTopic(keyword) {

    document.getElementById("keyword").value = keyword;

    searchPaper();

}


function loadKeywordNetwork() {

    fetch("http://127.0.0.1:5000/keyword-network")
        .then(response => response.json())
        .then(data => {

            let networkChart = echarts.init(
                document.getElementById("keyword-network")
            );


            let option = {

                tooltip: {
                    formatter: function (params) {
                        if (params.dataType === "node") {
                            return (
                                "Keyword: " +
                                params.data.name +
                                "<br>Count: " +
                                params.data.value
                            );
                        }
                        return "";
                    }
                },

                series: [
                    {
                        type: "graph",
                        layout: "force",
                        roam: true,

                        data: data.nodes.map(node => {
                            return {
                                name: node.id,
                                value: node.count,
                                symbolSize: Math.min(node.count / 5 + 10, 50)
                            };
                        }),

                        links: data.links,
                        lineStyle: {
                            opacity: 0.3
                        },

                        label: {
                            show: true,
                            formatter: function (params) {
                                return params.data.value >= 30
                                    ? params.data.name
                                    : "";
                            }
                        },

                        emphasis: {
                            focus: "adjacency"
                        },

                        force: {
                            repulsion: 200,
                            edgeLength: 120
                        },
                    }
                ]

            };

            networkChart.on("click", function (params) {
                if (
                    params.dataType === "node" &&
                    params.data.name
                ) {
                    searchTopic(params.data.name);
                }
            });

            networkChart.setOption(option);

        });

}

loadKeywordNetwork();


function loadTrendChart() {

    fetch("http://127.0.0.1:5000/trend")
        .then(response => response.json())
        .then(data => {


            let trendChart = echarts.init(
                document.getElementById("trend-chart")
            );


            let trends = data.data;


            let keywords = [
                ...new Set(
                    trends.map(item => item.keyword)
                )
            ];


            let series = keywords.map(keyword => {

                return {

                    name: keyword,

                    type: "line",

                    data:
                        trends
                            .filter(item => item.keyword === keyword)
                            .map(item => item.count)
                };
            });



            trendChart.setOption({

                tooltip: {
                    trigger: "axis"
                },


                legend: {
                    data: keywords
                },


                xAxis: {
                    type: "category",
                    data: [2022, 2023, 2024]
                },


                yAxis: {
                    type: "value"
                },


                series: series

            });


        });

}


function addPaper() {

    let data = {

        title:
            document.getElementById("crud-title").value,

        authors: [
            document.getElementById("crud-author").value
        ],

        year:
            Number(document.getElementById("crud-year").value),

        conference:
            document.getElementById("crud-conference").value,

        pdf: "",
        url: ""

    };


    fetch(
        "http://127.0.0.1:5000/paper",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body:
                JSON.stringify(data)
        }
    )
        .then(response => response.json())
        .then(data => {

            alert("新增成功");
            document.getElementById("crud-title").value = "";
        });

}


function updatePaper() {

    let title =
        document.getElementById("crud-title").value;


    let data = {

        authors: [
            document.getElementById("crud-author").value
        ],

        year: Number(
            document.getElementById("crud-year").value
        ),

        conference:
            document.getElementById("crud-conference").value

    };


    fetch(
        "http://127.0.0.1:5000/paper/"
        + encodeURIComponent(title),
        {

            method: "PUT",

            headers: {
                "Content-Type": "application/json"
            },

            body:
                JSON.stringify(data)

        }
    )
        .then(response => response.json())
        .then(() => {

            alert("修改成功");

        });

}


function deletePaper() {

    let title =
        document.getElementById("crud-title").value;


    fetch(
        "http://127.0.0.1:5000/paper/"
        + encodeURIComponent(title),
        {
            method: "DELETE"
        }
    )

        .then(response => response.json())

        .then(() => {

            alert("刪除成功");
            searchPaper();
        });

}


setTimeout(loadTrendChart, 500);