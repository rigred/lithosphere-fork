/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/

#version 120 core

uniform sampler2D texture;
uniform float factor, offset;
uniform bool invert;
uniform bool do_clamp;

void main(void){
    vec2 pos = gl_TexCoord[0].st;
    vec4 value = texture2D(texture, pos);
    value = value * factor + offset;
    if(invert){
        value = 1.0-value;
    }
    if(do_clamp){
        value = clamp(value, 0.0, 1.0);
    }
    gl_FragColor = value;
}
