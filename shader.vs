#version 150

// Model-view Projection
uniform mat4 mvp;
// Object Projection
uniform mat4 objp;
// Offset possition per instance
uniform vec4 objoffset[125];

in vec4 vs_position;
in vec4 vs_normal;
out vec4 fs_color;

void main() {
  fs_color = vec4((vs_normal.xyz/2.0)+0.5, 1.0);
  gl_Position = mvp * ((objp * vs_position) + objoffset[gl_InstanceID]);
}