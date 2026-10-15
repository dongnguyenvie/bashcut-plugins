// The frame: chrome bin/graphic draws around any composition while it renders, so an agent never edits a widget's
// HTML to give a series of cards one look (a backdrop, a section chip, a source credit, a callout line on a word, a
// bigger widget, a slow drift). It is a <style> and a <script> put before </body> for the render only (like the
// stretched data-duration); the script runs after the composition's own, wraps the composition's content in
// #bc-widget and adds its tweens to window.__timelines.main.
//
//   backdrop  "texture" | "paper" | "plain" | "none"  full-frame background behind the widget: the brand background
//             with faint accent glows and a grid ("texture"), with paper grain, fibres and a soft vignette ("paper":
//             kraft with a kraft-brown brand background, notebook with a cream one) or flat ("plain"); "none"
//             (default) keeps the alpha
//   fadeIn    seconds the backdrop takes to fade in (0: there from the first frame)
//   drift     true: the backdrop pans and the widget slides a few pixels over the whole span (too slow for review's
//             frozen-picture check; use float for that)
//   float     true: once the widget has landed (about 1.2 s in) it bobs and breathes until the end, enough for review
//             to count a held card as moving
//   chip      a short label in a pill at the top left ("2/4", "Bước 1"); fades out 0.3 s before the end. When chip
//             or credit pushes a widget with a painted full-frame layer down, a "plain" backdrop fills the top
//   credit    a source line at the top left, above the chip ("© OpenStreetMap contributors"); opt-in, only when
//             the user asks for a credit (nothing sets it by default)
//   callout   {text, at, top}: a plate under the widget that lands at `at` seconds ("@words" in plan); `*word*` is
//             drawn in the accent; top (px) overrides where it sits
//   scale     the widget's size (0.5–2.5) around its own centre, kept 60 px inside the frame
//
// Colours and fonts are the composition's own (--accent, --background, --text, --heading-font, --body-font), so the
// brand applies to the frame too.

/** Bumped when the drawing changes, so graphic plan renders a framed graphic again. */
export const FRAME_VERSION = 3;

const KEYS = new Set(["backdrop", "fadeIn", "drift", "float", "chip", "credit", "callout", "scale"]);
const BACKDROPS = ["texture", "paper", "plain", "none"];

/** A checked frame (keys and types), or null for none; throws Error with the reason. */
export function checkFrame(frame) {
    if (frame === undefined || frame === null) return null;
    if (typeof frame !== "object" || Array.isArray(frame)) throw new Error("frame must be a JSON object");
    const unknown = Object.keys(frame).filter((k) => !KEYS.has(k));
    if (unknown.length) throw new Error(`frame has no ${unknown.join(", ")} (it takes ${[...KEYS].join(", ")})`);
    const out = {};
    for (const [key, value] of Object.entries(frame)) {
        if (value === null || value === undefined || value === false || value === "") continue;
        if (key === "backdrop") {
            if (!BACKDROPS.includes(value)) throw new Error(`frame.backdrop is ${BACKDROPS.map((b) => `"${b}"`).join(", ")}`);
            if (value !== "none") out.backdrop = value;
        } else if (key === "fadeIn" || key === "scale") {
            const number = Number(value);
            if (!Number.isFinite(number)) throw new Error(`frame.${key} must be a number`);
            if (key === "scale" && (number < 0.5 || number > 2.5)) throw new Error("frame.scale is between 0.5 and 2.5");
            if (key === "fadeIn" && number < 0) throw new Error("frame.fadeIn must be 0 or more");
            if (key === "fadeIn" ? number > 0 : number !== 1) out[key] = number;
        } else if (key === "drift" || key === "float") {
            if (value !== true) throw new Error(`frame.${key} is true or left out`);
            out[key] = true;
        } else if (key === "chip" || key === "credit") {
            if (typeof value !== "string") throw new Error(`frame.${key} must be a string`);
            out[key] = value;
        } else if (key === "callout") {
            const callout = typeof value === "string" ? { text: value } : value;
            if (!callout || typeof callout !== "object" || typeof callout.text !== "string" || !callout.text) {
                throw new Error("frame.callout is {text, at, top} (or the text alone)");
            }
            const extra = Object.keys(callout).filter((k) => !["text", "at", "top"].includes(k));
            if (extra.length) throw new Error(`frame.callout has no ${extra.join(", ")} (it takes text, at, top)`);
            for (const k of ["at", "top"]) {
                if (callout[k] !== undefined && typeof callout[k] === "string" && callout[k].startsWith("@")) continue;
                if (callout[k] !== undefined && !Number.isFinite(Number(callout[k]))) throw new Error(`frame.callout.${k} must be a number`);
            }
            out.callout = Object.fromEntries(Object.entries(callout).map(([k, v]) => [k, k === "text" || typeof v === "string" && v.startsWith("@") ? v : Number(v)]));
        }
    }
    return Object.keys(out).length ? out : null;
}

