# Sources

Every product fact in the deck and the demos comes from these pages. All were read on **19 November 2026**. Microsoft Perception's documentation was changing every week in late 2026, so check the status lines again before the session (see [PRE-FLIGHT.md](PRE-FLIGHT.md)).

## Microsoft Perception

| Fact used | Source |
|---|---|
| "Microsoft's multi-agent system for the security operations center", in the Defender portal | [Agentic security overview](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-overview) |
| Cyber Stack layers (Signals and sensors → Context → Models → Harness → Agents → Actuators); the Harness "deciding which agent runs next and passing findings between them"; shared context | [Agentic security concepts](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-concepts) |
| Red, blue and green team agents and their roles | [Agent categories](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-agent-categories), [Agents](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-agents) |
| Recon Agent is read-only and covers Azure environments only | [Agents](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-agents) |
| Playbooks are "reusable templates"; preset by Microsoft; the list is read-only; "You can't create custom playbooks in this release"; a playbook runs only when every agent it needs is enabled; the nine playbook names; the "Protect against a threat" sequence | [Playbooks](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-playbooks) |
| "Waiting for input" with Approve / Reject / Suggest an alternative / Stop (Stop can't be undone); sessions are immutable records that serve as an audit trail; approval examples; "Introduce autonomy gradually" | [Supervise work](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-supervise-work) |
| Setup creates a Microsoft Entra Agent ID per agent; URBAC across all Defender workloads; Security Admin / Security Reader; data processing regions | [Get started](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-get-started) |
| Triage Agent can self-trigger and auto-resolve false positives; replaces the Phishing Triage Agent (one triage agent active at a time) | [Triage Agent](https://learn.microsoft.com/en-us/security/agentic-security/triage-agent) |
| Risk Reduction Agent: remediation plans, shielding, Intune patching | [Risk Reduction Agent](https://learn.microsoft.com/en-us/security/agentic-security/risk-reduction-agent) |
| Models and preview note | [Application card](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-application-card) |
| Announced 27 Jul 2026 as Project Perception; public preview from 3 Aug | [Microsoft blog, 27 Jul 2026](https://blogs.microsoft.com/2026/07/27/rethinking-security-for-the-age-of-ai/) |
| Renamed Microsoft Perception at Ignite 2026 and announced for GA; Web App Pen Test Agent; APIs and MCP to start playbooks from ITSM/SIEM/SOAR; usage dashboards and cost calculator | [What's new at Ignite 2026](https://techcommunity.microsoft.com/blog/perception-blog/whats-new-with-microsoft-perception-at-ignite-2026/4571834) |
| Consumption-based pricing: pay-as-you-go or AI Flex; counts toward MACC; "not a Security Copilot rebrand" | [Product page](https://www.microsoft.com/en-us/security/business/ai-powered-cybersecurity/project-perception-agentic-system) |

**Not stated anywhere Microsoft publishes, so not stated in the deck:** a Perception rate card, SLA or support terms, and any Microsoft comparison of Perception's cost or supportability with building your own. The "more supportable and cost-effective" argument in the deck comes from the maintenance model in Demo 6, using your assumptions.

## Designing and governing agents

| Fact used | Source |
|---|---|
| Agent identity options; "Create an agent identity" is currently only for Microsoft-built agents; a user-account identity inherits that user's access | [Security Copilot agents overview](https://learn.microsoft.com/en-us/copilot/security/agents-overview) |
| Entra Agent ID is GA and available to all Entra customers; object types | [What are agent identities](https://learn.microsoft.com/en-us/entra/agent-id/what-are-agent-identities), [What's new](https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id) |
| A sponsor is required; what owners, sponsors and managers can do | [Owners, sponsors and managers](https://learn.microsoft.com/en-us/entra/agent-id/agent-owners-sponsors-managers) |
| Not plain app registrations; managed identity or certificates; agents can't satisfy MFA; attest every 6–12 months | [Agent ID best practices](https://learn.microsoft.com/en-us/entra/agent-id/best-practices-agent-id) |
| Conditional Access for agents: licensing and targeting | [Conditional Access for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) |
| Phishing Triage Agent: permissions, self-assignment and the "Agent" tag, the FP/TP behaviour, the teach loop, feedback statuses, Performance tab | [Phishing Triage Agent](https://learn.microsoft.com/en-us/defender-xdr/phishing-triage-agent) |
| Security Alert Triage Agent (preview); the current list of Defender agents | [Security Copilot agents in Defender](https://learn.microsoft.com/en-us/defender-xdr/security-copilot-agents-defender) |
| Foundry agent evaluators and their preview status; 1–5 scale and threshold of 3 | [Agent evaluators](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/agent-evaluators) |
| AI Red Teaming Agent: PyRIT, ASR, agent risk categories | [AI Red Teaming Agent](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/ai-red-teaming-agent) |
| Provisioned vs overage SCUs | [SCU capacity](https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity) |
| E5/E7 inclusion: 400 SCUs per 1,000 user licences per month, capped at 10,000; $6 pay-as-you-go beyond it | [Security Copilot inclusion](https://learn.microsoft.com/en-us/copilot/security/security-copilot-inclusion) |
| $6 per overage SCU (worked example) | [Security Copilot pricing](https://www.microsoft.com/en-us/security/pricing/microsoft-security-copilot) (not Learn) |
| Start with a single agent unless boundaries are crossed | [Cloud Adoption Framework: AI agents](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/) |

## Building SOC agents

| Fact used | Source |
|---|---|
| Ways to build (NL2Agent, agent builder, YAML upload, MCP tools), all converging on a YAML manifest; publish scopes; roles | [Custom agents overview](https://learn.microsoft.com/en-us/copilot/security/developer/custom-agent-overview), [Publish](https://learn.microsoft.com/en-us/copilot/security/developer/publish-agent-dev) |
| Manifest components, tool formats (API, GPT, KQL, AGENT, MCP), triggers (DefaultPeriodSeconds, FetchSkill, ProcessSkill) | [Agent components](https://learn.microsoft.com/en-us/copilot/security/developer/agent-components) |
| Sentinel MCP server collections and tools; billing | [Overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-overview), [Tools](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-tools-overview), [Data exploration](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-data-exploration-tool), [Triage](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-triage-tool), [Billing](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-billing) |
| Five orchestration patterns, when to use and avoid each, "lowest level of complexity", the pitfalls Demo 3 shows | [AI agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) |
| Agent Framework: successor to Semantic Kernel and AutoGen; human-in-the-loop requests; checkpoints | [Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview), [Human-in-the-loop](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop), [Checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints) |
| Foundry classic connected agents retire 31 March 2027 | [Connected agents](https://learn.microsoft.com/en-us/azure/foundry-classic/agents/how-to/connected-agents) |
| Sentinel in the Azure portal is supported until 31 March 2027 | [Automation rules](https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules) |
| Custom detection frequencies; at most 150 alerts per run | [Custom detection rules](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules) |

## Where Microsoft's pages disagree (check again before the session)

1. **Perception's status.** The Ignite post says Microsoft Perception "will be generally available". The Learn Get started, Triage Agent and Risk Reduction Agent pages still say "Limited Public Preview … a small, invitation-only set of customers".
2. **Conditional Access for agents licensing.** A Learn training module says Entra ID P1. The current Conditional Access page requires Microsoft 365 E7, or Agent 365 plus Entra P1 or Microsoft 365 E3. The deck uses the current page.
3. **The Web App Pen Test Agent** is in the Ignite post but not yet in the Learn table of contents, so the deck leaves it off the agent slide and mentions it in the speaker notes only.
