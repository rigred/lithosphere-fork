uniform sampler2D heightmap;

vec3 get(vec2 uv){
    float height = texture2D(heightmap, vec2(uv.s, uv.t));
    return vec3(uv.s, height, uv.t);
}

void main(void){
    vec2 uv = gl_TexCoord[0].st;
    vec3 pos = get(uv);
    gl_FragData[0] = vec4(pos.x, pos.y, pos.z, 1.0);
}
