class DatakomCard extends HTMLElement {
  setConfig(config) {
    if (!config.camera) {
      throw new Error("camera is required");
    }

    this.config = {
      title: "Datakom controller",
      show_controls: false,
      ...config,
    };

    if (!this.content) {
      this.innerHTML = `<ha-card><div class="card"></div></ha-card>`;
      this.content = this.querySelector(".card");
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.config || !this.content) return;

    const camera = hass.states[this.config.camera];
    const prefix = this.config.entity_prefix || this._guessPrefix(this.config.camera);
    const state = this._state(`${prefix}operation_status`);
    const mode = this._state(`${prefix}unit_mode`);
    const rpm = this._state(`${prefix}engine_rpm`);
    const fuel = this._state(`${prefix}fuel_level`);
    const battery = this._state(`${prefix}battery_voltage`);
    const temperature = this._state(`${prefix}engine_temperature`);
    const engineRunning = this._isOn(`binary_sensor.${this._objectPrefix(prefix)}engine_running`);
    const onLoad = this._isOn(`binary_sensor.${this._objectPrefix(prefix)}genset_on_load`);
    const warning = this._isOn(`binary_sensor.${this._objectPrefix(prefix)}warning_alarm`);
    const shutdown = this._isOn(`binary_sensor.${this._objectPrefix(prefix)}shutdown_alarm`);

    const picture = camera?.attributes?.entity_picture;
    const imageUrl = picture
      ? `${picture}${picture.includes("?") ? "&" : "?"}v=${Date.now()}`
      : "";

    this.content.innerHTML = `
      <style>
        .card { padding: 16px; }
        .header { display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:12px; }
        .title { font-size:20px; font-weight:600; }
        .status { font-size:13px; opacity:.8; }
        .online { color: var(--success-color, #4caf50); }
        .offline { color: var(--error-color, #f44336); }
        .lcd-wrap { background:#111; border-radius:14px; padding:12px; }
        .lcd { display:block; width:100%; image-rendering:pixelated; border-radius:6px; aspect-ratio:2/1; object-fit:contain; background:#d6d8d2; }
        .grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:12px; }
        .metric { border-radius:12px; background:var(--secondary-background-color); padding:10px 12px; min-width:0; }
        .metric .label { font-size:12px; opacity:.7; }
        .metric .value { font-size:17px; margin-top:3px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .flags { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
        .flag { padding:5px 9px; border-radius:999px; font-size:12px; background:var(--secondary-background-color); }
        .flag.on { background:color-mix(in srgb, var(--success-color,#4caf50) 24%, transparent); }
        .flag.warn { background:color-mix(in srgb, var(--warning-color,#ff9800) 28%, transparent); }
        .flag.alarm { background:color-mix(in srgb, var(--error-color,#f44336) 28%, transparent); }
        .controls { display:grid; grid-template-columns:repeat(5,48px); justify-content:center; gap:8px; margin-top:14px; }
        .control { width:48px; height:42px; border:0; border-radius:12px; background:var(--secondary-background-color); color:var(--primary-text-color); font-size:20px; cursor:pointer; }
        .control[disabled] { opacity:.45; cursor:not-allowed; }
        @media (max-width:600px) { .grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
      </style>
      <div class="header">
        <div>
          <div class="title">${this._escape(this.config.title)}</div>
          <div class="status">${this._escape(state)} · ${this._escape(mode)}</div>
        </div>
        <div class="${camera ? "online" : "offline"}">${camera ? "● ONLINE" : "● OFFLINE"}</div>
      </div>
      <div class="lcd-wrap">
        ${imageUrl ? `<img class="lcd" src="${imageUrl}" alt="Datakom LCD">` : `<div class="lcd"></div>`}
      </div>
      <div class="flags">
        <span class="flag ${engineRunning ? "on" : ""}">Motor ${engineRunning ? "deluje" : "miruje"}</span>
        <span class="flag ${onLoad ? "on" : ""}">Breme ${onLoad ? "vklopljeno" : "izklopljeno"}</span>
        <span class="flag ${warning ? "warn" : ""}">Warning ${warning ? "aktiven" : "OK"}</span>
        <span class="flag ${shutdown ? "alarm" : ""}">Shutdown ${shutdown ? "aktiven" : "OK"}</span>
      </div>
      <div class="grid">
        ${this._metric("RPM", rpm)}
        ${this._metric("Gorivo", fuel)}
        ${this._metric("Baterija", battery)}
        ${this._metric("Temperatura", temperature)}
        ${this._metric("Stanje", state)}
        ${this._metric("Način", mode)}
      </div>
      ${this.config.show_controls ? `
        <div class="controls" title="Oddaljene tipke bodo omogočene v naslednji razvojni fazi">
          <button class="control" disabled>↖</button><button class="control" disabled>↑</button><button class="control" disabled>↗</button><button class="control" disabled>OK</button><button class="control" disabled>ESC</button>
          <button class="control" disabled>←</button><button class="control" disabled>↓</button><button class="control" disabled>→</button><button class="control" disabled>▶</button><button class="control" disabled>■</button>
        </div>` : ""}
    `;
  }

  _guessPrefix(cameraEntity) {
    const objectId = cameraEntity.split(".")[1] || "";
    return `sensor.${objectId.replace(/_lcd_display$/, "")}_`;
  }

  _objectPrefix(sensorPrefix) {
    return sensorPrefix.replace(/^sensor\./, "");
  }

  _state(entityId) {
    const entity = this._hass?.states?.[entityId];
    if (!entity) return "—";
    const unit = entity.attributes.unit_of_measurement;
    return `${entity.state}${unit ? ` ${unit}` : ""}`;
  }

  _isOn(entityId) {
    return this._hass?.states?.[entityId]?.state === "on";
  }

  _metric(label, value) {
    return `<div class="metric"><div class="label">${this._escape(label)}</div><div class="value">${this._escape(value)}</div></div>`;
  }

  _escape(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;",
    })[char]);
  }

  getCardSize() {
    return 8;
  }

  static getStubConfig() {
    return {
      camera: "camera.datakom_d502_lcd_display",
      title: "Datakom D502",
      entity_prefix: "sensor.datakom_d502_",
      show_controls: false,
    };
  }
}

customElements.define("datakom-card", DatakomCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "datakom-card",
  name: "Datakom Controller Card",
  description: "Physical Datakom LCD with live controller status.",
  preview: false,
});
