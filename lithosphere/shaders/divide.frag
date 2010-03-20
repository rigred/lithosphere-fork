/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/

#version 120 core

uniform sampler2D op1;
uniform sampler2D op2;

void main(void){
    vec2 pos = gl_TexCoord[0].st; 
    gl_FragColor = texture2D(op1, pos) / texture2D(op2, pos);
}
