const DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b";
const DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1";

function heuristic(goal: string, facts: string[]) {
  const text = (goal + " " + facts.join(" ")).toLowerCase();
  if (["bin","waste","trash","garbage","פח","אשפה"].some(k => text.includes(k))) {
    return {
      blocker: "A concrete service decision has not yet been converted into a verified physical outcome.",
      controller: "Municipal waste / sanitation operations",
      next_action: "Ask the responsible operations contact to confirm the exact placement date and location for the additional bin.",
      evidence_needed: ["Named responsible contact","Placement date or work order","Exact location"],
      verify: "Confirm the bin is physically present at the agreed location; an agreement alone is not success.",
      fallback: "If no placement date is provided, request the work-order/reference number and escalate only that unresolved dependency."
    };
  }
  if (["benefit","allowance","social security","קצבה","ביטוח לאומי","זכאות"].some(k => text.includes(k))) {
    return {
      blocker: "Eligibility cannot be acted on until the missing decision or document requirement is identified.",
      controller: "Benefits authority / case officer",
      next_action: "Request the current case status and the single missing item preventing a decision.",
      evidence_needed: ["Case/reference number","Current official status","Exact missing document or decision"],
      verify: "Verify that the authority marks the missing requirement as received or the case advances to a decision stage.",
      fallback: "If the answer is generic, ask for the exact unresolved requirement and the department currently holding the case."
    };
  }
  if (["permit","license","approval","היתר","רישיון","אישור"].some(k => text.includes(k))) {
    return {
      blocker: "The active prerequisite gate is not yet identified or evidenced as complete.",
      controller: "Approving authority / permit reviewer",
      next_action: "Ask which prerequisite currently prevents the application from advancing and request the official status of that prerequisite.",
      evidence_needed: ["Application/reference number","Named prerequisite","Official status or decision"],
      verify: "Verify the prerequisite is explicitly marked complete and the case advances to the next stage.",
      fallback: "If several prerequisites are listed, resolve the earliest blocking gate first rather than working all of them in parallel."
    };
  }
  return {
    blocker: "The next decision dependency is not yet explicit.",
    controller: "The person or institution that controls the next required decision",
    next_action: "Ask for the exact condition that must become true for the case to advance, and who controls that condition.",
    evidence_needed: ["Current official status","Next required condition","Responsible controller"],
    verify: "Verify the condition changed in the source system or through an official confirmation.",
    fallback: "If the response does not name a condition, ask for the current blocking requirement rather than requesting a general status update."
  };
}

function extractJson(text: string) {
  let value = (text || "").trim();
  if (value.startsWith("```")) {
    value = value.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  }
  return JSON.parse(value);
}

async function reason(goal: string, facts: string[], constraints: string[]) {
  const apiKey = Netlify.env.get("NEBIUS_API_KEY")?.trim();
  const model = Netlify.env.get("NEBIUS_MODEL")?.trim() || DEFAULT_MODEL;
  if (!apiKey) {
    return { ...heuristic(goal, facts), reasoning_provider: "local heuristic fallback" };
  }

  const baseUrl = (Netlify.env.get("NEBIUS_BASE_URL")?.trim() || DEFAULT_BASE_URL).replace(/\/$/, "");
  const response = await fetch(baseUrl + "/chat/completions", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + apiKey,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model,
      temperature: 0.2,
      messages: [
        {
          role: "system",
          content: "You are the reasoning engine inside Bureaucracy Outcome Accelerator. Work backward from a real-world bureaucratic goal to the earliest unresolved decision dependency. Return JSON only with these keys: blocker, controller, next_action, evidence_needed, verify, fallback. evidence_needed must be an array of short strings. Choose exactly one smallest safe next action. Never claim an external action was performed."
        },
        {
          role: "user",
          content: JSON.stringify({ goal, known_facts: facts, constraints })
        }
      ]
    })
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error("Nebius request failed: " + response.status + " " + detail.slice(0, 300));
  }
  const data = await response.json();
  const result = extractJson(data?.choices?.[0]?.message?.content || "");
  const required = ["blocker","controller","next_action","evidence_needed","verify","fallback"];
  for (const key of required) {
    if (!(key in result)) throw new Error("Nebius response missing " + key);
  }
  if (!Array.isArray(result.evidence_needed)) throw new Error("evidence_needed must be an array");
  return { ...result, reasoning_provider: "Nebius Token Factory", reasoning_model: model };
}

function newCaseId(goal: string) {
  const slug = goal.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 28);
  return slug || crypto.randomUUID().slice(0, 12);
}

export default async (req: Request) => {
  if (req.method === "GET") {
    return Response.json({
      ok: true,
      provider_configured: Boolean(Netlify.env.get("NEBIUS_API_KEY")?.trim()),
      model: Netlify.env.get("NEBIUS_MODEL")?.trim() || DEFAULT_MODEL
    });
  }
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  try {
    const body = await req.json();
    if (body.action === "break") {
      const goal = String(body.goal || "").trim();
      if (goal.length < 3) return Response.json({ error: "goal must contain at least 3 characters" }, { status: 400 });
      const facts = Array.isArray(body.known_facts) ? body.known_facts.map(String) : [];
      const constraints = Array.isArray(body.constraints) ? body.constraints.map(String) : [];
      const plan = await reason(goal, facts, constraints);
      return Response.json({
        case_id: newCaseId(goal),
        goal,
        known_facts: facts,
        constraints,
        status: "ACTION_NOW",
        ...plan,
        last_outcome: null,
        verified: false
      });
    }

    if (body.action === "record") {
      const current = body.case;
      if (!current || typeof current !== "object" || !current.case_id) {
        return Response.json({ error: "case is required" }, { status: 400 });
      }
      const verified = Boolean(body.verified);
      const next = { ...current, last_outcome: String(body.outcome || ""), verified };
      if (verified) {
        next.status = "VERIFIED_OUTCOME";
        next.next_action = "No further action. Preserve the proof of outcome.";
      } else {
        next.status = "REROUTE";
        next.next_action = current.fallback;
      }
      return Response.json(next);
    }

    return Response.json({ error: "unknown action" }, { status: 400 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return Response.json({ error: message }, { status: 500 });
  }
};

export const config = {
  path: "/api/agent"
};
