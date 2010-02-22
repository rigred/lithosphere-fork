uniform sampler2D op1;
uniform sampler2D op2;
uniform sampler2D alpha;

void main(void){
    vec2 pos = gl_TexCoord[0].st; 
    gl_FragColor = mix(texture2D(op1, pos), texture2D(op2, pos), texture2D(alpha, pos));
}
