"""Drive the review loop interactively — YOU play the service-line leader.

The graph pauses at interrupt() and waits. This script stops at an input() prompt until you
type a decision, then resumes the graph with it. That pause IS the human-in-the-loop: nothing
proceeds until you answer. A RETURN advances the offer to the next ranked line and re-pauses;
ACCEPT or DECLINE ends it.
"""
from __future__ import annotations
import sys, uuid
from dotenv import load_dotenv
load_dotenv()

from langgraph.types import Command
from src.graph import agent


def show_interrupt(result) -> dict | None:
    """Return the pending interrupt payload, or None if the graph finished."""
    intr = result.get("__interrupt__")
    if not intr:
        return None
    return intr[0].value


def main(path: str) -> None:
    text = open(path, encoding="utf-8").read()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    # Run until the first offer (the graph pauses inside review()).
    result = agent.invoke({"document_text": text, "source": "cli", "errors": []}, config)

    while True:
        offer = show_interrupt(result)
        if offer is None:
            break  # graph finished — no pending interrupt
        print(f"\n--- OFFER -> {offer['offered_to']} ({offer['team']}), "
              f"{offer['remaining_after_this']} candidate(s) left after this ---")

        # This is the human-in-the-loop pause: the graph is frozen until you answer.
        action = input("    Your call as this service-line leader [accept / decline / return]: ").strip().lower()
        while action not in ("accept", "decline", "return"):
            action = input("    Please type accept, decline, or return: ").strip().lower()

        decision = {"action": action}
        if action == "return":
            corrected = input("    (optional) which line does it actually belong to? [enter to skip]: ").strip()
            if corrected:
                decision["corrected_service_line"] = corrected
            note = input("    (optional) note: ").strip()
            if note:
                decision["note"] = note

        result = agent.invoke(Command(resume=decision), config)

    routing = result.get("routing")
    print("\n" + "=" * 60)
    print(f"FINAL: {routing.target_team}  —  {routing.reason}")
    log = result.get("review_log", [])
    print(f"REVIEW LOG ({len(log)} actions):")
    for d in log:
        line = f"  {d.action.value} by offer of {d.offered_service_line.value}"
        if d.corrected_service_line:
            line += f"  (corrected -> {d.corrected_service_line.value}, a GOLD label)"
        if d.note:
            line += f"  — \"{d.note}\""
        print(line)
    print("=" * 60)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/sample_rfp.txt")