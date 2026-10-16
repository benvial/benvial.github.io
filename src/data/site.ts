// Site-wide facts. Content lives here or in collections, not in markup.

export const site = {
  name: "Benjamin Vial",
  url: "https://bvial.info",
  title: "Benjamin Vial (wave physics and scientific software)",
  description:
    "Benjamin Vial is a wave physicist who writes the solvers: metamaterials, quasinormal modes, homogenization and topology optimization, plus open-source finite element tools for photonics and electronics.",
  // Public contact address. Leave empty to show links only.
  email: "",
  cv: "/downloads/cv.pdf",
  location: "Bras, France",
};

export const nav = [
  { title: "Research", href: "/research" },
  { title: "Publications", href: "/publications" },
  { title: "Code", href: "/code" },
  { title: "Writing", href: "/blog" },
  { title: "Consulting", href: "/consulting" },
  { title: "About", href: "/about" },
  { title: "Contact", href: "/contact" },
];

export const socials = [
  { title: "GitHub", handle: "benvial", href: "https://github.com/benvial" },
  { title: "GitLab", handle: "benvial", href: "https://gitlab.com/benvial" },
  { title: "LinkedIn", handle: "ben-vial", href: "https://linkedin.com/in/ben-vial" },
  { title: "X", handle: "bpmvial", href: "https://twitter.com/bpmvial" },
];

export const services = [
  {
    title: "Inverse design and topology optimization",
    body: "Free-form design where every mesh element becomes a design variable. Automatic differentiation gives adjoint gradients of the full physical model, and the optimizer returns layouts you can fabricate. Past work includes microwave cloaks, an illusion device and a bi-focal lens (3D printed and measured), and the doping profile of silicon phase shifters.",
    tools: ["topology optimization", "adjoint method", "automatic differentiation", "binary layouts"],
  },
  {
    title: "Computational electromagnetics",
    body: "Full-wave simulation of photonic, microwave and RF devices: scattering, gratings and metasurfaces, waveguides and resonators. Quasinormal mode analysis explains how a resonant device works, and chip layouts go from GDS to S-parameters.",
    tools: ["FEM", "Fourier modal method", "plane wave expansion", "FDTD", "quasinormal modes"],
  },
  {
    title: "Multiphysics and wave modelling",
    body: "Coupled electromagnetic, thermal, mechanical and carrier transport models at device level. The same methods extend to acoustic and elastic waves, phononic lattices and time-modulated media.",
    tools: ["EM", "thermal", "carrier transport", "acoustics", "elastodynamics"],
  },
  {
    title: "Custom solver development",
    body: "Tailored finite element solvers in Python, from mesh generation to post-processing. I also package them as binary wheels and conda-forge recipes, so your team installs them with one command (no compiler or MPI setup).",
    tools: ["FEniCSx", "PETSc", "SLEPc", "Gmsh", "Palace"],
  },
  {
    title: "Simulation acceleration",
    body: "Parallel and GPU execution, reduced models from homogenization and modal expansions, and machine learning surrogates when a design loop needs thousands of evaluations.",
    tools: ["MPI", "GPU", "homogenization", "ML surrogates"],
  },
];
