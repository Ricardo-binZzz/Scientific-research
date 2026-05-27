import { runWorkflowAction, updateReport as requestReport, MobileSummary } from "../../utils/api"

Page({
  data: {
    baseUrl: "",
    token: "",
    projectRoot: "",
    markdown: "",
    summary: {} as MobileSummary,
    message: "",
    reports: [
      {
        kind: "project_check",
        title: "项目体检报告",
        description: "查看当前文献、仿真、图表和稿件的主要缺口。"
      },
      {
        kind: "writing_pack",
        title: "写作材料包",
        description: "把论文写作常用材料重新整理一遍。"
      },
      {
        kind: "writing_dashboard",
        title: "写作看板",
        description: "按背景、方法、结果和稿件缺口重新排优先级。"
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
      },
      {
        kind: "literature_tracker",
        title: "追踪清单",
        description: "把下一轮检索主题整理成可继续推进的清单。"
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
    if (!baseUrl || !token || !projectRoot) {
      this.setData({ message: "还没有连接电脑端服务，请先回到连接页完成配对。" })
      return
    }
    if (reportKind === "project_check") {
      runWorkflowAction(baseUrl, token, projectRoot, "project_check").then((response) => {
        if (!response.ok) {
          this.setData({ message: response.summary?.primaryMessage || "项目体检报告没有生成成功。" })
          return
        }
        this.setData({
          summary: response.summary,
          markdown: response.markdown || "",
          message: ""
        })
      }).catch(() => {
        this.setData({ message: "暂时连不上电脑端服务，请确认电脑端窗口仍在运行。" })
      })
      return
    }
    requestReport(baseUrl, token, projectRoot, reportKind).then((response) => {
      if (!response.ok) {
        this.setData({ message: response.summary?.primaryMessage || "报告没有更新成功，请检查项目路径。" })
        return
      }
      this.setData({
        summary: response.summary,
        markdown: response.markdown || "",
        message: ""
      })
    }).catch(() => {
      this.setData({ message: "暂时连不上电脑端服务，请确认电脑端窗口仍在运行。" })
    })
  },

  openConnect() {
    wx.navigateTo({ url: "/pages/connect/connect" })
  }
})
