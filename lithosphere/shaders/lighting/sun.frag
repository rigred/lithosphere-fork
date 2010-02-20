uniform vec3 color, ambient, direction;
varying vec3 normal, pos, lightdir;

void main(){
    vec3 surface_normal = normalize(normal);
    vec3 incident_direction = normalize(lightdir);
    vec3 costheta = max(0.0, dot(surface_normal, incident_direction));
    vec3 diffuse = color * gl_Color.rgb * costheta;
    gl_FragColor = vec4(diffuse + ambient, gl_Color.w);
}
