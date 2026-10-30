import type { CastLine } from "./cast";

const RECORDS_KEY = "yaogua.records.v1";
const DRAFT_KEY = "yaogua.draft.v1";
const QUESTION_KEY = "yaogua.pending-question";
const THEME_KEY = "yaogua.theme";

export type CastRecord = {
  id: string;
  question: string;
  createdAt: string;
  lines: CastLine[];
};

export type Draft = {
  question: string;
  lines: CastLine[];
};

function readJson<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function isLine(value: unknown): value is CastLine {
  if (!value || typeof value !== "object") return false;
  const line = value as CastLine;
  return (
    Array.isArray(line.coins) &&
    line.coins.length === 3 &&
    line.coins.every((coin) => coin === 2 || coin === 3) &&
    [6, 7, 8, 9].includes(line.sum)
  );
}

export function loadRecords(): CastRecord[] {
  const parsed = readJson<CastRecord[]>(RECORDS_KEY);
  if (!Array.isArray(parsed)) return [];
  return parsed.filter(
    (record) =>
      record &&
      typeof record.id === "string" &&
      typeof record.question === "string" &&
      typeof record.createdAt === "string" &&
      Array.isArray(record.lines) &&
      record.lines.length === 6 &&
      record.lines.every(isLine),
  );
}

export function saveRecord(input: Omit<CastRecord, "id" | "createdAt">): CastRecord {
  const record: CastRecord = {
    id: crypto.randomUUID(),
    question: input.question.trim().slice(0, 40),
    createdAt: new Date().toISOString(),
    lines: input.lines,
  };
  const next = [record, ...loadRecords()].slice(0, 30);
  localStorage.setItem(RECORDS_KEY, JSON.stringify(next));
  return record;
}

export function getRecord(id: string): CastRecord | undefined {
  return loadRecords().find((record) => record.id === id);
}

export function deleteRecord(id: string): void {
  const next = loadRecords().filter((record) => record.id !== id);
  localStorage.setItem(RECORDS_KEY, JSON.stringify(next));
}

export function clearRecords(): void {
  localStorage.removeItem(RECORDS_KEY);
}

export function loadDraft(): Draft | null {
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (!raw) return null;
    const draft = JSON.parse(raw) as Draft;
    if (!draft || typeof draft.question !== "string" || !Array.isArray(draft.lines)) return null;
    if (draft.lines.length > 6 || !draft.lines.every(isLine)) return null;
    return { question: draft.question.slice(0, 40), lines: draft.lines };
  } catch {
    return null;
  }
}

export function saveDraft(draft: Draft): void {
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
}

export function clearDraft(): void {
  sessionStorage.removeItem(DRAFT_KEY);
}

export function savePendingQuestion(question: string): void {
  sessionStorage.setItem(QUESTION_KEY, question.trim().slice(0, 40));
}

export function loadPendingQuestion(): string {
  return sessionStorage.getItem(QUESTION_KEY) ?? "";
}

export function clearPendingQuestion(): void {
  sessionStorage.removeItem(QUESTION_KEY);
}

export type ThemeName = "day" | "night";

export function loadTheme(): ThemeName {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "day" || saved === "night") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "night" : "day";
}

export function saveTheme(theme: ThemeName): void {
  localStorage.setItem(THEME_KEY, theme);
  document.documentElement.dataset.theme = theme;
  const color = theme === "night" ? "#121816" : "#e4ebe6";
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", color);
}

export function formatWhen(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(date);
}
