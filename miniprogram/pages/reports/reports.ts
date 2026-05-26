import { updateReport as requestReport, MobileSummary } from "../../utils/api"

Page({
  data: {
    baseUrl: "",
    token: "",
    projectRoot: "",
    markdown: "",
    summary: {} as MobileSummary,
    reports: [
      {
        kind: "writing_pack",
        title: "写作材料包",
        description: "把论文写作常用材料重新整理一遍。"
      },
      {
        kind: "literature_table",
        title: "文献表",
        description: "更新文献、笔记和阅读状态的清单。"
      },
      {
        kind: "literature_map",
        title: "文献地图",
        description: "把研究线索放回一张更容易浏览的图谱。"
      }
    ]
  },

  onShow() {
    this.setData({
      baseUrl: wx.getStorageSync("baseUrl") || "",
      token: wx.getStorageSync("token") || "",
      projectRoot: wx.getStorageSync("projectRoot") || ""
    })
  },

  updateReport(event: any) {
    const { baseUrl, token, projectRoot } = this.data
    const reportKind = event.currentTarget.dataset.kind
    requestReport(baseUrl, token, projectRoot, reportKind).then((response) => {
      this.setData({
        summary: response.summary,
        markdown: response.markdown || ""
      })
    })
  }
})