/** Recorded frame + a change: keys of `change` replace, a null removes one; null when nothing is left. */
export function mergeFrame(recorded, change) {
    if (change === undefined) return recorded ?? null;
    if (change === null) return null;
    const merged = { ...(recorded ?? {}) };
    for (const [key, value] of Object.entries(change)) {
        if (value === null) delete merged[key];
        else merged[key] = value;
    }
    return checkFrame(merged);
}

/** The markup put before </body>: the frame's style and the script that builds it. */
export function frameMarkup(frame) {
    // JSON inside a script: "</" would end the script early.
    const data = JSON.stringify(frame).replace(/</g, "\\u003c");
    return `<style>${STYLE}</style>\n<script>(${build.toString()})(${data});</script>\n`;
}

/** index.html with the frame's markup before </body>. */
export function withFrameMarkup(html, frame) {
    const at = html.lastIndexOf("</body>");
    if (at < 0) throw new Error("the page has no </body> for the frame");
    return html.slice(0, at) + frameMarkup(frame) + html.slice(at);
}

const STYLE = `
#bc-backdrop { position: absolute; inset: -160px; background: var(--background, #0E1218); }
#bc-backdrop.texture { background:
  radial-gradient(ellipse at 22% 12%, color-mix(in srgb, var(--accent, #FFB547) 14%, transparent), transparent 52%),
  radial-gradient(ellipse at 85% 92%, color-mix(in srgb, var(--accent, #FFB547) 8%, transparent), transparent 50%),
  repeating-linear-gradient(0deg, color-mix(in srgb, var(--text, #FFFFFF) 4%, transparent) 0 2px, transparent 2px 96px),
  repeating-linear-gradient(90deg, color-mix(in srgb, var(--text, #FFFFFF) 4%, transparent) 0 2px, transparent 2px 96px),
  var(--background, #0E1218); }
#bc-backdrop.paper { background:
  radial-gradient(ellipse at 50% 42%, transparent 50%, color-mix(in srgb, var(--text, #2A1E14) 22%, transparent) 100%),
  url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='320' height='320'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.55 0 0 0 -0.18'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E"),
  url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1000' height='1000'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.012 0.09' numOctaves='3' seed='7' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.22 0 0 0 -0.07'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)'/%3E%3C/svg%3E"),
  var(--background, #C9A877); }
#bc-widget, #bc-float { position: absolute; inset: 0; }
#bc-chip { position: absolute; left: 72px; padding: 6px 26px 8px; border-radius: 999px; white-space: nowrap;
  border: 3px solid var(--accent, #FFB547); color: var(--accent, #FFB547); background: rgba(8, 10, 14, 0.55);
  font-family: var(--heading-font), Arial, sans-serif; font-size: 40px; font-weight: 800; letter-spacing: 0.04em; }
#bc-credit { position: absolute; left: 72px; right: 72px; font-family: var(--body-font), Arial, sans-serif;
  font-size: 30px; font-weight: 500; color: color-mix(in srgb, var(--text, #FFFFFF) 75%, transparent);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6); }
#bc-callout { position: absolute; left: 90px; right: 90px; padding: 26px 40px; border-radius: 30px; text-align: center;
  color: var(--text, #FFFFFF); background: color-mix(in srgb, var(--background, #0E1218) 88%, transparent);
  border: 2px solid var(--accent, #FFB547); box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
  font-family: var(--heading-font), Arial, sans-serif; font-size: 56px; font-weight: 800; line-height: 1.2; }
#bc-callout b { color: var(--accent, #FFB547); font-weight: 900; }
`;

