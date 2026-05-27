import { fetchDashboard, runWorkflowAction, MobileCard, MobileSummary } from "../../utils/api"

Page({
  data: {
    baseUrl: "",
    token: "",
    projectRoot: "",
    summary: {} as MobileSummary,
    cards: [] as MobileCard[],
    message: ""
  },

  onShow() {
    const baseUrl = wx.getStorageSync("baseUrl") || ""
    const token = wx.getStorageSync("token") || ""
    const projectRoot = wx.getStorageSync("projectRoot") || ""
    this.setData({ baseUrl, token, projectRoot })
    if (baseUrl && token && projectRoot) {
      fetchDashboard(baseUrl, token, projectRoot).then((response) => {
        if (!response.ok) {
          this.setData({ message: response.summary?.primaryMessage || "工作台暂时没有返回仪表盘。" })
          return
        }
        this.setData({ summary: response.summary, cards: response.cards || [], message: "" })
      }).catch(() => {
        this.setData({ message: "暂时连不上电脑端服务，请回到连接页检查地址、配对码和本地网络。" })
      })
    } else {
      this.setData({ message: "还没有连接电脑端服务，请先回到连接页完成配对。" })
    }
  },

  startProjectCheck() {
    const { baseUrl, token, projectRoot } = this.data
    runWorkflowAction(baseUrl, token, projectRoot, "project_check").then((response) => {
      if (!response.ok) {
        this.setData({ message: response.summary?.primaryMessage || "这次体检没有完成，请稍后再试。" })
        return
      }
      this.setData({ summary: response.summary, cards: response.cards || [], message: "" })
    }).catch(() => {
      this.setData({ message: "体检请求没有发出去，请确认电脑端服务仍在运行。" })
    })
  },

  openConnect() {
    wx.navigateTo({ url: "/pages/connect/connect" })
  }
})
