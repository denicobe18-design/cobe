"""Headless motor. Pokreni ovo na poslužitelju; kokpit može biti drugi proces."""

from __future__ import annotations

import time

from doxa.runtime import ensure_started


def main() -> None:
    handle = ensure_started()
    if handle.role != "engine" or handle.engine is None:
        print("Motor već radi u drugom procesu. Ovaj izlaz ne otvara drugi.")
        return
    print("DOXA motor radi. Papirnati nalozi, javni Binance tok. Ctrl+C gasi samo ovaj proces.")
    while True:
        state = handle.engine.snapshot_state()
        print(
            f"kapital {state['equity']:.2f} € · cash {state['cash']:.2f} € · "
            f"pozicije {len(state['positions'])} · {handle.hub.status}"
        )
        time.sleep(30)


if __name__ == "__main__":
    main()
