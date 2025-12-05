export function safeRender(value) {
  if (typeof value === "string" || typeof value === "number") return value;
  if (value == null) return "";
  try {
    return JSON.stringify(value, null, 2);
  } catch (e) {
    return String(value);
  }
}
