import { runWorkflowAction, MobileCard, MobileSummary } from "../../utils/api"

type RunAction = "workflow_status" | "project_report" | "project_check"

Page({
  data: {
    baseUrl: "",
    token: "",
    projectRoot: "",
    summary: {} as MobileSummary,
    cards: [] as MobileCard[]
  },

  onShow() {
    this.setData({
      baseUrl: wx.getStorageSync("baseUrl") || "",
      token: wx.getStorageSync("token") || "",
      projectRoot: wx.getStorageSync("projectRoot") || ""
    })
  },

  runWorkflowStatus() {
    this.runAction("workflow_status")
  },

  runProjectReport() {
    this.runAction("project_report")
  },

  runProjectCheck() {
    this.runAction("project_check")
  },

  runAction(action: RunAction) {
    const { baseUrl, token, projectRoot } = this.data
    runWorkflowAction(baseUrl, token, projectRoot, action).then((response) => {
      this.setData({ summary: response.summary, cards: response.cards || [] })
    })
  }
})
