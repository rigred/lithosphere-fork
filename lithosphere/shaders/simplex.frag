uniform float height, size, offset;
uniform sampler2D texture;

const int p[256] = {151,160,137,91,90,15,
131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180};

const vec2 grad[] = {
    vec2(1,1),vec2(-1,1),vec2(1,-1),vec2(-1,-1),
    vec2(1,0),vec2(-1,0),vec2(1,0),vec2(-1,0),
    vec2(0,1),vec2(0,-1),vec2(0,1),vec2(0,-1)
};

const float F2 = 0.5*(sqrt(3.0)-1.0);
const float G2 = (3.0-sqrt(3.0))/6.0;

int perm(const int index){
    return p[index%256];
}

float noise(const vec2 value){
    float n0, n1, n2;
    const float s = (value.x+value.y)*F2;
    const int i = floor(value.x+s);
    const int j = floor(value.y+s);
    const float t = (i+j)*G2;
    const vec2 xy0 = value-vec2(i-t, j-t);
    
    int i1, j1;

    if(xy0.x>xy0.y){i1=1; j1=0;}
    else{i1=0; j1=1;}

    const vec2 xy1 = xy0 - vec2(i1, j1) + G2;
    const vec2 xy2 = xy0 - 1.0 + 2.0 * G2;
    
    const int ii = i & 255;
    const int jj = j & 255;

    const int gi0 = perm(ii+perm(jj)) % 12;
    const int gi1 = perm(ii+i1+perm(jj+j1)) % 12;
    const int gi2 = perm(ii+1+perm(jj+1)) % 12;

    float t0 = 0.5 - xy0.x*xy0.x-xy0.y*xy0.y;
    if(t0<0) n0 = 0.0;
    else {
        t0 *= t0;
        n0 = t0 * t0 * dot(grad[gi0], xy0);
    }
    float t1 = 0.5 - xy1.x*xy1.x-xy1.y*xy1.y;
    if(t1<0) n1 = 0.0;
    else {
        t1 *= t1;
        n1 = t1 * t1 * dot(grad[gi1], xy1);
    }
    float t2 = 0.5 - xy2.x*xy2.x-xy2.y*xy2.y;
    if(t2<0) n2 = 0.0;
    else {
        t2 *= t2;
        n2 = t2 * t2 * dot(grad[gi2], xy2);
    }
    return 38.0 * (n0 + n1 + n2) + 0.48;
}

void main(){
    float start = texture2D(texture, gl_TexCoord[0].st).r;
    gl_FragColor = start + vec4(noise((gl_TexCoord[0].xy-0.5)*size+offset)) * height;
}
