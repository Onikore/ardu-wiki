(function () {
  "use strict";
  var W = window.WIKI, M = W.msgs;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- тема, вкладки ---------- */
  var root = document.documentElement, th = store.get("theme");
  if (th) root.setAttribute("data-theme", th);
  $("#theme").onclick = function () {
    var dark = root.getAttribute("data-theme") === "dark" || (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    var nt = dark ? "light" : "dark"; root.setAttribute("data-theme", nt); store.set("theme", nt);
  };
  $("#ver").textContent = W.tag; $("#a-tag").textContent = W.tag; $("#f-tag").textContent = W.tag;
  function showTab(n) {
    document.querySelectorAll(".tab").forEach(function (b) { b.classList.toggle("on", b.dataset.tab === n); });
    document.querySelectorAll(".pane").forEach(function (p) { p.classList.toggle("on", p.id === "tab-" + n); });
  }
  document.querySelectorAll(".tab").forEach(function (b) { b.onclick = function () { showTab(b.dataset.tab); }; });
  $("#home").onclick = function (e) { e.preventDefault(); showTab("search"); $("#q").focus(); };

  /* ---------- вердикты ---------- */
  var V = {
    block: { icon: "⛔", name: "Взлёт заблокирован", sub: "Дрон не даст запустить моторы, пока причина не устранена." },
    land: { icon: "🛬", name: "Сажай дрон", sub: "Сообщение в полёте: дрон в опасном состоянии." },
    warn: { icon: "⚠️", name: "Будь внимателен", sub: "Лететь можно, но что-то работает не так." },
    info: { icon: "ℹ️", name: "Можно не обращать внимания", sub: "Информационное сообщение." }
  };
  var VORDER = { block: 0, land: 1, warn: 2, info: 3 };

  /* ---------- индекс ---------- */
  var SPEC = /%[-+ #0-9.]*(?:l|h|ll|z)?[a-zA-Z]/g;
  function tplRe(t) {
    var lit = 0, parts = t.split(SPEC).map(function (p) { lit += p.trim().length; return p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\s+/g, "\\s+"); });
    var re = null; try { re = new RegExp(parts.join(".+?"), "i"); } catch (e) {}
    return { re: re, lit: lit };
  }
  M.forEach(function (m) {
    var o = m.ops;
    m._v = o ? o.v : "info";
    m._title = o ? o.title : (m.t || "Служебное сообщение");
    m._t = m.text.toLowerCase();
    m._ti = (m._title + " " + (m.t || "")).toLowerCase();
    var causes = o ? o.causes.map(function (c) { return c.c + " " + c.chk + " " + c.fix; }).join(" ") : "";
    m._h = (m.text + " " + m._ti + " " + (o ? o.what : "") + " " + causes + " " + m.c + " " + m.p.map(function (p) { return p.name; }).join(" ")).toLowerCase();
    m._w = {}; m._t.split(/[^a-z0-9_]+/).forEach(function (w) { if (w) m._w[w] = 1; });
    var tr = tplRe(m.text); m._re = tr.lit >= 10 ? tr.re : null; m._lit = tr.lit;
  });

  var STOP = { "не": 1, "и": 1, "в": 1, "на": 1, "при": 1, "как": 1, "что": 1, "это": 1, "у": 1, "с": 1, "по": 1, "из": 1, "я": 1, "ошибка": 1, "пишет": 1, "the": 1, "a": 1, "is": 1 };
  var SYN = [["компас", ["compass", "mag"]], ["магнит", ["mag", "compass"]], ["гпс", ["gps"]], ["спутник", ["gps", "sats"]], ["батаре", ["batt", "battery"]],
    ["аккум", ["batt", "battery"]], ["напряж", ["volt"]], ["пульт", ["rc", "radio"]], ["приемник", ["rc", "radio"]], ["приёмник", ["rc", "radio"]], ["арм", ["arm", "prearm"]],
    ["запуск", ["arm", "prearm"]], ["калибр", ["calib", "cal"]], ["вибрац", ["vibe", "vibration"]], ["барометр", ["baro"]], ["высот", ["alt", "baro"]], ["акселер", ["accel"]],
    ["гироскоп", ["gyro"]], ["мотор", ["motor"]], ["режим", ["mode"]], ["дальномер", ["rangefinder", "rngfnd"]], ["геозон", ["fence"]], ["забор", ["fence"]],
    ["миссия", ["mission"]], ["карт", ["sd", "card", "log"]], ["лог", ["log"]], ["потер", ["lost", "failsafe"]], ["связь", ["failsafe", "radio", "gcs"]],
    ["газ", ["throttle"]], ["регулятор", ["esc"]], ["навигац", ["ekf", "ahrs"]], ["экф", ["ekf"]], ["курс", ["yaw"]], ["краш", ["crash"]], ["упал", ["crash"]]];
  function expand(t) { var o = [t]; SYN.forEach(function (s) { if (t.indexOf(s[0]) === 0) o = o.concat(s[1]); }); return o; }
  function lev1(a, b) {
    if (Math.abs(a.length - b.length) > 1) return false;
    var i = 0, j = 0, d = 0;
    while (i < a.length && j < b.length) { if (a[i] === b[j]) { i++; j++; continue; } if (++d > 1) return false; if (a.length > b.length) i++; else if (a.length < b.length) j++; else { i++; j++; } }
    return d + (a.length - i) + (b.length - j) <= 1;
  }
  function toks(q) { return q.toLowerCase().split(/[\s,;:()"'\[\]=]+/).filter(function (t) { return t && !STOP[t]; }); }
  function search(q) {
    var ql = q.trim().toLowerCase(), tk = toks(q), res = [], part = [];
    if (!tk.length) return M.map(function (m) { return { m: m, s: 0 }; });
    var alts = tk.map(expand);
    M.forEach(function (m) {
      var s = 0, hit = 0;
      if (m._re && ql.length >= 8 && m._re.test(q)) s += 1000 + m._lit;
      alts.forEach(function (al) {
        var best = 0;
        al.forEach(function (a, j) {
          var w = 0;
          if (m._t.indexOf(a) >= 0) w = m._w[a] ? 15 : 10;
          else if (m._ti.indexOf(a) >= 0) w = 7;
          else if (m._h.indexOf(a) >= 0) w = 2;
          else if (a.length >= 5 && /^[a-z0-9_]+$/.test(a)) { for (var k in m._w) if (k[0] === a[0] && lev1(a, k)) { w = 4; break; } }
          if (j > 0) w *= 0.8;
          if (w > best) best = w;
        });
        if (best) { hit++; s += best; }
      });
      if (!hit) return;
      s += (m.cur ? 3 : 0) - m.rank * 2;
      (hit === tk.length || (tk.length >= 3 && hit / tk.length >= 0.6) ? res : part).push({ m: m, s: s });
    });
    if (!res.length) res = part;
    return res.sort(function (a, b) { return b.s - a.s; });
  }

  /* ---------- фильтр по вердикту ---------- */
  var vOn = { block: true, land: true, warn: true, info: true };
  ["block", "land", "warn", "info"].forEach(function (k) {
    var b = document.createElement("button");
    b.className = "vf on v-" + k; b.innerHTML = '<span class="dot"></span>' + esc(V[k].name);
    b.onclick = function () { vOn[k] = !vOn[k]; b.classList.toggle("on", vOn[k]); run(); };
    $("#vfilter").appendChild(b);
  });

  /* ---------- отрисовка ---------- */
  var cur = [], shown = 0, PAGE = 25, openId = null, lastQ = "";
  function hl(text, q) {
    var s = esc(text);
    var all = []; toks(q).forEach(function (t) { all = all.concat(expand(t)); });
    all.forEach(function (t) {
      if (t.length < 3) return;
      s = s.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")(?![^<]*>)(?![^&]*;)", "ig"), "<mark>$1</mark>");
    });
    return s;
  }
  function card(m) {
    var open = m.id === openId;
    return '<div class="item v-' + m._v + (open ? " open" : "") + '" id="i-' + m.id + '">' +
      '<button class="head" data-id="' + m.id + '"><div class="htitle">' + esc(m._title) + "</div>" +
      '<div class="msg">' + hl(m.text, lastQ) + "</div>" +
      '<span class="vchip">' + V[m._v].icon + " " + esc(V[m._v].name) + "</span></button>" +
      '<div class="body">' + (open ? detail(m) : "") + "</div></div>";
  }
  function detail(m) {
    var o = m.ops, v = V[m._v], h = "";
    h += '<div class="verdict"><span class="vi">' + v.icon + '</span><div><b>' + esc(v.name) + "</b><span>" + esc(o ? o.what : "Служебное сообщение прошивки. Обычно ничего делать не нужно.") + "</span></div></div>";
    if (o && o.causes.length) {
      h += '<div class="ch">Возможные причины — от частой к редкой</div>';
      o.causes.forEach(function (c, i) {
        h += '<details class="cause"' + (i === 0 ? " open" : "") + '><summary><span class="n">' + (i + 1) + "</span><span>" + esc(c.c) + "</span></summary><div class=\"cb\">" +
          (c.chk && c.chk !== "—" ? '<div class="step"><span class="lbl">Как проверить</span>' + esc(c.chk) + "</div>" : "") +
          '<div class="step fix"><span class="lbl">Как исправить</span>' + esc(c.fix) + "</div></div></details>";
      });
    } else if (o) {
      h += '<div class="nocause">Делать ничего не нужно.</div>';
    }
    h += tech(m);
    return h;
  }
  function tech(m) {
    var c = "";
    if (m.cur) {
      c += "<h5>Причина по коду " + esc(W.tag) + "</h5><div>" + esc(m.c) + "</div>";
      var steps = m.f.concat(m.more || []);
      if (steps.length) c += "<h5>Технические шаги</h5><ol>" + steps.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ol>";
      if (m.diag && m.diag.length) c += "<h5>Диагностика</h5><ul>" + m.diag.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ul>";
    }
    c += "<h5>Где в коде</h5>";
    if (m.cond) c += '<div class="cond"><code>' + esc(m.cond) + "</code></div>";
    c += '<div class="note">' + (m.gh ? '<a href="' + esc(m.gh) + '" target="_blank" rel="noopener">' + esc(m.file) + ":" + m.line + "</a>" : esc(m.file)) + (m.func ? " · " + esc(m.func) + "()" : "") + "</div>";
    if (m.via) c += '<div class="note">' + esc(m.via) + "</div>";
    if (m.chk && m.chk.bit) c += '<div class="note">Группа проверки «' + esc(m.chk.ru) + "» — бит " + m.chk.bit + " в ARMING_CHECK.</div>";
    if (m.ctx) c += "<pre>" + esc(m.ctx) + "</pre>";
    if (m.p.length) {
      c += "<h5>Параметры</h5>" + m.p.map(function (p) {
        return '<div class="p"><b>' + esc(p.name) + "</b>" + (p.display ? " — " + esc(p.display) : "") +
          (p.desc ? "<small>" + esc(p.desc.length > 300 ? p.desc.slice(0, 300) + "…" : p.desc) + "</small>" : "") +
          (p.values ? "<small>значения: " + esc(p.values.length > 220 ? p.values.slice(0, 220) + "…" : p.values) + "</small>" : "") +
          (p.range ? "<small>диапазон: " + esc(p.range) + (p.units ? " " + esc(p.units) : "") + "</small>" : "") + "</div>";
      }).join("");
    }
    var links = m.d.map(function (d) { return '<a href="' + esc(d[1]) + '" target="_blank" rel="noopener">' + esc(d[0]) + "</a>"; });
    links.push('<a href="https://discuss.ardupilot.org/search?q=' + encodeURIComponent(m.text.replace(SPEC, "").replace(/\s+/g, " ").trim()) + '" target="_blank" rel="noopener">Форум ArduPilot</a>');
    c += '<div class="links">' + links.join("") + '<button class="cp" data-copy="' + m.id + '">Скопировать ссылку</button></div>';
    return '<details class="code"><summary>Код и технические подробности</summary><div class="tc">' + c + "</div></details>";
  }
  function render() {
    var box = $("#results"), list = cur.slice(0, shown);
    box.innerHTML = list.length ? list.map(function (r) { return card(r.m); }).join("")
      : '<div class="empty"><b>Ничего не найдено</b>Попробуй вставить часть сообщения без чисел или слово: компас, GPS, батарея.</div>';
    $("#more").hidden = shown >= cur.length;
    $("#more").textContent = "Показать ещё (" + (cur.length - shown) + ")";
  }
  function run(push) {
    var q = $("#q").value; lastQ = q;
    $("#q").parentNode.classList.toggle("has", !!q);
    var r = search(q), hasQ = !!q.trim();
    cur = r.filter(function (x) {
      if (!vOn[x.m._v]) return false;
      if (x.m.rank >= 2 && x.s < 1000) return false;     // другие типы аппаратов — только при точном совпадении
      if (!hasQ && !x.m.cur) return false;               // без запроса — только разобранные
      return true;
    });
    if (!hasQ) cur.sort(function (a, b) { return VORDER[a.m._v] - VORDER[b.m._v] || a.m.rank - b.m.rank || a.m._title.localeCompare(b.m._title); });
    shown = Math.min(PAGE, cur.length);
    var exact = cur.length && cur[0].s >= 1000;
    if (exact && !openId) openId = cur[0].m.id;
    $("#meta").textContent = hasQ ? (exact ? "Найдено точное совпадение" : "Найдено: " + cur.length) : "Все сообщения Copter: " + cur.length + ". Вставь текст ошибки в поиск.";
    render();
    if (push !== false) { try { history.replaceState(null, "", location.pathname + location.search + (q.trim() ? "#q=" + encodeURIComponent(q.trim()) : "")); } catch (e) {} }
  }
  var timer;
  $("#q").addEventListener("input", function () { clearTimeout(timer); openId = null; timer = setTimeout(run, 90); });
  $("#clear").onclick = function () { $("#q").value = ""; openId = null; run(); $("#q").focus(); };
  $("#more").onclick = function () { shown = Math.min(cur.length, shown + PAGE); render(); };
  $("#results").addEventListener("click", function (e) {
    var cp = e.target.closest("[data-copy]");
    if (cp) {
      var url = location.origin + location.pathname + "#id=" + cp.dataset.copy;
      var ok = function () { cp.textContent = "Скопировано ✓"; setTimeout(function () { cp.textContent = "Скопировать ссылку"; }, 1500); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(ok, function () { prompt("Ссылка:", url); }); else prompt("Ссылка:", url);
      return;
    }
    var h = e.target.closest(".head"); if (!h) return;
    var item = h.parentNode, was = item.classList.contains("open");
    document.querySelectorAll(".item.open").forEach(function (i) { i.classList.remove("open"); $(".body", i).innerHTML = ""; });
    if (!was) { var m = M.filter(function (x) { return x.id === h.dataset.id; })[0]; $(".body", item).innerHTML = detail(m); item.classList.add("open"); openId = m.id; }
    else openId = null;
  });
  function fromHash() {
    var q = "", id = null;
    location.hash.slice(1).split("&").forEach(function (p) { var kv = p.split("="); if (kv[0] === "q") q = decodeURIComponent(kv.slice(1).join("=")); if (kv[0] === "id") id = kv[1]; });
    var m = id && M.filter(function (x) { return x.id === id; })[0];
    if (m) { $("#q").value = m.text; openId = id; run(false); var el = document.getElementById("i-" + id); if (el) el.scrollIntoView({ block: "center" }); return; }
    $("#q").value = q; run(false);
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();

  /* ---------- коды лога ---------- */
  var eSub = $("#e-sub"), eCode = $("#e-code");
  W.errSub.forEach(function (s) { var o = document.createElement("option"); o.value = s.sub; o.textContent = s.sub + " — " + s.ru; eSub.appendChild(o); });
  for (var c = 0; c <= 6; c++) { var o = document.createElement("option"); o.value = c; o.textContent = c; eCode.appendChild(o); }
  var FS = { 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 17: 1, 20: 1, 23: 1, 26: 1, 27: 1, 29: 1, 31: 1 };
  function errOut() {
    var s = +eSub.value, k = +eCode.value, sub = W.errSub.filter(function (x) { return x.sub === s; })[0], code = W.errCodes.filter(function (x) { return x.code === k; })[0];
    var t = "<b>" + esc(sub.ru) + "</b> (" + esc(sub.name) + "), код " + k + ": ";
    if (FS[s]) t += k === 1 ? "защита (failsafe) сработала." : k === 0 ? "защита снята, всё в норме." : "нестандартный код.";
    else if (k === 0) t += "проблема устранена.";
    else t += code ? esc(code.ru) : "";
    $("#e-out").innerHTML = t;
  }
  eSub.onchange = errOut; eCode.onchange = errOut; errOut();
  $("#t-sub").innerHTML = "<tr><th>Subsys</th><th>Имя</th><th>Что это</th></tr>" + W.errSub.map(function (s) { return "<tr><td>" + s.sub + "</td><td><code>" + esc(s.name) + "</code></td><td>" + esc(s.ru) + "</td></tr>"; }).join("");
  $("#t-code").innerHTML = "<tr><th>ECode</th><th>Имена</th><th>Смысл</th></tr>" + W.errCodes.map(function (s) { return "<tr><td>" + s.code + "</td><td><code>" + esc(s.name) + "</code></td><td>" + esc(s.ru) + "</td></tr>"; }).join("");
  $("#t-int").innerHTML = "<tr><th>Бит</th><th>Маска</th><th>Имя</th><th>Смысл</th></tr>" + W.internal.map(function (s) { return '<tr data-bit="' + s.bit + '"><td>' + s.bit + "</td><td>0x" + Math.pow(2, s.bit).toString(16) + "</td><td><code>" + esc(s.name) + "</code></td><td>" + esc(s.ru) + "</td></tr>"; }).join("");
  $("#mask").addEventListener("input", function () {
    var v = this.value.trim(), n = /^0x[0-9a-f]+$/i.test(v) ? parseInt(v, 16) : (/^\d+$/.test(v) ? parseInt(v, 10) : NaN), names = [];
    document.querySelectorAll("#t-int tr[data-bit]").forEach(function (r) { var on = !isNaN(n) && Math.floor(n / Math.pow(2, +r.dataset.bit)) % 2 === 1; r.classList.toggle("hit", on); if (on) names.push(r.children[3].textContent + " (" + r.children[2].textContent + ")"); });
    $("#m-out").innerHTML = isNaN(n) ? (v ? "Не число. Пример: 0x4000" : "") : (names.length ? "<ul>" + names.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" : "Известных битов нет.");
  });

  /* ---------- статистика ---------- */
  var nv = M.filter(function (m) { return m.cur; }).length, nb = M.filter(function (m) { return m._v === "block"; }).length;
  $("#stats").innerHTML = [[M.length, "сообщений в базе"], [nv, "с причинами и решениями"], [nb, "блокируют взлёт"]]
    .map(function (x) { return '<div class="stat"><b>' + x[0] + "</b><span>" + x[1] + "</span></div>"; }).join("");
})();
