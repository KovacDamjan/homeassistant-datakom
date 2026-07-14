const DATAKOM_TRANSLATIONS = {
  en: {
    controller: "Datakom controller",
    statusTitle: "Datakom status",
    online: "ONLINE",
    offline: "OFFLINE",
    mains: "MAINS",
    load: "LOAD",
    genset: "GENSET",
    engine: "Engine",
    engineRunning: "running",
    engineStopped: "stopped",
    loadState: "Load",
    loadOn: "on",
    loadOff: "off",
    warning: "Warning",
    shutdown: "Shutdown",
    active: "active",
    ok: "OK",
    fuel: "Fuel",
    battery: "Battery",
    temperature: "Temperature",
    state: "State",
    mode: "Mode",
    keyFailed: "Key failed",
    rest: "rest",
  },
  sl: {
    controller: "Krmilnik Datakom",
    statusTitle: "Stanje Datakom",
    online: "POVEZAN",
    offline: "NI POVEZAVE",
    mains: "OMREŽJE",
    load: "BREME",
    genset: "AGREGAT",
    engine: "Motor",
    engineRunning: "deluje",
    engineStopped: "miruje",
    loadState: "Breme",
    loadOn: "vklopljeno",
    loadOff: "izklopljeno",
    warning: "Opozorilo",
    shutdown: "Zaustavitev",
    active: "aktivno",
    ok: "OK",
    fuel: "Gorivo",
    battery: "Baterija",
    temperature: "Temperatura",
    state: "Stanje",
    mode: "Način",
    keyFailed: "Napaka tipke",
    rest: "mirovanje",
  },
};

function datakomLanguage(hass) {
  return String(hass?.language || hass?.locale?.language || "en").toLowerCase().startsWith("sl") ? "sl" : "en";
}

function datakomText(hass, key) {
  const language = datakomLanguage(hass);
  return DATAKOM_TRANSLATIONS[language][key] ?? DATAKOM_TRANSLATIONS.en[key] ?? key;
}

function datakomDisplayState(hass, value) {
  if (value === "rest") return datakomText(hass, "rest");
  return String(value ?? "—").replaceAll("_", " ");
}

const COMMON_STYLE = `
  *{box-sizing:border-box}.title{font-size:18px;font-weight:600}.lcd-frame,.frame{background:#d6d8d2;border:6px solid #000;border-radius:16px;padding:6px;box-shadow:inset 0 0 0 2px #333,0 3px 10px #0005}.lcd{display:block;width:100%;aspect-ratio:2/1;object-fit:contain;image-rendering:pixelated;border-radius:8px;background:#d6d8d2}.flags{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.flag{padding:8px;border-radius:999px;text-align:center;background:var(--secondary-background-color);font-size:12px}.flag.on{background:color-mix(in srgb,var(--success-color,#4caf50) 24%,transparent)}.flag.warn{background:color-mix(in srgb,var(--warning-color,#ff9800) 28%,transparent)}.flag.alarm{background:color-mix(in srgb,var(--error-color,#f44336) 28%,transparent)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}.metric{padding:10px 12px;border-radius:12px;background:var(--secondary-background-color);min-width:0}.label{font-size:12px;opacity:.7}.value{font-size:17px;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
`;

class DatakomCard extends HTMLElement {
  setConfig(config) {
    if (!config.camera) throw new Error("camera is required");
    this.config = { refresh_interval: 5000, ...config };
    if (!this._built) this._build();
  }

  connectedCallback() { this._startImageRefresh(); }
  disconnectedCallback() { if (this._imageTimer) clearInterval(this._imageTimer); }

  set hass(hass) {
    this._hass = hass;
    if (!this.config || !this._built) return;
    this._updateStates();
    if (!this._imageLoaded) this._refreshImage();
  }

