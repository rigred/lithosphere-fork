uniform sampler2D texture;
uniform float factor, offset;

void main(void){
    vec2 pos = gl_TexCoord[0].st;
    float value = texture2D(texture, pos).r;
    value = value * factor + offset;
    gl_FragColor = vec4(value);
}
