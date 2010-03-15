/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/
uniform vec2 offsets;
uniform sampler2D texture;
uniform sampler2D filter_weight;

const float a = 1.0/36.0;
const float b = 4.0/36.0;
const float c = 16.0/36.0;

vec4 get(float s, float t){
    return texture2D(texture, vec2(s, t));
}

void main(void){
    vec2 uv = gl_TexCoord[0].st;
    float s=uv.s;
    float t=uv.t;
    float x=offsets.x;
    float y=offsets.y;
    vec4 pos = get(uv.s, uv.t);
    vec4 weight = texture2D(filter_weight, uv);
    vec4 result = (
        a*get(uv.s-x, uv.t-y) + b*get(uv.s  , uv.t-y) + a*get(uv.s+x, uv.t-y) +
        b*get(uv.s-x, uv.t  ) + c*pos                 + b*get(uv.s+x, uv.t  ) +
        a*get(uv.s-x, uv.t+y) + b*get(uv.s  , uv.t+y) + a*get(uv.s+x, uv.t+y)
    );
    result = mix(result, pos, clamp(weight, 0.0, 1.0));
    gl_FragColor = result;
}
