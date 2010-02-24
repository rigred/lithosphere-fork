uniform sampler2D texture;
uniform vec2 offsets;
const float pih = 1.0/(3.14159265358979323846264*0.5);
uniform bool invert, shallow, rough;

const vec2 neighbors[] = {
    vec2(-1, 0),
    vec2(0, 1),
    vec2(0, -1),
    vec2(1, 0),
    vec2(1, 1),
    vec2(-1, -1),
    vec2(-1, 1),
    vec2(1, -1)
};


vec3 get(vec2 uv){
    float height = texture2D(texture, vec2(uv));
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

void main(){
    vec2 uv = gl_TexCoord[0].st;
    vec3 pos = get(uv);

    float count = 1.0;
    float result = pos.y;
    int end = 8;
    if(rough){
        end = 4;
    }

    for(int i=0; i<end; i++){
        vec3 neighbor = get(uv+neighbors[i]*offsets);
        if(invert){
            if(neighbor.y > pos.y){
                result += neighbor.y;
                count += 1.0;
            }
        }
        else{
            if(neighbor.y < pos.y){
                result += neighbor.y;
                count += 1.0;
            }
        }
    }
    vec3 normal = get_normal(pos);
    //float factor = 1.0-acos(dot(normal, vec3(0.0, 1.0, 0.0)))*pih;
    float factor = dot(normal, vec3(0.0, 1.0, 0.0));
    if(shallow){
        factor = 1.0-factor;
    }
    else{
        factor = factor-0.05*count;
    }
    result = mix(result/count, pos.y, factor);
    gl_FragColor = vec4(result);
}
