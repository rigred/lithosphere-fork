void main(void){
    vec2 uv = gl_TexCoord[0].st;
    gl_FragData[0] = vec4(uv.s, 0.0, uv.t, 1.0);
    gl_FragData[1] = vec4(0.0, 1.0, 0.0, 1.0);
}
