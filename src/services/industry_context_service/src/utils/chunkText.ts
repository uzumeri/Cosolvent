export function chunkText(
  text: string,
  maxTokens: number,
  overlap: number,
): string[] {
  const words = text.split(/\s+/); // Split on whitespace
  const chunks: string[] = [];

  let start = 0;
  while (start < words.length) {
    const end = Math.min(start + maxTokens, words.length);
    const chunk = words.slice(start, end).join(" ");
    chunks.push(chunk);

    start += maxTokens - overlap; // Move window with overlap
  }

  return chunks;
}
