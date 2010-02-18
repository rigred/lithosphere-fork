uniform vec3 color;
uniform vec3 ambient;
uniform vec3 direction;
varying vec3 normal;

void main(){
    vec3 surface_normal = normalize(normal);
    vec3 incident_direction = normalize(direction);
    vec3 dot_surface_incident = dot(surface_normal, incident_direction);
    vec3 diffuse = color * gl_Color.rgb * dot_surface_incident;
    gl_FragColor.rgb = diffuse + ambient;
    gl_FragColor.w = gl_Color.w;
}