  _build() {
    this.innerHTML = `<ha-card><style>${COMMON_STYLE}
      .card{padding:16px;overflow:hidden}.header{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:14px}.title{font-size:20px}.status{font-size:13px;opacity:.75;margin-top:2px}.online{color:var(--success-color,#4caf50);font-size:13px}.offline{color:var(--error-color,#f44336);font-size:13px}.console{display:grid;gap:12px}.panel{border:1px solid var(--divider-color);border-radius:14px;padding:12px;background:var(--secondary-background-color);overflow:hidden}.panel-top{display:grid;grid-template-columns:minmax(120px,.8fr) minmax(0,1.2fr);gap:12px;align-items:center}.dpad-wrap{display:flex;flex-direction:column;align-items:center;gap:8px}.dpad{display:grid;grid-template-columns:repeat(3,44px);grid-template-rows:repeat(3,44px);gap:5px}.key{border:1px solid #555;border-radius:50%;background:radial-gradient(circle at 35% 30%,#4a4a4a,#181818 68%);color:#fff;font-size:21px;box-shadow:inset 0 1px 2px #ffffff35,0 3px 6px #0008;cursor:pointer}.key:active,.key.pressed{transform:scale(.9);filter:brightness(.72)}.key:disabled,.soft-key:disabled{opacity:.45;cursor:wait}.up{grid-column:2;grid-row:1}.left{grid-column:1;grid-row:2}.right{grid-column:3;grid-row:2}.down{grid-column:2;grid-row:3}.secondary-keys{display:flex;gap:8px}.soft-key{border:1px solid #555;border-radius:10px;background:linear-gradient(#3b3b3b,#181818);color:#fff;padding:7px 12px;font-size:12px;font-weight:600;cursor:pointer}.hint{font-size:10px;min-height:13px;text-align:center}.hint.error{color:var(--error-color,#f44336)}.flow{display:grid;grid-template-columns:1fr 1.2fr 1fr;gap:7px;text-align:center}.flow-item{font-size:11px;font-weight:600}.lamp{width:42px;height:42px;margin:0 auto 5px;border-radius:50%;background:#242424;position:relative;box-shadow:inset 0 0 0 2px #777,0 2px 4px #0005}.lamp:after{content:"";position:absolute;right:1px;top:1px;width:8px;height:8px;border-radius:50%;background:#aaa}.lamp.on:after{background:#55d86a;box-shadow:0 0 7px #55d86a}.load-line{height:4px;background:#333;margin:18px 0 14px}.modes{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px;margin-top:12px;text-align:center}.mode-circle{width:42px;height:42px;margin:auto;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:700;box-shadow:inset 0 0 0 2px #aaa,0 2px 4px #0005;filter:saturate(.55)}.mode-circle.active{filter:none;box-shadow:inset 0 0 0 2px #eee,0 0 9px currentColor}.test{background:#f2d900;color:#222}.run{background:#0aa54f}.man,.auto{background:#30262a}.stop{background:#e02920}.mode-label{font-size:11px;font-weight:600;margin-top:4px}.card>.flags{grid-template-columns:repeat(4,minmax(0,1fr));margin-top:12px}.card>.grid{grid-template-columns:repeat(3,minmax(0,1fr));margin-top:12px}@media(max-width:520px){.card{padding:14px}.panel-top{grid-template-columns:1fr}.card>.flags{grid-template-columns:repeat(2,minmax(0,1fr))}.card>.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    </style><div class="card"><div class="header"><div><div class="title"></div><div class="status"></div></div><div class="connection"></div></div><div class="console"><div class="lcd-frame"><img class="lcd" alt="Datakom LCD"></div><div class="panel"><div class="panel-top"><div class="dpad-wrap"><div class="dpad"><button class="key up" data-key="up" aria-label="Up">▲</button><button class="key left" data-key="left" aria-label="Left / ESC">◀</button><button class="key right" data-key="right" aria-label="Right / OK">▶</button><button class="key down" data-key="down" aria-label="Down">▼</button></div><div class="secondary-keys"><button class="soft-key" data-key="esc">ESC</button><button class="soft-key" data-key="ok">OK</button></div><div class="hint"></div></div><div class="flow"><div><div class="lamp mains"></div><div class="flow-item mains-label"></div></div><div><div class="load-line"></div><div class="flow-item load-label"></div></div><div><div class="lamp genset"></div><div class="flow-item genset-label"></div></div></div></div><div class="modes"></div></div></div><div class="flags"></div><div class="grid"></div></div></ha-card>`;
    this._built = true;
    this._image = this.querySelector(".lcd");
    this.querySelectorAll("[data-key]").forEach((button) => button.addEventListener("click", () => this._pressKey(button)));
  }

