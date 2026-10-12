// bin/osm-map: puts an OpenStreetMap map and a route into a composition folder, so a page can draw the map and
// animate the route without network at render time.
//
//   bin/osm-map --dir D --points "21.0278,105.8342,Hồ Gươm;21.0545,105.8194,Hồ Tây" [--route car|bike|foot|none]
//               [--width 1080] [--height 1920] [--padding 0.2] [--zoom Z]
//
// Writes D/map/<z>-<x>-<y>.png (tiles, also cached in the plugin cache folder) and D/map-data.js, which sets
// window.MAP_DATA = {width, height, zoom, tiles: [{src, x, y, size}], points: [{x, y, label, lat, lon}],
// route: [[x, y]…], legs: [{from, to, km, minutes}], km, minutes, profile, attribution}, in canvas pixels.
// Prints the same summary (without tiles and route) as JSON. Routes come from routing.openstreetmap.de (OSRM run by
// FOSSGIS); "none" joins the points with straight lines (km as the crow flies, no minutes). The map shows
// OpenStreetMap data: keep "© OpenStreetMap contributors" on screen while it is visible.
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const TILE = 256;
const AGENT = `BashCut-HyperFrames/${pluginVersion()} (+https://github.com/dongnguyenvie/bashcut-plugins)`;
const PROFILES = { car: "routed-car", bike: "routed-bike", foot: "routed-foot" };

function pluginVersion() {
    try {
        return JSON.parse(readFileSync(new URL("../plugin.json", import.meta.url))).version;
    } catch {
        return "0";
    }
}

function fail(message) {
    process.stderr.write(`osm-map: ${message}\n`);
    process.exit(2);
}

function parseArgs(argv) {
    const options = { route: "car", width: 1080, height: 1920, padding: 0.2 };
    for (let i = 0; i < argv.length; i += 1) {
        const key = argv[i];
        const value = argv[i + 1];
        if (!key.startsWith("--") || value === undefined) fail(`unexpected argument ${key}`);
        options[key.slice(2)] = value;
        i += 1;
    }
    if (!options.dir) fail("--dir is required (the composition folder)");
    if (!options.points) fail('--points is required: "lat,lon,Label;lat,lon,Label"');
    for (const key of ["width", "height", "padding"]) options[key] = Number(options[key]);
    if (!(options.width > 0 && options.height > 0)) fail("--width and --height must be positive");
    if (!(options.padding >= 0 && options.padding < 0.5)) fail("--padding must be 0–0.5 (share of each side)");
    if (options.route !== "none" && !PROFILES[options.route]) fail("--route must be car, bike, foot or none");
    options.points = options.points.split(";").filter(Boolean).map((part) => {
        const [lat, lon, ...label] = part.split(",");
        const point = { lat: Number(lat), lon: Number(lon), label: label.join(",").trim() };
        if (!(Math.abs(point.lat) <= 85 && Math.abs(point.lon) <= 180)) fail(`not a latitude,longitude: ${part}`);
        return point;
    });
    if (options.points.length < 1) fail("give at least one point");
    if (options.zoom !== undefined) {
        options.zoom = Number(options.zoom);
        if (!Number.isInteger(options.zoom) || options.zoom < 1 || options.zoom > 19) fail("--zoom must be 1–19");
    }
    return options;
}

// Web Mercator, in pixels of the whole world at zoom z.
function project(lat, lon, z) {
    const scale = TILE * 2 ** z;
    const sin = Math.sin((lat * Math.PI) / 180);
    return [((lon + 180) / 360) * scale, (0.5 - Math.log((1 + sin) / (1 - sin)) / (4 * Math.PI)) * scale];
}

function haversineKm(a, b) {
    const rad = Math.PI / 180;
    const h = Math.sin(((b.lat - a.lat) * rad) / 2) ** 2
        + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(((b.lon - a.lon) * rad) / 2) ** 2;
    return 2 * 6371 * Math.asin(Math.sqrt(h));
}

async function get(url) {
    const response = await fetch(url, { headers: { "User-Agent": AGENT } });
    if (!response.ok) throw new Error(`${response.status} from ${new URL(url).host}`);
    return response;
}

async function route(points, profile) {
    if (profile === "none" || points.length < 2) {
        const legs = points.slice(1).map((to, i) => ({ from: i, to: i + 1, km: haversineKm(points[i], to), minutes: null }));
        return { line: points.map((p) => [p.lat, p.lon]), legs };
    }
    const coordinates = points.map((p) => `${p.lon},${p.lat}`).join(";");
    const url = `https://routing.openstreetmap.de/${PROFILES[profile]}/route/v1/driving/${coordinates}`
        + "?overview=full&geometries=geojson";
    const body = await (await get(url)).json();
    if (body.code !== "Ok" || !body.routes?.length) throw new Error(`no route: ${body.message ?? body.code}`);
    const best = body.routes[0];
    return {
        line: best.geometry.coordinates.map(([lon, lat]) => [lat, lon]),
        legs: best.legs.map((leg, i) => ({ from: i, to: i + 1, km: leg.distance / 1000, minutes: leg.duration / 60 })),
    };
}

