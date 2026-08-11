import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { spawn } from "node:child_process";

const ROLES = ["coordinator", "worker", "validator", "assessor"] as const;
type Role = (typeof ROLES)[number];

const resultSchema = Type.Union([
  Type.Literal("success"), Type.Literal("partial"), Type.Literal("failure"), Type.Literal("blocked"),
]);
const stringsSchema = Type.Array(Type.String({ minLength: 1 }));
const proposalSchema = Type.Object({
  slug: Type.String({ pattern: "^[a-z0-9]+(?:-[a-z0-9]+)*$" }),
  intent: Type.String({ minLength: 1 }),
  criteria: Type.Array(Type.String({ minLength: 1 }), { minItems: 1 }),
}, { additionalProperties: false });
const clarificationSchema = Type.Object({
  target: Type.Union([Type.Literal("worker"), Type.Literal("validator")]),
  request: Type.String({ minLength: 1 }),
}, { additionalProperties: false });

function isRole(value: unknown): value is Role { return typeof value === "string" && ROLES.includes(value as Role); }

function parametersFor(role: Role) {
  if (role === "coordinator") return Type.Object({ lessons: stringsSchema, proposals: Type.Array(proposalSchema), recommendation: Type.String() }, { additionalProperties: false });
  if (role === "worker") return Type.Object({ work_summary: Type.String({ minLength: 1 }), work_evidence: stringsSchema }, { additionalProperties: false });
  if (role === "validator") return Type.Object({
    result: resultSchema,
    validation_summary: Type.String({ minLength: 1 }),
    validation_evidence: stringsSchema,
    clarification_request: Type.Union([Type.String({ minLength: 1 }), Type.Null()]),
  }, { additionalProperties: false });
  return Type.Object({
    wins: stringsSchema, issues: stringsSchema, actions: stringsSchema,
    clarification_requests: Type.Array(clarificationSchema, { maxItems: 2 }),
  }, { additionalProperties: false });
}

function nonEmptyStrings(value: unknown, label: string): asserts value is string[] {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string" || !item.trim())) throw new Error(`${label} must be a list of non-empty strings`);
}
function nonEmptyString(value: unknown, label: string): asserts value is string {
  if (typeof value !== "string" || !value.trim()) throw new Error(`${label} is required`);
}

function canonicalInput(role: Role, params: Record<string, unknown>): Record<string, unknown> {
  if (role === "coordinator") {
    nonEmptyStrings(params.lessons, "lessons");
    if (!Array.isArray(params.proposals)) throw new Error("proposals must be a list");
    const slugs = params.proposals.map((proposal, index) => {
      if (typeof proposal !== "object" || proposal === null) throw new Error(`proposals[${index}] must be an object`);
      const item = proposal as Record<string, unknown>;
      nonEmptyString(item.slug, `proposals[${index}].slug`); nonEmptyString(item.intent, `proposals[${index}].intent`); nonEmptyStrings(item.criteria, `proposals[${index}].criteria`);
      if (!item.criteria.length) throw new Error(`proposals[${index}].criteria must not be empty`);
      return item.slug;
    });
    if (new Set(slugs).size !== slugs.length) throw new Error("proposals contains duplicate slugs");
    if (slugs.some((slug) => slug === "terminate")) throw new Error("terminate is reserved for terminal recommendations");
    if (params.recommendation !== "terminate" && !slugs.includes(params.recommendation as string)) throw new Error('recommendation must name a proposal or be "terminate"');
    return { lessons: params.lessons, proposals: params.proposals, recommendation: params.recommendation };
  }
  if (role === "worker") {
    nonEmptyString(params.work_summary, "work_summary"); nonEmptyStrings(params.work_evidence, "work_evidence");
    return { work: { summary: params.work_summary, evidence: params.work_evidence } };
  }
  if (role === "validator") {
    nonEmptyString(params.validation_summary, "validation_summary"); nonEmptyStrings(params.validation_evidence, "validation_evidence");
    if (params.clarification_request !== null) nonEmptyString(params.clarification_request, "clarification_request");
    return { validate: { result: params.result, summary: params.validation_summary, evidence: params.validation_evidence }, clarification_request: params.clarification_request };
  }
  nonEmptyStrings(params.wins, "wins"); nonEmptyStrings(params.issues, "issues"); nonEmptyStrings(params.actions, "actions");
  if (!Array.isArray(params.clarification_requests)) throw new Error("clarification_requests must be a list");
  const targets = new Set<string>();
  for (const [index, item] of params.clarification_requests.entries()) {
    if (typeof item !== "object" || item === null) throw new Error(`clarification_requests[${index}] must be an object`);
    const request = item as Record<string, unknown>;
    if (request.target !== "worker" && request.target !== "validator") throw new Error(`clarification_requests[${index}].target is invalid`);
    nonEmptyString(request.request, `clarification_requests[${index}].request`);
    if (targets.has(request.target)) throw new Error("clarification_requests contains duplicate targets");
    targets.add(request.target);
  }
  return { retro: { wins: params.wins, issues: params.issues, actions: params.actions }, clarification_requests: params.clarification_requests };
}

async function normalize(role: Role, packet: Record<string, unknown>, signal: AbortSignal): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn("stagger-step", ["normalize", "--role", role], { stdio: ["pipe", "pipe", "pipe"] });
    let stdout = ""; let stderr = "";
    child.stdout.on("data", (chunk) => (stdout += chunk)); child.stderr.on("data", (chunk) => (stderr += chunk));
    child.on("error", reject); child.on("close", (code) => { if (code === 0) resolve(stdout); else reject(new Error(stderr.trim() || `stagger-step normalize exited ${code}`)); });
    signal.addEventListener("abort", () => child.kill(), { once: true }); child.stdin.end(JSON.stringify(packet));
  });
}

export default function (pi: ExtensionAPI) {
  pi.registerFlag("step-role", { description: "STEP role selected by the stagger-step harness", type: "string" });
  let registered = false;
  pi.on("session_start", () => {
    if (registered) return;
    const role = pi.getFlag("step-role"); if (!isRole(role)) return;
    registered = true;
    const toolName = `stagger_step_finalize_${role}`;
    pi.registerTool({
      name: toolName, label: `Finalize STEP ${role}`, description: `Validate, normalize, and finalize the ${role} STEP response.`,
      promptSnippet: `Finalize the ${role} role response through ${toolName}.`,
      promptGuidelines: [`Use ${toolName} exactly once after completing the ${role} role work; return no packet outside this tool.`],
      parameters: parametersFor(role),
      async execute(_toolCallId, params, signal) {
        try { const packet = canonicalInput(role, params as Record<string, unknown>); const canonical = await normalize(role, packet, signal); const parsed = JSON.parse(canonical); return { content: [{ type: "text", text: canonical }], details: { role, canonical: parsed } }; }
        catch (error) { return { content: [{ type: "text", text: String(error) }], details: { role }, isError: true }; }
      },
    });
  });
}
