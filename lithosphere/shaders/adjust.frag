/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/
uniform sampler2D texture;
uniform float factor, offset;

void main(void){
    vec2 pos = gl_TexCoord[0].st;
    float value = texture2D(texture, pos).r;
    value = value * factor + offset;
    gl_FragColor = vec4(value);
}
