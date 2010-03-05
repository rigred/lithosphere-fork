/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/
uniform vec2 offsets;
uniform sampler2D heightmap;

vec3 get(vec2 uv){
    float height = texture2D(heightmap, vec2(uv.s, uv.t)).r;
    return vec3(uv.s, height, uv.t);
}

vec3 compute_normal(vec3 pos, vec3 neighbor_pos){
    vec3 neighbor_vec = neighbor_pos-pos;
    vec3 perp = cross(neighbor_vec, vec3(0.0, 1.0, 0.0));
    return normalize(cross(neighbor_vec, perp));
}

vec3 get_normal(vec3 p){
    float x = offsets.x;
    float z = offsets.y;
    // TODO maybe make this options, all models for normal calculation are interesting
    /*
    return normalize((
        compute_normal(p, get(vec2(p.x+x, p.z+z))) + 
        compute_normal(p, get(vec2(p.x-x, p.z-z))) + 
        compute_normal(p, get(vec2(p.x+x, p.z-z))) + 
        compute_normal(p, get(vec2(p.x-x, p.z+z))) + 
        compute_normal(p, get(vec2(p.x, p.z+z))) + 
        compute_normal(p, get(vec2(p.x, p.z-z))) + 
        compute_normal(p, get(vec2(p.x+x, p.z))) + 
        compute_normal(p, get(vec2(p.x-x, p.z)))
    )/8.0);
    return normalize((
        compute_normal(p, get(vec2(p.x, p.z+z))) + 
        compute_normal(p, get(vec2(p.x, p.z-z))) + 
        compute_normal(p, get(vec2(p.x+x, p.z))) + 
        compute_normal(p, get(vec2(p.x-x, p.z)))
    )/4.0);
    */
    return normalize(vec3(
        get(vec2(p.x-x, p.z)).y - get(vec2(p.x+x, p.z)).y,
        x+z,
        get(vec2(p.x, p.z-z)).y - get(vec2(p.x, p.z+z)).y
    ));
}

void main(void){
    vec2 uv = gl_TexCoord[0].st;
    vec3 pos = get(uv);
    vec3 normal = get_normal(pos);
    gl_FragData[0] = vec4(normal.x, normal.y, normal.z, 1.0);
    //gl_FragColor = vec4(0,1,0,1);
}
