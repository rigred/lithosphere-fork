/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/

#version 120 core

void main(void){
    gl_TexCoord[0].st = gl_Vertex.xz;
    gl_FrontColor = gl_Color;
    gl_Position = ftransform();
}
