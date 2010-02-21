uniform sampler2D texture;
uniform bool invert;
uniform vec2 offsets;
const float pi = 3.14159265358979323846264;

const float get(vec2 neighbor){
    return texture2D(texture, neighbor).r;
}

const vec2 neighbors[] = {
    vec2(1, 1),
    vec2(-1, -1),
    vec2(-1, 1),
    vec2(1, -1),
    vec2(-1, 0),
    vec2(0, 1),
    vec2(0, -1),
    vec2(1, 0)
};

vec3 get_normal(vec3 pos, vec3 neighbor_pos){
    vec3 neighbor_vec = neighbor_pos-pos;
    vec3 perp = cross(neighbor_vec, vec3(0.0, 1.0, 0.0));
    return normalize(cross(neighbor_vec, perp));
}

void main(){
    vec2 uv = gl_TexCoord[0].st;
    float height = get(uv);
    float count = 1.0;
    float result = height;
    vec3 pos = vec3(uv.x, height, uv.y);
    
    int i;
    float value;
    vec2 neighbor;
    vec3 neighbor_pos, normal;

    for(i=0; i<8; i++){
        neighbor = uv + neighbors[i] * offsets;
        value = get(neighbor);
        neighbor_pos = vec3(neighbor.x, value, neighbor.y);
        normal += get_normal(pos, neighbor_pos);

        if(i>3){
            if(invert){
                if(value > height){
                    result += value;
                    count += 1.0;
                }
            } else{
                if(value < height){
                    result += value;
                    count += 1.0;
                }
            }
        }
    }
    normal = normalize(normal/8.0);
    result = result/count;
    float factor = clamp(1.0 + dot(normal, vec3(0.0, 1.0, 0.0)), 0.05, 0.95);
    gl_FragColor = vec4(mix(height, result, factor));
}
