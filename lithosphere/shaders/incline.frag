/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/
uniform vec2 offsets;
uniform float offset;
uniform float factor;
uniform sampler2D heightmap;
uniform bool invert;
const float pih = 3.14159265358979323846264*0.5;

vec3 get(float s, float t){
    float height = texture2D(heightmap, vec2(s, t));
    return vec3(s, height, t);
}

vec3 get_normal(vec3 p){
    float x = offsets.x;
    float z = offsets.y;
    return normalize(vec3(
        get(p.x-x, p.z).y - get(p.x+x, p.z).y,
        x+z,
        get(p.x, p.z-z).y - get(p.x, p.z+z).y
    ));
}

void main(void){
    vec2 uv = gl_TexCoord[0].st;
    vec3 pos = get(uv.s, uv.t);
    vec3 normal = get_normal(pos);
    float result = dot(normal, vec3(0.0, 1.0, 0.0));
    result = result * factor + offset;
    if(invert){
        gl_FragColor = vec4(1.0-result);
    }
    else{
        gl_FragColor = vec4(result);
    }
}
