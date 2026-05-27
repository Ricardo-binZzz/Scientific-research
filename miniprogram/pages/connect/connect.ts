import { fetchDashboard, pairWithWorkbench } from "../../utils/api"

Page({
  data: {
    baseUrl: "",
    pin: "",
    projectRoot: "",
    message: ""
  },

  onLoad() {
    this.setData({
      baseUrl: wx.getStorageSync("baseUrl") || "http://127.0.0.1:8765",
      projectRoot: wx.getStorageSync("projectRoot") || ""
    })
  },

  onBaseUrlInput(event: any) {
    this.setData({ baseUrl: event.detail.value })
  },

  onPinInput(event: any) {
    this.setData({ pin: event.detail.value })
  },

  onProjectRootInput(event: any) {
    this.setData({ projectRoot: event.detail.value })
  },

  connect() {
    const { baseUrl, pin, projectRoot } = this.data
    if (!baseUrl || !pin) {
      this.setData({ message: "请先填写电脑服务地址和配对码。" })
      return
    }
    pairWithWorkbench(baseUrl, pin)
      .then((response) => {
        if (!response.ok || !response.token) {
          this.setData({ message: response.summary?.primaryMessage || "连接没有完成，请检查配对码。" })
          return
        }
        const selectedProjectRoot = projectRoot || (response.authorizedProjects || [])[0] || ""
        if (!selectedProjectRoot) {
          this.setData({ message: "请填写项目路径，或在电脑端启动服务时指定 --project-root。" })
          return
        }
        fetchDashboard(baseUrl, response.token, selectedProjectRoot).then((dashboard) => {
          if (!dashboard.ok) {
            this.setData({ message: dashboard.summary?.primaryMessage || "项目路径没有通过电脑端授权。" })
            return
          }
          wx.setStorageSync("baseUrl", baseUrl)
          wx.setStorageSync("token", response.token)
          wx.setStorageSync("projectRoot", selectedProjectRoot)
          this.setData({ projectRoot: selectedProjectRoot })
          this.setData({ message: "已经连接，可以查看今天的研究进度。" })
          wx.switchTab({ url: "/pages/dashboard/dashboard" })
        }).catch(() => {
          this.setData({ message: "配对成功，但暂时无法读取项目路径，请确认电脑端服务和项目路径。" })
        })
      })
      .catch(() => {
        this.setData({ message: "暂时连不上电脑端服务，请确认地址和本地网络。" })
      })
  }
})
