// Which model a request uses: the `provider` and `model` options, with a default model per provider.
import { createModels, createProvider, type Model, type MutableModels } from "@earendil-works/pi-ai";
import { openAICompletionsApi } from "@earendil-works/pi-ai/api/openai-completions.lazy";
import { anthropicProvider } from "@earendil-works/pi-ai/providers/anthropic";
import { googleProvider } from "@earendil-works/pi-ai/providers/google";
import { groqProvider } from "@earendil-works/pi-ai/providers/groq";
import { mistralProvider } from "@earendil-works/pi-ai/providers/mistral";
import { openaiProvider } from "@earendil-works/pi-ai/providers/openai";
import { openrouterProvider } from "@earendil-works/pi-ai/providers/openrouter";
import { xaiProvider } from "@earendil-works/pi-ai/providers/xai";
import { fauxFromEnvironment, FAUX_PROVIDER } from "./faux.ts";

/** The `provider` option's choices and the model used when `model` is empty. Keep in sync with plugin.json. */
export const DEFAULT_MODELS: Record<string, string> = {
    anthropic: "claude-sonnet-5-5",
    openai: "gpt-5.5",
    google: "gemini-3.5-flash",
    openrouter: "anthropic/claude-sonnet-5.5",
    groq: "openai/gpt-oss-120b",
    xai: "grok-4.7",
    mistral: "mistral-medium-latest",
};

/** `compatible`: any OpenAI Chat Completions endpoint (a proxy, a gateway, a local server) at `baseUrl`. */
export const COMPATIBLE = "compatible";

export const PROVIDER_NAMES: Record<string, string> = {
    anthropic: "Anthropic",
    openai: "OpenAI",
    google: "Google Gemini",
    openrouter: "OpenRouter",
    groq: "Groq",
    xai: "xAI",
    mistral: "Mistral",
    [COMPATIBLE]: "OpenAI-compatible",
    [FAUX_PROVIDER]: "Faux (tests)",
};

export const API_KEY_MISSING = "Add an API key in Settings › Plugins › Director";

let collection: MutableModels | undefined;

export function models(): MutableModels {
    if (collection) return collection;
    collection = createModels();
    for (const provider of [
        anthropicProvider(),
        openaiProvider(),
        googleProvider(),
        openrouterProvider(),
        groqProvider(),
        xaiProvider(),
        mistralProvider(),
    ]) {
        collection.setProvider(provider);
    }
    const faux = fauxFromEnvironment();
    if (faux) collection.setProvider(faux.provider);
    return collection;
}

export interface Options {
    provider?: unknown;
    model?: unknown;
    apiKey?: unknown;
    thinking?: unknown;
    maxTurns?: unknown;
    baseUrl?: unknown;
}

export interface Resolved {
    provider: string;
    modelId: string;
    model?: Model<any>;
    apiKey: string;
    /** Why the model cannot be used, when it cannot. */
    problem?: string;
}

export function resolve(options: Options | undefined): Resolved {
    const opts = options ?? {};
    const apiKey = typeof opts.apiKey === "string" ? opts.apiKey.trim() : "";
    // Test-only: BASHCUT_DIRECTOR_FAUX replaces every provider with the scripted faux model.
    const faux = fauxFromEnvironment();
    if (faux) {
        const model = faux.getModel();
        return { provider: FAUX_PROVIDER, modelId: model.id, model, apiKey };
    }
    const provider = typeof opts.provider === "string" && opts.provider ? opts.provider : "anthropic";
    const requested = typeof opts.model === "string" ? opts.model.trim() : "";
    if (provider === COMPATIBLE) return compatible(opts, requested, apiKey);
    if (!(provider in DEFAULT_MODELS)) {
        return { provider, modelId: requested, apiKey, problem: `Unknown provider "${provider}"` };
    }
    const modelId = requested || DEFAULT_MODELS[provider];
    const model = models().getModel(provider, modelId);
    if (!model) {
        return {
            provider,
            modelId,
            apiKey,
            problem: `${PROVIDER_NAMES[provider]} has no model "${modelId}" in Director's catalog; leave Model empty for ${DEFAULT_MODELS[provider]}`,
        };
    }
    return { provider, modelId, model, apiKey };
}

export function thinkingLevel(value: unknown, model: Model<any>): "off" | "low" | "medium" | "high" {
    if (!model.reasoning) return "off";
    return value === "low" || value === "medium" || value === "high" ? value : "off";
}

export function maxTurns(value: unknown): number {
    const n = typeof value === "number" ? value : typeof value === "string" ? Number(value) : NaN;
    return Number.isFinite(n) ? Math.min(200, Math.max(5, Math.round(n))) : 40;
}

export function supportsImages(model: Model<any>): boolean {
    return model.input.includes("image");
}

/** Plaintext is restricted to loopback; endpoint credentials never belong in a URL. */
function endpoint(value: unknown): string | undefined {
    if (typeof value !== "string" || /[\s\\]/.test(value.trim())) return undefined;
    try {
        const url = new URL(value.trim());
        const loopback = url.hostname === "localhost" || url.hostname === "[::1]" ||
            /^127\.\d+\.\d+\.\d+$/.test(url.hostname);
        if (url.protocol !== "https:" && !(url.protocol === "http:" && loopback)) return undefined;
        if (url.username || url.password || url.search || url.hash) return undefined;
        return url.href.replace(/\/+$/, "");
    } catch {
        return undefined;
    }
}

/** A model on an OpenAI-compatible endpoint: the catalog does not know it, so it is described here. */
function compatible(opts: Options, modelId: string, apiKey: string): Resolved {
    const baseUrl = endpoint(opts.baseUrl);
    if (!baseUrl) {
        return { provider: COMPATIBLE, modelId, apiKey,
            problem: "Set a valid HTTPS Base URL (HTTP is allowed only for loopback), without credentials, query or fragment" };
    }
    if (!modelId) return { provider: COMPATIBLE, modelId, apiKey, problem: "Set Model for the OpenAI-compatible provider" };
    const model: Model<"openai-completions"> = {
        id: modelId,
        name: modelId,
        api: "openai-completions",
        provider: COMPATIBLE,
        baseUrl,
        // The Thinking option is sent as reasoning_effort; endpoints that ignore it are unaffected.
        reasoning: true,
        input: ["text", "image"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 200000,
        maxTokens: 32000,
    };
    models().setProvider(
        createProvider({
            id: COMPATIBLE,
            name: "OpenAI-compatible",
            baseUrl,
            auth: { apiKey: { name: "API key", resolve: async () => ({ auth: {} }) } },
            models: [model],
            api: openAICompletionsApi(),
        }),
    );
    return { provider: COMPATIBLE, modelId, model, apiKey };
}
