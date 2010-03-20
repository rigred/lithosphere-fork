/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/

#version 120 core

uniform sampler2D texture;
uniform sampler2D filter_weight;
uniform vec2 offsets;
const float pih = 1.0/(3.14159265358979323846264*0.5);
uniform bool invert, shallow, rough, slope;

vec3 get(vec2 uv){
    float height = texture2D(texture, vec2(uv)).r;
    return vec3(uv.s, height, uv.t);
}

void main(){
    vec2 uv = gl_TexCoord[0].st;
    float s = offsets.x;
    float t = offsets.y;

    float weight = texture2D(filter_weight, uv).r;
    vec3 pos = get(uv);
    vec3 left = get(uv+vec2(-s, 0.0));
    vec3 right = get(uv+vec2(s, 0.0));
    vec3 top = get(uv+vec2(0.0, t));
    vec3 bottom = get(uv+vec2(0.0, -t));
    vec3 left_top = get(uv+vec2(-s, t));
    vec3 right_top = get(uv+vec2(s, t));
    vec3 left_bottom = get(uv+vec2(-s, -t));
    vec3 right_bottom = get(uv+vec2(s, -t));

    vec4 a = vec4(left.y, right.y, top.y, bottom.y);
    vec4 b = vec4(left_top.y, right_top.y, left_bottom.y, right_bottom.y);
    
    vec4 comparision;
    float count = 1.0;
    float sum = pos.y;
    float result;

    if(invert){
        comparision = vec4(greaterThan(a, vec4(pos.y)));
        count += dot(comparision, comparision);
        sum += dot(comparision, a);

        if(!rough){
            comparision = vec4(greaterThan(b, vec4(pos.y)));
            count += dot(comparision, comparision);
            sum += dot(comparision, b);
        }
    }
    else{
        comparision = vec4(lessThan(a, vec4(pos.y)));
        count += dot(comparision, comparision);
        sum += dot(comparision, a);

        if(!rough){
            comparision = vec4(lessThan(b, vec4(pos.y)));
            count += dot(comparision, comparision);
            sum += dot(comparision, b);
        }
    }

    if(slope){
        vec3 normal = normalize(vec3(
            left.y - right.y,
            s+t,
            bottom.y - top.y
        ));
        float factor = dot(normal, vec3(0.0, 1.0, 0.0));
        if(shallow){
            factor = 1.0-factor;
        }
        else{
            factor = factor-0.05*count;
        }
        result = mix(sum/count, pos.y, factor);
    }
    else{
        result = sum/count;
    }

    result = mix(result, pos.y, clamp(weight, 0.0, 1.0));

    gl_FragColor = vec4(result);
}
