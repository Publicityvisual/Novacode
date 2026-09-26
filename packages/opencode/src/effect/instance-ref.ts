import { Context } from "effect"
import type { InstanceContext } from "@/project/instance-context"
import type { WorkspaceV2 } from "@novacode-ai/core/workspace"

export const InstanceRef = Context.Reference<InstanceContext | undefined>("~novacode/InstanceRef", {
  defaultValue: () => undefined,
})

export const WorkspaceRef = Context.Reference<WorkspaceV2.ID | undefined>("~novacode/WorkspaceRef", {
  defaultValue: () => undefined,
})