// Runs in the page, after the composition's script: no closure, everything from `frame` and the DOM.
function build(frame) {
    const root = document.querySelector('[data-composition-id="main"]');
    const tl = window.__timelines && window.__timelines.main;
    if (!root || !tl) return;
    const END = Number(root.dataset.duration);
    const W = Number(root.dataset.width) || root.clientWidth;
    const H = Number(root.dataset.height) || root.clientHeight;
    const unit = Math.min(W, H) / 1080;
    const layer = (id, before) => {
        const el = document.createElement("div");
        el.id = id;
        if (before) root.insertBefore(el, root.firstChild);
        else root.appendChild(el);
        return el;
    };

    // The composition's own content, measured before anything is moved (union of its visible boxes that are not
    // full-frame backgrounds).
    const widget = document.createElement("div");
    widget.id = "bc-widget";
    while (root.firstChild) widget.appendChild(root.firstChild);
    root.appendChild(widget);
    const frameBox = root.getBoundingClientRect();
    let box = null;
    const boxes = [];
    // A painted full-frame layer (a map, a photo, a colour card) moves with the widget too.
    let fullFrame = false;
    for (const el of widget.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        if (r.width < 2 || r.height < 2) continue;
        const style = getComputedStyle(el);
        if (style.display === "none") continue;
        if (r.width >= W * 0.95 && r.height >= H * 0.95) {
            const clear = /^rgba\(.*,\s*0\)$|^transparent$/.test(style.backgroundColor);
            if (!clear || style.backgroundImage !== "none" || /^(IMG|CANVAS|VIDEO)$/.test(el.tagName)) fullFrame = true;
            continue;
        }
        const x0 = Math.max(0, r.left - frameBox.left), y0 = Math.max(0, r.top - frameBox.top);
        const x1 = Math.min(W, r.right - frameBox.left), y1 = Math.min(H, r.bottom - frameBox.top);
        if (x1 <= x0 || y1 <= y0) continue;
        boxes.push({ x0, y0, x1, y1 });
        box = box ? { x0: Math.min(box.x0, x0), y0: Math.min(box.y0, y0), x1: Math.max(box.x1, x1), y1: Math.max(box.y1, y1) }
            : { x0, y0, x1, y1 };
    }
    box = box || { x0: 0, y0: 0, x1: W, y1: H };

    // Where the widget's boxes end up after it is scaled and moved by (dx, dy) around (ox, oy).
    let place = { s: 1, ox: 0, oy: 0, dx: 0, dy: 0 };
    const moved = (b) => ({
        x0: place.ox + (b.x0 - place.ox) * place.s + place.dx, y0: place.oy + (b.y0 - place.oy) * place.s + place.dy,
        x1: place.ox + (b.x1 - place.ox) * place.s + place.dx, y1: place.oy + (b.y1 - place.oy) * place.s + place.dy,
    });
    const hits = (r) => boxes.some((b) => { const m = moved(b); return m.x0 < r.x1 && r.x0 < m.x1 && m.y0 < r.y1 && r.y0 < m.y1; });
    let scale = 1;
    if (frame.scale) {
        const margin = 60 * unit;
        const w = box.x1 - box.x0, h = box.y1 - box.y0;
        scale = Math.min(frame.scale, (W - 2 * margin) / w, (H - 2 * margin) / h);
        const cx = (box.x0 + box.x1) / 2, cy = (box.y0 + box.y1) / 2;
        // Centre kept, but moved in when the bigger box would cross the margin.
        const nx = Math.min(Math.max(cx, margin + (w * scale) / 2), W - margin - (w * scale) / 2);
        const ny = Math.min(Math.max(cy, margin + (h * scale) / 2), H - margin - (h * scale) / 2);
        place = { s: scale, ox: cx, oy: cy, dx: nx - cx, dy: ny - cy };
    }

    // Chip and credit sit top left, else top right, else the widget moves down under them (when it has room).
    const top = H > W ? 150 * unit : 60 * unit;
    let corner = null;
    if (frame.chip || frame.credit) {
        const probe = document.createElement("div");
        probe.id = "bc-chip";
        probe.textContent = frame.chip || "";
        root.appendChild(probe);
        const chipW = frame.chip ? probe.offsetWidth : 0, chipH = frame.chip ? probe.offsetHeight : 0;
        probe.remove();
        const y0 = frame.credit ? top - 58 * unit : top - 40 * unit;
        const y1 = frame.chip ? (frame.credit ? top : top - 40 * unit) + chipH : top - 16 * unit;
        const width = Math.max(chipW, frame.credit ? Math.min(W - 144 * unit, frame.credit.length * 15 * unit) : 0);
        const left = { x0: 72 * unit, y0, x1: 72 * unit + width, y1: y1 + 16 * unit };
        const right = { x0: W - 72 * unit - width, y0, x1: W - 72 * unit, y1: y1 + 16 * unit };
        if (!hits(left)) corner = "left";
        else if (!hits(right)) corner = "right";
        else {
            corner = "left";
            const b = moved(box);
            const push = left.y1 - b.y0;
            if (push > 0 && b.y1 + push <= H - 60 * unit) {
                place.dy += push;
                // The pushed full-frame layer would leave a transparent band at the top: fill it with the brand
                // background.
                if (fullFrame && !frame.backdrop) frame.backdrop = "plain";
            }
        }
    }
    if (place.s !== 1 || place.dx || place.dy) {
        widget.style.transformOrigin = `${place.ox}px ${place.oy}px`;
        gsap.set(widget, { scale: place.s, x: place.dx, y: place.dy });
    }
    // Float: an inner layer bobs and breathes around the widget's centre once it has landed, so a held card keeps
    // moving (review samples twice a second on a 24×24 grid; the drift alone stays under its threshold).
    if (frame.float) {
        const inner = document.createElement("div");
        inner.id = "bc-float";
        while (widget.firstChild) inner.appendChild(widget.firstChild);
        widget.appendChild(inner);
        inner.style.transformOrigin = `${(box.x0 + box.x1) / 2}px ${(box.y0 + box.y1) / 2}px`;
        // Bob and breathe on different periods, so one is moving while the other turns.
        const start = Math.min(1.2, END / 3);
        for (const [vars, half] of [[{ y: -18 * unit }, 1.3], [{ scale: 1.035 }, 0.85]]) {
            const repeat = Math.floor((END - start - 0.2) / half) - 1;
            if (repeat >= 0) tl.to(inner, { ...vars, duration: half, ease: "sine.inOut", yoyo: true, repeat }, start);
        }
    }
    box = moved(box);
    const pin = (el) => {
        if (corner === "right") { el.style.left = "auto"; el.style.right = `${72 * unit}px`; el.style.textAlign = "right"; }
    };

    if (frame.backdrop) {
        const back = layer("bc-backdrop", true);
        if (frame.backdrop !== "plain") back.className = frame.backdrop;
        if (frame.fadeIn) tl.fromTo(back, { opacity: 0 }, { opacity: 1, duration: frame.fadeIn, ease: "none" }, 0);
        if (frame.drift) tl.fromTo(back, { x: 0, y: 0 }, { x: -60 * unit, y: 45 * unit, duration: END, ease: "none" }, 0);
    }
    if (frame.drift) {
        const x = Number(gsap.getProperty(widget, "x")) || 0;
        tl.fromTo(widget, { x }, { x: x + 16 * unit, duration: END, ease: "none" }, 0);
    }
    if (frame.credit) {
        const credit = layer("bc-credit");
        credit.textContent = frame.credit;
        credit.style.top = `${top - 58 * unit}px`;
        pin(credit);
        tl.fromTo(credit, { opacity: 0 }, { opacity: 1, duration: 0.4 }, 0.2);
    }
    if (frame.chip) {
        const chip = layer("bc-chip");
        chip.textContent = frame.chip;
        chip.style.top = `${frame.credit ? top : top - 40 * unit}px`;
        pin(chip);
        tl.fromTo(chip, { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }, 0.25);
        tl.to(chip, { opacity: 0, duration: 0.3 }, Math.max(0.7, END - 0.4));
    }
    if (frame.callout) {
        const callout = layer("bc-callout");
        const escape = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        callout.innerHTML = escape(frame.callout.text).replace(/\*([^*]+)\*/g, "<b>$1</b>");
        // Under the widget when it fits above the bottom fifth (captions and the platform's buttons), else over it,
        // else as low as it can go.
        const height = callout.offsetHeight;
        const below = box.y1 + 40 * unit;
        const above = box.y0 - 40 * unit - height;
        const lowest = H * 0.78 - height;
        const y = Number.isFinite(frame.callout.top) ? frame.callout.top
            : below <= lowest ? below : above >= top + 80 * unit ? above : lowest;
        callout.style.top = `${y}px`;
        const at = Number.isFinite(frame.callout.at) ? frame.callout.at : Math.min(1, END / 3);
        tl.fromTo(callout, { opacity: 0, y: 50, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out" },
            Math.max(0.2, at - 0.4));
        tl.to(callout, { opacity: 0, y: -30, duration: 0.3, ease: "power2.in" }, Math.max(at + 0.4, END - 0.3));
    }
    tl.seek(0);
}
