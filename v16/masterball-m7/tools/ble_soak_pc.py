"""PC-side BLE soak for the PokeDock ball (protocol v2): repeated connect / command / disconnect cycles.

usage: python ble_soak_pc.py <minutes> <log.jsonl> [address]

Needs the PC to be bonded once (Windows Settings > Bluetooth > Add device > PokeDock-MB, 6 digits from
the ball's screen after menu "페어링"); the encrypted characteristics refuse unbonded links ("auth").
Per cycle: connect, read state, time_sync, partner, brightness, alarm_set, focus start / pause /
resume / cancel, read state again, disconnect. Every ACK and the state after each command are checked.
At the end the ball gets back the partner, brightness and alarm it had at the start. The gift message
is never sent. Close the phone app first: the ball takes one connection at a time.
"""
import asyncio
import json
import random
import sys
import time

from bleak import BleakClient, BleakScanner

SVC = "edc00001-8148-4b41-9a3e-7bd93d2ab771"
CMD = "edc00002-8148-4b41-9a3e-7bd93d2ab771"
EVT = "edc00003-8148-4b41-9a3e-7bd93d2ab771"
STATE = "edc00004-8148-4b41-9a3e-7bd93d2ab771"
PARTNERS = [94, 393, 468, 448, 195, 175, 417, 385]


class Ball:
    def __init__(self, client, log):
        self.c, self.log = client, log
        self.session = random.randrange(1, 0xFFFFFFFF)
        self.seq = 0
        self.acks = {}
        self.states = []

    def on_evt(self, _h, data: bytearray):
        try:
            o = json.loads(bytes(data).decode())
        except Exception as e:  # noqa: BLE001
            self.log({"bad_event": repr(bytes(data)), "err": str(e)})
            return
        if "q" in o and "ok" in o:
            self.acks[o["q"]] = o
        elif "r" in o and "p" in o:
            self.states.append(o)

    async def state(self):
        return json.loads(bytes(await self.c.read_gatt_char(STATE)).decode())

    async def cmd(self, c, **args):
        self.seq += 1
        q = self.seq
        body = json.dumps({"v": 2, "s": self.session, "q": q, "c": c, **args}, separators=(",", ":")).encode()
        t0 = time.monotonic()
        await self.c.write_gatt_char(CMD, body, response=True)
        while q not in self.acks and time.monotonic() - t0 < 3.0:
            await asyncio.sleep(0.02)
        ack = self.acks.pop(q, None)
        ms = round((time.monotonic() - t0) * 1000)
        ok = bool(ack and ack.get("ok") == 1)
        self.log({"cmd": c, "args": args, "ok": ok, "ack": ack, "ms": ms})
        if not ok:
            raise RuntimeError(f"{c} failed: {ack}")
        return ack


async def main():
    minutes, out = float(sys.argv[1]), sys.argv[2]
    addr = sys.argv[3] if len(sys.argv) > 3 else None
    f = open(out, "a", encoding="utf8")

    def log(o):
        o = {"t": time.strftime("%H:%M:%S"), **o}
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
        f.flush()

    if not addr:
        dev = await BleakScanner.find_device_by_filter(lambda d, a: (a.local_name or "").startswith("PokeDock"), timeout=15)
        if not dev:
            log({"fatal": "PokeDock-MB not found (phone still connected?)"})
            print("FAIL: not found")
            return 2
        addr = dev.address
    end = time.time() + minutes * 60
    cycles = fails = 0
    initial = None
    while time.time() < end:
        cycles += 1
        t0 = time.monotonic()
        try:
            async with BleakClient(addr, timeout=15) as client:
                ball = Ball(client, log)
                await client.start_notify(EVT, ball.on_evt)
                s0 = await ball.state()
                if initial is None:
                    initial = s0
                    log({"initial_state": s0})
                now = int(time.time())
                await ball.cmd("time_sync", t=now, tz=540)
                p = random.choice([x for x in PARTNERS if x != s0["p"]])
                await ball.cmd("partner", id=p)
                b = random.randint(20, 100)
                await ball.cmd("brightness", val=b)
                lt = time.localtime(now + 3600 * 3)  # never rings during the test
                await ball.cmd("alarm_set", h=lt.tm_hour, m=lt.tm_min, en=True)
                if s0["f"][0] == 0:
                    await ball.cmd("focus_start", min=1)
                    await ball.cmd("focus_pause")
                    await ball.cmd("focus_resume")
                    await ball.cmd("focus_cancel")
                s1 = await ball.state()
                good = s1["p"] == p and s1["b"] == b and s1["a"][1] == lt.tm_hour and s1["a"][2] == lt.tm_min \
                    and s1["clk"][0] == 1 and s1["f"][0] == 0
                log({"cycle": cycles, "state_ok": good, "fw": s1.get("fw"), "rev": s1["r"], "notified_states": len(ball.states),
                     "ms": round((time.monotonic() - t0) * 1000)})
                if not good:
                    fails += 1
                await client.stop_notify(EVT)
        except Exception as e:  # noqa: BLE001
            fails += 1
            log({"cycle": cycles, "error": f"{type(e).__name__}: {e}"})
        await asyncio.sleep(random.uniform(1.0, 4.0))
    # restore what the owner had
    if initial:
        try:
            async with BleakClient(addr, timeout=15) as client:
                ball = Ball(client, log)
                await client.start_notify(EVT, ball.on_evt)
                await ball.cmd("partner", id=initial["p"])
                await ball.cmd("brightness", val=initial["b"])
                await ball.cmd("alarm_set", h=initial["a"][1], m=initial["a"][2], en=initial["a"][0] == 1)
                await ball.cmd("time_sync", t=int(time.time()), tz=540)
                log({"restored": True, "state": await ball.state()})
        except Exception as e:  # noqa: BLE001
            log({"restore_error": f"{type(e).__name__}: {e}"})
    log({"summary": {"cycles": cycles, "fails": fails}})
    print(f"{'PASS' if cycles and not fails else 'FAIL'}: {cycles - fails}/{cycles} BLE cycles")
    return 0 if cycles and not fails else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
