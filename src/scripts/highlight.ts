// Syntax highlighting shared by Markdown code blocks, notebook cells and their
// live editors, so a cell looks the same before and after a kernel starts.

// Also the theme of Markdown code blocks (astro.config.mjs imports it).
export const CODE_THEME = "github-dark";

let highlighter: Promise<(code: string) => string> | undefined;

/** Lazily load Shiki in the browser; returns a function giving the inner HTML of <code>. */
export function loadHighlighter() {
  highlighter ??= (async () => {
    const [{ createHighlighterCore }, { createJavaScriptRegexEngine }] = await Promise.all([
      import("shiki/core"),
      import("shiki/engine/javascript"),
    ]);
    const shiki = await createHighlighterCore({
      themes: [import("@shikijs/themes/github-dark")], // must name CODE_THEME (static import path)
      langs: [import("@shikijs/langs/python")],
      engine: createJavaScriptRegexEngine(),
    });
    return (code: string) => {
      const html = shiki.codeToHtml(code, { lang: "python", theme: CODE_THEME });
      const tpl = document.createElement("template");
      tpl.innerHTML = html;
      return tpl.content.querySelector("code")?.innerHTML ?? "";
    };
  })();
  return highlighter;
}
