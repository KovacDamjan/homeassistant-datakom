class DatakomCard extends HTMLElement {
  setConfig(config) {
    if (!config.camera) throw new Error("camera is required");
    this.config = { title: "Datakom controller", refresh_interval: 5000, ...config };
    if (!this._built) this._build();
  }

  connectedCallback() {
    this._startImageRefresh();
  }

  disconnectedCallback() {
    if (this._imageTimer) clearInterval(this._imageTimer);
    this._imageTimer = undefined;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.config || !this._built) return;
    this._updateStates();
    if (!this._imageLoaded) this._refreshImage();
  }

  _build() {
    this.innerHTML = `
      <ha-card>
        <style>
          .card{padding:16px}.header{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:14px}
          .title{font-size:20px;font-weight:600}.status{font-size:13px;opacity:.75;margin-top:2px}.online{color:var(--success-color,#4caf50);font-size:13px}.offline{color:var(--error-color,#f44336);font-size:13px}
          .console{display:grid;grid-template-columns:minmax(230px,1fr) minmax(250px,1.2fr);gap:14px;align-items:stretch}
          .lcd-frame{background:#111;border-radius:16px;padding:11px;display:flex;align-items:center;min-height:140px}
          .lcd{display:block;width:100%;aspect-ratio:2/1;object-fit:contain;image-rendering:pixelated;border-radius:7px;background:#d6d8d2;opacity:1;transition:opacity .08s linear}
          .panel{border:1px solid var(--divider-color);border-radius:14px;padding:12px;background:var(--secondary-background-color)}
          .panel-top{display:grid;grid-template-columns:126px 1fr;gap:12px;align-items:center}.dpad{display:grid;grid-template-columns:repeat(3,38px);grid-template-rows:repeat(3,38px);gap:5px;justify-content:center}
          .key{border:0;border-radius:50%;background:#252525;color:#fff;font-size:21px;box-shadow:0 2px 5px #0006;opacity:.8}.up{grid-column:2;grid-row:1}.left{grid-column:1;grid-row:2}.right{grid-column:3;grid-row:2}.down{grid-column:2;grid-row:3}
          .flow{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:7px;align-items:start;text-align:center}.flow-item{font-size:11px;font-weight:600}.lamp{width:42px;height:42px;margin:0 auto 5px;border-radius:50%;background:#242424;position:relative;box-shadow:inset 0 0 0 2px #777,0 2px 4px #0005}.lamp:after{content:"";position:absolute;right:1px;top:1px;width:8px;height:8px;border-radius:50%;background:#aaa}.lamp.on:after{background:#55d86a;box-shadow:0 0 7px #55d86a}.load-line{height:4px;background:#333;margin:18px 0 14px;position:relative}
          .modes{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin-top:12px;text-align:center}.mode-circle{width:42px;height:42px;margin:auto;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:700;box-shadow:inset 0 0 0 2px #aaa,0 2px 4px #0005;filter:saturate(.55)}.mode-circle.active{filter:none;box-shadow:inset 0 0 0 2px #eee,0 0 9px currentColor}.test{background:#f2d900;color:#222}.run{background:#0aa54f}.man,.auto{background:#30262a}.stop{background:#e02920}.mode-label{font-size:11px;font-weight:600;margin-top:4px}
          .flags{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.flag{padding:5px 9px;border-radius:999px;font-size:12px;background:var(--secondary-background-color)}.flag.on{background:color-mix(in srgb,var(--success-color,#4caf50) 24%,transparent)}.flag.warn{background:color-mix(in srgb,var(--warning-color,#ff9800) 28%,transparent)}.flag.alarm{background:color-mix(in srgb,var(--error-color,#f44336) 28%,transparent)}
          .grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px}.metric{border-radius:12px;background:var(--secondary-background-color);padding:10px 12px;min-width:0}.label{font-size:12px;opacity:.7}.value{font-size:17px;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
          @media(max-width:700px){.console{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
        </style>
        <div class="card">
          <div class="header"><div><div class="title"></div><div class="status"></div></div><div class="connection"></div></div>
          <div class="console">
            <div class="lcd-frame"><img class="lcd" alt="Datakom LCD"></div>
            <div class="panel"><div class="panel-top"><div class="dpad"><button class="key up" disabled>▲</button><button class="key left" disabled>◀</button><button class="key right" disabled>▶</button><button class="key down" disabled>▼</button></div><div class="flow"><div><div class="lamp mains"></div><div class="flow-item">⚡ MAINS</div></div><div><div class="load-line"></div><div class="flow-item">LOAD</div></div><div><div class="lamp genset"></div><div class="flow-item">▰ GENSET</div></div></div></div><div class="modes"></div></div>
          </div>
          <div class="flags"></div><div class="grid"></div>
        </div>
      </ha-card>`;
    this._built = true;
    this._image = this.querySelector(".lcd");
    this.querySelector(".title").textContent = this.config?.title || "Datakom controller";
  }

  _updateStates() {
    const camera = this._hass.states[this.config.camera];
    const prefix = this.config.entity_prefix || this._guessPrefix(this.config.camera);
    const obj = prefix.replace(/^sensor\./, "");
    const state = this._state(`${prefix}operation_status`), mode = this._state(`${prefix}unit_mode`);
    const engine = this._on(`binary_sensor.${obj}engine_running`), load = this._on(`binary_sensor.${obj}genset_on_load`);
    const warning = this._on(`binary_sensor.${obj}warning_alarm`), shutdown = this._on(`binary_sensor.${obj}shutdown_alarm`);
    this.querySelector(".title").textContent = this.config.title;
    this.querySelector(".status").textContent = `${state} · ${mode}`;
    const connection = this.querySelector(".connection"); connection.className = `connection ${camera ? "online" : "offline"}`; connection.textContent = camera ? "● ONLINE" : "● OFFLINE";
    this.querySelector(".mains").classList.toggle("on", !load); this.querySelector(".genset").classList.toggle("on", engine);
    const modes = [["TEST","⚙","test","test_mode"],["RUN","I","run","run_mode"],["MAN","✋","man",null],["AUTO","A","auto","auto_mode"],["STOP","O","stop","stop_mode"]];
    this.querySelector(".modes").innerHTML = modes.map(([l,i,c,k])=>`<div><div class="mode-circle ${c} ${k&&this._on(`binary_sensor.${obj}${k}`)?"active":""}">${i}</div><div class="mode-label">${l}</div></div>`).join("");
    this.querySelector(".flags").innerHTML = `<span class="flag ${engine?"on":""}">Motor ${engine?"deluje":"miruje"}</span><span class="flag ${load?"on":""}">Breme ${load?"vklopljeno":"izklopljeno"}</span><span class="flag ${warning?"warn":""}">Warning ${warning?"aktiven":"OK"}</span><span class="flag ${shutdown?"alarm":""}">Shutdown ${shutdown?"aktiven":"OK"}</span>`;
    const metrics = [["RPM",`${prefix}engine_rpm`],["Gorivo",`${prefix}fuel_level`],["Baterija",`${prefix}battery_voltage`],["Temperatura",`${prefix}engine_temperature`],["Stanje",`${prefix}operation_status`],["Način",`${prefix}unit_mode`]];
    this.querySelector(".grid").innerHTML = metrics.map(([l,e])=>`<div class="metric"><div class="label">${l}</div><div class="value">${this._state(e)}</div></div>`).join("");
  }

  _startImageRefresh() {
    if (this._imageTimer) clearInterval(this._imageTimer);
    const interval = Math.max(2000, Number(this.config?.refresh_interval) || 5000);
    this._imageTimer = setInterval(() => this._refreshImage(), interval);
  }

  _refreshImage() {
    if (!this._hass || !this.config || !this._image) return;
    const camera = this._hass.states[this.config.camera];
    if (!camera) return;
    const token = camera.attributes?.access_token;
    const base = `/api/camera_proxy/${encodeURIComponent(this.config.camera)}`;
    const params = new URLSearchParams({ v: String(Date.now()) });
    if (token) params.set("token", token);
    const preload = new Image();
    preload.onload = () => { this._image.src = preload.src; this._imageLoaded = true; };
    preload.src = `${base}?${params.toString()}`;
  }

  _guessPrefix(camera) { const id = camera.split(".")[1] || ""; return `sensor.${id.replace(/_lcd_display$/, "")}_`; }
  _state(id) { const e = this._hass?.states?.[id]; if (!e) return "—"; const u=e.attributes.unit_of_measurement; return `${e.state}${u?` ${u}`:""}`; }
  _on(id) { return this._hass?.states?.[id]?.state === "on"; }
  getCardSize() { return 8; }
  static getStubConfig() { return { camera:"camera.datakom_d502_lcd_display", title:"Datakom D502", entity_prefix:"sensor.datakom_d502_" }; }
}
if (!customElements.get("datakom-card")) customElements.define("datakom-card", DatakomCard);
window.customCards = window.customCards || [];
if (!window.customCards.some(c=>c.type==="datakom-card")) window.customCards.push({type:"datakom-card",name:"Datakom Remote Console",description:"Live physical LCD and controller status for Datakom D-series.",preview:false});