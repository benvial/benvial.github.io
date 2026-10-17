// Interactive plotly figures in notebooks. A figure arrives as the JSON of the
// `application/vnd.plotly.v1+json` output (data, layout), either saved in the page
// by Notebook.astro or produced by a live kernel (see notebook.ts). plotly.js
// is fetched once, when the first figure comes near the viewport.
//
// The gl3d partial bundle covers 3D traces (mesh3d, surface, scatter3d, ...) and
// basic 2D scatter plots. Its version matches the plotly pinned in
// binder/environment.yml (plotly.offline.get_plotlyjs_version()).

export const PLOTLY_MIME = "application/vnd.plotly.v1+json";
const PLOTLY = "https://cdn.jsdelivr.net/npm/plotly.js-gl3d-dist-min@4.1.1/plotly-gl3d.min.js";

type Spec = { data?: unknown[]; layout?: Record<string, unknown>; config?: Record<string, unknown> };
type Plotly = {
  newPlot: (el: HTMLElement, data: unknown[], layout: object, config: object) => Promise<unknown>;
  Plots: { resize: (el: HTMLElement) => void };
};

let loading: Promise<Plotly> | null = null;
function loadPlotly(): Promise<Plotly> {
  loading ??= new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = PLOTLY;
    script.onload = () => resolve((window as unknown as { Plotly: Plotly }).Plotly);
    script.onerror = () => {
      loading = null;
      reject(new Error(`Could not load ${PLOTLY}`));
    };
    document.head.append(script);
  });
  return loading;
}

/** Draw a plotly figure into `el`, replacing its content. */
export async function drawPlotly(el: HTMLElement, spec: Spec) {
  const Plotly = await loadPlotly();
  // A live output is drawn before it is attached; plotly sizes itself on the page.
  for (let i = 0; i < 60 && !el.isConnected; i++) await new Promise(requestAnimationFrame);
  el.replaceChildren();
  el.classList.add("nb-plotly");
  await Plotly.newPlot(el, spec.data ?? [], { autosize: true, ...spec.layout }, {
    responsive: true,
    displaylogo: false,
    modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d"],
    ...spec.config,
  });
}

// Saved figures: <div data-plotly> holding the figure JSON in a script tag.
const observer =
  typeof IntersectionObserver === "undefined"
    ? null
    : new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            observer!.unobserve(entry.target);
            hydrate(entry.target as HTMLElement);
          }
        },
        { rootMargin: "600px 0px" }
      );

function hydrate(el: HTMLElement) {
  const json = el.querySelector("script[type='application/json']")?.textContent;
  if (!json) return;
  drawPlotly(el, JSON.parse(json)).catch((err) => {
    console.error(err);
    const wait = el.querySelector(".nb-plotly-wait");
    if (wait) wait.textContent = "The interactive figure could not be loaded.";
  });
}

for (const el of document.querySelectorAll<HTMLElement>("[data-plotly]")) {
  if (observer) observer.observe(el);
  else hydrate(el);
}
