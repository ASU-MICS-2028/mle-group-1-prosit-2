// NkwaPay demo: one page, one screen at a time. Browser back goes back one screen.
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const fmt = n => new Intl.NumberFormat("en").format(n);
const pct = p => `${(p * 100).toFixed(1)}%`;
const longDate = iso => new Date(iso + "T00:00:00").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "long" });
const FEE = { KES: 0.02, GHS: 0.03 };
const QUICK = { KES: [1000, 3000, 5000], GHS: [300, 1000, 3000] };
const MIN_CHECK_MS = 1400; // long enough to read "Checking…", short enough not to annoy

const state = { customer: null, type: null, days: 7, result: null, busy: false };

function show(name, push = true) {
  $$(".screen").forEach(s => (s.hidden = s.dataset.screen !== name));
  const inner = name !== "start";
  $(".top").hidden = !inner;
  document.body.classList.toggle("on-start", !inner);
  const step = Number($(`[data-screen="${name}"]`).dataset.step || 0);
  $$(".steps li").forEach((li, i) => li.classList.toggle("on", i < step));
  if (push) history.pushState({ screen: name }, "", `#${name}`);
  window.scrollTo(0, 0);
  $(`[data-screen="${name}"] h2`)?.focus({ preventScroll: true });
}

window.addEventListener("popstate", e => {
  const s = e.state?.screen || "start";
  // Screens that need data we no longer have fall back to the phone screen.
  if (["welcome", "loan"].includes(s) && !state.customer) return show("phone", false);
  if (["decision", "done"].includes(s) && !state.result) return show(state.customer ? "loan" : "phone", false);
  if (s === "checking") return history.back();
  show(s, false);
});

$(".back").addEventListener("click", () => history.back());
$("#start").addEventListener("click", () => show("phone"));
$("#restart").addEventListener("click", () => {
  Object.assign(state, { customer: null, type: null, days: 7, result: null });
  $("#phone").value = ""; $$(".demo-chip").forEach(c => c.classList.remove("on"));
  show("start");
});

// 2 · phone
$$(".demo-chip").forEach(chip => chip.addEventListener("click", () => {
  $("#phone").value = chip.dataset.phone.replace(/(\d{4})(\d{3})(\d{3})/, "$1 $2 $3");
  $$(".demo-chip").forEach(c => c.classList.toggle("on", c === chip));
  $("#phone-error").hidden = true;
  $("#phone-next").focus();
}));

$("#phone-form").addEventListener("submit", async e => {
  e.preventDefault();
  const err = $("#phone-error"), raw = $("#phone").value.trim();
  err.hidden = true;
  if (raw.replace(/\D/g, "").length < 9) { err.textContent = "Please enter your full phone number."; err.hidden = false; return; }
  const btn = $("#phone-next"); btn.disabled = true;
  try {
    const r = await fetch(`/api/customers/${encodeURIComponent(raw)}`);
    if (r.status === 404) { err.textContent = "We couldn't find that number. Try one of the demo customers below."; err.hidden = false; return; }
    if (!r.ok) throw new Error();
    state.customer = await r.json();
    renderWelcome(); show("welcome");
  } catch { err.textContent = "Something went wrong on our side. Please try again."; err.hidden = false; }
  finally { btn.disabled = false; }
});

// 3 · welcome back
function renderWelcome() {
  const c = state.customer;
  $("#avatar").textContent = c.name[0];
  $("#welcome-name").textContent = c.first_loan ? `Welcome to NkwaPay, ${c.name}` : `Welcome back, ${c.name}`;
  $("#welcome-country").textContent = c.first_loan ? `${c.country} · we're glad to have you.` : `${c.country} · here's your record with us.`;
  $("#summary").innerHTML = "";
  c.summary.forEach(line => {
    const m = line.match(/^(\d+)\s+(.*)$/), d = document.createElement("div");
    d.className = "stat";
    d.innerHTML = m ? `<b>${m[1]}</b><span></span>` : `<span></span>`;
    d.querySelector("span").textContent = m ? m[2] : line;
    $("#summary").append(d);
  });
}
$("#welcome-next").addEventListener("click", () => { renderLoan(); show("loan"); });

// 4 · loan
function renderLoan() {
  const c = state.customer;
  state.type = state.type && c.loan_types.some(t => t.code === state.type) ? state.type : c.loan_types[0].code;
  $("#types").innerHTML = "";
  c.loan_types.forEach(t => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "loan-type"; b.dataset.code = t.code; b.setAttribute("role", "radio");
    b.innerHTML = "<div><b></b><br><span></span></div>";
    b.querySelector("b").textContent = t.label; b.querySelector("span").textContent = t.note;
    b.addEventListener("click", () => { state.type = t.code; syncLoan(); });
    $("#types").append(b);
  });
  $("#cur").textContent = c.currency;
  $("#quick").innerHTML = "";
  QUICK[c.currency].forEach(v => {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = `${fmt(v)} ${c.currency}`;
    b.addEventListener("click", () => { $("#amount").value = fmt(v); syncLoan(); });
    $("#quick").append(b);
  });
  $("#amount-error").hidden = true;
  syncLoan();
}
function amount() { const v = Number($("#amount").value.replace(/[,\s]/g, "")); return Number.isFinite(v) ? v : NaN; }
function syncLoan() {
  $$(".loan-type").forEach(b => b.setAttribute("aria-checked", b.dataset.code === state.type));
  $$(".length").forEach(b => b.setAttribute("aria-checked", Number(b.dataset.days) === state.days));
  const a = amount(), cur = state.customer.currency, due = new Date(Date.now() + state.days * 864e5);
  $("#preview").textContent = a > 0 && a <= 1e6
    ? `You'd repay ${fmt(Math.round(a * (1 + FEE[cur])))} ${cur} by ${due.toLocaleDateString("en-GB", { day: "numeric", month: "long" })} (fee ${FEE[cur] * 100}%).` : "";
}
$$(".length").forEach(b => b.addEventListener("click", () => { state.days = Number(b.dataset.days); syncLoan(); }));
$("#amount").addEventListener("input", () => { $("#amount-error").hidden = true; syncLoan(); });
$("#amount").addEventListener("keydown", e => { if (e.key === "Enter") $("#check").click(); });

