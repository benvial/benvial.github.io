// Live notebooks: on demand, load Thebe from the CDN and attach the code cells
// of a <Notebook> to a kernel started on mybinder.org. Nothing is fetched until
// the reader asks for it; the saved outputs stay in place until a cell is re-run.
//
// Only thebe-core (kernel, outputs) is used. Cells stay the server-rendered Shiki
// blocks and become editable in place: a transparent textarea sits over the
// highlighted code, which Shiki re-renders with the same theme on every edit.

import { loadHighlighter } from "@/scripts/highlight";
import { PLOTLY_MIME, drawPlotly } from "@/scripts/plotly";

const THEBE = "https://cdn.jsdelivr.net/npm/thebe@0.9.3/lib/";
const ATTEMPTS = 3; // each launch may land on another mybinder.org federation member

type StatusEvent = { subject?: string; status?: string; message?: string };
type Listener = (name: string, data: StatusEvent) => void;
type ThebeCell = {
  execute: (source: string) => Promise<{ error?: unknown[] } | null>;
  attachToDOM: (el: HTMLElement) => void;
  executionCount: number | null;
};
type ThebeSession = { restart: () => Promise<void>; kernel?: { interrupt: () => Promise<void> } };
type Cell = {
  id: string;
  root: HTMLElement;
  host: HTMLElement;
  output: HTMLElement;
  editor: HTMLTextAreaElement;
  count: HTMLElement;
  ran?: string; // source of the last run, to flag edits made since
  thebe?: ThebeCell;
};

declare global {
  interface Window {
    thebe?: {
      events: unknown;
      on: (event: string, cb: Listener) => void;
      off: (event: string, cb: Listener) => void;
    };
    thebeCore?: {
      module: { ThebeServer: any };
      api: {
        makeConfiguration: (options: object, events: unknown) => any;
        makeRenderMimeRegistry: (mathjax: unknown) => any;
        setupNotebookFromBlocks: (blocks: { id: string; source: string }[], config: any, rendermime: any) => any;
      };
    };
  }
}

function load(tag: "script" | "link", url: string) {
  return new Promise<void>((resolve, reject) => {
    const el = document.createElement(tag);
    if (el instanceof HTMLScriptElement) el.src = url;
    else Object.assign(el, { rel: "stylesheet", href: url });
    el.onload = () => resolve();
    el.onerror = () => reject(new Error(`Could not load ${url}`));
    document.head.append(el);
  });
}

// Live plotly figures: a renderer for the plotly MIME type, ranked above HTML.
// thebe does not expose the Lumino widget base class, so it extends the class
// of the HTML renderer and only overrides what it draws.
function addPlotlyRenderer(rendermime: any) {
  const HTMLRenderer = rendermime.createRenderer("text/html").constructor;
  class PlotlyRenderer extends HTMLRenderer {
    render(model: { data: Record<string, unknown> }) {
      return drawPlotly((this as unknown as { node: HTMLElement }).node, model.data[PLOTLY_MIME] as object);
    }
  }
  rendermime.addFactory(
    { safe: true, mimeTypes: [PLOTLY_MIME], createRenderer: (options: object) => new PlotlyRenderer(options) },
    0
  );
}

// Binder reports its build phases as "Binder is: <phase> - <log line>".
const BINDER_PHASES: Record<string, string> = {
  waiting: "Waiting for a mybinder.org build slot…",
  fetching: "Fetching the environment…",
  building: "Preparing the environment. Right after an update this can take up to 15 minutes.",
  built: "Environment built, starting a server…",
  pushing: "Storing the environment…",
  launching: "Starting a server on mybinder.org…",
};

function describe({ subject, status, message = "" }: StatusEvent): string | undefined {
  const phase = message.match(/^Binder is: (\w+)/)?.[1];
  if (phase) return BINDER_PHASES[phase];
  if (subject === "server" && status === "launching") return "Contacting mybinder.org…";
  if (subject === "server" && status === "server-ready") return "Server ready, starting the kernel…";
  if (subject === "session" && status === "shutdown") return "The kernel has stopped. Reload the page to start a new one.";
  return undefined;
}

