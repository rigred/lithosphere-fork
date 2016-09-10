 > This is a fork of https://bitbucket.org/pyalot/lithosphere/
 > Credit goes to the Original Creator [Florian Bösch](https://github.com/pyalot)
 > The associated website can be found here http://lithosphere.codeflow.org/
  
Lithosphere is a GPU driven terrain generator. It allows you to create and export material textures and heightmaps intended for use in realtime graphics applications.

All terrain algorithms are implemented as GLSL fragment shaders operating on floating point textures. This allows realtime modification of the terrain. A graph of nodes is evaluated in order to arrive at the terrain output.
Features

 * Realtime terrain modification
 * Save/Open of scene.lth files
 * Simplex noise height source
 * Wind and Erosion algorithms
 * Gaussian Filtering
 * Mixing and Adjusting
 * Mathemathical operators
 * Float array and DXF mesh export
 * PNG texture export

## Requirements

## Lithosphere requires a fast computer and graphics card to operate. It also requires specific opengl compatibility

 * OpenGL shading language version 1.20
 * GL_ARB_texture_float
 * GL_ARB_pixel_buffer_object
 * GL_ARB_vertex_buffer_object
 * GL_ARB_framebuffer_object

## Recommended system specs

 * Intel Quad Core CPU
 * 2gb RAM
 * Nvidia Geforce GTX-285
 * 1gb video ram

## Working with

 * Nvidia Geforce GTX-285
 * Nvidia Geforce 8800 GTS
 * Nvidia Quadro FX1700 512mb

## Not working with

 * Intel Corporation Mobile GM965/GL960 Integrated Graphics Controller (no floating point textures)
 * Mac OSX Leopard (comes with python2.5, you can install python2.6)
 * Geforce 7700 (too slow)
 * Multiple grapics cards in use on the system (non SLI, tri-monitor setups etc., OpenGL context sharing does not work in such setups)

## License

Lithosphere is licenced as AGPL version 3.0 or above.

## Who

Lithosphere is written by Florian Bösch (facebook, linkedin)
