# Demo 01 — Shield the Model, Alert the SOC

Slide 18 · runs offline, standard library only · also on the [demo site](../../web/)

A prompt reaches a Foundry model deployment (Azure OpenAI). Prompt Shields annotates it, Defender for AI Services raises the alert, and the end-user context in the request tells the SOC who and where.

## What it shows

- The Azure OpenAI annotation shape: `prompt_filter_results[].content_filter_results.jailbreak` / `.indirect_attack` with `filtered` and `detected`.
- Alert names and types copied verbatim from *Alerts for AI services*: `AI.Azure_Jailbreak.ContentFiltering.BlockedAttempt`, `…DetectedAttempt`, `AI.Azure_ASCIISmuggling`.
- Why `blocked` vs `detected` matters, and what an alert looks like without `user_security_context`.
- A document (indirect) attack that is annotated but raises no model-deployment alert — the current alert list has no stand-alone XPIA alert for deployments; for agents that is Defender XDR's job (demos 02–03).

## Run it

```bash
cd demos/01-shield-the-model
python shield_and_alert.py                        # jailbreak, guardrail set to block
python shield_and_alert.py --annotate-only        # same prompt, annotate-only guardrail
python shield_and_alert.py --scenario smuggling   # ASCII smuggling — invisible Unicode tag characters
python shield_and_alert.py --scenario document    # attack hidden in a grounding document
python shield_and_alert.py --no-user-context      # the same alert with no user to act on
python shield_and_alert.py --scenario benign      # control: nothing fires
python shield_and_alert.py --self-test            # 10 checks
```

Add `--fast` to skip the on-stage pacing.

## Note

In a real tenant: enable **AI services** in Defender for Cloud > Environment settings > Defender plans, turn on **Suspicious prompt evidence**, and pass `user_security_context` (`end_user_id`, `source_ip`, `application_name`) from your app.

Detection logic is a local stand-in for the Microsoft services named (see `../common/`). All data is synthetic.
