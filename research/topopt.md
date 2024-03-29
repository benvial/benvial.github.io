---
layout: page
title: "Topology Optimization"
description: ""
weight: 2
sublink: true
---
I am interrested in optimizing the shape of photonic and microwave devices for various applications and control of electromagnetic waves.

<section id="hero" class="section ">
  <div class="container">
    <div class="row">
    <h2>Open-Source Inverse Photonic Design</h2>
    <div class="col-md-4 col-sm-6 ">
    <img src="{{ "/images/research/metasurface.png"  | prepend: site.baseurl | prepend: site.url }}" class="img-responsive" alt="">
    </div>
    <div class="col-md-7 col-sm-6 ">
      <p>
        In recent years, technological advances in nanofabrication have opened up new applications in the field of nanophotonics. To engineer and develop novel functionalities, rigorous and efficient numerical methods are required. In parallel, tremendous advances in algorithmic differentiation, in part pushed by the intensive development of machine learning and artificial intelligence, has made possible large-scale optimization of devices with a few extra modifications of the underlying code. We present here our development of three different software libraries for solving Maxwell’s equations in various contexts: a finite element code with a high-level interface for problems commonly encountered in photonics, an implementation of the Fourier modal method for multilayered bi-periodic metasurfaces and a plane wave expansion method for the calculation of band diagrams in two-dimensional photonic crystals. All of them are endowed with automatic differentiation capabilities and we present typical inverse design examples.
        </p>
        <h4>Related article</h4>
        <ul class="biblio">
            <li  >B. Vial, and Y. Hao, <em  >Open-Source Computational Photonics with Auto Differentiable Topology Optimization</em>. Mathematics&nbsp;10&nbsp;(20), (2022)<span class="biblinks" > <a href="https://doi.org/10.3390/math10203912" ><i class="fa fa-link" > </i> DOI</a> | <a href="https://www.mdpi.com/2227-7390/10/20/3912" ><i class="fa fa-download" > </i> URL</a></span></li>
        </ul>
      </div>
    </div>
  </div>
        <div class="row">
      <div class="col-md-5 col-sm-6 ">
          <img src="{{ "/images/research/videos/animation_gyptis_TM.gif"  | prepend: site.baseurl | prepend: site.url }}" class="img-responsive" alt="">
        </div>
      <div class="col-md-7 col-sm-6 ">
          <img src="{{ "/images/research/opt_pho_superscatt.png"  | prepend: site.baseurl | prepend: site.url }}" class="img-responsive" alt="">
        </div>
        </div>
  </section>
    
<!-- ################################################################################################ -->

<section id="hero" class="section ">
  <div class="row">
    <h2>Illusion device</h2>
      <div class="col-md-4 col-sm-6 ">
      <img src="{{ "/images/research/illusion_fab.jpg"  | prepend: site.baseurl | prepend: site.url }}" class="img-responsive" alt="">
      </div>
      <div class="col-md-7 col-sm-6 ">
            <p>
            We report the design, fabrication and experimental verification of an illusion device working at microwave frequencies. A two dimensional topology optimization procedure is employed to find the binary layout of a dielectric coating that, when wrapped around a metallic cylinder, mimics the scattering from a predefined, arbitrarily-shaped dielectric object. Fabrication is carried out with 3D-printing and spatially resolved near field measurements in a waveguide configuration were performed, allowing us to map the illusion effect. Our work provides general guidelines for engineering electromagnetic illusions but can be extended to shape the near and far-field radiations using low index isotropic materials.
            </p>
        <h4>Related article</h4>
          <ul class="biblio">
            <li  >B. Vial, M. Torrico, and Y. Hao, <em  >Optimized microwave illusion device</em>. Sci Rep&nbsp;7&nbsp;(1):3929, (2017)<span class="biblinks" > <a href="https://doi.org/10.1038/s41598-017-04410-4" ><i class="fa fa-link" > </i> DOI</a> | <a href="https://doi.org/10.1038/s41598-017-04410-4" ><i class="fa fa-download" > </i> URL</a></span></li>
          </ul>
      </div>
      </div>
      <div class="imagebox">
        <div class="row">
          <img src="{{ "/images/research/illusion_fields.jpg"  | prepend: site.baseurl | prepend: site.url }}" class="img-responsive" alt="">
        </div>
      </div>
</section>


<section id="hero" class="section ">
  <div class="container">
    <div class="row">
    <h2>Invisibility cloaking</h2>
    <div class="col-md-4 col-sm-6 ">
    <img src="{{ "/images/research/cloak.png"  | prepend: site.baseurl | prepend: site.url }}" class="img-responsive" alt="">
    </div>
    <div class="col-md-7 col-sm-6 ">
      <p>
        I designed an all-dielectric cloaking device at microwave frequencies. A gradient based topology optimization is employed to find a dielectric permittivity distribution that minimizes the diffracted field in free space. The layout is binary, i.e. made either of standard ABS plastic or air and is designed to reduce the scattering from an ABS cylinder excited by a line source for TE polarization. We study the performances of cloaks optimized for one, two and three frequencies in terms of scattering reduction and correlations with respect to the free space propagation case. Finally, a modal analysis is carried out providing physical insights on the resonant cloaking mechanism at stake.
        </p>
        <h4>Related article</h4>
        <ul class="biblio">
            <li  >B. Vial, and Y. Hao, <em  >Topology optimized all-dielectric cloak: Design, performances and modal picture of the invisibility effect</em>. Opt. Express&nbsp;23&nbsp;(18):23551, (2015)<span class="biblinks" > <a href="https://doi.org/10.1364/oe.23.023551" ><i class="fa fa-link" > </i> DOI</a> | <a href="https://doi.org/10.1364/oe.23.023551" ><i class="fa fa-download" > </i> URL</a></span></li>
        </ul>
      </div>
    </div>
  </div>
  </section>
    
    