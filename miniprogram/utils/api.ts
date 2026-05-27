export interface MobileSummary {
  title: string
  primaryMessage: string
  nextAction: string
}

export interface MobileCard {
  label: string
  status: "ready" | "needs_attention"
  message: string
}

export interface MobileResponse {
  ok: boolean
  action: string
  summary: MobileSummary
  cards: MobileCard[]
  markdown: string
  project?: { name: string; root: string }
  token?: string
  expiresInSeconds?: number
  authorizedProjects?: string[]
}

function request<T>(baseUrl: string, path: string, payload: object, token = ""): Promise<T> {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseUrl}${path}`,
      method: "POST",
      data: payload,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (result) => resolve(result.data as T),
      fail: reject
    })
  })
}

export function pairWithWorkbench(baseUrl: string, pin: string): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/pair", { pin })
}

export function fetchDashboard(baseUrl: string, token: string, projectRoot: string): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/dashboard", { project_root: projectRoot }, token)
}

export function runWorkflowAction(
  baseUrl: string,
  token: string,
  projectRoot: string,
  action: "workflow_status" | "project_report" | "project_check"
): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/run", { action, project_root: projectRoot }, token)
}

export function updateReport(
  baseUrl: string,
  token: string,
  projectRoot: string,
  reportKind: string
): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/report", { project_root: projectRoot, report_kind: reportKind }, token)
}