const READY =
  "Kernel ready. Edit any cell; Shift+Enter runs it and moves on, Ctrl+Enter runs it in place. “Run all” recomputes everything in order.";

/** Make a server-rendered Shiki block editable in place. */
function makeEditable(host: HTMLElement, highlight: (code: string) => string) {
  const pre = host.querySelector("pre")!;
  const code = pre.querySelector("code")!;
  const editor = document.createElement("textarea");
  editor.className = "nb-editor";
  editor.value = (code.textContent ?? "").replace(/\n$/, "");
  editor.spellcheck = false;
  editor.wrap = "off";
  editor.rows = 1; // let the highlighted code set the height, not the default two rows
  editor.style.caretColor = getComputedStyle(pre).color; // the theme's text colour
  editor.setAttribute("autocapitalize", "off");
  editor.setAttribute("autocomplete", "off");
  editor.setAttribute("aria-label", "Code cell");
  host.classList.add("nb-editable");
  pre.style.overflowX = "visible"; // the wrapper scrolls, so code and textarea scroll together
  pre.removeAttribute("tabindex");
  host.append(editor);

  let frame = 0;
  editor.addEventListener("input", () => {
    cancelAnimationFrame(frame);
    // A trailing newline needs a character after it to take up a line in <pre>.
    frame = requestAnimationFrame(() => (code.innerHTML = highlight(editor.value + (editor.value.endsWith("\n") ? " " : ""))));
  });
  editor.addEventListener("keydown", (e) => {
    if (e.key === "Tab" && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      document.execCommand("insertText", false, "    ");
    } else if (e.key === "Escape") {
      editor.blur();
    }
  });
  return editor;
}

// Copy buttons work with or without a kernel.
for (const button of document.querySelectorAll<HTMLButtonElement>("[data-nb-copy]")) {
  button.addEventListener("click", async () => {
    const cell = button.closest("[data-cell]")!;
    const source = cell.querySelector<HTMLTextAreaElement>(".nb-editor")?.value ?? cell.querySelector("pre")?.textContent ?? "";
    try {
      await navigator.clipboard.writeText(source.replace(/\n$/, ""));
      button.textContent = "Copied";
    } catch {
      button.textContent = "Copy failed";
    }
    setTimeout(() => (button.textContent = "Copy"), 1500);
  });
}

