// @ts-nocheck

import { NovaCode } from "@novacode-ai/core"
import { ReadTool } from "@novacode-ai/core/tools"

const novacode = NovaCode.make({})

novacode.tool.add(ReadTool)

novacode.tool.add({
  name: "bash",
  schema: {
    type: "object",
    properties: {
      command: {
        type: "string",
        description: "The command to run.",
      },
    },
    required: ["command"],
  },
  execute(input, ctx) {},
})

novacode.auth.add({
  provider: "openai",
  type: "api",
  value: process.env.OPENAI_API_KEY,
})

novacode.agent.add({
  name: "build",
  permissions: [],
  model: {
    id: "gpt-5-5",
    provider: "openai",
    variant: "xhigh",
  },
})

const sessionID = await novacode.session.create({
  agent: "build",
})

novacode.subscribe((event) => {
  console.log(event)
})

await novacode.session.prompt({
  sessionID,
  text: "hey what is up",
})

await novacode.session.prompt({
  sessionID,
  text: "what is up with this",
  files: [
    {
      mime: "image/png",
      uri: "data:image/png;base64,xxxx",
    },
  ],
})

await novacode.session.wait()

console.log(await novacode.session.messages(sessionID))
