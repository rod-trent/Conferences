# Sources

Every product fact in the deck and demos traces to one of these Microsoft Learn
pages, read on **19 November 2026**. Where Learn pages disagreed, it is noted.

## Defender for Cloud — AI services (model protection)

| Topic | Page |
|---|---|
| Threat protection for AI services (overview, trial cap, supported services) | https://learn.microsoft.com/azure/defender-for-cloud/ai-threat-protection |
| Enable the plan; suspicious prompt evidence; data security for AI interactions; AI model security | https://learn.microsoft.com/azure/defender-for-cloud/ai-onboarding |
| Alerts for AI services (alert names, types, severities, tactics — slide 17, demo 01) | https://learn.microsoft.com/azure/defender-for-cloud/alerts-ai-workloads |
| End-user context (`UserSecurityContext`) | https://learn.microsoft.com/azure/defender-for-cloud/gain-end-user-context-ai |
| Wire format `user_security_context` / `end_user_id` / `source_ip` / `application_name` / `end_user_tenant_id` | https://learn.microsoft.com/rest/api/microsoft-foundry/azureopenai/chat |
| AI security posture management | https://learn.microsoft.com/azure/defender-for-cloud/ai-security-posture |
| AI recommendations (Foundry agent recommendation names — demo 04) | https://learn.microsoft.com/azure/defender-for-cloud/recommendations-reference-ai |
| Release notes (Feb 2 2026 agent threat protection preview; deprecations) | https://learn.microsoft.com/azure/defender-for-cloud/release-notes · https://learn.microsoft.com/azure/defender-for-cloud/release-notes-recommendations-alerts |

## Prompt Shields, Foundry guardrails, red teaming

| Topic | Page |
|---|---|
| Prompt Shields: user prompt vs document attacks, classes, defaults, spotlighting, limits | https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection |
| Guardrails: intervention points, agent override, annotate-and-block | https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview |
| AI Red Teaming Agent: PyRIT, ASR, strategies, agent risk categories, supported targets | https://learn.microsoft.com/azure/foundry/concepts/ai-red-teaming-agent |

## Defender XDR — security for AI agents

| Topic | Page |
|---|---|
| Transition to Agent 365 licensing (1 July 2026) | https://learn.microsoft.com/defender-xdr/security-for-ai/transition-agent-security-to-agent-365 |
| Real-time protection rules, detection types, Dec 23 2026 retirement, coverage by platform | https://learn.microsoft.com/defender-xdr/security-for-ai/ai-agent-real-time-protection |
| Detection and protection; hunting tables | https://learn.microsoft.com/defender-xdr/security-for-ai/ai-agent-detection-protection |
| Get started (Security for AI, Microsoft 365 connector) | https://learn.microsoft.com/defender-xdr/security-for-ai/get-started-defender-security-for-ai |
| AI agent inventory | https://learn.microsoft.com/defender-xdr/security-for-ai/ai-agent-inventory |
| Risk assessment: risk levels and indicators | https://learn.microsoft.com/defender-xdr/security-for-ai/ai-agent-risk-assessment |
| Trusted-identity attacks on agents (GitHub Copilot CLI device-code phishing) | https://learn.microsoft.com/defender-xdr/security-for-ai/protect-ai-agents-from-trusted-identity-attacks |
| `AgentsInfo` table | https://learn.microsoft.com/defender-xdr/advanced-hunting-agentsinfo-table |
| `BehaviorInfo` table | https://learn.microsoft.com/defender-xdr/advanced-hunting-behaviorinfo-table |
| `CloudAppEvents` table | https://learn.microsoft.com/defender-xdr/advanced-hunting-cloudappevents-table |
| Agent 365 observability (`InvokeAgent`, `InferenceCall`, `ExecuteToolBy*`) | https://learn.microsoft.com/microsoft-agent-365/developer/observability-concepts |

## Copilot Studio

| Topic | Page |
|---|---|
| External threat detection (webhook, 1-second fail-open, error behavior, setup) | https://learn.microsoft.com/microsoft-copilot-studio/external-security-provider |
| Developer interface (`/analyze-tool-execution`, request/response shape) | https://learn.microsoft.com/microsoft-copilot-studio/external-security-webhooks-interface-developers |
| Training module: Copilot Studio agent protection | https://learn.microsoft.com/training/modules/enable-protection-copilot-studio-agents/2-explore-copilot-studio-ai-agent-protection |

## Defender for Endpoint

| Topic | Page |
|---|---|
| AI agent runtime protection (Preview): inspection methods, modes, alert, known issues | https://learn.microsoft.com/defender-endpoint/ai-agent-runtime-protection-overview |

## Identity, data, governance

| Topic | Page |
|---|---|
| Microsoft Agent 365 overview | https://learn.microsoft.com/microsoft-agent-365/overview |
| Agent 365 security summary | https://learn.microsoft.com/security/security-for-ai/agent-365-security |
| Microsoft Entra Agent ID | https://learn.microsoft.com/entra/agent-id/what-is-microsoft-entra-agent-id |
| Conditional Access for agents | https://learn.microsoft.com/entra/identity/conditional-access/agent-id |
| ID Protection: risky agents | https://learn.microsoft.com/entra/id-protection/concept-risky-agents |
| Zero Trust for AI (quote on slide 28) | https://learn.microsoft.com/entra/fundamentals/zero-trust-ai |
| Purview for Agent 365 | https://learn.microsoft.com/purview/ai-agent-365 |
| Cloud Adoption Framework: AI agent governance | https://learn.microsoft.com/azure/cloud-adoption-framework/ai-agents/architecture-governance |

## Not from Learn

- OWASP Top 10 for LLM Applications 2025 (slide 9; demo 06 mapping) — owasp.org.
- Event details — workplaceninjas.us.

## Known disagreements between Learn pages (19 Nov 2026)

1. **Copilot Studio real-time protection.** The Agent 365 transition page says it
   is "unchanged"; the newer real-time protection page says the legacy onboarding
   retires **23 December 2026**. The deck follows the newer page.
2. **Prompt Shields blocks as behaviors.** The real-time protection page says
   Prompt Shields block events from Copilot Studio are recorded as behaviors; the
   detection page says this isn't yet supported for Copilot Studio agents.
3. **Defender for AI Services and agents.** The onboarding page still says the plan
   protects "agents"; the transition page moves Foundry agent threat protection to
   Agent 365. The deck treats the plan as model protection.