function fitZoom(line, options) {
    if (options.zoom) return options.zoom;
    const roomX = options.width * (1 - 2 * options.padding);
    const roomY = options.height * (1 - 2 * options.padding);
    for (let z = 17; z >= 2; z -= 1) {
        const xy = line.map(([lat, lon]) => project(lat, lon, z));
        const spanX = Math.max(...xy.map((p) => p[0])) - Math.min(...xy.map((p) => p[0]));
        const spanY = Math.max(...xy.map((p) => p[1])) - Math.min(...xy.map((p) => p[1]));
        if (spanX <= roomX && spanY <= roomY) return z;
    }
    return 2;
}

async function tiles(origin, z, options) {
    const cacheRoot = process.env.BASHCUT_PLUGIN_CACHE
        ?? join(homedir(), "Library/Caches/BashCut/PluginData/bashcut.hyperframes");
    const cache = join(cacheRoot, "osm-tiles");
    const out = join(options.dir, "map");
    mkdirSync(cache, { recursive: true });
    mkdirSync(out, { recursive: true });
    const count = 2 ** z;
    const wanted = [];
    for (let ty = Math.floor(origin[1] / TILE); ty * TILE < origin[1] + options.height; ty += 1) {
        for (let tx = Math.floor(origin[0] / TILE); tx * TILE < origin[0] + options.width; tx += 1) {
            if (ty < 0 || ty >= count) continue;
            wanted.push({ tx, ty, wrapped: ((tx % count) + count) % count });
        }
    }
    let downloaded = 0;
    // Two at a time, cached: the OpenStreetMap tile policy asks for a real User-Agent and no bulk downloads.
    const queue = [...wanted];
    async function worker() {
        for (let item = queue.shift(); item; item = queue.shift()) {
            const name = `${z}-${item.wrapped}-${item.ty}.png`;
            const cached = join(cache, name);
            if (!existsSync(cached)) {
                const bytes = Buffer.from(await (await get(`https://tile.openstreetmap.org/${z}/${item.wrapped}/${item.ty}.png`)).arrayBuffer());
                writeFileSync(cached, bytes);
                downloaded += 1;
            }
            copyFileSync(cached, join(out, name));
        }
    }
    await Promise.all([worker(), worker()]);
    const placed = wanted.map((t) => ({
        src: `map/${z}-${t.wrapped}-${t.ty}.png`,
        x: Math.round(t.tx * TILE - origin[0]),
        y: Math.round(t.ty * TILE - origin[1]),
        size: TILE,
    }));
    return { placed, downloaded };
}

const round = (value, digits) => (value === null ? null : Number(value.toFixed(digits)));

async function main() {
    const options = parseArgs(process.argv.slice(2));
    if (!existsSync(options.dir)) fail(`${options.dir} does not exist`);
    const { line, legs } = await route(options.points, options.route);
    const z = fitZoom(line.concat(options.points.map((p) => [p.lat, p.lon])), options);
    const xy = line.map(([lat, lon]) => project(lat, lon, z));
    const minX = Math.min(...xy.map((p) => p[0]));
    const maxX = Math.max(...xy.map((p) => p[0]));
    const minY = Math.min(...xy.map((p) => p[1]));
    const maxY = Math.max(...xy.map((p) => p[1]));
    const origin = [(minX + maxX) / 2 - options.width / 2, (minY + maxY) / 2 - options.height / 2];
    const local = ([x, y]) => [Math.round((x - origin[0]) * 10) / 10, Math.round((y - origin[1]) * 10) / 10];
    const { placed, downloaded } = await tiles(origin, z, options);
    const km = legs.reduce((sum, leg) => sum + leg.km, 0);
    const minutes = legs.every((leg) => leg.minutes !== null) ? legs.reduce((sum, leg) => sum + leg.minutes, 0) : null;
    const summary = {
        width: options.width,
        height: options.height,
        zoom: z,
        profile: options.route,
        km: round(km, 2),
        minutes: round(minutes, 1),
        legs: legs.map((leg) => ({ ...leg, km: round(leg.km, 2), minutes: round(leg.minutes, 1) })),
        points: options.points.map((p) => {
            const [x, y] = local(project(p.lat, p.lon, z));
            return { x, y, label: p.label, lat: p.lat, lon: p.lon };
        }),
        attribution: "© OpenStreetMap contributors",
        routeSource: options.route === "none" ? "straight lines" : "OSRM, routing.openstreetmap.de (FOSSGIS)",
    };
    const data = { ...summary, tiles: placed, route: xy.map(local) };
    writeFileSync(join(options.dir, "map-data.js"),
        `// Written by bin/osm-map. Map data © OpenStreetMap contributors (ODbL).\nwindow.MAP_DATA = ${JSON.stringify(data)};\n`);
    process.stdout.write(`${JSON.stringify({ ...summary, tiles: placed.length, downloaded, file: join(options.dir, "map-data.js") }, null, 2)}\n`);
}

main().catch((error) => fail(error.message));
