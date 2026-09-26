import { registerCustomTheme } from "@pierre/diffs"
import { NovaCodeTheme } from "./marked-theme"

let registered = false

export function registerNovaCodeTheme() {
  if (registered) return
  registered = true
  registerCustomTheme("NovaCode", () => Promise.resolve(NovaCodeTheme))
}
