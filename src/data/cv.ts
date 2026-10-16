// Curriculum vitae. Periods are display strings; most recent first.

export type CvItem = { title: string; where: string; period: string; detail?: string };

export const positions: CvItem[] = [
  {
    title: "Freelance software developer",
    where: "Bras, France",
    period: "Oct. 2025 – present",
    detail:
      "Consulting and open-source software development. Contributing to gsim, a GDSFactory plugin for full-wave electromagnetic simulation in photonics and electronics.",
  },
  {
    title: "Research Associate",
    where: "Imperial College London",
    period: "Aug. 2022 – Aug. 2025",
    detail:
      "METAVEH project: high-frequency homogenization in dispersive media for vibration energy harvesting with metamaterials.",
  },
  {
    title: "Research Assistant",
    where: "Queen Mary, University of London",
    period: "Jan. 2019 – Jul. 2022",
    detail:
      "ANIMATE project: nonlinear coupling and homogenization of ferroelectric metamaterials, inverse design for tunability, microwave and THz material characterization.",
  },
  {
    title: "Research Assistant",
    where: "Queen Mary, University of London",
    period: "Jan. 2017 – Dec. 2018",
    detail:
      "AOTOMAT project: optimization tools and machine learning for the design of electromagnetic devices and materials.",
  },
  {
    title: "Research Assistant",
    where: "Queen Mary, University of London",
    period: "Jul. 2014 – Dec. 2016",
    detail:
      "QUEST project: transformation optics applied to invisibility cloaks and metamaterial-based devices. Simulation tools and topology optimization for exotic material properties.",
  },
  {
    title: "Research Assistant",
    where: "Institut Fresnel, Marseille",
    period: "Nov. 2013 – Jan. 2014",
    detail:
      "Resonant optical antennas: coupling of light to subwavelength particles, modal analysis of electric and magnetic resonances for emission pattern shaping.",
  },
  {
    title: "Research Assistant",
    where: "Institut Fresnel, Marseille",
    period: "May 2013 – Oct. 2014",
    detail:
      "Ray tracing in complex media, inverse index distribution problems, deshomogenization with graded-index photonic crystals.",
  },
  {
    title: "PhD in Physics",
    where: "Institut Fresnel and Silios Technologies",
    period: "Oct. 2009 – Apr. 2013",
    detail:
      "Study of open electromagnetic resonators by modal approach (CIFRE scholarship). FEM eigenmode analysis of bi-periodic diffractive structures. Design, fabrication and characterization of metamaterial-based infrared filters.",
  },
  {
    title: "MS research internship",
    where: "LMA, CNRS, Marseille",
    period: "Apr. 2009 – Sept. 2009",
    detail: "Model order reduction of reed instruments for sound synthesis via proper orthogonal decomposition.",
  },
];

export const education: CvItem[] = [
  {
    title: "PhD in Physics",
    where: "Institut Fresnel, CNRS, Centrale Marseille",
    period: "Apr. 2013",
    detail: "Optics, Photonics and Image Processing",
  },
  {
    title: "Master's degree in Physics",
    where: "Centrale Marseille / LMA, CNRS",
    period: "Oct. 2009",
    detail: "Mechanics, Physics and Engineering, specialization in Acoustics",
  },
  {
    title: "Master's degree in Engineering",
    where: "Centrale Marseille",
    period: "Oct. 2009",
    detail: "High-level scientific and technical training",
  },
];

export const teaching: CvItem[] = [
  {
    title: "PhD co-supervision",
    where: "Imperial College London",
    period: "Feb. 2023 – Sept. 2023",
    detail: "Visiting student from Politecnico di Milano. Isospectral open cavities and curvilinear homogenization.",
  },
  {
    title: "Summer project supervision",
    where: "Imperial College London",
    period: "Jul. 2023 – Sept. 2023",
    detail: "Applied mathematics undergraduate project on optimizing dispersion in discrete phononic lattices (3 months).",
  },
  {
    title: "Teaching assistant",
    where: "Queen Mary, University of London",
    period: "2019",
    detail: "Quantum Programming: lectures, tutorials and coding projects in Q# and Python for 10 Master students.",
  },
  {
    title: "PhD co-supervision",
    where: "Queen Mary, University of London",
    period: "Sept. 2018 – Apr. 2022",
    detail: "Data-driven optimization of metasurfaces (2 PhD students).",
  },
  {
    title: "Undergraduate project co-supervision",
    where: "Queen Mary, University of London",
    period: "Nov. 2018 – Apr. 2019",
    detail: "Multidisciplinary project on detecting emotions with physiological and microwave measurements (4 students).",
  },
  {
    title: "Internship supervisor",
    where: "Institut Fresnel, CNRS",
    period: "2012",
    detail: "Optimization of diffractive infrared filters for multispectral imaging (1 engineering student, 6 months).",
  },
  {
    title: "Project tutor",
    where: "Institut Fresnel, CNRS",
    period: "2011",
    detail: "Design of high-efficiency solar cells with metamaterials (5 students, 2 months).",
  },
];

export const awards: CvItem[] = [
  {
    title: "Best PhD Thesis 2013",
    where: "Doctoral School 352, Physics and Condensed Matter Science",
    period: "2014",
  },
  {
    title: "Best PhD Thesis 2013",
    where: "CNano PACA, nanosciences and nanotechnologies cluster",
    period: "2014",
    detail: "Finalized research category",
  },
];

export const skills = [
  { label: "Languages", value: "Python, Matlab, C, C++, Mathematica, Q#, LaTeX, HTML, CSS" },
  { label: "Tools", value: "git, FEniCS, COMSOL Multiphysics, Gmsh, GetDP, Gsolver, Gimp, LibreOffice, Labview" },
  { label: "Spoken", value: "French (mother tongue), English (fluent), Spanish (basic)" },
  {
    label: "Interests",
    value:
      "Optics, photonics, metamaterials, wave physics, light-matter interaction, homogenization, computational electromagnetics, optimization, inverse design, finite element and Fourier modal methods, machine learning, transformation optics, open-source science",
  },
  { label: "Outside work", value: "Music, guitar, football, snowboard, hiking, traveling, cooking" },
];
