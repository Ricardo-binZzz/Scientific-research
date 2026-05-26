import { fetchDashboard, runWorkflowAction, MobileCard, MobileSummary } from "../../utils/api"

Page({
  data: {
    baseUrl: "",
    token: "",
    projectRoot: "",
    summary: {} as MobileSummary,
    cards: [] as MobileCard[]
  },

  onShow() {
    const baseUrl = wx.getStorageSync("baseUrl") || ""
    const token = wx.getStorageSync("token") || ""
    const projectRoot = wx.getStorageSync("projectRoot") || ""
    this.setData({ baseUrl, token, projectRoot })
    if (baseUrl && token && projectRoot) {
      fetchDashboard(baseUrl, token, projectRoot).then((response) => {
        this.setData({ summary: response.summary, cards: response.cards || [] })
      })
    }
  },

  startProjectCheck() {
    const { baseUrl, token, projectRoot } = this.data
    runWorkflowAction(baseUrl, token, projectRoot, "project_check").then((response) => {
      this.setData({ summary: response.summary, cards: response.cards || [] })
    })
  }
})