for (const nb of document.querySelectorAll<HTMLElement>("[data-notebook]")) {
  const button = nb.querySelector<HTMLButtonElement>("[data-nb-run]");
  const restart = nb.querySelector<HTMLButtonElement>("[data-nb-restart]");
  const restartAll = nb.querySelector<HTMLButtonElement>("[data-nb-restart-all]");
  const interrupt = nb.querySelector<HTMLButtonElement>("[data-nb-interrupt]");
  const status = nb.querySelector<HTMLElement>("[data-nb-status]");
  if (!button || !status || !restart || !restartAll || !interrupt) continue;
  const label = button.firstChild!;

  const say = (text: string, state = "busy") => {
    status.textContent = text;
    nb.dataset.state = state;
  };

  let started = false;
  let runAll: (() => Promise<void>) | undefined;

  button.addEventListener("click", async () => {
    if (runAll) return runAll();
    // A failed start leaves half-built state behind; a fresh page is simplest.
    if (started) return location.reload();
    started = true;
    button.disabled = true;
    say("Loading the notebook runtime…");
    try {
      const [highlight] = await Promise.all([
        loadHighlighter(),
        load("link", `${THEBE}thebe.css`),
        load("script", `${THEBE}index.js`),
      ]);
      const { thebe, thebeCore } = window;
      if (!thebe || !thebeCore) throw new Error("Thebe did not load");

      thebe.on("status", (_, data) => {
        const text = describe(data);
        if (text && nb.dataset.state === "busy") say(text);
      });

      // ---- Cells --------------------------------------------------------
      const setCurrent = (cell: Cell) => {
        for (const el of nb.querySelectorAll<HTMLElement>("[data-cell][data-current]")) delete el.dataset.current;
        cell.root.dataset.current = "";
      };
      // Jupyter-style execution count: [ ] never run, [*] running, [n] done.
      const showCount = (cell: Cell) => {
        const n = cell.thebe?.executionCount;
        const edited = cell.ran !== undefined && cell.ran !== cell.editor.value;
        const running = cell.root.dataset.state === "running";
        cell.count.textContent = `[${running ? "*" : (n ?? " ")}]${edited ? " edited" : ""}`;
        if (n == null) delete cell.root.dataset.ran;
        else cell.root.dataset.ran = edited ? "edited" : "yes";
      };

      // Progress in the (sticky) status line, since the running cell is often
      // off-screen and a solve can take half a minute on mybinder.org.
      let pending = 0;
      let ticker = 0;
      const progress = (cell: Cell) => {
        const index = cells.indexOf(cell) + 1;
        const start = Date.now();
        const show = document.createElement("button");
        show.type = "button";
        show.className = "nb-show link";
        show.textContent = "Show";
        show.addEventListener("click", () => cell.root.scrollIntoView({ block: "center", behavior: "smooth" }));
        const text = document.createTextNode("");
        const tick = () => {
          const t = Math.round((Date.now() - start) / 1000);
          const queued = pending > 1 ? `, ${pending - 1} queued` : "";
          text.textContent = `Running cell ${index} of ${cells.length} · ${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}${queued}. `;
        };
        tick();
        clearInterval(ticker);
        ticker = window.setInterval(tick, 1000);
        status.replaceChildren(text, show);
        nb.dataset.state = "running";
      };

      // One kernel queue: cells run one at a time, in the order asked.
      let queue: Promise<boolean> = Promise.resolve(true);
      const run = (cell: Cell) => {
        setCurrent(cell);
        cell.root.dataset.state = "queued";
        pending++;
        interrupt.disabled = false;
        return (queue = queue.then(async (): Promise<boolean> => {
          try {
            if (!cell.thebe) return false;
            const source = cell.editor.value;
            cell.root.dataset.state = "running";
            showCount(cell);
            progress(cell);
            const result = await cell.thebe.execute(source);
            cell.ran = source;
            return !!result && !result.error;
          } finally {
            delete cell.root.dataset.state;
            showCount(cell);
            if (--pending === 0) {
              clearInterval(ticker);
              interrupt.disabled = true;
              say(READY, "live");
            }
          }
        }));
      };

      const cells: Cell[] = [...nb.querySelectorAll<HTMLElement>("[data-cell]")].map((root, i) => {
        const host = root.querySelector<HTMLElement>("[data-executable]")!;
        const tools = document.createElement("div");
        tools.className = "nb-tools";
        const count = document.createElement("span");
        count.className = "nb-count t-mono";
        count.textContent = "[ ]";
        const runButton = document.createElement("button");
        runButton.type = "button";
        runButton.className = "nb-button";
        runButton.textContent = "Run";
        runButton.disabled = true;
        tools.append(runButton, count);
        host.after(tools);
        const cell: Cell = {
          id: `${i}`,
          root,
          host,
          output: root.querySelector<HTMLElement>("[data-output]")!,
          editor: makeEditable(host, highlight),
          count,
        };
        runButton.addEventListener("click", () => run(cell));
        cell.editor.addEventListener("focus", () => setCurrent(cell));
        cell.editor.addEventListener("input", () => showCount(cell));
        return cell;
      });
      cells.forEach((cell, i) =>
        cell.editor.addEventListener("keydown", (e) => {
          if (e.key !== "Enter" || !(e.shiftKey || e.ctrlKey || e.metaKey)) return;
          e.preventDefault();
          run(cell);
          const next = cells[i + 1];
          if (e.shiftKey && next) {
            next.editor.focus({ preventScroll: true });
            next.root.scrollIntoView({ block: "nearest", behavior: "smooth" });
          }
        })
      );

      // ---- Kernel -------------------------------------------------------
      const { makeConfiguration, makeRenderMimeRegistry, setupNotebookFromBlocks } = thebeCore.api;
      const config = makeConfiguration(
        {
          useBinder: true,
          binderOptions: { repo: nb.dataset.repo, ref: nb.dataset.ref, binderUrl: "https://mybinder.org" },
          kernelOptions: { name: "python3" },
        },
        thebe.events
      );
      const rendermime = makeRenderMimeRegistry(config.mathjax);
      addPlotlyRenderer(rendermime);
      const notebook = setupNotebookFromBlocks(
        cells.map((c) => ({ id: c.id, source: c.editor.value })),
        config,
        rendermime
      );

      // Thebe gives up on any hiccup of the Binder event stream (a build failing
      // on one federation member, a dropped connection), so retry the launch.
      let session: ThebeSession | null = null;
      let reason = "";
      for (let attempt = 1; attempt <= ATTEMPTS && !session; attempt++) {
        if (attempt > 1) say(`mybinder.org failed (${reason}). Retrying, attempt ${attempt} of ${ATTEMPTS}…`);
        const server = new thebeCore.module.ThebeServer(config);
        let onError: Listener = () => {};
        const failed = new Promise<never>((_, reject) => {
          onError = (_, data) => {
            if (data.status === "error") reject(new Error(data.message));
          };
        });
        failed.catch(() => {}); // only raced while this attempt is pending
        thebe.on("error", onError);
        try {
          server.connectToServerViaBinder();
          await Promise.race([server.ready, failed]);
          session = await Promise.race([server.startNewSession(rendermime), failed]);
          if (!session) reason = "no kernel session";
        } catch (err) {
          reason = String(err instanceof Error ? err.message : err)
            .split("\n")[0]
            .replace(/^Binder: failed to build - \S+ - /, "build failed: ")
            .replace(/^Lost connection to binder: \S+/, "lost the connection to Binder")
            .slice(0, 160);
          console.error("thebe launch failed", err);
        } finally {
          thebe.off("error", onError);
        }
      }
      if (!session) throw new Error(reason);
      notebook.attachSession(session);

      for (const c of cells) {
        c.thebe = notebook.getCellById(c.id) as ThebeCell;
        c.thebe.attachToDOM(c.output);
      }
      for (const b of nb.querySelectorAll<HTMLButtonElement>(".nb-tools .nb-button")) b.disabled = false;

      const busy = (on: boolean) => {
        [button, restart, restartAll].forEach((b) => (b.disabled = on));
        label.textContent = on ? "Running… " : "Run all ";
      };
      runAll = async () => {
        busy(true);
        try {
          for (const c of cells) if (!(await run(c))) break; // stop at the first error, like Jupyter
        } finally {
          busy(false);
        }
      };
      interrupt.addEventListener("click", () => session!.kernel?.interrupt());
      const restartKernel = async () => {
        busy(true);
        say("Restarting the kernel…");
        await queue;
        await session!.restart();
        for (const c of cells) {
          c.ran = undefined;
          if (c.thebe) c.thebe.executionCount = null;
          showCount(c);
        }
        say(READY, "live");
        busy(false);
      };
      restart.addEventListener("click", restartKernel);
      restartAll.addEventListener("click", async () => {
        await restartKernel();
        await runAll!();
      });

      label.textContent = "Run all ";
      restart.hidden = restartAll.hidden = interrupt.hidden = false;
      interrupt.disabled = true;
      button.disabled = false;
      say(READY, "live");
    } catch (err) {
      console.error(err);
      const why = err instanceof Error && err.message ? ` (${err.message})` : "";
      say(`mybinder.org could not start a kernel${why}. The outputs shown come from a saved run.`, "error");
      label.textContent = "Try again ";
      button.disabled = false;
    }
  });
}

export {};
