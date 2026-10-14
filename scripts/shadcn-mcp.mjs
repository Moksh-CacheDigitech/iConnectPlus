import { spawn } from "node:child_process"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../apps/web")
process.chdir(root)

// Avoid shell:true (CWE-78). On Windows, spawn the npx.cmd shim directly.
const npxBin = process.platform === "win32" ? "npx.cmd" : "npx"
const child = spawn(npxBin, ["-y", "shadcn@latest", "mcp"], {
  cwd: root,
  stdio: "inherit",
  shell: false,
  env: process.env,
})

child.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal)
  process.exit(code ?? 1)
})
