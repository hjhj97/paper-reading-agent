/**
 * Convert various LaTeX bracket formats to standard $$ format
 * Handles: [ ... ], \[ ... \], and ensures proper $$ format
 */
export function normalizeMathNotation(text: string): string {
  if (!text) return text;

  // Replace \[ ... \] with $$ ... $$
  text = text.replace(/\\\[([\s\S]*?)\\\]/g, (match, formula) => {
    return `$$${formula.trim()}$$`;
  });

  // Replace [ ... ] with $$ ... $$ (only if it looks like a formula)
  // Check for common math symbols to avoid replacing regular brackets
  text = text.replace(/\[\s*([^[\]]*?(?:[\\$=+\-*/^_{}()∑∫∏∂∇α-ωΑ-Ω])[^[\]]*?)\s*\]/g, (match, formula) => {
    return `$$${formula.trim()}$$`;
  });

  // Ensure $$ formulas are on separate lines
  text = text.replace(/\$\$([^\n])/g, '$$\n$1');
  text = text.replace(/([^\n])\$\$/g, '$1\n$$');

  return text;
}

