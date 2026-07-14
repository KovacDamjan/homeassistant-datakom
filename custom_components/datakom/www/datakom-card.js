class DatakomCard extends HTMLElement {
  setConfig(config) {
    if (!config.camera) {
      throw new Error("camera is required");
    }

    this.config = {
      title: "Datakom controller",
      show_controls: true,
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
    const objectPrefix = this._objectPrefix(prefix);

    const state = this._state(`${prefix}operation_status`);
    const mode = this._state(`${prefix}unit_mode`);
    const rpm = this._state(`${prefix}engine_rpm`);
    const fuel = this._state(`${prefix}fuel_level`);
    const battery = this._state(`${prefix}battery_voltage`);
    const temperature = this._state(`${prefix}engine_temperature`);

    const engineRunning = this._isOn(`binary_sensor.${objectPrefix}engine_running`);
    const onLoad = this._isOn(`binary_sensor.${objectPrefix}genset_on_load`);
    const warning = this._isOn(`binary_sensor.${objectPrefix}warning_alarm`);
    const shutdown = this._isOn(`binary_sensor.${objectPrefix}shutdown_alarm`);
    const autoMode = this._isOn(`binary_sensor.${objectPrefix}auto_mode`);
    const runMode = this._isOn(`binary_sensor.${objectPrefix}run_mode`);
    const testMode = this._isOn(`binary_sensor.${objectPrefix}test_mode`);
    const stopMode = this._isOn(`binary_sensor.${objectPrefix}stop_mode`);

    const imageUrl = this._cameraImageUrl(camera);

    this.content.innerHTML = `
      <style>
        .card { padding:16px; }
        .header { display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:14px; }
        .title { font-size:20px; font-weight:600; }
        .status { font-size:13px; opacity:.75; margin-top:2px; }
        .online { color:var(--success-color,#4caf50); font-size:13px; }
        .offline { color:var(--error-color,#f44336); font-size:13px; }
        .console { display:grid; grid-template-columns:minmax(230px,1fr) minmax(250px,1.2fr); gap:14px; align-items:stretch; }
        .lcd-frame { background:#111; border-radius:16px; padding:11px; display:flex; align-items:center; }
        .lcd { display:block; width:100%; aspect-ratio:2/1; object-fit:contain; image-rendering:pixelated; border-radius:7px; background:#d6d8d2; }
        .panel { border:1px solid var(--divider-color); border-radius:14px; padding:12px; background:var(--secondary-background-color); }
        .panel-top { display:grid; grid-template-columns:126px 1fr; gap:12px; align-items:center; }
        .dpad { display:grid; grid-template-columns:repeat(3,38px); grid-template-rows:repeat(3,38px); gap:5px; justify-content:center; }
        .key { border:0; border-radius:50%; background:#252525; color:#fff; font-size:21px; box-shadow:0 2px 5px #0006; }
        .key[disabled] { opacity:.8; cursor:not-allowed; }
        .up { grid-column:2; grid-row:1; }
        .left { grid-column:1; grid-row:2; }
        .right { grid-column:3; grid-row:2; }
        .down { grid-column:2; grid-row:3; }
        .flow { display:grid; grid-template-columns:1fr 1.3fr 1fr; gap:7px; align-items:start; text-align:center; }
        .flow-item { font-size:11px; font-weight:600; }
        .lamp { width:42px; height:42px; margin:0 auto 5px; border-radius:50%; background:#242424; position:relative; box-shadow:inset 0 0 0 2px #777,0 2px 4px #0005; }
        .lamp::after { content:""; position:absolute; right:1px; top:1px; width:8px; height:8px; border-radius:50%; background:#aaa; }
        .lamp.on::after { background:#55d86a; box-shadow:0 0 7px #55d86a; }
        .load-line { height:4px; background:#333; margin:18px 0 14px; position:relative; }
        .load-line::after { content:""; position:absolute; right:35%; top:-7px; width:18px; height:12px; border-left:3px solid #333; border-bottom:3px solid #333; transform:skewX(-20deg); }
        .modes { display:grid; grid-template-columns:repeat(5,1fr); gap:7px; margin-top:12px; text-align:center; }
        .mode-button { min-width:0; }
        .mode-circle { width:42px; height:42px; margin:auto; border-radius:50%; display:grid; place-items:center; color:#fff; font-weight:700; box-shadow:inset 0 0 0 2px #aaa,0 2px 4px #0005; filter:saturate(.55); }
        .mode-circle.active { filter:none; box-shadow:inset 0 0 0 2px #eee,0 0 9px currentColor; }
        .test { background:#f2d900; color:#222; }
        .run { background:#0aa54f; }
        .man { background:#2b2025; }
        .auto { background:#30262a; }
        .stop { background:#e02920; }
        .mode-label { font-size:11px; font-weight:600; margin-top:4px; }
        .flags { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
        .flag { padding:5px 9px; border-radius:999px; font-size:12px; background:var(--secondary-background-color); }
        .flag.on { background:color-mix(in srgb,var(--success-color,#4caf50) 24%,transparent); }
        .flag.warn { background:color-mix(in srgb,var(--warning-color,#ff9800) 28%,transparent); }
        .flag.alarm { background:color-mix(in srgb,var(--error-color,#f44336) 28%,transparent); }
        .grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:12px; }
        .metric { border-radius:12px; background:var(--secondary-background-color); padding:10px 12px; min-width:0; }
        .metric .label { font-size:12px; opacity:.7; }
        .metric .value { font-size:17px; margin-top:3px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        @media (max-width:700px) {
          .console { grid-template-columns:1fr; }
          .panel-top { grid-template-columns:126px 1fr; }
          .grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
        }
      </style>
      <div class="header">
        <div>
          <div class="title">${this._escape(this.config.title)}</div>
          <div class="status">${this._escape(state)} · ${this._escape(mode)}</div>
        </div>
        <div class="${camera ? "online" : "offline"}">${camera ? "● ONLINE" : "● OFFLINE"}</div>
      </div>
      <div class="console">
        <div class="lcd-frame">
          ${imageUrl ? `<img class="lcd" src="${imageUrl}" alt="Datakom LCD">` : `<div class="lcd"></div>`}
        </div>
        <div class="panel">
          <div class="panel-top">
            <div class="dpad" title="Oddaljene tipke bodo omogočene v naslednji različici">
              <button class="key up" disabled>▲</button>
              <button class="key left" disabled>◀</button>
              <button class="key right" disabled>▶</button>
              <button class="key down" disabled>▼</button>
            </div>
            <div class="flow">
              ${this._flowLamp("MAINS", !onLoad, "⚡")}
              <div><div class="load-line"></div><div class="flow-item">LOAD</div></div>
              ${this._flowLamp("GENSET", engineRunning, "▰")}
            </div>
          </div>
          <div class="modes">
            ${this._mode("TEST", "⚙", "test", testMode)}
            ${this._mode("RUN", "I", "run", runMode)}
            ${this._mode("MAN", "✋", "man", false)}
            ${this._mode("AUTO", "A", "auto", autoMode)}
            ${this._mode("STOP", "O", "stop", stopMode)}
          </div>
        </div>
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
    `;
  }

  _cameraImageUrl(camera) {
    if (!camera) return "";
    const token = camera.attributes?.access_token;
    const base = `/api/camera_proxy/${encodeURIComponent(this.config.camera)}`;
    const params = new URLSearchParams({ v: String(Date.now()) });
    if (token) params.set("token", token);
    return `${base}?${params.toString()}`;
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

  _flowLamp(label, active, icon) {
    return `<div><div class="lamp ${active ? "on" : ""}"></div><div class="flow-item">${this._escape(icon)} ${this._escape(label)}</div></div>`;
  }

  _mode(label, icon, cssClass, active) {
    return `<div class="mode-button"><div class="mode-circle ${cssClass} ${active ? "active" : ""}">${this._escape(icon)}</div><div class="mode-label">${this._escape(label)}</div></div>`;
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
    };
  }
}

if (!customElements.get("datakom-card")) {
  customElements.define("datakom-card", DatakomCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "datakom-card")) {
  window.customCards.push({
    type: "datakom-card",
    name: "Datakom Remote Console",
    description: "Live physical LCD and controller status for Datakom D-series.",
    preview: false,
  });
}
