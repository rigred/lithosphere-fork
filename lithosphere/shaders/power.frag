uniform sampler2D op1;
uniform sampler2D op2;

void main(void){
    vec2 pos = gl_TexCoord[0].st; 
    gl_FragColor = pow(texture2D(op1, pos), texture2D(op2, pos));
}
