# Test Matrix

| Test | Expected | Pass criterion |
|---|---|---|
| Cold boot no Wi-Fi | clock UI boots | <10 s usable |
| RTC power cycle | time retained | no reset to epoch |
| SD missing | fallback UI | no crash |
| Dock node off | HMI still usable | no reboot loop |
| Phone place | Pachirisu mode | <=2 s |
| Phone remove | exit dock mode | <=3 s |
| Low light | Gengar mode | stable after 3–5 s |
| Bright again | exit night | no flicker |
| NFC Gengar | Gengar override | <=1 s after read |
| NFC remove | override times out | configurable |
| Focus start | Lucario | timer accurate ±1 s/min |
| Birthday test flag | Jirachi sequence | always wins over dock/night |
| Random encounter | does not interrupt focus | pass |
| Qi 45 min | stable charge | no excessive enclosure heat |
| Qi + NFC | both usable | no repeated NFC false trigger |
| 20 reboot cycles | returns to Home | 20/20 |