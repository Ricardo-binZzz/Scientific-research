import { runWorkflowAction, MobileCard, MobileSummary } from "../../utils/api"

type RunAction = "workflow_status" | "project_report" | "project_check"

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
    if (!baseUrl || !token || !projectRoot) {
      this.setData({ message: "还没有连接电脑端服务，请先回到连接页完成配对。" })
      return
    }
    runWorkflowAction(baseUrl, token, projectRoot, action).then((response) => {
      if (!response.ok) {
        this.setData({ message: response.summary?.primaryMessage || "这次运行没有完成，请检查项目路径。" })
        return
      }
      this.setData({ summary: response.summary, cards: response.cards || [], message: "" })
    }).catch(() => {
      this.setData({ message: "暂时连不上电脑端服务，请确认电脑端窗口仍在运行。" })
    })
  },

  openConnect() {
    wx.navigateTo({ url: "/pages/connect/connect" })
  }
})
