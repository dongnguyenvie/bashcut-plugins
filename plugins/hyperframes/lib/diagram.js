// Diagram layout and motion shared by the flow-diagram, mind-map, isometric-system and big-canvas examples: the
// agent passes nodes, edges and steps as JSON, never coordinates; this script lays them out for the canvas the page
// renders at (9:16 or 16:9) and builds the GSAP timeline. graphics.render copies it next to the page (like GSAP), and
// the tests load it in Node to check the layout (no two node boxes overlap).
//
// data: {title?, nodes: [{id, label, icon?, group?}], edges: [{from, to, label?}], root? (mind-map centre),
//        direction? ("lr" | "tb", flow; auto by default), steps: [{at, focus: [ids], reveal: [ids], note?}]}
//   at: seconds from the graphic's start (bin/graphic --steps-from voice|sections fills it from the voice lines or
//   section markers); a step without a number is spread evenly over the graphic.
//   A node in no step's reveal is there from the start; reveal brings it in on that step; focus lights it up (the
//   rest dims) until the next step; packets run along the edges that touch a focused node.
// big-canvas data adds stops: [{at, focus: id | [x, y, w, h] (0–1 of the canvas), zoom?, note?}], summary?.
(function (root) {
    "use strict";

    // MARK: text measure (an estimate the layout and the tests share; the page shrinks a label that still overflows)

    function charWidth(cp, ch) {
        if (cp >= 0x2e80) return 1.0;
        if (ch === " ") return 0.3;
        if (/[il.,:;'|!]/.test(ch)) return 0.3;
        if (/[fjrt()[\]\-]/.test(ch)) return 0.42;
        if (/[MW]/.test(ch)) return 0.92;
        if (/[mw]/.test(ch)) return 0.84;
        if (/[0-9]/.test(ch)) return 0.6;
        if (ch !== ch.toLowerCase()) return 0.7;
        return 0.58;
    }

    function textWidth(text, size) {
        let sum = 0;
        for (const ch of String(text)) sum += charWidth(ch.codePointAt(0), ch);
        return sum * size * 1.04;
    }

    /** Greedy word wrap into lines no wider than `width`, or null when a word or the line count does not fit. */
    function wrap(text, width, size, maxLines) {
        const words = String(text).trim().split(/\s+/).filter(Boolean);
        if (!words.length) return [""];
        const lines = [];
        let line = "";
        for (const word of words) {
            if (textWidth(word, size) > width) return null;
            const next = line ? `${line} ${word}` : word;
            if (textWidth(next, size) <= width) line = next;
            else {
                lines.push(line);
                line = word;
            }
        }
        lines.push(line);
        return lines.length <= maxLines ? lines : null;
    }

    /** The largest font from maxFont down to minFont at which `text` fits w × h, with its lines. */
    function fitLabel(text, w, h, maxFont, minFont) {
        for (let font = maxFont; font >= minFont; font *= 0.93) {
            const lines = wrap(text, w, font, Math.max(1, Math.min(3, Math.floor(h / (font * 1.18)))));
            if (lines) return { font, lines, width: Math.max(...lines.map((l) => textWidth(l, font))) };
        }
        const font = minFont;
        const perLine = Math.max(4, Math.floor(w / (font * 0.6)));
        const flat = String(text).trim();
        const lines = [];
        for (let i = 0; i < flat.length && lines.length < 3; i += perLine) lines.push(flat.slice(i, i + perLine));
        return { font, lines, width: Math.min(w, Math.max(...lines.map((l) => textWidth(l, font)))) };
    }

    // MARK: graph helpers

    function readData(data) {
        const nodes = (data.nodes ?? []).map((n, i) => ({ ...n, id: String(n.id ?? `n${i}`), label: String(n.label ?? n.id ?? "") }));
        const ids = new Set(nodes.map((n) => n.id));
        const edges = (data.edges ?? []).filter((e) => ids.has(String(e.from)) && ids.has(String(e.to)) && String(e.from) !== String(e.to))
            .map((e) => ({ ...e, from: String(e.from), to: String(e.to) }));
        return { nodes, edges };
    }

    /** Layer of each node: longest path from the sources (Kahn's order; a cycle is broken at its first node). */
    function layering(nodes, edges) {
        const out = new Map(nodes.map((n) => [n.id, []]));
        const indeg = new Map(nodes.map((n) => [n.id, 0]));
        for (const e of edges) {
            out.get(e.from).push(e.to);
            indeg.set(e.to, indeg.get(e.to) + 1);
        }
        const layer = new Map(nodes.map((n) => [n.id, 0]));
        const done = new Set();
        const queue = nodes.filter((n) => indeg.get(n.id) === 0).map((n) => n.id);
        while (done.size < nodes.length) {
            if (!queue.length) queue.push(nodes.find((n) => !done.has(n.id)).id);
            const id = queue.shift();
            if (done.has(id)) continue;
            done.add(id);
            for (const to of out.get(id)) {
                if (done.has(to)) continue;
                layer.set(to, Math.max(layer.get(to), layer.get(id) + 1));
                indeg.set(to, indeg.get(to) - 1);
                if (indeg.get(to) === 0) queue.push(to);
            }
        }
        const count = Math.max(...layer.values()) + 1;
        const rows = Array.from({ length: count }, () => []);
        for (const n of nodes) rows[layer.get(n.id)].push(n.id);
        // Order inside a layer by the mean position of the nodes it links to in the layers before (two sweeps).
        const pos = new Map();
        const place = () => rows.forEach((row) => row.forEach((id, i) => pos.set(id, (i + 0.5) / row.length)));
        place();
        const near = new Map(nodes.map((n) => [n.id, []]));
        for (const e of edges) {
            near.get(e.to).push(e.from);
            near.get(e.from).push(e.to);
        }
        for (let sweep = 0; sweep < 2; sweep += 1) {
            for (let r = 1; r < rows.length; r += 1) {
                const mean = (id) => {
                    const linked = near.get(id).filter((o) => layer.get(o) < r);
                    return linked.length ? linked.reduce((s, o) => s + pos.get(o), 0) / linked.length : pos.get(id);
                };
                rows[r] = rows[r].map((id, i) => ({ id, key: mean(id), i })).sort((a, b) => a.key - b.key || a.i - b.i).map((x) => x.id);
                place();
            }
        }
        return { rows, layer };
    }

    function overlaps(a, b, gap = 0) {
        return Math.abs(a.x - b.x) < (a.w + b.w) / 2 + gap - 0.01 && Math.abs(a.y - b.y) < (a.h + b.h) / 2 + gap - 0.01;
    }

    /** Pairs of node boxes that overlap (the tests' check). */
    function overlapping(nodes, gap = 0) {
        const pairs = [];
        for (let i = 0; i < nodes.length; i += 1) {
            for (let j = i + 1; j < nodes.length; j += 1) if (overlaps(nodes[i], nodes[j], gap)) pairs.push([nodes[i].id, nodes[j].id]);
        }
        return pairs;
    }

    function clampInto(n, area) {
        n.x = Math.min(Math.max(n.x, area.x + n.w / 2), area.x + area.w - n.w / 2);
        n.y = Math.min(Math.max(n.y, area.y + n.h / 2), area.y + area.h - n.h / 2);
    }

    /** Pushes overlapping boxes apart inside `area`; shrinks every box (and its font) a little when that is not enough. */
    function separate(nodes, area, gap) {
        for (let round = 0; round < 30; round += 1) {
            for (let iter = 0; iter < 150; iter += 1) {
                let moved = false;
                for (let i = 0; i < nodes.length; i += 1) {
                    for (let j = i + 1; j < nodes.length; j += 1) {
                        const a = nodes[i];
                        const b = nodes[j];
                        if (!overlaps(a, b, gap)) continue;
                        moved = true;
                        const dx = b.x - a.x;
                        const dy = b.y - a.y;
                        const ox = (a.w + b.w) / 2 + gap - Math.abs(dx);
                        const oy = (a.h + b.h) / 2 + gap - Math.abs(dy);
                        if (ox < oy) {
                            const s = dx > 0 || (dx === 0 && i < j) ? 1 : -1;
                            a.x -= (s * ox) / 2;
                            b.x += (s * ox) / 2;
                        } else {
                            const s = dy > 0 || (dy === 0 && i < j) ? 1 : -1;
                            a.y -= (s * oy) / 2;
                            b.y += (s * oy) / 2;
                        }
                    }
                }
                nodes.forEach((n) => clampInto(n, area));
                if (!moved) break;
            }
            if (!overlapping(nodes, gap / 2).length) return nodes;
            for (const n of nodes) {
                for (const key of ["w", "h", "font", "dy", "size", "labelW", "labelH"]) if (n[key] !== undefined) n[key] *= 0.92;
            }
        }
        return nodes;
    }

    /** A node box sized to its label inside at most bw × bh. */
    function sizeNode(n, bw, bh, u, { maxFont = 46, minFont = 22, pad = 22, icon = true } = {}) {
        const iconW = icon && n.icon ? maxFont * u * 1.35 : 0;
        const fit = fitLabel(n.label, bw - pad * 2 * u - iconW, bh - pad * 1.6 * u, maxFont * u, minFont * u);
        const w = Math.min(bw, Math.max(fit.width + pad * 2 * u + iconW, Math.min(bw, 150 * u)));
        const h = Math.min(bh, Math.max(fit.lines.length * fit.font * 1.18 + pad * 1.6 * u, 84 * u));
        return { ...n, w, h, font: fit.font, lines: fit.lines };
    }

    // MARK: layouts (all return {nodes: [{id, x, y, w, h, font, lines, …}], edges, unit, …}; x, y are centres)

    function flowLayout(data, area, unit, direction) {
        const { nodes, edges } = readData(data);
        if (!nodes.length) return { nodes: [], edges: [], unit, direction: "lr" };
        const { rows, layer } = layering(nodes, edges);
        const byId = new Map(nodes.map((n) => [n.id, n]));
        const widest = Math.max(...rows.map((r) => r.length));
        const build = (dir) => {
            const lr = dir === "lr";
            const main = lr ? area.w : area.h;
            const cross = lr ? area.h : area.w;
            const cellMain = main / rows.length;
            const cellCross = cross / widest;
            const bw = Math.min(lr ? cellMain * 0.74 : cellCross * 0.86, 470 * unit);
            const bh = Math.min(lr ? cellCross * 0.76 : cellMain * 0.6, 230 * unit);
            const out = [];
            rows.forEach((row, r) => {
                row.forEach((id, i) => {
                    const n = sizeNode(byId.get(id), bw, bh, unit);
                    const along = (r + 0.5) * cellMain;
                    const across = (i + 0.5 + (widest - row.length) / 2) * cellCross;
                    n.x = area.x + (lr ? along : across);
                    n.y = area.y + (lr ? across : along);
                    n.depth = layer.get(id);
                    out.push(n);
                });
            });
            return { nodes: out, edges, unit, direction: dir, minFont: Math.min(...out.map((n) => n.font)) };
        };
        let chosen;
        if (direction === "lr" || direction === "tb") chosen = build(direction);
        else {
            const lr = build("lr");
            const tb = build("tb");
            const prefer = area.w >= area.h ? lr : tb;
            const other = prefer === lr ? tb : lr;
            chosen = other.minFont > prefer.minFont * 1.15 ? other : prefer;
        }
        separate(chosen.nodes, area, 12 * unit);
        return chosen;
    }

    /** Tree from the root (data.root, else the first node nothing points to), children in edge order. */
    function tree(nodes, edges, rootId) {
        const ids = nodes.map((n) => n.id);
        const pointed = new Set(edges.map((e) => e.to));
        const top = rootId && ids.includes(String(rootId)) ? String(rootId) : ids.find((id) => !pointed.has(id)) ?? ids[0];
        const near = new Map(ids.map((id) => [id, []]));
        for (const e of edges) {
            near.get(e.from).push(e.to);
            near.get(e.to).push(e.from);
        }
        const parent = new Map([[top, null]]);
        const children = new Map(ids.map((id) => [id, []]));
        const order = [top];
        for (let k = 0; k < order.length; k += 1) {
            for (const next of near.get(order[k])) {
                if (parent.has(next)) continue;
                parent.set(next, order[k]);
                children.get(order[k]).push(next);
                order.push(next);
            }
        }
        // Nodes no edge reaches hang off the root.
        for (const id of ids) {
            if (parent.has(id)) continue;
            parent.set(id, top);
            children.get(top).push(id);
            order.push(id);
        }
        const depth = new Map([[top, 0]]);
        for (const id of order.slice(1)) depth.set(id, depth.get(parent.get(id)) + 1);
        return { top, parent, children, depth, order };
    }

    function mindLayout(data, area, unit) {
        const { nodes, edges } = readData(data);
        if (!nodes.length) return { nodes: [], edges: [], unit };
        const t = tree(nodes, edges, data.root);
        const byId = new Map(nodes.map((n) => [n.id, n]));
        const weight = new Map();
        const weigh = (id) => {
            const kids = t.children.get(id);
            const w = kids.length ? kids.reduce((s, k) => s + weigh(k), 0) : 1;
            weight.set(id, w);
            return w;
        };
        weigh(t.top);
        const D = Math.max(...t.depth.values());
        const landscape = area.w >= area.h;
        const cx = area.x + area.w / 2;
        const cy = area.y + area.h / 2;
        const size = (d) => (d === 0 ? [Math.min(area.w * 0.46, 480 * unit), 190 * unit, 54] : d === 1
            ? [Math.min(area.w * 0.4, 400 * unit), 150 * unit, 44] : [Math.min(area.w * 0.36, 340 * unit), 124 * unit, 38]);
        const out = new Map();
        const rootSize = size(0);
        out.set(t.top, { ...sizeNode(byId.get(t.top), rootSize[0], rootSize[1], unit, { maxFont: rootSize[2] }), x: cx, y: cy, depth: 0 });
        const leafSize = size(Math.max(1, D));
        const rx = area.w / 2 - leafSize[0] / 2;
        const ry = area.h / 2 - leafSize[1] / 2;
        const radius = (d) => (D <= 1 ? 1 : 0.6 + (0.4 * (d - 1)) / (D - 1));
        const visit = (id, from, span) => {
            let start = from;
            for (const kid of t.children.get(id)) {
                const share = (span * weight.get(kid)) / weight.get(id);
                const angle = start + share / 2;
                const d = t.depth.get(kid);
                const [bw, bh, font] = size(d);
                const n = sizeNode(byId.get(kid), bw, bh, unit, { maxFont: font });
                n.x = cx + rx * radius(d) * Math.cos(angle);
                n.y = cy + ry * radius(d) * Math.sin(angle);
                n.depth = d;
                n.angle = angle;
                out.set(kid, n);
                visit(kid, start, share);
                start += share;
            }
        };
        const kids = t.children.get(t.top).length;
        // Branches face the long sides first: left and right on 16:9, up and down on 9:16.
        const start = (landscape ? -Math.PI / 2 : -Math.PI) + (kids === 1 ? Math.PI / 2 : 0);
        visit(t.top, start, Math.PI * 2);
        const placed = t.order.map((id) => out.get(id));
        separate(placed, area, 22 * unit);
        const tight = edges.filter((e) => t.parent.get(e.to) === e.from || t.parent.get(e.from) === e.to);
        const treeEdges = t.order.slice(1).map((id) => {
            const given = tight.find((e) => (e.from === t.parent.get(id) && e.to === id) || (e.to === t.parent.get(id) && e.from === id));
            return { from: t.parent.get(id), to: id, label: given?.label };
        });
        return { nodes: placed, edges: treeEdges, unit, tree: t };
    }

    /** Blocks on an isometric grid: layer → one grid axis, place in the layer → the other. */
    function isoLayout(data, area, unit) {
        const { nodes, edges } = readData(data);
        if (!nodes.length) return { nodes: [], edges: [], unit };
        const { rows, layer } = layering(nodes, edges);
        const byId = new Map(nodes.map((n) => [n.id, n]));
        const s = 0.4;
        const lift = 0.3;
        const labelRoom = 120 * unit;
        // Two ways onto the grid: layers along a grid axis (the diagram runs down-right) or along both (layers run
        // straight down, the nodes of a layer side by side); the one that gives larger blocks wins.
        const fit = (mapping) => {
            const grid = new Map();
            rows.forEach((row, r) => row.forEach((id, i) => {
                const j = i - (row.length - 1) / 2;
                grid.set(id, mapping === "axis" ? { gx: r, gy: j } : { gx: r + j * 0.75, gy: r - j * 0.75 });
            }));
            const keys = [...grid.values()];
            const spanX = Math.max(...keys.map((g) => g.gx - g.gy)) - Math.min(...keys.map((g) => g.gx - g.gy)) + 2 * s;
            const spanY = (Math.max(...keys.map((g) => g.gx + g.gy)) - Math.min(...keys.map((g) => g.gx + g.gy))) * 0.5 + s + lift * s;
            const c = Math.min(area.w / (spanX + 0.9), (area.h - labelRoom - 40 * unit) / Math.max(spanY, 0.5), 420 * unit);
            return { grid, keys, c };
        };
        const axis = fit("axis");
        const down = fit("down");
        const { grid, keys, c } = (area.w >= area.h ? down.c > axis.c * 1.2 : down.c * 1.2 >= axis.c) ? down : axis;
        const midX = (Math.max(...keys.map((g) => g.gx - g.gy)) + Math.min(...keys.map((g) => g.gx - g.gy))) / 2;
        const midY = (Math.max(...keys.map((g) => g.gx + g.gy)) + Math.min(...keys.map((g) => g.gx + g.gy))) / 4;
        const out = nodes.map((node) => {
            const g = grid.get(node.id);
            const px = area.x + area.w / 2 + (g.gx - g.gy - midX) * c;
            const py = area.y + (area.h - labelRoom) / 2 + ((g.gx + g.gy) * 0.5 - midY) * c;
            const blockW = 2 * s * c;
            const blockH = s * c + lift * s * c;
            const label = fitLabel(node.label, Math.max(blockW * 1.25, 230 * unit), 96 * unit, 36 * unit, 20 * unit);
            const labelW = label.width + 28 * unit;
            const labelH = label.lines.length * label.font * 1.18 + 18 * unit;
            const w = Math.max(blockW, labelW);
            const h = blockH + 14 * unit + labelH;
            const top = py - (s * c) / 2;
            return {
                ...node, x: px, y: top + h / 2, w, h, font: label.font, lines: label.lines, depth: layer.get(node.id),
                gx: g.gx, gy: g.gy, size: s * c, dy: (s * c) / 2 - h / 2, labelW, labelH, lift,
            };
        });
        separate(out, area, 10 * unit);
        return { nodes: out, edges, unit, cell: c };
    }

    // MARK: drawing

    function rng(seed) {
        let a = 0;
        for (const ch of String(seed)) a = (Math.imul(a ^ ch.codePointAt(0), 2654435761) >>> 0);
        return () => {
            a = (a + 0x6d2b79f5) >>> 0;
            let t = a;
            t = Math.imul(t ^ (t >>> 15), t | 1);
            t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }

    /** Where the line from a box's centre towards (tx, ty) leaves the box. */
    function boxEdge(n, tx, ty) {
        const dx = tx - n.x;
        const dy = ty - n.y;
        if (!dx && !dy) return { x: n.x, y: n.y };
        const k = Math.min(Math.abs(n.w / 2 / (dx || 1e-9)), Math.abs(n.h / 2 / (dy || 1e-9)));
        return { x: n.x + dx * k, y: n.y + dy * k };
    }

    function edgePath(a, b, kind, direction, sketch, seed, unit) {
        if (kind === "iso") {
            const c = a.cell;
            const ax = a.x;
            const ay = a.y + a.dy;
            const bx = b.x;
            const by = b.y + b.dy;
            const dx = (bx - ax) / c;
            const dy = (by - ay) / c;
            const alpha = (dx + 2 * dy) / 2;
            const mx = ax + alpha * c;
            const my = ay + alpha * c * 0.5;
            return `M${ax},${ay} L${mx},${my} L${bx},${by}`;
        }
        let p;
        let q;
        let c1;
        let c2;
        if (kind === "flow") {
            const lr = direction === "lr";
            const forward = lr ? b.x > a.x + 1 : b.y > a.y + 1;
            if (forward) {
                p = lr ? { x: a.x + a.w / 2, y: a.y } : { x: a.x, y: a.y + a.h / 2 };
                q = lr ? { x: b.x - b.w / 2, y: b.y } : { x: b.x, y: b.y - b.h / 2 };
                const m = lr ? (q.x - p.x) / 2 : (q.y - p.y) / 2;
                c1 = lr ? { x: p.x + m, y: p.y } : { x: p.x, y: p.y + m };
                c2 = lr ? { x: q.x - m, y: q.y } : { x: q.x, y: q.y - m };
            }
        }
        if (!p) {
            p = boxEdge(a, b.x, b.y);
            q = boxEdge(b, a.x, a.y);
            const mx = (p.x + q.x) / 2;
            const my = (p.y + q.y) / 2;
            const bend = kind === "mind" ? 0.12 : 0.18;
            c1 = { x: mx - (q.y - p.y) * bend, y: my + (q.x - p.x) * bend };
            c2 = c1;
        }
        if (!sketch) return `M${p.x},${p.y} C${c1.x},${c1.y} ${c2.x},${c2.y} ${q.x},${q.y}`;
        const r = rng(seed);
        const j = () => (r() - 0.5) * 14 * unit;
        return `M${p.x + j()},${p.y + j()} C${c1.x + j() * 2},${c1.y + j() * 2} ${c2.x + j() * 2},${c2.y + j() * 2} ${q.x},${q.y}`;
    }

    /** A rounded-rectangle outline (wobbly when sketched) for draw-on. */
    function boxPath(n, sketch, seed, unit) {
        const x0 = n.x - n.w / 2;
        const y0 = n.y - n.h / 2;
        const x1 = n.x + n.w / 2;
        const y1 = n.y + n.h / 2;
        const r = Math.min(26 * unit, n.h / 3);
        if (!sketch) {
            return `M${x0 + r},${y0} H${x1 - r} Q${x1},${y0} ${x1},${y0 + r} V${y1 - r} Q${x1},${y1} ${x1 - r},${y1} H${x0 + r} Q${x0},${y1} ${x0},${y1 - r} V${y0 + r} Q${x0},${y0} ${x0 + r},${y0} Z`;
        }
        const g = rng(seed);
        const j = () => (g() - 0.5) * 8 * unit;
        return `M${x0 + r + j()},${y0 + j()} L${x1 - r + j()},${y0 + j()} Q${x1 + j()},${y0 + j()} ${x1 + j()},${y0 + r} L${x1 + j()},${y1 - r + j()} Q${x1},${y1} ${x1 - r + j()},${y1 + j()} L${x0 + r + j()},${y1 + j()} Q${x0},${y1} ${x0 + j()},${y1 - r} L${x0 + j()},${y0 + r + j()} Q${x0},${y0} ${x0 + r + 10 * unit},${y0 + j()}`;
    }

    const SVG = "http://www.w3.org/2000/svg";

    function el(tag, attrs, parent, ns) {
        const node = ns ? document.createElementNS(SVG, tag) : document.createElement(tag);
        for (const [k, v] of Object.entries(attrs ?? {})) {
            if (k === "text") node.textContent = v;
            else if (k === "style") node.style.cssText = v;
            else node.setAttribute(k, v);
        }
        if (parent) parent.appendChild(node);
        return node;
    }

    const CSS = `
.dg-layer { position: absolute; left: 0; top: 0; overflow: visible; pointer-events: none; }
.dg-title { position: absolute; left: 0; right: 0; text-align: center; font-family: var(--heading-font), Arial, sans-serif;
  font-weight: 800; color: var(--text); letter-spacing: -0.01em; text-shadow: 0 3px 18px rgba(0,0,0,.45); }
.dg-node { position: absolute; display: flex; align-items: center; justify-content: center; gap: .35em; opacity: 0; }
.dg-plate { position: absolute; inset: 0; border-radius: var(--dg-radius); background: color-mix(in srgb, var(--background) 92%, transparent);
  box-shadow: 0 14px 34px rgba(0,0,0,.35); border: var(--dg-border) solid color-mix(in srgb, var(--text) 22%, transparent); }
.dg-sketch .dg-plate { border-color: transparent; box-shadow: none; }
.dg-ring { position: absolute; inset: calc(var(--dg-border) * -1.5); border-radius: var(--dg-radius); border: calc(var(--dg-border) * 2.2) solid var(--accent);
  box-shadow: 0 0 calc(var(--dg-border) * 9) color-mix(in srgb, var(--accent) 55%, transparent); opacity: 0; }
.dg-label { position: relative; font-family: var(--heading-font), Arial, sans-serif; font-weight: 700; color: var(--text); line-height: 1.18;
  text-align: center; white-space: nowrap; }
.dg-icon { position: relative; line-height: 1; }
.dg-icon img { width: 1.25em; height: 1.25em; object-fit: contain; display: block; }
.dg-edge-label { position: absolute; transform: translate(-50%, -50%); padding: .18em .6em; border-radius: 99px; white-space: nowrap;
  background: color-mix(in srgb, var(--background) 88%, transparent); color: var(--text); font-family: var(--body-font), Arial, sans-serif;
  font-weight: 600; opacity: 0; }
.dg-packet { position: absolute; left: 0; top: 0; border-radius: 50%; background: var(--accent); opacity: 0;
  box-shadow: 0 0 calc(var(--dg-border) * 5) var(--accent); offset-rotate: 0deg; }
.dg-note { position: absolute; padding: .7em .9em; background: #FFE27A; color: #2B2412; border-radius: .2em; font-family: var(--hand-font);
  font-weight: 700; line-height: 1.2; box-shadow: 0 .4em 1em rgba(0,0,0,.28); opacity: 0; text-align: left; }
.dg-sketch .dg-label, .dg-sketch .dg-title { font-family: var(--hand-font); }
`;

    function brand(v) {
        const look = document.documentElement.style;
        for (const key of ["accent", "background", "text", "secondary"]) if (v[key]) look.setProperty(`--${key}`, v[key]);
        const faces = document.createElement("style");
        for (const [key, slot] of [["headingFont", "--heading-font"], ["bodyFont", "--body-font"]]) {
            const name = String(v[key] ?? "").trim();
            if (!name) continue;
            const file = /\.(ttf|otf|woff2?)$/i.test(name);
            if (!name.startsWith("System-")) faces.textContent += `@font-face { font-family: "${key}"; src: ${file ? `url("${name}")` : `local("${name}")`}; }`;
            const family = name.startsWith("System-") ? "system-ui" : file ? `"${key}"` : `"${name}", "${key}"`;
            look.setProperty(slot, family);
            if (key === "headingFont") look.setProperty("--hand-font", family);
        }
        faces.textContent += CSS;
        document.head.appendChild(faces);
    }

    /** The canvas the page renders at: the root's data-width/height (bin/graphic sets them to the project's). */
    function canvas(rootEl) {
        const W = Number(rootEl.dataset.width) || 1080;
        const H = Number(rootEl.dataset.height) || 1920;
        for (const node of [document.documentElement, document.body, rootEl]) {
            node.style.width = `${W}px`;
            node.style.height = `${H}px`;
        }
        return { W, H, unit: Math.min(W, H) / 1080, END: Number(rootEl.dataset.duration) || 6 };
    }

    /** The area a diagram fills: inside 72 px, under the title, above a phone's caption band on 9:16. */
    function areaFor(W, H, unit, hasTitle) {
        const portrait = H > W;
        const top = (hasTitle ? (portrait ? 0.15 : 0.17) : portrait ? 0.1 : 0.08) * H;
        const bottom = (portrait ? 0.76 : 0.92) * H;
        return { x: 72 * unit, y: top, w: W - 144 * unit, h: bottom - top };
    }

    /** Steps with times: a number is kept; the others are spread evenly from 0.9 s to the end. */
    function timedSteps(steps, END) {
        const list = (steps ?? []).map((s) => ({ ...s, focus: [].concat(s.focus ?? []).map(String), reveal: [].concat(s.reveal ?? []).map(String) }));
        const free = list.filter((s) => typeof s.at !== "number" || !Number.isFinite(s.at));
        const span = Math.max(0.5, END - 1.6);
        free.forEach((s, i) => (s.at = Math.round((0.9 + (span * i) / Math.max(1, free.length)) * 100) / 100));
        return list.sort((a, b) => a.at - b.at);
    }

    function fromToState(tl, target, a, b, at, duration, ease) {
        tl.fromTo(target, a, { ...b, duration, ease: ease ?? "power2.out", immediateRender: false }, at);
    }

    /**
     * Builds a flow, mind or iso diagram on `rootEl` into the paused timeline `tl`. v: the page's variables (data JSON,
     * title, sketch, packets, brand ids).
     */
    function mount(tl, v, kind, rootEl) {
        brand(v);
        const { W, H, unit, END } = canvas(rootEl);
        const data = typeof v.data === "string" ? JSON.parse(v.data || "{}") : v.data ?? {};
        const title = data.title ?? v.title ?? "";
        const sketch = Boolean(data.sketch ?? v.sketch);
        if (sketch) rootEl.classList.add("dg-sketch");
        rootEl.style.setProperty("--dg-border", `${3 * unit}px`);
        rootEl.style.setProperty("--dg-radius", `${(kind === "mind" ? 40 : 22) * unit}px`);
        const area = areaFor(W, H, unit, Boolean(title));
        const layout = kind === "flow" ? flowLayout(data, area, unit, data.direction) : kind === "mind" ? mindLayout(data, area, unit) : isoLayout(data, area, unit);
        const byId = new Map(layout.nodes.map((n) => [n.id, n]));
        if (kind === "iso") layout.nodes.forEach((n) => (n.cell = layout.cell));
        const steps = timedSteps(data.steps, END);
        const groups = [...new Set(layout.nodes.map((n) => n.group).filter(Boolean))];
        const tint = (n) => {
            const g = groups.indexOf(n.group);
            return g < 0 ? null : ["var(--secondary)", "#4FC3F7", "#81C784", "#BA68C8", "#FF8A65"][g % 6];
        };

        if (title) {
            const t = el("div", { class: "dg-title", text: title }, rootEl);
            const portrait = H > W;
            t.style.top = `${(portrait ? 0.075 : 0.05) * H}px`;
            t.style.fontSize = `${Math.min(64 * unit, ((W - 160 * unit) / Math.max(1, textWidth(title, 1))))}px`;
            t.style.padding = `0 ${72 * unit}px`;
            fromToState(tl, t, { opacity: 0, y: 30 * unit }, { opacity: 1, y: 0 }, 0.15, 0.5, "power3.out");
        }

        // Edges under the nodes (iso blocks hide the ends of their connectors).
        const svg = el("svg", { class: "dg-layer", width: W, height: H, viewBox: `0 0 ${W} ${H}` }, rootEl, true);
        const edgeLayer = el("g", {}, svg, true);
        const blockLayer = el("g", {}, svg, true);
        const htmlLayer = el("div", { class: "dg-layer", style: `width:${W}px;height:${H}px` }, rootEl);
        const overSvg = el("svg", { class: "dg-layer", width: W, height: H, viewBox: `0 0 ${W} ${H}` }, rootEl, true);

        // When each node shows: from the start unless a step reveals it.
        const revealAt = new Map();
        for (const s of steps) for (const id of s.reveal) if (byId.has(id) && !revealAt.has(id)) revealAt.set(id, s.at);
        const initial = layout.nodes.filter((n) => !revealAt.has(n.id));
        const order = kind === "mind" ? initial.sort((a, b) => a.depth - b.depth) : initial.sort((a, b) => a.depth - b.depth || a.y - b.y);
        const stagger = Math.min(0.2, 1.3 / Math.max(1, order.length));
        order.forEach((n, i) => revealAt.set(n.id, 0.35 + i * stagger));
        const shown = (id) => revealAt.get(id);

        // Nodes.
        const parts = new Map();
        const sorted = [...layout.nodes].sort((a, b) => a.y - b.y);
        for (const n of sorted) {
            const box = el("div", { class: "dg-node" }, htmlLayer);
            if (kind === "iso") {
                // The block: top face and two sides, the label on a plate under it.
                const s = n.size;
                const cx = n.x;
                const cy = n.y + n.dy;
                const lift = n.lift * s * 2;
                const g = el("g", { opacity: 0 }, blockLayer, true);
                const fill = tint(n) ?? "var(--secondary)";
                el("polygon", { points: `${cx - s},${cy} ${cx},${cy + s / 2} ${cx},${cy + s / 2 + lift} ${cx - s},${cy + lift}`, style: `fill:${fill};filter:brightness(.72)` }, g, true);
                el("polygon", { points: `${cx + s},${cy} ${cx},${cy + s / 2} ${cx},${cy + s / 2 + lift} ${cx + s},${cy + lift}`, style: `fill:${fill};filter:brightness(.52)` }, g, true);
                const top = el("polygon", { points: `${cx - s},${cy} ${cx},${cy - s / 2} ${cx + s},${cy} ${cx},${cy + s / 2}`, style: `fill:${fill}` }, g, true);
                const glow = el("polygon", { points: top.getAttribute("points"), style: `fill:var(--accent);opacity:0;stroke:var(--accent);stroke-width:${6 * unit}` }, g, true);
                const shade = el("polygon", { points: `${cx - s},${cy} ${cx},${cy - s / 2} ${cx + s},${cy} ${cx + s},${cy + lift} ${cx},${cy + s / 2 + lift} ${cx - s},${cy + lift}`, style: "fill:#000;opacity:0" }, g, true);
                if (n.icon) {
                    const icon = el("text", { x: cx, y: cy + s * 0.18, "text-anchor": "middle", fill: "#FFFFFF", "data-layout-ignore": "", style: `font-size:${s * 0.55}px`, text: /\.(png|jpe?g|svg|webp)$/i.test(n.icon) ? "" : n.icon }, g, true);
                    if (/\.(png|jpe?g|svg|webp)$/i.test(n.icon)) {
                        icon.remove();
                        el("image", { "data-layout-ignore": "", href: n.icon, x: cx - s * 0.3, y: cy - s * 0.32, width: s * 0.6, height: s * 0.6 }, g, true);
                    }
                }
                box.style.cssText = `left:${n.x - n.labelW / 2}px;top:${n.y + n.h / 2 - n.labelH}px;width:${n.labelW}px;height:${n.labelH}px;`;
                parts.set(n.id, { box, block: g, glow, shade, ring: null });
            } else {
                box.style.cssText = `left:${n.x - n.w / 2}px;top:${n.y - n.h / 2}px;width:${n.w}px;height:${n.h}px;`;
                const plate = el("div", { class: "dg-plate" }, box);
                const color = tint(n);
                if (color) plate.style.borderColor = color;
                const ring = el("div", { class: "dg-ring" }, box);
                if (sketch) {
                    const outline = el("path", { d: boxPath(n, true, n.id, unit), fill: "none", stroke: color ?? "var(--text)", "stroke-width": 4 * unit, "stroke-linecap": "round", opacity: 0 }, overSvg, true);
                    parts.set(n.id, { box, ring, outline });
                } else parts.set(n.id, { box, ring });
            }
            if (n.icon && kind !== "iso") {
                const icon = el("div", { class: "dg-icon", style: `font-size:${n.font * 1.15}px` }, box);
                if (/\.(png|jpe?g|svg|webp)$/i.test(n.icon)) el("img", { src: n.icon }, icon);
                else icon.textContent = n.icon;
            }
            if (kind === "iso") el("div", { class: "dg-plate" }, box);
            const label = el("div", { class: "dg-label", style: `font-size:${n.font}px` }, box);
            n.lines.forEach((line, i) => {
                if (i) el("br", {}, label);
                label.appendChild(document.createTextNode(line));
            });
            // The estimate is close but not exact: shrink a label that still overflows its box.
            const room = (kind === "iso" ? n.labelW : n.w) - 16 * unit - (n.icon && kind !== "iso" ? n.font * 1.4 : 0);
            if (label.scrollWidth > room) label.style.fontSize = `${n.font * (room / label.scrollWidth)}px`;
        }

        // Edges: drawn on once both ends are there.
        const edgeParts = [];
        layout.edges.forEach((e, i) => {
            const a = byId.get(e.from);
            const b = byId.get(e.to);
            const d = edgePath(a, b, kind, layout.direction, sketch, `${e.from}>${e.to}`, unit);
            const base = el("path", { d, fill: "none", stroke: "var(--text)", "stroke-opacity": kind === "iso" ? 0.55 : 0.7, "stroke-width": (kind === "iso" ? 7 : 5) * unit, "stroke-linecap": "round", "stroke-linejoin": "round" }, edgeLayer, true);
            const hot = el("path", { d, fill: "none", stroke: "var(--accent)", "stroke-width": (kind === "iso" ? 9 : 7) * unit, "stroke-linecap": "round", "stroke-linejoin": "round", opacity: 0 }, edgeLayer, true);
            const length = base.getTotalLength();
            base.style.strokeDasharray = `${length}`;
            base.style.strokeDashoffset = `${length}`;
            const at = Math.max(shown(e.from), shown(e.to)) + 0.2;
            fromToState(tl, base, { strokeDashoffset: length }, { strokeDashoffset: 0 }, at, 0.5, "power2.inOut");
            let arrow = null;
            if (kind !== "mind") {
                const end = base.getPointAtLength(length);
                const before = base.getPointAtLength(Math.max(0, length - 12 * unit));
                const angle = (Math.atan2(end.y - before.y, end.x - before.x) * 180) / Math.PI;
                const sz = 16 * unit;
                arrow = el("polygon", { points: `0,0 ${-sz * 1.6},${-sz} ${-sz * 1.6},${sz}`, fill: "var(--text)", "fill-opacity": 0.8, transform: `translate(${end.x},${end.y}) rotate(${angle})`, opacity: 0 }, edgeLayer, true);
                fromToState(tl, arrow, { opacity: 0 }, { opacity: 1 }, at + 0.42, 0.15);
            }
            let tag = null;
            if (e.label) {
                const mid = base.getPointAtLength(length / 2);
                tag = el("div", { class: "dg-edge-label", text: e.label, style: `left:${mid.x}px;top:${mid.y}px;font-size:${24 * unit}px` }, htmlLayer);
                fromToState(tl, tag, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1 }, at + 0.35, 0.3);
            }
            edgeParts.push({ e, base, hot, length, d, at, arrow, tag });
        });

        // Node motion: hidden → shown, then focused or dimmed per step.
        const HIDDEN = { opacity: 0, scale: 0.7, ring: 0, dim: 0 };
        const stateAt = (id, step) => {
            if (!step || !step.focus.length) return { opacity: 1, scale: 1, ring: 0, dim: 0 };
            return step.focus.includes(id) ? { opacity: 1, scale: 1.07, ring: 1, dim: 0 } : { opacity: 0.42, scale: 1, ring: 0, dim: 1 };
        };
        const apply = (id, from, to, at, duration, ease) => {
            const p = parts.get(id);
            if (kind === "iso") {
                // A dimmed block stays solid (connectors would show through) and is shaded instead.
                const solid = (st) => (st.opacity > 0 ? 1 : 0);
                fromToState(tl, p.block, { opacity: solid(from), y: from.opacity ? 0 : -40 * unit }, { opacity: solid(to), y: 0 }, at, duration, ease);
                fromToState(tl, p.box, { opacity: from.opacity, scale: from.scale }, { opacity: to.opacity, scale: to.scale }, at, duration, ease);
                fromToState(tl, p.glow, { opacity: from.ring * 0.45 }, { opacity: to.ring * 0.45 }, at, duration);
                fromToState(tl, p.shade, { opacity: from.dim * 0.5 }, { opacity: to.dim * 0.5 }, at, duration);
            } else {
                fromToState(tl, p.box, { opacity: from.opacity, scale: from.scale }, { opacity: to.opacity, scale: to.scale }, at, duration, ease);
                fromToState(tl, p.ring, { opacity: from.ring }, { opacity: to.ring }, at, duration);
                if (p.outline) fromToState(tl, p.outline, { opacity: from.opacity * 0.9 }, { opacity: to.opacity * 0.9 }, at, duration);
            }
        };
        for (const n of layout.nodes) {
            const t0 = shown(n.id);
            const active = [...steps].reverse().find((s) => s.at <= t0 + 1e-6);
            let state = stateAt(n.id, active);
            apply(n.id, HIDDEN, state, Math.max(0.05, t0 - 0.25), 0.45, "back.out(1.6)");
            const p = parts.get(n.id);
            if (p.outline) {
                const len = p.outline.getTotalLength();
                p.outline.style.strokeDasharray = `${len}`;
                p.outline.style.strokeDashoffset = `${len}`;
                fromToState(tl, p.outline, { strokeDashoffset: len }, { strokeDashoffset: 0 }, Math.max(0.05, t0 - 0.25), 0.6, "power1.inOut");
            }
            for (const s of steps) {
                if (s.at <= t0 + 1e-6) continue;
                const next = stateAt(n.id, s);
                if (JSON.stringify(next) === JSON.stringify(state)) continue;
                apply(n.id, state, next, s.at - 0.15, 0.35);
                state = next;
            }
        }

        // Focused edges glow and carry packets until the next step.
        const packets = data.packets ?? v.packets ?? kind === "iso";
        steps.forEach((s, k) => {
            if (!s.focus.length) return;
            const until = Math.min(k + 1 < steps.length ? steps[k + 1].at : END - 0.5, END - 0.5);
            for (const part of edgeParts) {
                const { e } = part;
                if (!s.focus.includes(e.from) && !s.focus.includes(e.to)) continue;
                const from = Math.max(s.at, part.at + 0.5);
                if (until - from < 0.3) continue;
                fromToState(tl, part.hot, { opacity: 0 }, { opacity: 0.9 }, from - 0.1, 0.25);
                fromToState(tl, part.hot, { opacity: 0.9 }, { opacity: 0 }, until - 0.15, 0.25);
                if (!packets) continue;
                const per = Math.min(1.6, Math.max(0.7, part.length / (520 * unit)));
                const runs = Math.max(1, Math.floor((until - from) / per));
                for (const lag of [0, per / 2]) {
                    if (lag && runs < 2) continue;
                    const dot = el("div", { class: "dg-packet", style: `width:${16 * unit}px;height:${16 * unit}px;margin:${-8 * unit}px 0 0 ${-8 * unit}px;offset-path:path('${part.d}')` }, htmlLayer);
                    tl.fromTo(dot, { opacity: 0 }, { opacity: 1, duration: 0.12, immediateRender: false }, from + lag);
                    tl.fromTo(dot, { offsetDistance: "0%" }, { offsetDistance: "100%", duration: per, ease: "none", repeat: runs - (lag ? 2 : 1), immediateRender: false }, from + lag);
                    tl.fromTo(dot, { opacity: 1 }, { opacity: 0, duration: 0.12, immediateRender: false }, from + lag + per * (runs - (lag ? 1 : 0)) - 0.12);
                }
            }
        });

        // Step notes: a sticky note low in the frame while its step lasts.
        steps.forEach((s, k) => {
            if (!s.note) return;
            const until = k + 1 < steps.length ? steps[k + 1].at : END - 0.5;
            const note = el("div", { class: "dg-note", text: s.note }, rootEl);
            note.style.cssText += `font-size:${34 * unit}px;max-width:${W * 0.7}px;left:${W * 0.15}px;top:${area.y + area.h + 24 * unit}px;transform:rotate(-2deg)`;
            fromToState(tl, note, { opacity: 0, y: 30 * unit }, { opacity: 1, y: 0 }, s.at + 0.2, 0.35, "back.out(1.7)");
            fromToState(tl, note, { opacity: 1 }, { opacity: 0 }, until - 0.25, 0.25);
        });

        // Exit on the composition's end (bin/graphic plan stretches data-duration to the span).
        tl.fromTo([svg, htmlLayer, overSvg], { opacity: 1, y: 0 }, { opacity: 0, y: -40 * unit, duration: 0.45, ease: "power2.in", immediateRender: false }, END - 0.5);
        const heading = rootEl.querySelector(".dg-title");
        if (heading) tl.fromTo(heading, { opacity: 1 }, { opacity: 0, duration: 0.4, immediateRender: false }, END - 0.5);
        return layout;
    }

    // MARK: big canvas

    /** The camera frame (centre and scale) that shows box b on a W × H screen. */
    function frameBox(b, W, H, maxScale, noteSide) {
        const s = Math.min((W * 0.84) / b.w, (H * (noteSide ? 0.54 : 0.74)) / b.h, maxScale);
        return { cx: b.x + b.w / 2, cy: b.y + b.h / 2 + (noteSide * H * 0.13) / s, s };
    }

    function unionBox(nodes, pad) {
        const x0 = Math.min(...nodes.map((n) => n.x - n.w / 2)) - pad;
        const y0 = Math.min(...nodes.map((n) => n.y - n.h / 2)) - pad;
        const x1 = Math.max(...nodes.map((n) => n.x + n.w / 2)) + pad;
        const y1 = Math.max(...nodes.map((n) => n.y + n.h / 2)) + pad;
        return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
    }

    /** The big-canvas world: the mind-map laid out on a canvas `size` screens wide and tall. */
    function canvasLayout(data, W, H, size) {
        const k = Math.max(1.2, Math.min(4, Number(size) || 2));
        // A tall canvas is kept squarer than the screen: a radial map uses the width, and the end view (width-bound
        // on 9:16) keeps its labels larger.
        const worldW = W >= H ? Math.min(W * k, H * k * 1.6) : W * k;
        const worldH = W >= H ? H * k : Math.min(H * k, W * k * 1.25);
        const unit = Math.min(worldW, worldH) / 1080;
        const area = { x: 80 * unit, y: 80 * unit, w: worldW - 160 * unit, h: worldH - 160 * unit };
        const layout = mindLayout(data, area, unit);
        return { ...layout, worldW, worldH, k, unit };
    }

    /**
     * One canvas several screens big, drawn on branch by branch while the camera flies to each stop, ending on the
     * whole map. v: data (mind-map data + stops, summary), size, pen, brand ids.
     */
    function mountCanvas(tl, v, rootEl) {
        brand(v);
        const { W, H, unit: screenUnit, END } = canvas(rootEl);
        const data = typeof v.data === "string" ? JSON.parse(v.data || "{}") : v.data ?? {};
        rootEl.classList.add("dg-sketch");
        const world = canvasLayout(data, W, H, data.size ?? v.size);
        const { worldW, worldH, unit } = world;
        rootEl.style.setProperty("--dg-border", `${3 * unit}px`);
        rootEl.style.setProperty("--dg-radius", `${36 * unit}px`);
        const byId = new Map(world.nodes.map((n) => [n.id, n]));
        const t = world.tree;
        const view = el("div", { class: "dg-layer", style: `width:${worldW}px;height:${worldH}px;transform-origin:0 0;` }, rootEl);
        view.setAttribute("data-layout-allow-overflow", "");
        const paper = el("div", { class: "dg-layer", style: `width:${worldW}px;height:${worldH}px;background-color:var(--background);background-image:radial-gradient(color-mix(in srgb, var(--text) 16%, transparent) ${2.2 * unit}px, transparent ${2.6 * unit}px);background-size:${44 * unit}px ${44 * unit}px;` }, view);
        paper.setAttribute("data-layout-allow-overflow", "");
        const under = el("div", { class: "dg-layer", style: `width:${worldW}px;height:${worldH}px` }, view);
        const svg = el("svg", { class: "dg-layer", width: worldW, height: worldH, viewBox: `0 0 ${worldW} ${worldH}` }, view, true);
        const html = el("div", { class: "dg-layer", style: `width:${worldW}px;height:${worldH}px` }, view);
        const ink = "var(--text)";

        // Stops: given, else the root and then each branch.
        let stops = (data.stops ?? []).map((s) => ({ ...s }));
        if (!stops.length) stops = [t.top, ...t.children.get(t.top)].map((id) => ({ focus: id }));
        const free = stops.filter((s) => typeof s.at !== "number");
        const outro = Math.min(3.2, Math.max(2, END * 0.12));
        free.forEach((s, i) => (s.at = 0.6 + ((END - outro - 1.2) * i) / Math.max(1, free.length)));
        stops.sort((a, b) => a.at - b.at);

        // What each stop draws: its node's subtree not drawn before (the root first).
        const drawn = new Set();
        const subtree = (id) => [id, ...t.children.get(id).flatMap((k) => subtree(k))];
        const plan = stops.map((s) => {
            const ids = typeof s.focus === "string" && byId.has(String(s.focus)) ? subtree(String(s.focus)).filter((id) => !drawn.has(id)) : [];
            const own = typeof s.focus === "string" && String(s.focus) === t.top ? [t.top] : ids;
            own.forEach((id) => drawn.add(id));
            return own;
        });
        if (!drawn.has(t.top) && plan.length) {
            plan[0].unshift(t.top);
            drawn.add(t.top);
        }
        const rest = world.nodes.map((n) => n.id).filter((id) => !drawn.has(id));

        // A pen follows each stroke while it is drawn (one per stroke, its path fixed: no state carried between seeks).
        const PEN = `<svg viewBox="0 0 70 70" width="100%" height="100%"><g transform="rotate(38 35 35)"><rect x="29" y="-14" width="12" height="62" rx="3" fill="var(--accent)"/><rect x="29" y="-14" width="12" height="10" rx="3" fill="#333"/><polygon points="29,48 41,48 35,66" fill="#E8C9A0"/><polygon points="33,59 37,59 35,66" fill="#222"/></g></svg>`;
        const usePen = (data.pen ?? v.pen) !== false;

        const strokes = (d, at, duration, width, color, parent = svg) => {
            const path = el("path", { d, fill: "none", stroke: color, "stroke-width": width, "stroke-linecap": "round", "stroke-linejoin": "round" }, parent, true);
            const len = path.getTotalLength();
            path.style.strokeDasharray = `${len}`;
            path.style.strokeDashoffset = `${len}`;
            fromToState(tl, path, { strokeDashoffset: len }, { strokeDashoffset: 0 }, at, duration, "power1.inOut");
            if (usePen && duration >= 0.2) {
                const pen = el("div", { class: "dg-layer", style: `width:${80 * unit}px;height:${80 * unit}px;margin:${-80 * unit * 0.93}px 0 0 ${-80 * unit * 0.36}px;offset-path:path('${d}');offset-rotate:0deg;offset-anchor:0 0;opacity:0` }, html);
                pen.innerHTML = PEN;
                fromToState(tl, pen, { opacity: 0 }, { opacity: 1 }, at, 0.01, "none");
                fromToState(tl, pen, { offsetDistance: "0%" }, { offsetDistance: "100%" }, at, duration, "power1.inOut");
                fromToState(tl, pen, { opacity: 1 }, { opacity: 0 }, at + duration, 0.01, "none");
            }
            return path;
        };

        const drawNode = (n, at, dur) => {
            const color = n.depth === 0 ? "var(--accent)" : ink;
            const parent = t.parent.get(n.id);
            let start = at;
            if (parent !== null && parent !== undefined) {
                const p = byId.get(parent);
                strokes(edgePath(p, n, "mind", null, true, `${parent}>${n.id}`, unit), start, dur * 0.4, 5 * unit, ink);
                start += dur * 0.4;
            }
            const plate = el("div", { class: "dg-plate", style: `left:${n.x - n.w / 2}px;top:${n.y - n.h / 2}px;width:${n.w}px;height:${n.h}px;position:absolute;opacity:0;background:color-mix(in srgb, var(--background) 70%, ${n.depth === 0 ? "var(--accent)" : "white"} 30%)` }, under);
            strokes(boxPath(n, true, n.id, unit), start, dur * 0.45, (n.depth === 0 ? 7 : 5) * unit, color);
            fromToState(tl, plate, { opacity: 0 }, { opacity: 1 }, start + dur * 0.2, dur * 0.3);
            const label = el("div", { class: "dg-label", "data-layout-allow-overflow": "", style: `position:absolute;left:${n.x - n.w / 2}px;top:${n.y - n.h / 2}px;width:${n.w}px;height:${n.h}px;display:flex;align-items:center;justify-content:center;font-size:${n.font}px;opacity:0` }, html);
            const inner = el("div", {}, label);
            n.lines.forEach((line, i) => {
                if (i) el("br", {}, inner);
                inner.appendChild(document.createTextNode(line));
            });
            if (inner.scrollWidth > n.w - 16 * unit) inner.style.fontSize = `${n.font * ((n.w - 16 * unit) / inner.scrollWidth)}px`;
            fromToState(tl, label, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1 }, start + dur * 0.4, dur * 0.25);
            return start + dur * 0.45;
        };

        // Camera.
        // The end view shows the whole canvas (above the summary note when there is one); the paper colour fills the
        // frame around it. A stop's view stays inside the canvas and zooms in at most 0.8 (labels ~1.5× their size).
        rootEl.style.background = "var(--background)";
        const noteRoom = data.summary ? 0.8 : 1;
        const overviewScale = Math.min(W / worldW, (H * noteRoom) / worldH) * 0.98;
        const overview = { cx: worldW / 2, cy: worldH / 2 + (H * (1 - noteRoom)) / 2 / overviewScale, s: overviewScale };
        const maxScale = 0.8;
        const cover = Math.max(W / worldW, H / worldH);
        const inside = (f) => {
            const sc = Math.max(f.s, cover);
            return {
                s: sc,
                cx: Math.min(Math.max(f.cx, W / (2 * sc)), worldW - W / (2 * sc)),
                cy: Math.min(Math.max(f.cy, H / (2 * sc)), worldH - H / (2 * sc)),
            };
        };
        const frames = stops.map((s) => {
            let noteSide = 0;
            let box;
            if (Array.isArray(s.focus) && s.focus.length === 4) box = { x: s.focus[0] * worldW, y: s.focus[1] * worldH, w: s.focus[2] * worldW, h: s.focus[3] * worldH };
            else if (byId.has(String(s.focus))) {
                const id = String(s.focus);
                const group = id === t.top ? [byId.get(id), ...t.children.get(id).map((k) => byId.get(k))] : subtree(id).map((k) => byId.get(k));
                box = unionBox(group, 60 * unit);
                // The note goes on the screen side away from the root, so it never covers the centre of the map.
                if (s.note) noteSide = byId.get(t.top).y > box.y + box.h / 2 + 1 ? -1 : 1;
            } else box = { x: 0, y: 0, w: worldW, h: worldH };
            if (s.note && !noteSide) noteSide = 1;
            let f = frameBox(box, W, H, maxScale, noteSide);
            if (typeof s.zoom === "number" && s.zoom > 0) f.s = overview.s * s.zoom;
            f = inside(f);
            // Keeping the view inside the canvas can undo the room made for the note: then the note takes the other
            // band, or the view zooms out until one band is clear of the branch.
            if (s.note) {
                // The branch and the root (usually in view next to it) both stay clear of the note.
                const r = byId.get(t.top);
                const y0 = Math.min(box.y, r.y - r.h / 2);
                const y1 = Math.max(box.y + box.h, r.y + r.h / 2);
                const clear = (g, side) => {
                    const top = H / 2 + (y0 - g.cy) * g.s;
                    const bottom = H / 2 + (y1 - g.cy) * g.s;
                    const band = side < 0 ? [H * 0.05, H * 0.23] : [H * (H > W ? 0.66 : 0.7), H * (H > W ? 0.84 : 0.95)];
                    return bottom < band[0] || top > band[1];
                };
                for (let k = 0; k < 6 && !clear(f, noteSide); k += 1) {
                    if (clear(f, -noteSide)) noteSide = -noteSide;
                    else {
                        const sc = f.s * 0.85;
                        f = inside({ cx: box.x + box.w / 2, cy: box.y + box.h / 2 + (noteSide * H * 0.13) / sc, s: sc });
                    }
                }
            }
            s.noteSide = noteSide;
            return f;
        });
        const place = (f) => ({ x: W / 2 - f.cx * f.s, y: H / 2 - f.cy * f.s, scale: f.s });
        let current = frames[0] ?? overview;
        gsap.set(view, { ...place(current), transformOrigin: "0 0" });
        stops.forEach((s, i) => {
            if (i === 0) return;
            const pan = Math.min(1.1, Math.max(0.5, (s.at - stops[i - 1].at) * 0.35));
            fromToState(tl, view, place(current), place(frames[i]), Math.max(0, s.at - pan), pan, "power2.inOut");
            current = frames[i];
        });
        const outAt = END - outro;
        fromToState(tl, view, place(current), place(overview), outAt, Math.min(1.4, outro * 0.5), "power2.inOut");

        // Drawing: each stop draws its part from its start, finished before the camera leaves.
        stops.forEach((s, i) => {
            const next = i + 1 < stops.length ? stops[i + 1].at : outAt;
            const room = next - s.at - (i + 1 < stops.length ? Math.min(1.1, Math.max(0.5, (next - s.at) * 0.35)) : 0) - 0.15;
            const ids = plan[i];
            if (!ids.length) return;
            const each = Math.max(0.35, Math.min(1.6, room / ids.length));
            let at = s.at;
            for (const id of ids) at = drawNode(byId.get(id), at, each);
            if (s.note) {
                const note = el("div", { class: "dg-note", text: s.note }, rootEl);
                note.style.cssText += `font-size:${40 * screenUnit}px;max-width:${W * 0.72}px;left:${W * 0.14}px;top:${s.noteSide < 0 ? H * 0.07 : H * (H > W ? 0.68 : 0.72)}px;transform:rotate(-2deg)`;
                fromToState(tl, note, { opacity: 0, y: 40 * screenUnit, rotation: -6 }, { opacity: 1, y: 0, rotation: -2 }, Math.min(at, next - 0.8), 0.4, "back.out(1.7)");
                fromToState(tl, note, { opacity: 1 }, { opacity: 0 }, next - 0.35, 0.3);
            }
        });
        let late = outAt;
        for (const id of rest) late = drawNode(byId.get(id), late, 0.5);
        if (data.summary) {
            const note = el("div", { class: "dg-note", text: data.summary }, rootEl);
            note.style.cssText += `font-size:${44 * screenUnit}px;max-width:${W * 0.74}px;left:${W * 0.13}px;top:${H * 0.83}px;transform:rotate(-2deg)`;
            fromToState(tl, note, { opacity: 0, y: 40 * screenUnit }, { opacity: 1, y: 0 }, outAt + 0.9, 0.45, "back.out(1.7)");
            fromToState(tl, note, { opacity: 1 }, { opacity: 0 }, END - 0.5, 0.4);
        }
        tl.fromTo(view, { opacity: 1 }, { opacity: 0, duration: 0.45, ease: "power1.in", immediateRender: false }, END - 0.5);
        return world;
    }

    const api = { textWidth, wrap, fitLabel, layering, flowLayout, mindLayout, isoLayout, canvasLayout, overlapping, separate, timedSteps, areaFor, mount, mountCanvas };
    root.BCDiagram = api;
    if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
