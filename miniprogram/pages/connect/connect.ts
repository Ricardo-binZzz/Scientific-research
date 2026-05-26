import { pairWithWorkbench } from "../../utils/api"

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
    pairWithWorkbench(baseUrl, pin)
      .then((response) => {
        if (!response.ok || !response.token) {
          this.setData({ message: response.summary?.primaryMessage || "连接没有完成，请检查配对码。" })
          return
        }
        wx.setStorageSync("baseUrl", baseUrl)
        wx.setStorageSync("token", response.token)
        wx.setStorageSync("projectRoot", projectRoot)
        this.setData({ message: "已经连接，可以查看今天的研究进度。" })
        wx.switchTab({ url: "/pages/dashboard/dashboard" })
      })
      .catch(() => {
        this.setData({ message: "暂时连不上电脑端服务，请确认地址和本地网络。" })
      })
  }
})
