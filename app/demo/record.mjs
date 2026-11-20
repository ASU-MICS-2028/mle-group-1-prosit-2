// Records Amina's journey on the live site as a video with short captions (1280x800 after scaling).
// Run: BASE_URL=https://… node app/demo/record.mjs OUT_DIR   → OUT_DIR/<id>.webm, then:
//   ffmpeg -i OUT_DIR/<id>.webm -vf scale=1280:800:flags=lanczos -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "NkwaPay demo.mp4"
import { chromium } from "playwright";

const BASE = process.env.BASE_URL || "http://localhost:8080";
const OUT = process.argv[2] || ".";
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
// Captions are lost on page load, so the first one goes in after the page is ready.
async function type(sel, text) { await page.click(sel); for (const ch of text) { await page.keyboard.type(ch); await wait(90); } }

await page.goto(BASE);
await page.waitForLoadState("networkidle");
await wait(1500);
await caption("1 · Amina wants a small loan. She opens NkwaPay.");
await wait(3200);
await page.click("#start");
await caption("2 · She signs in with her phone number.");
await wait(1200);
await type("#phone", "0712 000 001");
await wait(900);
await page.click("#phone-next");
await page.waitForSelector("#screen-welcome:not([hidden])");
await caption("3 · NkwaPay finds her record: 12 loans, 11 repaid.");
await wait(3600);
await page.click("#welcome-next");
await caption("4 · She picks a 7-day loan and asks for 5,000 KES.");
await wait(1500);
await page.click('.loan-type[data-code="Type_1"]');
await wait(700);
await page.click('.length[data-days="7"]');
await wait(700);
await type("#amount", "5000");
await wait(2200);
await page.click("#check");
await caption("5 · The model scores her application…");
await page.waitForSelector("#decision[data-decision]", { state: "visible" });
await wait(500);
await caption("6 · Approved, with the reasons in plain words.");
await wait(4200);
await caption("7 · “How we decided” shows her risk against our 2.1% line.");
await page.click("#how summary");
await wait(800);
await page.evaluate(() => document.querySelector("#how").scrollIntoView({ behavior: "smooth", block: "center" }));
await wait(5200);
await page.evaluate(() => document.querySelector("#accept").scrollIntoView({ behavior: "smooth", block: "center" }));
await wait(1200);
await page.click("#accept");
await caption("8 · She accepts. Her loan is on its way.");
await wait(4500);

await ctx.close(); // writes the video
await browser.close();
console.log("Recorded to", OUT);
