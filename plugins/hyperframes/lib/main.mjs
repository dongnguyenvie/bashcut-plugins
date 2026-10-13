// Entrypoint of HyperFrames Graphics (bashcut.hyperframes), started by bin/provider. The protocol is in bashcut-plugin.mjs and your code in
// handlers.mjs.
import { run } from "./bashcut-plugin.mjs";
import { handle } from "./handlers.mjs";

await run(handle);