$("#check").addEventListener("click", async () => {
  if (state.busy) return;
  const a = amount(), err = $("#amount-error"), cur = state.customer.currency;
  if (!(a > 0)) { err.textContent = "Please enter how much you'd like to borrow."; err.hidden = false; return; }
  if (a > 1e6) { err.textContent = `That's more than we lend. Please enter up to ${fmt(1e6)} ${cur}.`; err.hidden = false; return; }
  state.busy = true; $("#check").disabled = true;
  $("#decision").removeAttribute("data-decision");
  show("checking");
  try {
    const [r] = await Promise.all([
      fetch("/api/apply", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: state.customer.phone, loan_type: state.type, duration: state.days, amount: a }) }),
      new Promise(res => setTimeout(res, MIN_CHECK_MS)),
    ]);
    if (!r.ok) throw new Error();
    state.result = await r.json();
    renderDecision();
    history.replaceState({ screen: "decision" }, "", "#decision"); // back from the decision goes to the loan screen
    show("decision", false);
  } catch {
    history.back();
    err.textContent = "We couldn't check your loan just now. Please try again."; err.hidden = false;
  } finally { state.busy = false; $("#check").disabled = false; }
});

// 6 · decision
const TITLES = {
  approve: ["Approved", "You're approved"],
  starter: ["Starter loan", "Let's start small"],
  decline: ["Not this time", "We can't offer this loan right now"],
};
function renderDecision() {
  const r = state.result, c = state.customer, d = r.decision;
  const box = $("#decision");
  box.dataset.decision = d;
  $("#verdict-kicker").textContent = TITLES[d][0];
  $("#verdict-title").textContent = TITLES[d][1];
  $("#verdict-amount").textContent = r.offer ? `${fmt(r.offer)} ${r.currency}` : "";
  $("#verdict-amount").hidden = !r.offer;
  $("#verdict-sub").textContent = r.offer ? `Repay ${fmt(r.repay)} ${r.currency} by ${longDate(r.due_date)}` : `You asked for ${fmt(r.requested)} ${r.currency}.`;

  const cap = $("#cap-note");
  cap.hidden = true;
  if (d === "approve" && r.offer < r.requested) { cap.textContent = `We can offer up to ${fmt(r.offer)} ${r.currency}, less than the ${fmt(r.requested)} you asked for.`; cap.hidden = false; }
  if (d === "starter") { cap.textContent = `A starter loan is a small first step. You asked for ${fmt(r.requested)} ${r.currency}.`; cap.hidden = false; }

  $("#reasons").innerHTML = "";
  r.reasons.forEach(t => { const li = document.createElement("li"); li.textContent = t; $("#reasons").append(li); });

  $("#next-step").textContent = {
    approve: "Accept the loan below. Repaying on time keeps your limit growing.",
    starter: "Accept the starter loan and repay it on time. Next time you can ask for more.",
    decline: "This isn't a judgement of you as a person. You can change your request, for example a shorter loan, or come back when your record changes.",
  }[d];

  const how = $("#how-body");
  how.innerHTML = "";
  const p = t => { const el = document.createElement("p"); el.textContent = t; how.append(el); };
  if (r.cutoff !== null) {
    p(`Our model looked at your record with us and this loan, and put your chance of not repaying at ${pct(r.probability)}.`);
    p(`We lend when that chance is ${pct(r.cutoff)} or lower: below that line, the fees from loans that are repaid cover the money lost on the ones that aren't.`);
    const max = Math.max(r.probability, r.cutoff) * 1.6, m = document.createElement("div");
    m.className = "meter";
    m.innerHTML = `<i class="line" style="left:${(r.cutoff / max) * 100}%"></i><small style="left:${(r.cutoff / max) * 100}%">our line ${pct(r.cutoff)}</small>` +
      `<i class="you" style="left:${(r.probability / max) * 100}%"></i><small style="left:${(r.probability / max) * 100}%;top:-26px;color:var(--maroon)">you ${pct(r.probability)}</small>`;
    how.prepend(m);
    if (d === "starter") p("You're above the line, but this is your first loan and your risk is low enough for a small starter loan instead of a no.");
    if (d === "decline" && r.probability <= r.cutoff) p("Your score was under the line, but a safety rule overrides it: we don't lend to someone who hasn't repaid two or more earlier loans.");
  } else {
    p(`In Ghana we don't score each person yet: we have no repayment records there. Instead we use how often this kind of loan has not been repaid in Ghana: ${pct(r.probability)}.`);
  }
  r.notes.forEach(n => p(n.replace(/\s*\((ADR|learnings)[^)]*\)\.?/g, ".").replace(/\.\.$/, ".")));
  $("#how").open = false;

  $("#accept").hidden = d === "decline";
  $("#accept").textContent = d === "starter" ? "Accept starter loan" : "Accept loan";
}
$("#change").addEventListener("click", () => history.back());
$("#accept").addEventListener("click", () => {
  const r = state.result;
  $("#done-amount").textContent = `${fmt(r.offer)} ${r.currency}`;
  $("#done-repay").textContent = `Repay ${fmt(r.repay)} ${r.currency} by ${longDate(r.due_date)}.`;
  show("done");
});

history.replaceState({ screen: "start" }, "", location.pathname);
show("start", false);
