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
    title: "Computational electromagnetics",
    body: "Full-wave simulation using FEM, FDTD and BEM. Modal analysis, scattering and resonance problems.",
    tools: ["FEM", "FDTD", "BEM", "modal analysis"],
  },
  {
    title: "Multiphysics modelling",
    body: "Coupled electromagnetic, thermal, mechanical and electronic simulations. Device-level multiphysics with custom solver integration.",
    tools: ["EM", "thermal", "mechanical", "electronic"],
  },
  {
    title: "Custom solver development",
    body: "Tailored numerical solvers in Python with FEniCSx, dolfinx, SLEPc and PETSc for HPC applications.",
    tools: ["FEniCSx", "dolfinx", "SLEPc", "PETSc"],
  },
  {
    title: "Simulation acceleration",
    body: "Performance optimization via parallel computing, GPU acceleration, and machine learning surrogates for inverse design.",
    tools: ["parallel", "GPU", "ML surrogates", "inverse design"],
  },
];
