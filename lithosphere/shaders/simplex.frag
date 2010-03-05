/*
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
*/
uniform float height, size, offset;
uniform int p[256];
uniform vec2 grad[12];

float F2 = 0.5*(sqrt(3.0)-1.0);
float G2 = (3.0-sqrt(3.0))/6.0;

int modulo(int a, int b){
    int tmp = a/b;
    return a-tmp*b;
}

int perm(int index){
    return p[modulo(index, 256)];
}

float noise(vec2 value){
    float n0, n1, n2;
    float s = (value.x+value.y)*F2;
    int i = int(floor(value.x+s));
    int j = int(floor(value.y+s));
    float t = float(i+j)*G2;
    vec2 xy0 = value-vec2(float(i)-t, float(j)-t);
    
    int i1, j1;

    if(xy0.x>xy0.y){i1=1; j1=0;}
    else{i1=0; j1=1;}

    vec2 xy1 = xy0 - vec2(i1, j1) + G2;
    vec2 xy2 = xy0 - 1.0 + 2.0 * G2;
   
    int ii = i&255;
    //int ii = int(frac(float(i)/256.0)*256.0);
    int jj = j&255;
    //int jj = int(frac(float(j)/256.0)*256.0);

    int gi0 = modulo(perm(ii+perm(jj)), 12);
    int gi1 = modulo(perm(ii+i1+perm(jj+j1)), 12);
    int gi2 = modulo(perm(ii+1+perm(jj+1)), 12);

    float t0 = 0.5 - xy0.x*xy0.x-xy0.y*xy0.y;
    if(t0<0.0) n0 = 0.0;
    else {
        t0 *= t0;
        n0 = t0 * t0 * dot(grad[gi0], xy0);
    }
    float t1 = 0.5 - xy1.x*xy1.x-xy1.y*xy1.y;
    if(t1<0.0) n1 = 0.0;
    else {
        t1 *= t1;
        n1 = t1 * t1 * dot(grad[gi1], xy1);
    }
    float t2 = 0.5 - xy2.x*xy2.x-xy2.y*xy2.y;
    if(t2<0.0) n2 = 0.0;
    else {
        t2 *= t2;
        n2 = t2 * t2 * dot(grad[gi2], xy2);
    }
    return 38.0 * (n0 + n1 + n2) + 0.48;
}

void main(){
    float value = noise((gl_TexCoord[0].xy-0.5)*size+offset)*height;
    gl_FragColor = vec4(value, value, value, 1.0);
}
