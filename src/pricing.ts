/**
 * Claude API list pricing — used to estimate cost when the SDK doesn't
 * return `total_cost_usd` (raw Anthropic SDK responses don't, only the
 * Agent SDK does). Prices are USD per million tokens.
 *
 * Verified 2026-05-03. Update + bump the date when Anthropic changes
 * pricing — silent drift here makes /budget meaningless.
 */

export interface ModelPrice {
  /** Input token price (USD per 1M). */
  input: number;
  /** Output token price (USD per 1M). */
  output: number;
}

const MODEL_PRICING: Record<string, ModelPrice> = {
  'claude-haiku-4-5': { input: 1.0, output: 5.0 },
  'claude-sonnet-4-5': { input: 3.0, output: 15.0 },
  'claude-sonnet-4-6': { input: 3.0, output: 15.0 },
  'claude-opus-4-5': { input: 15.0, output: 75.0 },
  'claude-opus-4-7': { input: 15.0, output: 75.0 },
};

// Cache-write cost multipliers (relative to base input price).
// 5min ephemeral default; 1h is supported via `cache_control.ttl: "1h"`.
const CACHE_WRITE_MULT_5M = 1.25;
const CACHE_WRITE_MULT_1H = 2.0;

// Cache reads are 10% of base input price across all models.
const CACHE_READ_MULT = 0.1;

export interface UsageBreakdown {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens?: number;
  cache_read_input_tokens?: number;
}

/**
 * Estimate request cost in USD from a usage breakdown.
 *
 * Returns undefined for unknown models so the caller can decide whether
 * to drop the row or tag it as unbillable.
 */
export function estimateCostUsd(
  model: string,
  usage: UsageBreakdown,
  cacheTtl: '5m' | '1h' = '5m',
): number | undefined {
  const key = Object.keys(MODEL_PRICING).find((k) => model.startsWith(k));
  if (!key) return undefined;
  const p = MODEL_PRICING[key];
  const writeMult =
    cacheTtl === '1h' ? CACHE_WRITE_MULT_1H : CACHE_WRITE_MULT_5M;

  const cost =
    usage.input_tokens * p.input +
    (usage.cache_creation_input_tokens || 0) * p.input * writeMult +
    (usage.cache_read_input_tokens || 0) * p.input * CACHE_READ_MULT +
    usage.output_tokens * p.output;
  return cost / 1e6;
}
