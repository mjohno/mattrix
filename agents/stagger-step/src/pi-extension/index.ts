import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { spawn } from "node:child_process";

const ROLES = ["coordinator", "worker", "assessor"] as const;
type Role = (typeof ROLES)[number];

function isRole(value: unknown): value is Role {
  return typeof value === "string" && ROLES.includes(value as Role);
}

async function normalize(role: Role, yaml: string, signal: AbortSignal): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn("stagger-step", ["normalize", "--role", role], {
      stdio: ["pipe", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => (stdout += chunk));
    child.stderr.on("data", (chunk) => (stderr += chunk));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve(stdout);
      else reject(new Error(stderr.trim() || `stagger-step normalize exited ${code}`));
    });
    signal.addEventListener("abort", () => child.kill(), { once: true });
    child.stdin.end(yaml);
  });
}

export default function (pi: ExtensionAPI) {
  pi.registerFlag("step-role", {
    description: "STEP role selected by the stagger-step harness",
    type: "string",
  });
  let registered = false;

  pi.on("session_start", () => {
    if (registered) return;
    const role = pi.getFlag("step-role");
    if (!isRole(role)) return;
    registered = true;

    const toolName = `stagger_step_finalize_${role}`;
    pi.registerTool({
      name: toolName,
      label: `Finalize STEP ${role}`,
      description: `Normalize and finalize the ${role} STEP role response.`,
      promptSnippet: `Finalize the ${role} role packet through ${toolName}.`,
      promptGuidelines: [
        `Use ${toolName} exactly once after completing the ${role} role work; return no packet outside this tool.`,
      ],
      parameters: Type.Object({
        yaml: Type.String({ description: `Candidate ${role} YAML response.` }),
      }),
      async execute(_toolCallId, params, signal) {
        try {
          const canonical = await normalize(role, params.yaml, signal);
          return {
            content: [{ type: "text", text: canonical }],
            details: { role, canonical },
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: String(error) }],
            details: { role },
            isError: true,
          };
        }
      },
    });
  });
}
