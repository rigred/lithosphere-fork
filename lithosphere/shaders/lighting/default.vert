uniform vec3 direction;
varying vec3 frag_normal, pos, frag_lightdir;

void main(void){
    //frag_normal = normalize(gl_NormalMatrix * gl_Normal);
    frag_normal = normalize(gl_Normal);
    pos = vec3(gl_ModelViewMatrix * gl_Vertex);
    frag_lightdir = normalize(direction);
    
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_FrontColor = gl_Color;
    gl_Position = ftransform();
}
