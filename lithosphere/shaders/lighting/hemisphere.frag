uniform vec3 ground_color, sky_color, ambient;
varying vec3 frag_normal, pos, frag_lightdir;

void main(){
    vec3 normal = normalize(frag_normal);
    vec3 lightdir = normalize(frag_lightdir);

    const float costheta = max(0.0, dot(normal, lightdir));
    const float a = 0.5 + 0.5 * costheta;
    vec3 diffuse = gl_Color.rgb * mix(ground_color, sky_color, a);

    gl_FragColor = vec4(diffuse + ambient, gl_Color.w);
}
