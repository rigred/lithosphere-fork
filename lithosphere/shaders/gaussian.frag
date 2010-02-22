uniform vec2 offsets;
uniform sampler2D texture;
const float a = 1.0/36.0;
const float b = 4.0/36.0;
const float c = 16.0/36.0;

float get(float s, float t){
    return texture2D(texture, vec2(s, t)).r;
}

void main(void){
    vec2 uv = gl_TexCoord[0].st;
    float s=uv.s;
    float t=uv.t;
    float x=offsets.x;
    float y=offsets.y;
    float result = (
        a*get(uv.s-x, uv.t-y) + b*get(uv.s  , uv.t-y) + a*get(uv.s+x, uv.t-y) +
        b*get(uv.s-x, uv.t  ) + c*get(uv.s  , uv.t  ) + b*get(uv.s+x, uv.t  ) +
        a*get(uv.s-x, uv.t+y) + b*get(uv.s  , uv.t+y) + a*get(uv.s+x, uv.t+y)
    );
    gl_FragColor = vec4(result);
}
