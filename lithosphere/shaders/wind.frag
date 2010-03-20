/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/

#version 120 core

uniform sampler2D texture;
uniform sampler2D filter_weight;
uniform vec2 offsets;
const float pi = 3.14159265358979323846264;
uniform float direction, strengh, strengh2, x;

vec3 get(vec2 uv){
    float height = texture2D(texture, vec2(uv)).r;
    return vec3(uv.s, height, uv.t);
}

vec3 get_normal(vec3 p){
    float x = offsets.x;
    float z = offsets.y;
    return normalize(vec3(
        get(vec2(p.x-x, p.z)).y - get(vec2(p.x+x, p.z)).y,
        x+z,
        get(vec2(p.x, p.z-z)).y - get(vec2(p.x, p.z+z)).y
    ));
}

float sample(vec2 uv, float s, float t){
    return get(vec2(uv.s+s*offsets.s, uv.t+t*offsets.s)).y;
}

void main(){
    float dir = direction * pi * 2.0;
    vec2 uv = gl_TexCoord[0].st;
    vec3 pos = get(uv);
    float weight = texture2D(filter_weight, uv).r;
    float low = min(sample(uv, cos(dir), cos(dir+pi/2.0)), pos.y);
    float high = sample(uv, cos(dir-pi), cos(dir-pi/2.0));
    vec3 normal = get_normal(pos);
    float factor = dot(normal, vec3(0, 1, 0));
    float height = (mix(pos.y, low, factor*strengh2) + mix(pos.y, high, acos(factor)*strengh))/2.0;
    height = mix(height, pos.y, clamp(weight, 0.0, 1.0));
    gl_FragColor = vec4(height);
}
