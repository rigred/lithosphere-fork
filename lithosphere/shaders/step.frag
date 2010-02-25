uniform sampler2D texture;
uniform float low, high;

void main(void){
    vec2 pos = gl_TexCoord[0].st; 
    float height = texture2D(texture, pos);
    gl_FragColor = smoothstep(low, high, height);
}
