/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/
void main(void){
    vec2 uv = gl_TexCoord[0].st;
    gl_FragData[0] = vec4(uv.s, 0.0, uv.t, 1.0);
}
