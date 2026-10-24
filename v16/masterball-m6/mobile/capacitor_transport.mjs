// Capacitor 7 transport for PokeDockClient using @capacitor-community/bluetooth-le (native Android/iOS).
// Not exercised in CI: requires a signed native build and the physical device.
// Android 12+: BLUETOOTH_SCAN (neverForLocation) + BLUETOOTH_CONNECT in AndroidManifest.xml.
// iOS: NSBluetoothAlwaysUsageDescription in Info.plist. iOS negotiates MTU itself (185 typical).
import { BleClient } from '@capacitor-community/bluetooth-le';
import { COMMAND_UUID, EVENT_UUID, SERVICE_UUID, STATE_UUID } from './pokedock_ble_protocol.mjs';

const view = (u8) => new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
const bytes = (dv) => new Uint8Array(dv.buffer, dv.byteOffset, dv.byteLength);

export class CapacitorTransport {
  constructor({ deviceId = null } = {}) { this.deviceId = deviceId; }

  async connect(onEvent, onDisconnect) {
    await BleClient.initialize({ androidNeverForLocation: true });
    if (!this.deviceId) {
      const dev = await BleClient.requestDevice({ services: [SERVICE_UUID], namePrefix: 'PokeDock' });
      this.deviceId = dev.deviceId;
    }
    await BleClient.connect(this.deviceId, () => onDisconnect());
    // Bond first so the encrypted+authenticated characteristic does not fail mid-command.
    // Android shows the system passkey dialog; the 6 digits are on the ball's screen.
    if (BleClient.createBond) await BleClient.createBond(this.deviceId).catch(() => {});
    let mtu = 185;
    if (BleClient.requestMtu) mtu = await BleClient.requestMtu(this.deviceId, 247).catch(() => 23);
    if (BleClient.getMtu) mtu = await BleClient.getMtu(this.deviceId).catch(() => mtu);
    await BleClient.startNotifications(this.deviceId, SERVICE_UUID, EVENT_UUID, (dv) => onEvent(bytes(dv)));
    return { mtu };
  }

  write(u8) { return BleClient.write(this.deviceId, SERVICE_UUID, COMMAND_UUID, view(u8)); }

  async read() { return bytes(await BleClient.read(this.deviceId, SERVICE_UUID, STATE_UUID)); }

  async disconnect() { if (this.deviceId) await BleClient.disconnect(this.deviceId).catch(() => {}); }
}