  async _pressKey(button) {
    if (!this._hass || this._keyPending) return;
    this._keyPending = true;
    const key = button.dataset.key;
    const prefix = this.config.entity_prefix || this._guessPrefix(this.config.camera);
    const entityId = `button.${prefix.replace(/^sensor\./, "")}key_${key}`;
    const hint = this.querySelector(".hint");
    button.classList.add("pressed");
    this.querySelectorAll("[data-key]").forEach((item) => item.disabled = true);
    hint.className = "hint";
    hint.textContent = "";
    try {
      await this._hass.callService("button", "press", { entity_id: entityId });
      window.setTimeout(() => this._refreshImage(), 350);
      window.setTimeout(() => this._refreshImage(), 1100);
    } catch (error) {
      hint.className = "hint error";
      hint.textContent = `${datakomText(this._hass, "keyFailed")}: ${error?.message || error}`;
    } finally {
      window.setTimeout(() => button.classList.remove("pressed"), 140);
      this.querySelectorAll("[data-key]").forEach((item) => item.disabled = false);
      this._keyPending = false;
    }
  }

  _updateStates() {
    const camera = this._hass.states[this.config.camera];
    const prefix = this.config.entity_prefix || this._guessPrefix(this.config.camera);
    const obj = prefix.replace(/^sensor\./, "");
    const state = this._state(`${prefix}operation_status`, true);
    const mode = this._state(`${prefix}unit_mode`, true);
    const engine = this._on(`binary_sensor.${obj}engine_running`);
    const load = this._on(`binary_sensor.${obj}genset_on_load`);
    const warning = this._on(`binary_sensor.${obj}warning_alarm`);
    const shutdown = this._on(`binary_sensor.${obj}shutdown_alarm`);
    this.querySelector(".title").textContent = this.config.title || datakomText(this._hass, "controller");
    this.querySelector(".status").textContent = `${state} · ${mode}`;
    const connection = this.querySelector(".connection");
    connection.className = `connection ${camera ? "online" : "offline"}`;
    connection.textContent = `● ${datakomText(this._hass, camera ? "online" : "offline")}`;
    this.querySelector(".mains-label").textContent = `⚡ ${datakomText(this._hass, "mains")}`;
    this.querySelector(".load-label").textContent = datakomText(this._hass, "load");
    this.querySelector(".genset-label").textContent = `▰ ${datakomText(this._hass, "genset")}`;
    this.querySelector(".mains").classList.toggle("on", !load);
    this.querySelector(".genset").classList.toggle("on", engine);
    const modes = [["TEST","⚙","test","test_mode"],["RUN","I","run","run_mode"],["MAN","✋","man",null],["AUTO","A","auto","auto_mode"],["STOP","O","stop","stop_mode"]];
    this.querySelector(".modes").innerHTML = modes.map(([label,icon,css,key]) => `<div><div class="mode-circle ${css} ${key && this._on(`binary_sensor.${obj}${key}`) ? "active" : ""}">${icon}</div><div class="mode-label">${label}</div></div>`).join("");
    this.querySelector(".flags").innerHTML = `<span class="flag ${engine ? "on" : ""}">${datakomText(this._hass,"engine")} ${datakomText(this._hass,engine ? "engineRunning" : "engineStopped")}</span><span class="flag ${load ? "on" : ""}">${datakomText(this._hass,"loadState")} ${datakomText(this._hass,load ? "loadOn" : "loadOff")}</span><span class="flag ${warning ? "warn" : ""}">${datakomText(this._hass,"warning")} ${datakomText(this._hass,warning ? "active" : "ok")}</span><span class="flag ${shutdown ? "alarm" : ""}">${datakomText(this._hass,"shutdown")} ${datakomText(this._hass,shutdown ? "active" : "ok")}</span>`;
    const metrics = [["RPM",`${prefix}engine_rpm`],[datakomText(this._hass,"fuel"),`${prefix}fuel_level`],[datakomText(this._hass,"battery"),`${prefix}battery_voltage`],[datakomText(this._hass,"temperature"),`${prefix}engine_temperature`],[datakomText(this._hass,"state"),`${prefix}operation_status`,true],[datakomText(this._hass,"mode"),`${prefix}unit_mode`,true]];
    this.querySelector(".grid").innerHTML = metrics.map(([label,id,translate]) => `<div class="metric"><div class="label">${label}</div><div class="value">${this._state(id,translate)}</div></div>`).join("");
  }

