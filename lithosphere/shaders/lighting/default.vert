void main(void){
    gl_TexCoord[0].st = gl_Vertex.xz;
    gl_FrontColor = gl_Color;
    gl_Position = ftransform();
}
