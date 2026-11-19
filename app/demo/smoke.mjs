// Browser check of every demo journey. Run: node app/demo/smoke.mjs (BASE_URL defaults to http://localhost:8080). Exit 1 on any failure.
import { chromium } from "playwright";

const BASE = process.env.BASE_URL || "http://localhost:8080";
const browser = await chromium.launch({ channel: process.env.PW_CHANNEL || "chrome" });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
let applies = 0;
page.on("request", r => { if (r.url().includes("/api/apply")) applies++; });
const ok = (cond, msg) => { if (!cond) { console.error("FAIL:", msg); process.exitCode = 1; } };
const visible = sel => page.locator(sel).isVisible();

async function signIn(phone, { chip = true } = {}) {
  await page.goto(BASE);
  await page.click("#start");
  if (chip) await page.click(`.demo-chip[data-phone="${phone}"]`);
  else await page.fill("#phone", phone);
  await page.click("#phone-next");
  await page.waitForSelector("#screen-welcome:not([hidden]), #phone-error:not([hidden])", { timeout: 10000 });
}

async function ask(type, days, amount) {
  await page.click("#welcome-next");
  await page.click(`.loan-type[data-code="${type}"]`);
  await page.click(`.length[data-days="${days}"]`);
  await page.fill("#amount", String(amount));
  await page.click("#check");
  await page.waitForSelector("#decision[data-decision]", { state: "visible", timeout: 15000 });
  return page.getAttribute("#decision", "data-decision");
}

// Amina: approved, accepts, sees the done screen
await signIn("0712000001");
ok((await page.textContent("#welcome-name")).includes("Amina"), "Amina welcome");
ok(await ask("Type_1", 7, 5000) === "approve", "Amina approved");
ok((await page.locator("#reasons li").count()) > 0, "Amina has reasons");
await page.goBack();
ok(await visible("#screen-loan"), "back from decision returns to the loan screen");
await page.goForward().catch(() => {});
await page.goto(BASE); await signIn("0712000001"); await ask("Type_1", 7, 5000);
await page.click("#accept");
ok(await visible("#screen-done"), "done screen after accept");

// Brian: starter; Wanjiru: decline with reasons; Kofi Type 2: decline
await signIn("0712000002"); ok(await ask("Type_1", 7, 3000) === "starter", "Brian starter");
await signIn("0712000003"); ok(await ask("Type_1", 7, 3000) === "decline", "Wanjiru declined");
ok((await page.locator("#reasons li").count()) > 0, "Wanjiru has reasons");
await signIn("0244000004"); ok(await ask("Type_2", 7, 1000) === "decline", "Kofi Type 2 declined");

// Typed number with country code finds Amina; unknown number shows a message and the chips
await signIn("+254 712 000 001", { chip: false });
ok(await visible("#screen-welcome"), "typed +254 number finds Amina");
await signIn("0799 999 999", { chip: false });
ok((await page.textContent("#phone-error")).includes("couldn't find"), "unknown number message");
ok(await page.locator(".demo-chip").first().isVisible(), "chips still shown");

// Amount 0: inline error, no request
await signIn("0712000001");
await page.click("#welcome-next");
const before = applies;
await page.fill("#amount", "0"); await page.click("#check");
ok(await page.locator("#amount-error").isVisible(), "amount 0 shows an error");
ok(applies === before, "amount 0 sends no request");

// Double click sends one request
await page.fill("#amount", "4000");
const b2 = applies;
await page.dblclick("#check");
await page.waitForSelector("#decision[data-decision]", { state: "visible", timeout: 15000 });
ok(applies === b2 + 1, `double click sent ${applies - b2} requests`);

await browser.close();
if (!process.exitCode) console.log("Smoke passed");