  _startImageRefresh() { if (this._imageTimer) clearInterval(this._imageTimer); this._imageTimer = setInterval(() => this._refreshImage(), Math.max(2000, Number(this.config?.refresh_interval) || 5000)); }
  _refreshImage() { if (!this._hass || !this._image) return; const camera=this._hass.states[this.config.camera]; if(!camera)return; const params=new URLSearchParams({v:String(Date.now())}); if(camera.attributes?.access_token)params.set("token",camera.attributes.access_token); const preload=new Image(); preload.onload=()=>{this._image.src=preload.src;this._imageLoaded=true;}; preload.src=`/api/camera_proxy/${encodeURIComponent(this.config.camera)}?${params}`; }
  _guessPrefix(camera) { return `sensor.${(camera.split(".")[1] || "").replace(/_lcd_display$/, "")}_`; }
  _state(id, translate=false) { const entity=this._hass?.states?.[id]; if(!entity)return "—"; const value=translate?datakomDisplayState(this._hass,entity.state):entity.state; return `${value}${entity.attributes.unit_of_measurement?` ${entity.attributes.unit_of_measurement}`:""}`; }
  _on(id) { return this._hass?.states?.[id]?.state === "on"; }
  getCardSize() { return 10; }
  static getStubConfig() { return { camera:"camera.datakom_d502_lcd_display", entity_prefix:"sensor.datakom_d502_" }; }
}

class DatakomLcdCard extends HTMLElement {
  setConfig(config){if(!config.camera)throw new Error("camera is required");this.config={refresh_interval:5000,...config};if(!this._built)this._build();}
  connectedCallback(){this._start();} disconnectedCallback(){if(this._timer)clearInterval(this._timer);}
  set hass(hass){this._hass=hass;if(this._built)this.querySelector(".title").textContent=this.config.title||"Datakom LCD";if(!this._loaded)this._refresh();}
  _build(){this.innerHTML=`<ha-card><style>${COMMON_STYLE}.wrap{padding:14px}.title{margin-bottom:10px}</style><div class="wrap"><div class="title"></div><div class="frame"><img class="lcd" alt="Datakom LCD"></div></div></ha-card>`;this._image=this.querySelector(".lcd");this._built=true;}
  _start(){if(this._timer)clearInterval(this._timer);this._timer=setInterval(()=>this._refresh(),Math.max(2000,Number(this.config?.refresh_interval)||5000));}
  _refresh(){if(!this._hass||!this._image)return;const camera=this._hass.states[this.config.camera];if(!camera)return;const params=new URLSearchParams({v:String(Date.now())});if(camera.attributes?.access_token)params.set("token",camera.attributes.access_token);const preload=new Image();preload.onload=()=>{this._image.src=preload.src;this._loaded=true;};preload.src=`/api/camera_proxy/${encodeURIComponent(this.config.camera)}?${params}`;}
  getCardSize(){return 4;} static getStubConfig(){return{camera:"camera.datakom_d502_lcd_display"};}
}

