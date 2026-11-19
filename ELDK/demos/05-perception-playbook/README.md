# Demo 05 — A Microsoft Perception Playbook

Slide 27 · runs offline, standard library only · also on the [demo site](https://eldk2027-demos.vercel.app/?demo=perception)

This demo models what Microsoft Learn documents about Microsoft Perception (checked 19 Nov 2026), using the same threat as Demos 02–04.

## What it shows

- **The agents, by team.**
  - Red: Recon Agent (read-only, Azure only).
  - Blue: Triage, Threat Intelligence, Attack Investigation, Detection Authoring.
  - Green: Posture Prioritization, Identity Risk Reduction, Risk Reduction.
- **The documented "Protect against a threat" sequence.** Threat Intelligence → Recon → Posture Prioritization → Detection Authoring / Attack Investigation. Each agent's output is the next agent's structured input.
- **Waiting for input.** At the gate you can Approve, Reject, Suggest an alternative, or Stop. Stop can't be undone.
- **An immutable session record.** The hash chain here only illustrates "immutable"; how Perception actually stores sessions isn't documented.
- **The limits.**
  - A playbook won't start unless every agent it needs is enabled.
  - The playbook list is read-only ("You can't create custom playbooks in this release").

## Run it

```bash
cd demos/05-perception-playbook
python perception_playbook.py                          # approve at the gate
python perception_playbook.py --decision suggest       # the agent revises the step
python perception_playbook.py --decision reject
python perception_playbook.py --decision stop
python perception_playbook.py --disable "Recon Agent"  # playbook won't start
python perception_playbook.py --custom                 # read-only library
python perception_playbook.py --self-test              # 10 checks
```

The names, sequence and controls are Microsoft's. The agents' reasoning is a stand-in, because Perception's internals are not public.

All data is synthetic. The agent logic is a deterministic local stand-in for the systems named.
