import { createStore } from "/js/AlpineStore.js";
import * as API from "/js/api.js";

const LABELS = ["benign", "threat-advisory", "ioc-ish"];

const store = createStore("osintStore", {
  mode: "text",
  text: "",
  url: "",
  user: "",
  justification: "",
  loading: false,
  error: null,
  result: null,
  showAdvanced: false,
  lastSubmitted: null,
  labels: LABELS,

  onOpen() {
    this.reset();
  },

  onClose() {
    this.loading = false;
  },

  reset() {
    this.mode = "text";
    this.text = "";
    this.url = "";
    this.user = "";
    this.justification = "";
    this.loading = false;
    this.error = null;
    this.result = null;
    this.showAdvanced = false;
    this.lastSubmitted = null;
  },

  setMode(mode) {
    if (this.mode === mode) return;
    this.mode = mode;
    this.error = null;
    this.result = null;
    this.lastSubmitted = null;

    if (mode === "text") {
      this.url = "";
      this.user = "";
      this.justification = "";
      this.showAdvanced = false;
    } else {
      this.text = "";
    }
  },

  canSubmit() {
    if (this.loading) return false;
    if (this.mode === "text") {
      return this.text.trim().length > 0;
    }
    return this.url.trim().length > 0;
  },

  get riskPercent() {
    if (!this.result) return 0;
    const risk = Number(this.result.risk ?? 0);
    if (Number.isNaN(risk)) {
      return 0;
    }
    return Math.round(Math.min(Math.max(risk, 0), 1) * 100);
  },

  get probabilitySummary() {
    if (!this.result || !Array.isArray(this.result.probs)) {
      return [];
    }
    return this.labels.map((label, index) => ({
      label,
      value: Number(this.result.probs[index] ?? 0),
    }));
  },

  get winningProbability() {
    if (!this.result || !Array.isArray(this.result.probs)) {
      return 0;
    }
    const labelIndex = Number(this.result.label ?? 0);
    return Number(this.result.probs[labelIndex] ?? 0);
  },

  get prettyJson() {
    if (!this.result) return "";
    return JSON.stringify(this.result, null, 2);
  },

  formatPercent(value) {
    const normalized = Math.max(Math.min(Number(value ?? 0), 1), 0);
    return `${Math.round(normalized * 100)}%`;
  },

  async copyResult() {
    if (!this.result || !navigator?.clipboard) {
      return;
    }
    try {
      await navigator.clipboard.writeText(this.prettyJson);
      globalThis.toast?.("Intel result copied to clipboard.", "success", 2000);
    } catch (error) {
      console.error("Failed to copy OSINT result", error);
      globalThis.toast?.("Unable to copy result to clipboard.", "error");
    }
  },

  _normalizeOptional(value) {
    if (typeof value !== "string") return undefined;
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : undefined;
  },

  async classify() {
    if (!this.canSubmit()) {
      this.error = "Provide text or a URL to classify.";
      return;
    }

    const payload = {};
    if (this.mode === "text") {
      payload.text = this.text.trim();
    } else {
      payload.url = this.url.trim();
      const user = this._normalizeOptional(this.user);
      const justification = this._normalizeOptional(this.justification);
      if (user) payload.user = user;
      if (justification) payload.justification = justification;
    }

    // Avoid duplicate submissions
    const serialized = JSON.stringify(payload);
    if (serialized === this.lastSubmitted && this.result) {
      globalThis.toast?.("Already classified this input.", "info", 2000);
      return;
    }

    this.loading = true;
    this.error = null;
    this.result = null;

    try {
      const response = await API.callJsonApi("intel_classify", payload);
      if (!response?.success) {
        const message = response?.error || "Classification failed.";
        throw new Error(message);
      }
      this.result = response.result;
      this.lastSubmitted = serialized;
      globalThis.toast?.("Classification complete.", "success", 2500);
    } catch (error) {
      console.error("OSINT classification failed", error);
      this.error = error?.message || "Unable to classify input.";
      globalThis.toast?.(this.error, "error");
    } finally {
      this.loading = false;
    }
  },
});

export { store };
