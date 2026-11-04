(function () {
  "use strict";
  var W = window.WIKI, M = W.msgs;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- theme ---------- */
  var root = document.documentElement;
  var th = store.get("theme");
  if (th) root.setAttribute("data-theme", th);
  $("#theme").onclick = function () {
    var dark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    var nt = dark ? "light" : "dark";
    root.setAttribute("data-theme", nt); store.set("theme", nt);
  };

  $("#ver").textContent = W.tag; $("#a-tag").textContent = W.tag; $("#f-tag").textContent = W.tag;

  /* ---------- tabs ---------- */
  function showTab(name) {
    document.querySelectorAll(".tab").forEach(function (b) { b.classList.toggle("on", b.dataset.tab === name); });
    document.querySelectorAll(".pane").forEach(function (p) { p.classList.toggle("on", p.id === "tab-" + name); });
  }
  document.querySelectorAll(".tab").forEach(function (b) { b.onclick = function () { showTab(b.dataset.tab); }; });
  $("#home").onclick = function (e) { e.preventDefault(); showTab("search"); $("#q").focus(); };

  /* ---------- search index ---------- */
  var SPEC = /%[-+ #0-9.]*(?:l|h|ll|z)?[a-zA-Z]/g;
  function tplRe(t) {
    var parts = t.split(SPEC), lit = 0;
    parts = parts.map(function (p) { lit += p.trim().length; return p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\s+/g, "\\s+"); });
    var re = null;
    try { re = new RegExp(parts.join(".+?"), "i"); } catch (e) {}
    return { re: re, lit: lit };
  }
  M.forEach(function (m) {
    var pn = m.p.map(function (p) { return p.name; }).join(" ");
    m._pn = pn.toLowerCase();
    m._t = m.text.toLowerCase();
    m._ti = (m.t || "").toLowerCase();
    m._h = (m.text + " " + m.t + " " + m.c + " " + m.f.join(" ") + " " + pn + " " + m.sub + " " + m.file.split("/").pop()).toLowerCase();
    m._w = {};
    m._t.split(/[^a-z0-9_]+/).forEach(function (w) { if (w) m._w[w] = 1; });
    var tr = tplRe(m.text); m._re = tr.lit >= 10 ? tr.re : null; m._lit = tr.lit;
    m._sg = (m.sev === "WARNING") ? "w" : (/^(INFO|NOTICE|DEBUG)$/.test(m.sev) ? "i" : "c");
  });

  var STOP = { "не": 1, "и": 1, "в": 1, "на": 1, "при": 1, "как": 1, "что": 1, "это": 1, "у": 1, "с": 1, "по": 1, "из": 1, "я": 1, "мой": 1, "ошибка": 1, "ошибки": 1, "сообщение": 1, "the": 1, "a": 1, "is": 1 };
  var SYN = [
    ["компас", ["compass", "mag"]], ["магнит", ["mag", "compass"]], ["гпс", ["gps"]], ["спутник", ["gps", "sats"]],
    ["батаре", ["batt", "battery"]], ["аккум", ["batt", "battery"]], ["напряж", ["volt", "voltage"]], ["пульт", ["rc", "radio"]],
    ["приемник", ["rc", "radio"]], ["приёмник", ["rc", "radio"]], ["радио", ["radio", "rc"]], ["арм", ["arm", "prearm"]], ["калибр", ["calib", "cal"]],
    ["вибрац", ["vibe", "vibration"]], ["барометр", ["baro"]], ["акселер", ["accel"]], ["гироскоп", ["gyro"]], ["мотор", ["motor"]],
    ["двигател", ["motor"]], ["высот", ["alt", "altitude"]], ["режим", ["mode"]], ["парашют", ["chute", "parachute"]],
    ["дальномер", ["rangefinder", "rngfnd"]], ["лидар", ["rangefinder", "lidar"]], ["забор", ["fence"]], ["фенс", ["fence"]],
    ["геозон", ["fence"]], ["миссия", ["mission"]], ["миссии", ["mission"]], ["лог", ["log", "logging"]], ["памят", ["memory"]],
    ["карт", ["sd", "card"]], ["камер", ["camera", "mount"]], ["подвес", ["mount", "gimbal"]], ["потер", ["lost", "failsafe"]],
    ["нездоров", ["healthy"]], ["сбой", ["fail", "failed"]], ["отказ", ["fail", "failsafe"]], ["посад", ["land"]],
    ["взлет", ["takeoff"]], ["взлёт", ["takeoff"]], ["краш", ["crash"]], ["падени", ["crash"]], ["оптик", ["flow"]],
    ["флоу", ["flow"]], ["ekf", ["ekf"]], ["экф", ["ekf"]], ["навигац", ["ekf", "nav"]], ["курс", ["yaw", "heading"]],
    ["перезагруз", ["reboot"]], ["прошивк", ["firmware", "bootloader"]], ["параметр", ["param"]], ["телеметр", ["telem", "gcs"]],
    ["связь", ["gcs", "radio", "failsafe"]], ["esc", ["esc"]], ["регулятор", ["esc"]], ["пропеллер", ["motor", "thrust"]]
  ];
  function expand(tok) {
    var out = [tok];
    for (var i = 0; i < SYN.length; i++) if (tok.indexOf(SYN[i][0]) === 0) out = out.concat(SYN[i][1]);
    return out;
  }
  function lev1(a, b) {
    if (Math.abs(a.length - b.length) > 1) return false;
    var i = 0, j = 0, d = 0;
    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) { i++; j++; continue; }
      if (++d > 1) return false;
      if (a.length > b.length) i++; else if (a.length < b.length) j++; else { i++; j++; }
    }
    return d + (a.length - i) + (b.length - j) <= 1;
  }

  function search(q) {
    q = q.trim();
    var ql = q.toLowerCase();
    var toks = ql.split(/[\s,;:()"'\[\]=]+/).filter(function (t) { return t && !STOP[t]; });
    var res = [], part = [];
    if (!toks.length) return M.map(function (m, i) { return { m: m, s: 0 }; });
    var alts = toks.map(expand);
    M.forEach(function (m) {
      var s = 0, hit = 0, miss = 0;
      if (m._re && q.length >= 8 && m._re.test(q)) s += 1000 + m._lit;
      if (m._t === ql) s += 500;
      for (var i = 0; i < alts.length; i++) {
        var best = 0;
        for (var j = 0; j < alts[i].length; j++) {
          var a = alts[i][j], w = 0;
          if (m._t.indexOf(a) >= 0) { w = m._w[a] ? 15 : 10; }
          else if (m._pn.indexOf(a) >= 0) w = 8;
          else if (m._ti.indexOf(a) >= 0) w = 6;
          else if (m._h.indexOf(a) >= 0) w = 2;
          else if (a.length >= 5 && /^[a-z0-9_]+$/.test(a)) {
            for (var k in m._w) if (k[0] === a[0] && lev1(a, k)) { w = 4; break; }
          }
          if (j > 0) w *= 0.8;
          if (w > best) best = w;
        }
        if (best) { hit++; s += best; } else miss++;
      }
      if (hit === 0) return;
      var partial = false;
      if (miss > 0) { if (toks.length >= 3 && hit / toks.length >= 0.6) s *= 0.4; else partial = true; }
      s += m.cur * 3 - m.rank * 2 + (m._sg === "c" ? 1 : 0);
      (partial ? part : res).push({ m: m, s: s });
    });
    if (!res.length) res = part;
    res.sort(function (a, b) { return b.s - a.s; });
    return res;
  }

  /* ---------- filters ---------- */
  var SG = [["c", "Критичные"], ["w", "Предупреждения"], ["i", "Инфо"]];
  var sgOn = { c: true, w: true, i: true };
  var sevsEl = $("#sevs");
  SG.forEach(function (x) {
    var b = document.createElement("button");
    b.className = "sev on"; b.textContent = x[1]; b.dataset.k = x[0];
    b.onclick = function () { sgOn[x[0]] = !sgOn[x[0]]; b.classList.toggle("on", sgOn[x[0]]); run(); };
    sevsEl.appendChild(b);
  });
  var subs = {};
  M.forEach(function (m) { subs[m.sub] = (subs[m.sub] || 0) + 1; });
  Object.keys(subs).sort(function (a, b) { return subs[b] - subs[a]; }).forEach(function (k) {
    var o = document.createElement("option"); o.value = k; o.textContent = k + " (" + subs[k] + ")"; $("#sub").appendChild(o);
  });
  $("#sub").onchange = run; $("#onlyCur").onchange = run; $("#onlyCopter").onchange = run;

  /* ---------- quick chips ---------- */
  ["PreArm", "компас", "GPS", "EKF", "батарея", "failsafe", "вибрации", "не армится", "пульт", "моторы", "дальномер", "SD карта", "fence"].forEach(function (t) {
    var b = document.createElement("button"); b.className = "chip"; b.textContent = t;
    b.onclick = function () { $("#q").value = t; run(true); $("#q").focus(); };
    $("#quick").appendChild(b);
  });

  /* ---------- render ---------- */
  var cur = [], shown = 0, PAGE = 30, openId = null, lastQ = "";
  function hl(text, toks) {
    var s = esc(text);
    toks.forEach(function (t) {
      if (t.length < 2) return;
      var re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      s = s.replace(re, function (m, a, off, str) {
        // не ломаем html-сущности
        var before = str.lastIndexOf("&", off), semi = str.lastIndexOf(";", off);
        if (before > semi && str.indexOf(";", off) > 0 && str.indexOf(";", off) - before < 8) return m;
        return "<mark>" + m + "</mark>";
      });
    });
    return s;
  }
  function qtoks(q) {
    var t = q.toLowerCase().split(/[\s,;:()"'\[\]=]+/).filter(function (x) { return x && !STOP[x]; });
    var all = [];
    t.forEach(function (x) { all = all.concat(expand(x)); });
    return all.filter(function (v, i, a) { return a.indexOf(v) === i; });
  }
  function card(m, toks) {
    var open = m.id === openId;
    var html = '<div class="item' + (open ? " open" : "") + '" id="i-' + m.id + '">' +
      '<button class="head" data-id="' + m.id + '" aria-expanded="' + open + '"><div class="line1"><span class="badge b-' + esc(m.sev) + '">' + esc(m.sev) + '</span>' +
      '<div><div class="msg">' + hl(m.text, toks) + '</div>' +
      (m.t ? '<div class="title">' + esc(m.t) + '</div>' : "") +
      '<div class="tags"><span class="tag">' + esc(m.sub) + '</span>' + (m.cur ? '<span class="tag ok">есть разбор</span>' : "") + '</div></div></div></button>' +
      '<div class="body">' + (open ? detail(m) : "") + "</div></div>";
    return html;
  }
  function detail(m) {
    var h = "";
    h += "<h4>Почему это происходит</h4><div>" + esc(m.c) + "</div>";
    if (m.note) h += '<div class="note" style="margin-top:6px">' + esc(m.note) + "</div>";
    if (m.f.length) h += "<h4>Что делать</h4><ol>" + m.f.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ol>";
    if (m.p.length) {
      h += "<h4>Связанные параметры</h4>" + m.p.map(function (p) {
        var meta = [];
        if (p.range) meta.push("диапазон: " + p.range);
        if (p.units) meta.push("ед.: " + p.units);
        if (p.default !== undefined && p.default !== "") meta.push("по умолчанию: " + p.default);
        return '<div class="p"><b>' + esc(p.name) + "</b>" + (p.display ? " — " + esc(p.display) : "") +
          (p.desc ? "<small>" + esc(p.desc.length > 420 ? p.desc.slice(0, 420) + "…" : p.desc) + "</small>" : "") +
          (p.values ? "<small>значения: " + esc(p.values.length > 260 ? p.values.slice(0, 260) + "…" : p.values) + "</small>" : "") +
          (meta.length ? "<small>" + esc(meta.join(" · ")) + "</small>" : "") + "</div>";
      }).join("");
    }
    if (m.ctx) {
      h += "<h4>Где это в коде (" + esc(W.tag) + ")</h4>";
      h += '<div class="note">' + (m.gh ? '<a href="' + esc(m.gh) + '" target="_blank" rel="noopener">' + esc(m.file) + ":" + m.line + "</a>" : esc(m.file)) +
        (m.func ? " · " + esc(m.func) + "()" : "") + "</div><pre>" + esc(m.ctx) + "</pre>";
    } else if (m.file) {
      h += '<h4>Источник</h4><div class="note">' + esc(m.file) + "</div>";
    }
    var links = [];
    m.d.forEach(function (d) { links.push('<a href="' + esc(d[1]) + '" target="_blank" rel="noopener">' + esc(d[0]) + "</a>"); });
    var qq = encodeURIComponent(m.text.replace(SPEC, "").replace(/\s+/g, " ").trim());
    links.push('<a href="https://discuss.ardupilot.org/search?q=' + qq + '" target="_blank" rel="noopener">Поиск на форуме ArduPilot</a>');
    links.push('<a href="https://ardupilot.org/copter/search.html?q=' + qq + '" target="_blank" rel="noopener">Поиск в документации</a>');
    h += "<h4>Ссылки</h4><div class=\"links\">" + links.join("") + '<button class="cp" data-copy="' + m.id + '">Скопировать ссылку</button></div>';
    return h;
  }
  function render() {
    var toks = qtoks(lastQ);
    var box = $("#results");
    var list = cur.slice(0, shown);
    if (!list.length) {
      box.innerHTML = '<div class="empty"><b>Ничего не найдено</b>Попробуй часть сообщения без чисел, английское слово (compass, baro, ekf) или сбрось фильтры.</div>';
    } else {
      box.innerHTML = list.map(function (r) { return card(r.m, toks); }).join("");
    }
    $("#more").hidden = shown >= cur.length;
    $("#more").textContent = "Показать ещё (" + Math.min(PAGE, cur.length - shown) + " из " + (cur.length - shown) + ")";
  }
  function run(push) {
    var q = $("#q").value;
    lastQ = q;
    $("#q").parentNode.classList.toggle("has", !!q);
    var r = search(q);
    var sub = $("#sub").value, oc = $("#onlyCur").checked, ocp = $("#onlyCopter").checked;
    cur = r.filter(function (x) {
      var m = x.m;
      if (!sgOn[m._sg]) return false;
      if (sub && m.sub !== sub) return false;
      if (oc && !m.cur) return false;
      if (ocp && m.rank >= 2 && !m._exact) return false;
      return true;
    });
    // точное совпадение шаблона не прячем фильтром "Copter"
    if (q.trim().length >= 8) {
      var ex = r.filter(function (x) { return x.s >= 1000; });
      ex.forEach(function (x) { if (cur.indexOf(x) < 0 && sgOn[x.m._sg]) cur.unshift(x); });
    }
    shown = Math.min(PAGE, cur.length);
    var exact = cur.length && cur[0].s >= 1000;
    $("#meta").textContent = q.trim()
      ? (cur.length ? (exact ? "Найдено точное совпадение. Всего результатов: " + cur.length : "Результатов: " + cur.length) : "")
      : "Всего записей: " + cur.length + " — с разбором показаны первыми";
    if (!exact) { /* openId остаётся только если он в выдаче */ }
    if (exact && !openId) openId = cur[0].m.id;
    render();
    if (push !== false) {
      var hs = q.trim() ? "#q=" + encodeURIComponent(q.trim()) : "";
      try { history.replaceState(null, "", location.pathname + location.search + hs); } catch (e) {}
    }
  }
  var timer;
  $("#q").addEventListener("input", function () { clearTimeout(timer); openId = null; timer = setTimeout(function () { run(); }, 90); });
  $("#clear").onclick = function () { $("#q").value = ""; openId = null; run(); $("#q").focus(); };
  $("#more").onclick = function () { shown = Math.min(cur.length, shown + PAGE); render(); };
  $("#results").addEventListener("click", function (e) {
    var cp = e.target.closest("[data-copy]");
    if (cp) {
      var url = location.origin + location.pathname + "#id=" + cp.dataset.copy;
      var done = function () { cp.textContent = "Скопировано ✓"; setTimeout(function () { cp.textContent = "Скопировать ссылку"; }, 1500); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, function () { prompt("Ссылка:", url); });
      else prompt("Ссылка:", url);
      return;
    }
    var h = e.target.closest(".head");
    if (!h) return;
    var id = h.dataset.id, item = h.parentNode, body = $(".body", item);
    var was = item.classList.contains("open");
    document.querySelectorAll(".item.open").forEach(function (i) { i.classList.remove("open"); $(".body", i).innerHTML = ""; $(".head", i).setAttribute("aria-expanded", "false"); });
    if (!was) {
      var m = M.filter(function (x) { return x.id === id; })[0];
      body.innerHTML = detail(m); item.classList.add("open"); openId = id; h.setAttribute("aria-expanded", "true");
    } else openId = null;
  });

  function fromHash() {
    var h = location.hash.slice(1), q = "", id = null;
    h.split("&").forEach(function (p) {
      var kv = p.split("="); if (kv[0] === "q") q = decodeURIComponent(kv.slice(1).join("=")); if (kv[0] === "id") id = kv[1];
    });
    if (id) {
      var m = M.filter(function (x) { return x.id === id; })[0];
      if (m) { $("#q").value = ""; openId = id; run(false); var idx = cur.findIndex(function (r) { return r.m.id === id; });
        if (idx >= shown) { shown = idx + 1; render(); } var el = document.getElementById("i-" + id); if (el) el.scrollIntoView({ block: "center" }); return; }
    }
    $("#q").value = q; run(false);
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();

  /* ---------- codes tab ---------- */
  var eSub = $("#e-sub"), eCode = $("#e-code");
  W.errSub.forEach(function (s) { var o = document.createElement("option"); o.value = s.sub; o.textContent = s.sub + " — " + s.ru; eSub.appendChild(o); });
  for (var c = 0; c <= 6; c++) { var o = document.createElement("option"); o.value = c; o.textContent = c; eCode.appendChild(o); }
  var FS = { 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 17: 1, 20: 1, 23: 1, 26: 1, 27: 1, 29: 1, 31: 1 };
  function errOut() {
    var s = +eSub.value, c = +eCode.value;
    var sub = W.errSub.filter(function (x) { return x.sub === s; })[0];
    var codes = W.errCodes.filter(function (x) { return x.code === c; })[0];
    var h = "<b>" + esc(sub.name) + "</b> (" + esc(sub.ru) + "), код " + c + "<br>";
    if (FS[s]) h += c === 1 ? "→ <b>Failsafe сработал</b>: смотри раздел «Failsafe» и параметры FS_*/BATT_FS_*." : c === 0 ? "→ Failsafe снят (ситуация нормализовалась)." : "→ Нестандартный код для failsafe.";
    else if (c === 0) h += "→ Проблема устранена (ERROR_RESOLVED).";
    else if (codes) h += "→ Возможные значения кода " + c + " (зависят от подсистемы):<br>" + esc(codes.ru);
    h += '<br><span class="note">Имена: ' + esc(codes ? codes.name : "") + "</span>";
    $("#e-out").innerHTML = h;
  }
  eSub.onchange = errOut; eCode.onchange = errOut; errOut();
  $("#t-sub").innerHTML = "<tr><th>Subsys</th><th>Имя</th><th>Что это</th></tr>" + W.errSub.map(function (s) { return "<tr><td>" + s.sub + "</td><td><code>" + esc(s.name) + "</code></td><td>" + esc(s.ru) + "</td></tr>"; }).join("");
  $("#t-code").innerHTML = "<tr><th>ECode</th><th>Имена</th><th>Смысл</th></tr>" + W.errCodes.map(function (s) { return "<tr><td>" + s.code + "</td><td><code>" + esc(s.name) + "</code></td><td>" + esc(s.ru) + "</td></tr>"; }).join("");
  $("#t-int").innerHTML = "<tr><th>Бит</th><th>Маска</th><th>Имя</th><th>Смысл</th></tr>" + W.internal.map(function (s) { return '<tr data-bit="' + s.bit + '"><td>' + s.bit + "</td><td>0x" + (Math.pow(2, s.bit)).toString(16) + "</td><td><code>" + esc(s.name) + "</code></td><td>" + esc(s.ru) + "</td></tr>"; }).join("");
  $("#mask").addEventListener("input", function () {
    var v = this.value.trim(), n = NaN;
    if (/^0x[0-9a-f]+$/i.test(v)) n = parseInt(v, 16); else if (/^\d+$/.test(v)) n = parseInt(v, 10);
    var rows = document.querySelectorAll("#t-int tr[data-bit]"), names = [];
    rows.forEach(function (r) { var on = !isNaN(n) && Math.floor(n / Math.pow(2, +r.dataset.bit)) % 2 === 1; r.classList.toggle("hit", on); if (on) names.push(r.children[2].textContent + " — " + r.children[3].textContent); });
    $("#m-out").innerHTML = isNaN(n) ? (v ? "Не число. Пример: 0x4000" : "") : (names.length ? "<ul>" + names.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" : "Установленных известных битов нет.");
  });

  /* ---------- stats ---------- */
  var nc = M.filter(function (m) { return m.cur; }).length;
  var np = M.filter(function (m) { return /^PreArm|^Arm:/.test(m.text); }).length;
  $("#stats").innerHTML = [[M.length, "сообщений в базе"], [nc, "с готовым разбором"], [np, "PreArm-проверок"], [Object.keys(subs).length, "подсистем"]]
    .map(function (x) { return '<div class="stat"><b>' + x[0] + "</b><span>" + x[1] + "</span></div>"; }).join("");
})();
