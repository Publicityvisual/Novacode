import type { ElectronAPI } from "../preload/types"

declare global {
  interface Window {
    api: ElectronAPI
    __OPENCODE__?: {
      deepLinks?: string[]
    }
    __NOVACODE__?: {
      deepLinks?: string[]
    }
  }
}
