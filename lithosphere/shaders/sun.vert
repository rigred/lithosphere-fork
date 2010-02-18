varying vec3 normal;

void main(void){
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_FrontColor = gl_Color;
    normal = gl_Normal;
    gl_Position = ftransform();
}
