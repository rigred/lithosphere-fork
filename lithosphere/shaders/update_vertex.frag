/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/

#version 120 core

uniform sampler2D heightmap;

vec3 get(vec2 uv){
    float height = texture2D(heightmap, vec2(uv.s, uv.t)).r;
    return vec3(uv.s, height, uv.t);
}

void main(void){
    vec2 uv = gl_TexCoord[0].st;
    vec3 pos = get(uv);
    gl_FragData[0] = vec4(pos.x, pos.y, pos.z, 1.0);
}
