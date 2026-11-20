// Records a demo journey on the live site as a video with short captions (1280x800 after scaling).
// Run: BASE_URL=https://… node app/demo/record.mjs OUT_DIR [amina|kofi]   → OUT_DIR/<id>.webm, then:
//   ffmpeg -i OUT_DIR/<id>.webm -vf scale=1280:800:flags=lanczos -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "NkwaPay demo.mp4"
import { chromium } from "playwright";

const BASE = process.env.BASE_URL || "http://localhost:8080";
const OUT = process.argv[2] || ".";
const JOURNEY = process.argv[3] || "amina";
const viewport = { width: 1100, height: 688 }; // ffmpeg scales it to 1280x800, so the phone-width column fills more of the frame
const browser = await chromium.launch({ channel: process.env.PW_CHANNEL || "chrome" });
const ctx = await browser.newContext({ viewport, recordVideo: { dir: OUT, size: viewport } });
const page = await ctx.newPage();
const wait = ms => page.waitForTimeout(ms);

// A caption bar at the top of the frame, styled to match the page.
async function caption(text) {
  await page.evaluate(t => {
    let el = document.getElementById("demo-caption");
    if (!el) {
      el = document.createElement("div");
      el.id = "demo-caption";
      Object.assign(el.style, { position: "fixed", top: "18px", right: "24px", zIndex: 99, maxWidth: "270px",
        background: "#222", color: "#fff", font: "500 17px/1.4 Poppins, sans-serif", padding: "12px 18px",
        borderRadius: "12px", borderLeft: "6px solid #EFB05C", boxShadow: "0 8px 24px rgba(0,0,0,.2)", transition: "opacity .3s" });
      document.body.append(el);
    }
    el.style.opacity = 0;
    setTimeout(() => { el.textContent = t; el.style.opacity = 1; }, 150);
  }, text);
  await wait(400);
}
async function type(sel, text) { await page.click(sel); for (const ch of text) { await page.keyboard.type(ch); await wait(90); } }
const decided = () => page.waitForSelector("#decision[data-decision]", { state: "visible" });
const scrollTo = sel => page.evaluate(s => document.querySelector(s).scrollIntoView({ behavior: "smooth", block: "center" }), sel);

async function signIn(phone, intro, found) {
  await page.goto(BASE);
  await page.waitForLoadState("networkidle");
  await wait(1500);
  await caption(intro); // captions are lost on page load, so the first one goes in after the page is ready
  await wait(3200);
  await page.click("#start");
  await caption("2 · Signs in with a phone number.");
  await wait(1200);
  await type("#phone", phone);
  await wait(900);
  await page.click("#phone-next");
  await page.waitForSelector("#screen-welcome:not([hidden])");
  await caption(found);
  await wait(3600);
  await page.click("#welcome-next");
}

const JOURNEYS = {
  async amina() {
    await signIn("0712 000 001", "1 · Amina wants a small loan. She opens NkwaPay.", "3 · NkwaPay finds her record: 12 loans, 11 repaid.");
    await caption("4 · She picks a 7-day loan and asks for 5,000 KES.");
    await wait(1500);
    await page.click('.loan-type[data-code="Type_1"]'); await wait(700);
    await page.click('.length[data-days="7"]'); await wait(700);
    await type("#amount", "5000"); await wait(2200);
    await page.click("#check");
    await caption("5 · The model scores her application…");
    await decided(); await wait(500);
    await caption("6 · Approved, with the reasons in plain words.");
    await wait(4200);
    await caption("7 · “How we decided” shows her risk against our 2.1% line.");
    await page.click("#how summary"); await wait(800);
    await scrollTo("#how"); await wait(5200);
    await scrollTo("#accept"); await wait(1200);
    await page.click("#accept");
    await caption("8 · She accepts. Her loan is on its way.");
    await wait(4500);
  },
  async kofi() {
    await signIn("0244 000 004", "1 · Kofi in Ghana wants a loan. He opens NkwaPay.", "3 · His first loan with us: no record yet.");
    await caption("4 · He asks for a Type 2 loan: 3,000 GHS for 7 days.");
    await wait(1500);
    await page.click('.loan-type[data-code="Type_2"]'); await wait(700);
    await page.click('.length[data-days="7"]'); await wait(700);
    await type("#amount", "3000"); await wait(2000);
    await page.click("#check");
    await caption("5 · The model checks it…");
    await decided(); await wait(500);
    await caption("6 · Declined: about half of Type 2 loans in Ghana aren't repaid.");
    await wait(4800);
    await scrollTo("#change"); await wait(1000);
    await page.click("#change");
    await caption("7 · He tries a Type 3 loan instead, still 3,000 GHS.");
    await wait(1800);
    await page.click('.loan-type[data-code="Type_3"]'); await wait(2000);
    await page.click("#check");
    await caption("8 · Checking again…");
    await decided(); await wait(500);
    await caption("9 · A 300 GHS starter loan: a small first step while we learn Ghana.");
    await wait(5000);
    await scrollTo("#accept"); await wait(1200);
    await page.click("#accept");
    await caption("10 · He accepts. If he repays, he can ask for more next time.");
    await wait(4500);
  },
};

await JOURNEYS[JOURNEY]();
await ctx.close(); // writes the video
await browser.close();
console.log("Recorded", JOURNEY, "to", OUT);
