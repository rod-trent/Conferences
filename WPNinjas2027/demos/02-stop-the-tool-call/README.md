# Demo 02 — Stop the Tool Call

Slide 22 · runs offline, standard library only · also on the [demo site](../../web/)

A Copilot Studio agent with generative orchestration processes an accounts-payable inbox. One email hides an instruction. The orchestrator proposes SendEmail to a look-alike domain — and the proposed tool call goes to Microsoft Defender before it runs.

## What it shows

- The request body Copilot Studio sends to `POST /analyze-tool-execution?api-version=2025-05-01`: `plannerContext`, `toolDefinition`, `inputValues`, `conversationMetadata`.
- Defender XDR real-time protection detection types: **Secret exfiltration**, **Malicious content propagation**, **Evasion techniques**, **Unsafe email domain**.
- Default rule (audit) vs custom rule (block) — and that only agents with a Microsoft Entra agent ID can be scoped into a custom rule.
- The one-second budget: a late verdict is treated as allow unless the environment's error behavior is **Block the query**.

## Run it

```bash
cd demos/02-stop-the-tool-call
python runtime_protection.py                                         # custom block rule — SendEmail blocked
python runtime_protection.py --rule audit                            # default rule only — audited, and the data leaves
python runtime_protection.py --no-agent-id                           # agent cannot be scoped into the block rule
python runtime_protection.py --latency 1400                          # Defender answers late — fail-open
python runtime_protection.py --latency 1400 --error-behavior block   # fail-closed
python runtime_protection.py --benign                                # control
python runtime_protection.py --self-test                             # 10 checks
```

Add `--fast` to skip the on-stage pacing.

## Note

In a real tenant: Defender portal > Settings > Security for AI > Policies & rules > Real-time protection > **Create rule**. `reasonCode` values in the demo are illustrative.

Detection logic is a local stand-in for the Microsoft services named (see `../common/`). All data is synthetic.