class DatakomStatusCard extends HTMLElement {
  setConfig(config){if(!config.entity_prefix)throw new Error("entity_prefix is required");this.config={...config};if(!this._built)this._build();}
  set hass(hass){this._hass=hass;if(this._built)this._update();}
  _build(){this.innerHTML=`<ha-card><style>${COMMON_STYLE}.wrap{padding:16px}.title{margin-bottom:12px}</style><div class="wrap"><div class="title"></div><div class="flags"></div><div class="grid"></div></div></ha-card>`;this._built=true;}
  _update(){const p=this.config.entity_prefix,obj=p.replace(/^sensor\./,"");const engine=this._on(`binary_sensor.${obj}engine_running`),load=this._on(`binary_sensor.${obj}genset_on_load`),warning=this._on(`binary_sensor.${obj}warning_alarm`),shutdown=this._on(`binary_sensor.${obj}shutdown_alarm`);this.querySelector(".title").textContent=this.config.title||datakomText(this._hass,"statusTitle");this.querySelector(".flags").innerHTML=`<span class="flag ${engine?"on":""}">${datakomText(this._hass,"engine")} ${datakomText(this._hass,engine?"engineRunning":"engineStopped")}</span><span class="flag ${load?"on":""}">${datakomText(this._hass,"loadState")} ${datakomText(this._hass,load?"loadOn":"loadOff")}</span><span class="flag ${warning?"warn":""}">${datakomText(this._hass,"warning")} ${datakomText(this._hass,warning?"active":"ok")}</span><span class="flag ${shutdown?"alarm":""}">${datakomText(this._hass,"shutdown")} ${datakomText(this._hass,shutdown?"active":"ok")}</span>`;const metrics=[["RPM",`${p}engine_rpm`],[datakomText(this._hass,"fuel"),`${p}fuel_level`],[datakomText(this._hass,"battery"),`${p}battery_voltage`],[datakomText(this._hass,"temperature"),`${p}engine_temperature`],[datakomText(this._hass,"state"),`${p}operation_status`,true],[datakomText(this._hass,"mode"),`${p}unit_mode`,true]];this.querySelector(".grid").innerHTML=metrics.map(([label,id,translate])=>`<div class="metric"><div class="label">${label}</div><div class="value">${this._state(id,translate)}</div></div>`).join("");}
  _state(id,translate=false){const entity=this._hass?.states?.[id];if(!entity)return"—";const value=translate?datakomDisplayState(this._hass,entity.state):entity.state;return`${value}${entity.attributes.unit_of_measurement?` ${entity.attributes.unit_of_measurement}`:""}`;}
  _on(id){return this._hass?.states?.[id]?.state==="on";} getCardSize(){return 4;} static getStubConfig(){return{entity_prefix:"sensor.datakom_d502_"};}
}

if(!customElements.get("datakom-card"))customElements.define("datakom-card",DatakomCard);
if(!customElements.get("datakom-lcd-card"))customElements.define("datakom-lcd-card",DatakomLcdCard);
if(!customElements.get("datakom-status-card"))customElements.define("datakom-status-card",DatakomStatusCard);
window.customCards=window.customCards||[];
[
 {type:"datakom-card",name:"Datakom Remote Console",description:"Live physical LCD and controller status for Datakom D-series."},
 {type:"datakom-lcd-card",name:"Datakom LCD",description:"Standalone live physical LCD card."},
 {type:"datakom-status-card",name:"Datakom Status",description:"Compact Datakom status and measurements card."}
].forEach(card=>{if(!window.customCards.some(c=>c.type===card.type))window.customCards.push({...card,preview:false});});